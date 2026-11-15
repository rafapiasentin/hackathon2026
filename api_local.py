"""API de catálogo e consulta documental; modo local explícito sem revisão presumida."""
import os
import re

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from peewee import Case, DatabaseError, Expression, SQL, fn
from pydantic import BaseModel, Field

from banco import (Artigo, ArtigoDecreto, Carga, Decreto, Lei, LeiDecreto, PublicacaoLei, Relacao,
                   artigos_para_chatbot, conectar)
from busca_documental import (VERSAO_BUSCA, administrativa, avaliar, contem, ementa_limpa, ementa_sobre,
                              frase_resposta, normalizar_texto, numero_legivel, planejar, pontos_ementa,
                              refs_numero, termos_grupo)
from decretos import (ANEXO_ATUALIZADO_POR, EFICACIA_SUSPENSA_POR, REGULAMENTADA_POR, montar_camadas,
                      nome_decreto, preve_regulamentacao, redacoes_dadas)

AVISO = ('Consulta documental local: a situação foi informada pela Câmara; '
         'a revisão institucional de vigência ainda está pendente. '
         'Os trechos abaixo não substituem orientação jurídica.')
VETOR_LEI = SQL("to_tsvector('portuguese', coalesce(titulo, '') || ' ' || coalesce(ementa, ''))")
VETOR_ARTIGO = SQL("to_tsvector('portuguese', texto)")
SITUACOES = {'vigente', 'vigente_com_alteracoes', 'revogada', 'inexistente'}
def preparar_indices(db):
    with db.connection_context():
        db.execute_sql("CREATE INDEX IF NOT EXISTS lei_busca_pt ON lei USING gin "
                       "(to_tsvector('portuguese', coalesce(titulo, '') || ' ' || coalesce(ementa, '')))")
        db.execute_sql("CREATE INDEX IF NOT EXISTS artigo_busca_pt ON artigo USING gin "
                       "(to_tsvector('portuguese', texto))")


def resumo(lei, verificada=False):
    return dict(id=lei.id, chave=lei.chave, ano=str(lei.ano),
                data_lei=lei.data_lei.isoformat() if lei.data_lei else None,
                titulo=lei.titulo, ementa=lei.ementa, situacao=lei.situacao,
                link=lei.link, vigencia_verificada=verificada)


def _aprovadas():
    return PublicacaoLei.select(PublicacaoLei.lei_id).where(
        PublicacaoLei.estado == 'publicado', PublicacaoLei.vigencia_verificada == True)


def _catalogo(local):
    consulta = Lei.select()
    return consulta if local else consulta.where(Lei.id.in_(_aprovadas()))


def _curto(texto, limite=600):
    texto = ' '.join((texto or '').split())
    return texto if len(texto) <= limite else texto[:limite - 1].rstrip() + '…'


def decretos_das_leis(lei_ids):
    """{lei_id: [decreto + vínculo]}, um item por decreto e tipo de vínculo, com os dispositivos citados.
    Vazio quando a tabela de decretos ainda não foi carregada (carregar_decretos.py)."""
    if not lei_ids or not LeiDecreto.table_exists():
        return {}
    resultado = {}
    for v in LeiDecreto.select(LeiDecreto, Decreto).join(Decreto).where(LeiDecreto.lei_id.in_(list(lei_ids))):
        d = v.decreto
        item = resultado.setdefault(v.lei_id, {}).setdefault((d.id, v.tipo), dict(
            id=d.id, tipo=d.tipo, numero=d.numero, ano=d.ano, ementa=d.ementa, link=d.link,
            situacao=d.situacao, revogado_por=d.revogado_por, texto_disponivel=d.texto_disponivel,
            vinculo=v.tipo, dispositivos=[]))
        if v.dispositivo and v.dispositivo not in item['dispositivos']:
            item['dispositivos'].append(v.dispositivo)
    return {k: sorted(v.values(), key=lambda x: (x['situacao'] == 'revogado', -x['ano']))
            for k, v in resultado.items()}


def decretos_para_artigo(vinculados, artigo):
    """Decretos que importam para um artigo: suspensão só se atinge a lei toda ou este artigo;
    regulamentação e anexo valem para a lei toda (o decreto pode detalhar outro ponto dela)."""
    escolhidos = []
    for d in vinculados:
        dispositivos = d['dispositivos']
        if d['vinculo'] == EFICACIA_SUSPENSA_POR and dispositivos and artigo not in dispositivos:
            continue
        escolhidos.append(dict(d, dispositivo=artigo if artigo in dispositivos else None))
    return escolhidos


def artigo_de_decreto(decreto_ids, plano):
    """Artigo de decreto que responde à pergunta. A súmula dá o assunto ("Consulta Prévia de Parcelamento
    do Solo"); o próprio artigo precisa trazer ao menos um termo da pergunta."""
    if not decreto_ids:
        return None
    melhor = None
    termos = list(plano.grupos) + list(plano.complementares)
    consulta = (ArtigoDecreto.select(ArtigoDecreto, Decreto).join(Decreto)
                .where(ArtigoDecreto.decreto.in_(decreto_ids)).order_by(Decreto.ano.desc(), ArtigoDecreto.ordem))
    for a in consulta:
        evidencia = avaliar((a.decreto.ementa or '') + '\n' + a.texto, plano)
        if not evidencia:
            continue
        proprio = normalizar_texto(a.texto)
        if not any(contem(proprio, s, True) for g in termos for s in g):
            continue
        if melhor is None or evidencia['pontos'] > melhor[1]:
            melhor = (a, evidencia['pontos'])
    return melhor[0] if melhor else None


def frase_do_decreto(texto, plano):
    """Frase do artigo do decreto; se ela para numa enumeração ("documentos: I."), usa o artigo inteiro,
    porque a lista é justamente o detalhe que a lei não traz."""
    frase = frase_resposta(texto, plano)
    if re.search(r':\s*(?:[IVXL]+|[a-z]|\d+)?\s*[.)\-–]?\s*$', frase):
        corpo = re.sub(r'^\s*art\.?\s*\d+[º°o]?(?:-[A-Z])?\s*[.\-–]?\s*', '', ' '.join(texto.split()), flags=re.I)
        return _curto(corpo, 450)
    return frase


def repete(a, b):
    """True quando duas frases dizem praticamente o mesmo (o decreto copia a lei)."""
    pa, pb = (set(re.findall(r'\w{4,}', normalizar_texto(x))) for x in (a, b))
    return bool(pa and pb) and len(pa & pb) / len(pa | pb) >= 0.7


def leis_alteradoras(texto, consulta_catalogo, principal):
    """Leis citadas em "(Redação dada pela Lei nº ...)" no artigo, ligadas ao catálogo quando possível."""
    alteradoras = []
    for chave, ano in redacoes_dadas(texto)[:3]:
        if chave == principal['chave'] and (ano is None or str(ano) == principal['ano']):
            continue  # nota que cita a própria lei (erro comum de digitação na fonte)
        consulta = consulta_catalogo.where(Lei.chave == chave)
        if ano:
            consulta = consulta.where(Lei.ano == ano)
        achadas = list(consulta.limit(2))
        lei = achadas[0] if len(achadas) == 1 else None
        alteradoras.append(dict(lei_id=lei.id if lei else None, chave=chave, ano=str(lei.ano if lei else ano or ''),
                                link=lei.link if lei else None, ementa=ementa_limpa(lei.ementa) if lei else None,
                                situacao=lei.situacao if lei else None))
    return alteradoras


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=1, max_length=1000)


def create_app(db=None, catalogo_local=None):
    db = db or conectar()
    somente_local = (os.getenv('API_MODO_DOCUMENTAL_LOCAL', '').lower() == 'true'
                     if catalogo_local is None else catalogo_local)
    modo = os.getenv('API_MODO', 'governado')
    if modo not in ('governado', 'documental'):
        raise ValueError('API_MODO deve ser governado ou documental.')
    nuvem = bool(os.getenv('VERCEL') or os.getenv('RENDER'))
    if somente_local and nuvem:
        raise RuntimeError('Modo documental local não pode ser ativado nesta hospedagem.')
    if nuvem and not os.getenv('DATABASE_URL'):
        raise RuntimeError('DATABASE_URL é obrigatória na hospedagem.')
    # Consulta documental pública é um modo explícito de publicação,
    # sem alterar ou presumir aprovações institucionais na governança.
    local = somente_local or modo == 'documental'
    nome_modo = 'documental_local' if somente_local else 'documental' if local else 'governado'
    aviso = AVISO if somente_local else AVISO.replace('documental local', 'documental')
    app = FastAPI(title='Londrina Conecta', version='0.1.0')
    origens = os.getenv('CORS_ORIGINS', 'http://127.0.0.1:5173,http://localhost:5173').split(',')
    app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in origens],
                       allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

    @app.exception_handler(DatabaseError)
    async def falha_banco(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={'detail': 'Banco indisponível. Tente novamente.'})

    @app.get('/api/health')
    def health():
        with db.connection_context():
            carga = Carga.select().order_by(Carga.id.desc()).first()
            return dict(status='ok', banco='conectado', leis=Lei.select().count(),
                        artigos=Artigo.select().count(), modo=nome_modo,
                        versao_busca=VERSAO_BUSCA, consulta='PostgreSQL', modo_publicacao=nome_modo,
                        sha256=carga.sha256 if carga else None)

    @app.get('/api/leis')
    def buscar(q: str = Query('', max_length=1000), situacao: str | None = None,
               numero: str | None = Query(None, max_length=30), ano: int | None = None,
               pagina: int = Query(1, ge=1, le=10000)):
        if situacao and situacao not in SITUACOES:
            raise HTTPException(422, 'Situação inválida.')
        with db.connection_context():
            consulta = _catalogo(local)
            if situacao:
                consulta = consulta.where(Lei.situacao == situacao)
            if numero:
                consulta = consulta.where(Lei.chave == numero.replace('.', '').strip())
            elif q.strip():
                referencia = re.fullmatch(r'(?:lei\s*)?(\d[\d.]*)(?:/(\d{4}))?', q.strip(), re.I)
                if referencia:
                    consulta = consulta.where(Lei.chave == referencia[1].replace('.', ''))
                    if referencia[2]:
                        consulta = consulta.where(Lei.ano == int(referencia[2]))
                else:
                    consulta = consulta.where(Expression(VETOR_LEI, '@@', fn.websearch_to_tsquery('portuguese', q)))
            if ano is not None:
                consulta = consulta.where(Lei.ano == ano)
            total = consulta.count()
            leis = list(consulta.order_by(Lei.ano.desc(), Lei.id.desc()).paginate(pagina, 20))
            return dict(total=total, pagina=pagina, itens=[resumo(l, not local) for l in leis])

    @app.get('/api/leis/{lei_id}')
    def obter(lei_id: str):
        with db.connection_context():
            lei = _catalogo(local).where(Lei.id == lei_id).first()
            if not lei:
                raise HTTPException(404, 'Lei não encontrada no catálogo disponível.')
            return dict(resumo(lei, not local),
                artigos=[dict(ordem=a.ordem, artigo=a.artigo, texto=a.texto,
                              texto_riscado=a.texto_riscado, revogado=a.revogado)
                         for a in Artigo.select().where(Artigo.lei == lei_id).order_by(Artigo.ordem)],
                relacoes=[dict(tipo=r.tipo, id=r.lei_destino_id, chave=r.chave_destino or '')
                          for r in Relacao.select().where(Relacao.lei_origem == lei_id)],
                decretos=[dict(d, titulo=nome_decreto(d['tipo'], d['numero'], d['ano']))
                          for d in (decretos_das_leis([lei_id]).get(lei_id, []) if local else [])])

    @app.post('/api/perguntar')
    def perguntar(corpo: Pergunta):
        pergunta = corpo.pergunta.strip()
        if not pergunta:
            raise HTTPException(422, 'Informe uma pergunta.')
        def frequencias(grupos):
            # Frequência documental, somente leitura e com o mesmo escopo
            # de publicação da busca; não altera vigência ou governança.
            consulta = (Artigo.select().join(Lei).where(
                Lei.situacao.in_(['vigente', 'vigente_com_alteracoes']),
                Artigo.revogado == False, Artigo.texto != '')) if local else artigos_para_chatbot()
            return [consulta.where(Expression(VETOR_ARTIGO, '@@',
                fn.to_tsquery('portuguese', termos_grupo(g, True)))).count() for g in grupos]
        with db.connection_context():
            plano = planejar(pergunta, frequencias=frequencias)
        if plano.esclarecimento:
            return dict(resposta=plano.esclarecimento, fontes=[], ignoradas=[], modo='documental',
                        evidencia=dict(estado='precisa_contexto', versao_busca=VERSAO_BUSCA))
        termos = plano.termos_sql
        if not termos:
            return dict(resposta='Informe um assunto de legislação municipal ou busque uma lei pelo número.',
                        fontes=[], ignoradas=[], modo='documental',
                        evidencia=dict(estado='insuficiente', versao_busca=VERSAO_BUSCA))
        with db.connection_context():
            tsquery = fn.to_tsquery('portuguese', termos)
            if local:
                # Exceção somente local, explicitamente identificada. A consulta governada permanece intacta.
                consulta = (Artigo.select(Artigo, Lei).join(Lei).where(
                    Lei.situacao.in_(['vigente', 'vigente_com_alteracoes']),
                    Artigo.revogado == False, Artigo.texto != ''))
            else:
                consulta = artigos_para_chatbot()
            consulta = consulta.where(Expression(VETOR_ARTIGO, '@@', tsquery))
            # PostgreSQL gera candidatos; a relevância precisa passar pelo contrato de conceitos.
            # Complementos só ordenam: nunca ampliam ou restringem o conjunto
            # obrigatório, mas precisam pontuar antes do corte de 100 candidatos.
            cobertura = SQL('(0 + 0)')
            for grupo in plano.complementares:
                cobertura += Case(None, [(Expression(VETOR_ARTIGO, '@@',
                    fn.to_tsquery('portuguese', termos_grupo(grupo, True))), 1)], 0)
            candidatos = list(consulta.order_by(cobertura.desc(), fn.ts_rank_cd(VETOR_ARTIGO, tsquery, 2).desc(),
                                                Lei.ano.desc(), Artigo.lei, Artigo.ordem).limit(100))
            aceitos = []
            for artigo in candidatos:
                evidencia = avaliar(artigo.texto, plano)
                if evidencia:
                    evidencia['pontos'] += pontos_ementa(artigo.lei.ementa, plano)
                    if administrativa(artigo.lei.ementa):
                        evidencia['pontos'] *= 0.3
                    aceitos.append((artigo, evidencia))
            aceitos.sort(key=lambda item: (-item[1]['pontos'], -item[0].lei.ano, len(item[0].texto), item[0].lei_id, item[0].ordem))
            corte = aceitos[0][1]['pontos'] * 0.75 if aceitos else 0
            fontes = [dict(lei_id=a.lei_id, chave=a.lei.chave, ano=str(a.lei.ano),
                           ementa=a.lei.ementa, situacao=a.lei.situacao, artigo=a.artigo,
                           trecho=e['trecho'], link=a.lei.link, vigencia_verificada=not local)
                      for a, e in aceitos[:3] if e['pontos'] >= corte]
            camadas, alertas = [], []
            if not fontes:
                texto = ('Não foi possível confirmar essa informação na base de leis disponível. '
                         'A base reúne as leis ordinárias de Londrina; a informação pode estar em norma ainda não incluída. '
                         'Tente descrever o assunto com outras palavras ou busque a lei pelo número.')
            else:
                principal = fontes[0]
                artigo_principal = aceitos[0][0].texto
                lei_principal = f'Lei nº {numero_legivel(principal["chave"])}/{principal["ano"]}'
                frase = (frase_resposta(artigo_principal, plano) if len(artigo_principal) <= 4000 else
                         frase_resposta(principal['trecho'], plano, artigo_principal.startswith(principal['trecho'])))
                if plano.intencao == 'requisito' and ementa_sobre(principal['ementa'], plano):
                    texto = (f'As regras sobre esse assunto estão na {lei_principal}: {ementa_limpa(principal["ementa"])}\n\n'
                             f'Por exemplo, o {principal["artigo"]} diz: “{frase}”')
                else:
                    texto = f'Segundo a {lei_principal}, {principal["artigo"]}: “{frase}”'
                if plano.intencao_horario:
                    texto = ('Estes são trechos relacionados ao assunto, não uma confirmação de horário-limite. '
                             'Não há evidência suficiente nesta consulta documental para concluir qual horário '
                             'se aplica ao seu caso.\n\n' + texto)
                # Camadas: a lei, as leis que mudaram a redação do artigo e os decretos ligados a ela.
                # Decretos ainda não passam pela revisão institucional: só entram no modo documental.
                vinculados = decretos_das_leis({f['lei_id'] for f in fontes}) if local else {}
                decretos = decretos_para_artigo(vinculados.get(principal['lei_id'], []), principal['artigo'])
                com_texto = [d['id'] for f in fontes for d in vinculados.get(f['lei_id'], [])
                             if d['texto_disponivel'] and d['situacao'] != 'revogado'
                             and d['vinculo'] in (REGULAMENTADA_POR, ANEXO_ATUALIZADO_POR)]
                achado = artigo_de_decreto(list(dict.fromkeys(com_texto)), plano)
                if achado:
                    regulada = next(f for f in fontes if any(d['id'] == achado.decreto_id
                                                             for d in vinculados.get(f['lei_id'], [])))
                    frase_decreto = frase_do_decreto(achado.texto, plano)
                    nome = nome_decreto(achado.decreto.tipo, achado.decreto.numero, achado.decreto.ano)
                    lei_regulada = f'Lei nº {numero_legivel(regulada["chave"])}/{regulada["ano"]}'
                    if repete(frase_decreto, frase):
                        texto += f'\n\nO {nome}, que regulamenta a {lei_regulada}, repete essa regra no {achado.artigo}.'
                    else:
                        texto += f'\n\nO {nome}, que regulamenta a {lei_regulada}, detalha no {achado.artigo}: “{frase_decreto}”'
                    if not any(d['id'] == achado.decreto_id for d in decretos):
                        decretos += [dict(d, dispositivo=None) for d in vinculados[regulada['lei_id']]
                                     if d['id'] == achado.decreto_id][:1]
                    for d in decretos:
                        if d['id'] == achado.decreto_id:
                            d.update(artigo=achado.artigo, trecho=_curto(achado.texto))
                textos_lei = [t for (t,) in Artigo.select(Artigo.texto).where(Artigo.lei == principal['lei_id']).tuples()]
                camadas, alertas = montar_camadas(
                    dict(lei_id=principal['lei_id'], chave=principal['chave'], ano=principal['ano'],
                         ementa=ementa_limpa(principal['ementa']), link=principal['link'], situacao=principal['situacao'],
                         artigo=principal['artigo'], trecho=_curto(artigo_principal)),
                    leis_alteradoras(artigo_principal, _catalogo(local), principal), decretos,
                    artigo_preve_regulamentacao=preve_regulamentacao(artigo_principal),
                    lei_preve_regulamentacao=any(preve_regulamentacao(t) for t in textos_lei))
                # Suspensão de eficácia muda o que vale hoje: entra também na resposta curta.
                urgente = next((a for a in alertas if a.startswith('Atenção')), None)
                if urgente:
                    texto += '\n\n' + urgente
            usadas = {f['lei_id'] for f in fontes}
            consulta_ignoradas = _catalogo(local).where(Lei.situacao == 'revogada', Expression(VETOR_LEI, '@@', tsquery))
            ignoradas = []
            for l in consulta_ignoradas.limit(30) if fontes else []:
                if avaliar((l.titulo or '') + '\n' + (l.ementa or ''), plano) is None:
                    continue
                revogadoras = [r for r in Relacao.select().where(Relacao.lei_origem == l.id, Relacao.tipo == 'revogada_por',
                                                                  Relacao.lei_destino.is_null(False))]
                if not revogadoras:
                    continue
                citadas = refs_numero(l.revogacao_nota or '')
                revogadora = next((r for r in revogadoras if r.lei_destino_id in usadas), None) or \
                    next((r for r in revogadoras if r.chave_destino in citadas), None) or revogadoras[0]
                destino = Lei.get_or_none(Lei.id == revogadora.lei_destino_id)
                if not destino:
                    continue
                if destino.id not in usadas and not (
                        destino.situacao in ('vigente', 'vigente_com_alteracoes')
                        and avaliar((destino.titulo or '') + '\n' + (destino.ementa or ''), plano) is not None):
                    continue
                ignoradas.append(dict(lei_id=l.id, chave=l.chave, ano=str(l.ano), revogada_por_id=destino.id,
                                      motivo=f'Revogada pela Lei nº {numero_legivel(destino.chave)}/{destino.ano}.'))
                if len(ignoradas) >= 5:
                    break
            return dict(resposta=(aviso + '\n\n' if local else '') + texto,
                        fontes=fontes, ignoradas=ignoradas, modo='documental',
                        camadas=camadas, alertas=alertas,
                        evidencia=dict(estado='trechos_relacionados' if fontes else 'insuficiente',
                                       conceitos=list(plano.nomes), candidatos=len(candidatos),
                                       aceitos=len(aceitos), versao_busca=VERSAO_BUSCA),
                        vigencia_verificada=not local)

    return app


app = create_app()

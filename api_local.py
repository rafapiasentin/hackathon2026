"""API de catálogo e consulta documental; modo local explícito sem revisão presumida."""
import os
import re

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from peewee import Case, DatabaseError, Expression, SQL, fn
from pydantic import BaseModel, Field

from banco import Artigo, Carga, Lei, PublicacaoLei, Relacao, artigos_para_chatbot, conectar
from busca_documental import (VERSAO_BUSCA, administrativa, avaliar, ementa_limpa, ementa_sobre, frase_resposta,
                              numero_legivel, planejar, pontos_ementa, refs_numero, termos_grupo)

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
                          for r in Relacao.select().where(Relacao.lei_origem == lei_id)])

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
                        evidencia=dict(estado='trechos_relacionados' if fontes else 'insuficiente',
                                       conceitos=list(plano.nomes), candidatos=len(candidatos),
                                       aceitos=len(aceitos), versao_busca=VERSAO_BUSCA),
                        vigencia_verificada=not local)

    return app


app = create_app()

"""API de catálogo e consulta documental; modo local explícito sem revisão presumida."""
import os
import re
import unicodedata

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from peewee import DatabaseError, Expression, SQL, fn
from pydantic import BaseModel, Field

from banco import Artigo, Carga, Lei, PublicacaoLei, Relacao, artigos_para_chatbot, conectar

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


def _termos(pergunta):
    normal = lambda s: ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c))
    stop = {'posso', 'pode', 'podem', 'quero', 'gostaria', 'como', 'qual', 'quais', 'para', 'uma',
            'das', 'dos', 'com', 'que', 'por', 'sobre', 'preciso', 'londrina', 'regras', 'saber', 'tem', 'lei', 'leis'}
    palavras = [p for p in re.findall(r'[^\W\d_]{3,}', pergunta.lower()) if normal(p) not in stop][:12]
    temas = {'arvore': ['árvore', 'vegetação', 'poda', 'supressão'],
             'arvores': ['árvore', 'vegetação', 'poda'], 'cortar': ['corte', 'supressão'],
             'ambiental': ['ambiental'], 'calcada': ['calçada', 'passeio']}
    termos = []
    for palavra in palavras:
        termos.extend(temas.get(normal(palavra), [palavra]))
    return ' | '.join(dict.fromkeys(termos))


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=1, max_length=1000)


def create_app(db=None, catalogo_local=None):
    db = db or conectar()
    local = (os.getenv('API_MODO_DOCUMENTAL_LOCAL', '').lower() == 'true'
             if catalogo_local is None else catalogo_local)
    if local and (os.getenv('VERCEL') or os.getenv('RENDER')):
        raise RuntimeError('Modo documental local não pode ser ativado nesta hospedagem.')
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
                        artigos=Artigo.select().count(), modo='documental_local' if local else 'governado',
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
        termos = _termos(pergunta)
        if not termos:
            return dict(resposta='Informe o assunto ou busque uma lei pelo número.', fontes=[], ignoradas=[], modo='documental')
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
            assunto = ''.join(c for c in unicodedata.normalize('NFD', pergunta.lower()) if not unicodedata.combining(c))
            # O radical português de "poda" também encontra "poderá". Exige contexto
            # discriminativo para não citar cláusulas genéricas como resultado ambiental.
            if any(p in assunto for p in ('arvore', 'podar', 'poda', 'vegetacao')):
                consulta = consulta.where(Expression(Artigo.texto, '~*',
                    r'\m(árvores?|arvores?|vegetação|vegetacao|supressão|supressao|podas?|podar)\M'))
            elif 'ambient' in assunto:
                consulta = consulta.where(Expression(Artigo.texto, '~*', r'\m(ambiental|ambientais|ambiente)\M'))
            # Normaliza pelo tamanho: anexos extensos não devem superar artigos específicos.
            artigos = list(consulta.order_by(fn.ts_rank_cd(VETOR_ARTIGO, tsquery, 2).desc(), Artigo.lei, Artigo.ordem).limit(3))
            fontes = [dict(lei_id=a.lei_id, chave=a.lei.chave, ano=str(a.lei.ano),
                           ementa=a.lei.ementa, situacao=a.lei.situacao, artigo=a.artigo,
                           trecho=a.texto[:1800], link=a.lei.link, vigencia_verificada=not local) for a in artigos]
            if not fontes:
                texto = 'Não encontrei artigos suficientes para responder na base disponível. Tente outro termo ou busque pelo número da lei.'
            else:
                texto = 'Encontrei estes trechos nos documentos da Câmara:\n\n' + '\n\n'.join(
                    f'Lei {f["chave"]}/{f["ano"]}, {f["artigo"]}:\n{f["trecho"]}' for f in fontes)
            ignoradas = [dict(lei_id=l.id, chave=l.chave, ano=str(l.ano),
                             motivo='Consta como revogada na fonte; não usada na resposta.')
                         for l in _catalogo(local).where(Lei.situacao == 'revogada',
                             Expression(VETOR_LEI, '@@', tsquery)).limit(5)]
            return dict(resposta=(AVISO + '\n\n' if local else '') + texto,
                        fontes=fontes, ignoradas=ignoradas, modo='documental',
                        vigencia_verificada=not local)

    return app


app = create_app()

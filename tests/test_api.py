"""Contrato do front, respostas documentais e isolamento da governança."""
import pytest
from fastapi.testclient import TestClient

from api_local import create_app
from banco import Artigo, Lei
from carregar_leis import normalizar
from test_governanca import lei_sintetica


@pytest.fixture
def api(db_api, lei_sintetica):
    dados, _, _ = normalizar([lei_sintetica])
    Lei.insert_many(dados['leis']).execute()
    Artigo.insert_many(dados['artigos']).execute()
    Artigo.update(texto='A poda de árvores depende de autorização do Município.').execute()
    Artigo.create(lei='123', ordem=2, artigo='Art. 2º', texto='', texto_riscado='Redação antiga removida.', revogado=True)
    Artigo.create(lei='123', ordem=3, artigo='Art. 3º', texto='O Poder Executivo poderá regulamentar esta lei.', revogado=False)
    with TestClient(create_app(db_api, catalogo_local=True)) as client:
        yield client


@pytest.mark.postgres
def test_busca_e_lei_no_contrato_do_front(api):
    r = api.get('/api/leis', params=dict(numero='48', ano=2026))
    assert r.status_code == 200
    resultado = r.json()
    assert resultado['total'] == 1
    assert resultado['itens'][0]['vigencia_verificada'] is False
    assert resultado['itens'][0]['ementa'] is None
    lei = api.get('/api/leis/123').json()
    assert lei['ano'] == '2026' and len(lei['artigos']) == 3
    assert lei['artigos'][1]['revogado'] and lei['artigos'][1]['texto_riscado']
    assert api.get('/api/leis/999').status_code == 404
    assert api.get('/api/leis?pagina=0').status_code == 422
    assert api.get('/api/leis?situacao=desconhecida').status_code == 422


@pytest.mark.postgres
def test_chat_recupera_somente_texto_vigente_e_declara_limite(api):
    r = api.post('/api/perguntar', json=dict(pergunta='Posso podar uma árvore?'))
    assert r.status_code == 200
    resposta = r.json()
    assert resposta['fontes'] and resposta['fontes'][0]['lei_id'] == '123'
    assert 'institucional' in resposta['resposta']
    assert 'Redação antiga removida' not in resposta['resposta']
    assert all('poderá regulamentar' not in f['trecho'] for f in resposta['fontes'])
    assert resposta['modo'] == 'documental'
    assert api.post('/api/perguntar', json=dict(pergunta=' ')).status_code == 422
    assert api.post('/api/perguntar', json=dict(pergunta='x' * 1001)).status_code == 422


@pytest.mark.postgres
def test_cors_local_e_health(api):
    r = api.options('/api/perguntar', headers={'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type'})
    assert r.status_code == 200
    assert r.headers['access-control-allow-origin'] == 'http://localhost:5173'
    assert api.get('/api/health').json()['modo'] == 'documental_local'


@pytest.mark.postgres
def test_som_do_carro_nao_recupera_carga_descarga_ou_deixar(api):
    Artigo.create(lei='123', ordem=4, artigo='Art. 4º', texto='A carga e descarga somente poderá ocorrer entre as 8 horas e as 22 horas.', revogado=False)
    Artigo.create(lei='123', ordem=5, artigo='Art. 5º', texto='São motivos de suspensão: deixar de afixar o alvará; deixar de cumprir a escala.', revogado=False)
    resposta = api.post('/api/perguntar', json={'pergunta': 'até que horas posso deixar o som do carro ligado?'}).json()
    assert resposta['fontes'] == []
    assert '22 horas' not in resposta['resposta']
    assert 'Não encontrei' in resposta['resposta']


@pytest.mark.postgres
def test_som_do_carro_cita_ruido_sem_inventar_horario(api):
    Artigo.create(lei='123', ordem=4, artigo='Art. 4º', texto='A emissão de som por veículos deve observar os limites de ruído e as normas vigentes.', revogado=False)
    resposta = api.post('/api/perguntar', json={'pergunta': 'até que horas posso deixar o som do carro ligado?'}).json()
    assert len(resposta['fontes']) == 1
    assert resposta['fontes'][0]['artigo'] == 'Art. 4º'
    assert 'Não há evidência suficiente' in resposta['resposta']
    assert resposta['resposta'].count('Consulta documental local:') == 1
    assert resposta['evidencia']['estado'] == 'trechos_relacionados'


@pytest.mark.postgres
def test_chat_pede_contexto_e_nao_retoma_artigo_generico(api):
    resposta = api.post('/api/perguntar', json={'pergunta': 'Até que horas posso fazer barulho?'}).json()
    assert resposta['evidencia']['estado'] == 'precisa_contexto'
    assert resposta['fontes'] == []
    resposta = api.post('/api/perguntar', json={'pergunta': 'Tenho desconto no IPTU?'}).json()
    assert resposta['evidencia']['estado'] == 'insuficiente'
    assert resposta['fontes'] == []


@pytest.mark.postgres
def test_api_governada_nao_publica_carga_sem_revisao(db_api, lei_sintetica):
    dados, _, _ = normalizar([lei_sintetica])
    Lei.insert_many(dados['leis']).execute()
    Artigo.insert_many(dados['artigos']).execute()
    with TestClient(create_app(db_api, catalogo_local=False)) as client:
        assert client.get('/api/leis').json()['total'] == 0
        assert client.get('/api/leis/123').status_code == 404
        assert client.post('/api/perguntar', json=dict(pergunta='árvore')).json()['fontes'] == []

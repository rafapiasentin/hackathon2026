"""Regressão de recuperação no snapshot real: somente leituras, sem atestar validade jurídica."""
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api_local import create_app
from banco import Artigo, Lei, conectar

CASOS = json.loads(Path(__file__).with_name('casos_consulta.json').read_text(encoding='utf-8'))


@pytest.mark.acervo
@pytest.mark.parametrize('caso', CASOS, ids=[c['pergunta'] for c in CASOS])
def test_recuperacao_acervo_real(caso):
    nome = os.getenv('TEST_ACERVO_DB')
    if not nome:
        pytest.skip('Defina TEST_ACERVO_DB para verificar o acervo real em modo somente leitura.')
    db = conectar(nome)
    with TestClient(create_app(db, catalogo_local=True)) as client:
        r = client.post('/api/perguntar', json={'pergunta': caso['pergunta']})
    assert r.status_code == 200
    resposta = r.json()
    assert resposta['evidencia']['estado'] == caso['estado']
    chaves = {f['chave'] for f in resposta['fontes']}
    assert not chaves.intersection(caso['leis_inadequadas'])
    if caso['leis_relacionadas']:
        assert chaves.intersection(caso['leis_relacionadas'])
    else:
        assert not resposta['fontes']
    if caso.get('nao_concluir_horario'):
        assert 'Não há evidência suficiente' in resposta['resposta']
    with db.connection_context():
        for fonte in resposta['fontes']:
            lei = Lei.get_by_id(fonte['lei_id'])
            assert lei.situacao in ('vigente', 'vigente_com_alteracoes')
            artigos = Artigo.select().where(Artigo.lei == lei.id, Artigo.artigo == fonte['artigo'], Artigo.revogado == False)
            assert any(fonte['trecho'] in artigo.texto for artigo in artigos)

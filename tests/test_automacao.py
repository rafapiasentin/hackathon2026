"""Conferência HTTP simulada e consumidor automático; sem rede nos testes."""
import json

import pytest
import requests

from adaptadores import padronizar
from atualizar_base import processar_pasta
from banco import LoteIngestao, VersaoRegistro
from conferir_fonte import API, consultar
from governanca import contrato_atual, validar_registro
from test_governanca import entrada, lei_sintetica, revisar


def test_catalogo_cml_nao_confunde_publicacao_com_data_do_ato():
    # Amostra sintética com os mesmos cinco campos encontrados na API real.
    registro = dict(titulo='LEI N.º 14294, DE 29 DE OUTUBRO DE 2026',
        ementa='SÚMULA: Exemplo sintético.', data='2026-11-04 18:44:30', autoria='',
        link='https://www.cml.pr.gov.br/proposicoes/0/0/0/0/296902#pesquisa')
    normal = padronizar(registro)
    assert normal['id'] == '296902'
    assert normal['data_lei'] == '2026-10-29'
    assert normal['publicado_site'] == '2026-11-04 18:44:30'
    assert 'situacao' not in normal
    dados, erros = validar_registro(normal, {'296902'}, contrato_atual())
    assert dados is None
    assert any(p['campo'] == 'situacao' for p in erros)


class RespostaSimulada:
    status_code = 200
    headers = {'Content-Type': 'application/json'}
    content = b'[{"titulo":"Lei sintetica","ementa":"Exemplo","data":"2026-01-01","autoria":"","link":"https://www.cml.pr.gov.br/123"}]'

    def json(self):
        return json.loads(self.content)


class SessaoSimulada:
    def get(self, *args, **kwargs):
        return RespostaSimulada()


def test_conferencia_fonte_registra_campos_sem_token(tmp_path):
    resultado = consultar(API, tmp_path, 'pagina', dict(keysoft='SEGREDO_TESTE', call='legislacoes'), SessaoSimulada())
    assert resultado['status_http'] == 200 and resultado['contrato_compativel']
    assert resultado['quantidade'] == 1
    assert 'SEGREDO_TESTE' not in json.dumps(resultado)
    assert (tmp_path / 'pagina.json').read_bytes() == RespostaSimulada.content


def test_indisponibilidade_fonte_nao_vaza_url_preparada(tmp_path):
    class Falha:
        def get(self, *args, **kwargs):
            raise requests.ConnectionError('https://example.invalid/?keysoft=SEGREDO_TESTE')
    resultado = consultar(API, tmp_path, 'pagina', dict(keysoft='SEGREDO_TESTE'), Falha())
    assert not resultado['contrato_compativel']
    assert resultado['erro'] == 'ConnectionError'
    assert 'SEGREDO_TESTE' not in json.dumps(resultado)


@pytest.mark.parametrize('api_valida,esperado', [(True, 0), (False, 2)])
def test_documentacao_divergente_nao_substitui_validacao_da_api(tmp_path, monkeypatch, api_valida, esperado):
    import conferir_fonte as fonte
    monkeypatch.setenv('CML_TOKEN', 'sintetico')
    monkeypatch.setattr('sys.argv', ['conferir_fonte.py', '--api', '--saida', str(tmp_path)])
    def consultar_fake(url, pasta, nome, params=None):
        return dict(contrato_compativel=api_valida if params else False,
                    contratos=['Leis'] if params else [])
    monkeypatch.setattr(fonte, 'consultar', consultar_fake)
    assert fonte.main() == esperado
    assert (tmp_path / 'resultado.json').exists()


@pytest.mark.postgres
def test_consumidor_espera_estabilidade_e_nao_duplica(db_governanca, tmp_path, lei_sintetica, monkeypatch):
    lei = revisar(lei_sintetica, monkeypatch)
    entrada(tmp_path, [lei])
    (tmp_path / 'download.part').write_bytes(b'incompleto')
    estaveis = {}
    assert processar_pasta(db_governanca, tmp_path, 'https://www.cml.pr.gov.br/dadosabertos', estaveis) == []
    resultados = processar_pasta(db_governanca, tmp_path, 'https://www.cml.pr.gov.br/dadosabertos', estaveis)
    assert len(resultados) == 1 and resultados[0]['estado'] == 'publicado'
    resultados = processar_pasta(db_governanca, tmp_path, 'https://www.cml.pr.gov.br/dadosabertos', estaveis)
    assert resultados[0]['repetido']
    assert LoteIngestao.select().count() == 1 and VersaoRegistro.select().count() == 1

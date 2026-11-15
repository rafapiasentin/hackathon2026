"""Decretos: leitura das notas da Câmara, do texto do decreto, camadas da resposta e API."""
import json

import pytest

import coleta_decretos
import coleta_leis
import decretos as d
from carregar_decretos import normalizar as normalizar_decretos

EMENTA_13905 = ('Dispõe sobre o uso e ocupação do solo urbano no Município de Londrina e dá outras providências.\n\n'
                '(Vide Decreto nº 413, de 1º de abril de 2025) (Revogado pelo Decreto 1.341, de 5 de novembro de 2026)\n\n'
                '(Vide Decreto nº 466, de 16 de abril de 2025)\n\n'
                '(Vide Decreto nº 404, de 1º de abril de 2025 - Revogado pelo Art. 69 do Decreto nº 45/2026)\n\n'
                '(Vide Decreto nº 45, de 19 de janeiro de 2026)')

TEXTO_DECRETO = """16/10/2025 16:02 SEI/PML - 15422930 - SMG: Decreto Municipal
DECRETO Nº 466 DE 16 DE ABRIL DE 2025
SÚMULA: Regulamenta procedimentos para emissão de Consulta Prévia e Diretrizes Urbanísticas de
Parcelamento do Solo, nos termos da Lei Municipal nº 13.898 de 20 de dezembro de 2024, e da Lei Federal nº 6.766/1979.
O PREFEITO DO MUNICÍPIO DE LONDRINA, ESTADO DO PARANÁ, no exercício de suas atribuições legais,
D E C R E T A:
Art. 1º. A Consulta de Parcelamento do Solo (CPS) tem a finalidade informativa.
https://sei.londrina.pr.gov.br/sei/controlador.php?acao=documento_imprimir_web 1/8
Art. 2º. Para obtenção da Consulta de Parcelamento do Solo (CPS) o interessado deverá protocolizar requerimento,
anexando os seguintes documentos: I. formulário eletrônico no sistema SEI; II. croqui de localização do imóvel.
CAPÍTULO II
DAS DIRETRIZES
Art. 3º Este decreto entra em vigor na data de sua publicação.
Londrina, 16 de abril de 2025.
"""


def test_anotacao_que_cita_so_decreto_nao_revoga_a_lei():
    assert coleta_leis.revogacao_na_ementa(EMENTA_13905) is None
    assert coleta_leis.revogacao_na_ementa('Institui o Código. (REVOGADA pelo Art. 225. da Lei nº 14.294, de 2026)') == ['14294']
    # Anotação quebrada na fonte continua sendo revogação, sem revogador identificável.
    assert coleta_leis.revogacao_na_ementa('Texto (REVOGADA pelo Art. da Lei nº de de de 20)') == []
    assert coleta_leis.revogacao_na_ementa('Texto (REVOGADA)') == []


def test_reprocessar_corrige_somente_a_lei_lida_errado():
    leis = [dict(id='222790', chave='13905', ano='2024', ementa=EMENTA_13905, situacao='revogada',
                 revogacao_nota='(Revogado pelo Decreto 1.341, de 5 de novembro de 2026)',
                 alterada_por=[], revogada_por=[], complementa_id=None),
            dict(id='1', chave='10', ano='2000', ementa='X (REVOGADA pela Lei nº 20, de 2001)', situacao='revogada',
                 revogacao_nota='(REVOGADA pela Lei nº 20, de 2001)', alterada_por=[], revogada_por=['20'],
                 complementa_id=None)]
    corrigidas = coleta_leis.reaplicar_anotacao_revogada(leis)
    assert [(l['id'], antes) for l, antes in corrigidas] == [('222790', 'revogada')]
    assert leis[0]['situacao'] == 'vigente' and leis[0]['revogacao_nota'] is None
    assert leis[1]['situacao'] == 'revogada'


def test_notas_de_decreto_da_camara():
    notas = d.notas_de_decreto(EMENTA_13905)
    resumo = [(n['decreto']['numero'], n['decreto']['ano'], n['revogado_por'] and n['revogado_por']['numero'])
              for n in notas]
    assert resumo == [('413', 2025, '1341'), ('466', 2025, None), ('404', 2025, '45'), ('45', 2026, None)]
    assert all(n['tipo_vinculo'] == d.REGULAMENTADA_POR for n in notas)
    assert notas[1]['decreto']['data'] == '2025-04-16'

    suspensa = d.notas_de_decreto('(Eficácia suspensa do inciso V a XVI pelo Decreto-Legislativo nº 221, de 4 de setembro de 2007)')
    assert [(n['tipo_vinculo'], n['decreto']['tipo'], n['decreto']['numero']) for n in suspensa] == \
        [(d.EFICACIA_SUSPENSA_POR, 'Decreto Legislativo', '221')]
    anexo = d.notas_de_decreto('(Anexo atualizado pelo Decreto nº 1148, de 3/9/2024 - JO nº 5295, de 10/9/2024)')
    assert anexo[0]['tipo_vinculo'] == d.ANEXO_ATUALIZADO_POR and anexo[0]['decreto']['data'] == '2024-09-03'
    revogou = d.notas_de_decreto('(Vide o art. 1º, VI do Decreto nº 783, de 7/7/25 - JO nº 5534 que Revogou o Decreto nº 714/2021)')
    assert [n['decreto']['numero'] for n in revogou] == ['783']
    # Citação solta e decreto-lei federal não são vínculos.
    assert d.notas_de_decreto('(constante do Decreto nº 727/82) (Decreto-Lei nº 3.688, de 3 de outubro de 1941)') == []


def test_redacao_dada_e_previsao_de_regulamentacao():
    texto = 'Art. 2º Texto. (Redação dada pela Lei nº 13.931, de 21 de março de 2025) (Incluído pela Lei nº 12.000/2014)'
    assert d.redacoes_dadas(texto) == [('13931', 2025), ('12000', 2014)]
    assert d.preve_regulamentacao('Art. 56. Decreto Municipal regulamentará a emissão de Consulta Prévia.')
    assert d.preve_regulamentacao('Os valores das multas serão regulamentados por Decreto Municipal.')
    assert not d.preve_regulamentacao('Esta Lei entra em vigor na data de sua publicação.')


def test_ler_texto_do_decreto():
    lido = d.ler_decreto(TEXTO_DECRETO)
    assert (lido['tipo'], lido['numero'], lido['ano'], lido['data']) == ('Decreto', '466', 2025, '2025-04-16')
    assert lido['ementa'].startswith('Regulamenta procedimentos para emissão de Consulta Prévia')
    assert lido['leis'] == [('13898', 2024)]  # a lei federal não entra
    assert 'SEI/PML' not in lido['texto'] and 'controlador.php' not in lido['texto']
    artigos = coleta_decretos.artigos_do_texto(lido['texto'])
    assert [a['artigo'] for a in artigos] == ['Art. 1º', 'Art. 2º', 'Art. 3º']
    assert 'croqui' in artigos[1]['texto'] and 'CAPÍTULO' not in artigos[1]['texto']
    assert 'Londrina, 16' not in artigos[2]['texto']
    with pytest.raises(ValueError):
        d.ler_decreto('Documento sem título de decreto.')


def test_coletar_vinculos_sem_download():
    leis = [dict(id='222790', chave='13905', ano='2024', ementa=EMENTA_13905, relacionamentos=[],
                 artigos=[dict(artigo='Art. 22', texto='Art. 22. Texto. (Vide Decreto nº 466, de 16 de abril de 2025)')]),
            dict(id='9', chave='11133', ano='2011', ementa='Acrescenta dispositivo.', artigos=[],
                 relacionamentos=[dict(tipo='Suspende', descricao='DECRETO LEGISLATIVO Nº 246/2012 Suspende a eficácia da Lei nº 11.133/2011')])]
    lista, vinculos = coleta_decretos.coletar(leis, [])
    por_id = {x['id']: x for x in lista}
    assert por_id['decreto-413-2025']['situacao'] == 'revogado'
    assert por_id['decreto-413-2025']['revogado_por'] == 'Decreto 1.341/2026'
    assert por_id['decreto-466-2025']['situacao'] == 'sem_registro_de_revogacao'
    assert ('222790', 'decreto-466-2025', 'Art. 22') in {(v['lei_id'], v['decreto_id'], v['dispositivo']) for v in vinculos}
    assert ('9', 'decreto-legislativo-246-2012', d.EFICACIA_SUSPENSA_POR) in \
        {(v['lei_id'], v['decreto_id'], v['tipo']) for v in vinculos}
    decretos_, artigos, linhas = normalizar_decretos(dict(decretos=lista, vinculos=vinculos))
    assert len(decretos_) == len(lista) and artigos == [] and len(linhas) == len(vinculos)


def test_fonte_fora_do_municipio_e_recusada():
    with pytest.raises(ValueError, match='Município'):
        coleta_decretos.coletar([], [dict(tipo='Decreto', numero='1', ano=2025, url='https://exemplo.com/d.pdf')])
    assert coleta_decretos.url_do_municipio('https://repositorio.londrina.pr.gov.br/x')
    assert not coleta_decretos.url_do_municipio('http://repositorio.londrina.pr.gov.br/x')
    assert not coleta_decretos.url_do_municipio('https://londrina.pr.gov.br.exemplo.com/x')


def test_camadas_e_alertas():
    lei = dict(lei_id='1', chave='13898', ano='2024', ementa='Parcelamento do solo.', link='l', situacao='vigente',
               artigo='Art. 56', trecho='Decreto Municipal regulamentará...')
    base = dict(tipo='Decreto', ementa=None, link=None, revogado_por=None, dispositivo=None)
    com_texto = dict(base, id='decreto-466-2025', numero='466', ano=2025, situacao='sem_registro_de_revogacao',
                     texto_disponivel=True, vinculo=d.REGULAMENTADA_POR, artigo='Art. 2º', trecho='croqui')
    sem_texto = dict(base, id='decreto-45-2026', numero='45', ano=2026, situacao='sem_registro_de_revogacao',
                     texto_disponivel=False, vinculo=d.REGULAMENTADA_POR)
    revogado = dict(base, id='decreto-404-2025', numero='404', ano=2025, situacao='revogado',
                    texto_disponivel=False, vinculo=d.REGULAMENTADA_POR)
    suspenso = dict(base, tipo='Decreto Legislativo', id='decreto-legislativo-221-2007', numero='221', ano=2007,
                    situacao='sem_registro_de_revogacao', texto_disponivel=False, vinculo=d.EFICACIA_SUSPENSA_POR,
                    dispositivo='Art. 56')
    camadas, alertas = d.montar_camadas(lei, [dict(lei_id='7', chave='13931', ano='2025')],
                                        [sem_texto, com_texto, revogado], artigo_preve_regulamentacao=True)
    assert [c['papel'] for c in camadas] == ['lei', 'alteracao', d.REGULAMENTADA_POR, d.REGULAMENTADA_POR]
    assert camadas[0]['titulo'] == 'Lei 13.898/2024' and camadas[1]['titulo'] == 'Lei 13.931/2025'
    assert camadas[2]['titulo'] == 'Decreto 466/2025' and camadas[2]['trecho'] == 'croqui'  # com trecho primeiro
    assert 'Decreto 404/2025' not in json.dumps(camadas, ensure_ascii=False)  # revogado fica de fora
    assert len(alertas) == 1 and 'Decreto 45/2026' in alertas[0]

    camadas, alertas = d.montar_camadas(lei, [], [suspenso])
    assert camadas[1]['papel'] == d.EFICACIA_SUSPENSA_POR
    assert alertas[0].startswith('Atenção') and 'este artigo' in alertas[0]

    _, alertas = d.montar_camadas(lei, [], [], artigo_preve_regulamentacao=True)
    assert alertas and 'depende de regulamentação' in alertas[0]
    _, alertas = d.montar_camadas(lei, [], [])
    assert alertas == []


# ----------------------------------------------------------------------------------------- API

@pytest.fixture
def api_decretos(db_api):
    from fastapi.testclient import TestClient

    from api_local import create_app
    from banco import Artigo, Lei
    from carregar_decretos import importar
    Lei.create(id='123', chave='48', tipo='Lei', numero='48', ano=2026, titulo='LEI SINTÉTICA',
               ementa='Dispõe sobre o parcelamento do solo.', link='https://www.cml.pr.gov.br/proposicoes/0/0/0/0/123',
               situacao='vigente', texto_disponivel=True)
    Lei.create(id='124', chave='50', tipo='Lei', numero='50', ano=2026, titulo='LEI QUE ALTERA',
               ementa='Altera a Lei nº 48/2026.', link='https://www.cml.pr.gov.br/proposicoes/0/0/0/0/124',
               situacao='vigente', texto_disponivel=False)
    Artigo.create(lei='123', ordem=1, artigo='Art. 56', texto='Art. 56. Decreto Municipal regulamentará a emissão de '
                  'Consulta Prévia de Parcelamento do Solo sobre os parâmetros urbanísticos. (Redação dada pela Lei nº 50/2026)')
    # Artigos que tornam "consulta" o termo mais raro da pergunta, como no acervo real.
    Artigo.create(lei='123', ordem=2, artigo='Art. 57', texto='Art. 57. Os documentos do parcelamento do solo e a análise prévia.')
    Artigo.create(lei='123', ordem=3, artigo='Art. 58', texto='Art. 58. Os documentos prévios do solo serão arquivados.')
    ementa = 'Regulamenta procedimentos para emissão de Consulta Prévia de Parcelamento do Solo, nos termos da Lei Municipal nº 48/2026.'
    importar(db_api, dict(
        decretos=[dict(id='decreto-466-2025', tipo='Decreto', numero='466', ano=2025, data='2025-04-16', ementa=ementa,
                       link='https://repositorio.londrina.pr.gov.br/decreto-466/file', situacao='sem_registro_de_revogacao',
                       revogado_por=None, texto_disponivel=True, fonte_texto=None, artigos=[
                           dict(ordem=1, artigo='Art. 1º', texto='Art. 1º A Consulta de Parcelamento do Solo tem finalidade informativa.'),
                           dict(ordem=2, artigo='Art. 2º', texto='Art. 2º Para obtenção da Consulta de Parcelamento do Solo o '
                                'interessado deverá protocolizar requerimento, anexando os seguintes documentos: '
                                'formulário eletrônico e croqui de localização do imóvel.')]),
                  dict(id='decreto-404-2025', tipo='Decreto', numero='404', ano=2025, data=None, ementa=None, link=None,
                       situacao='revogado', revogado_por='Decreto 45/2026', texto_disponivel=False, fonte_texto=None, artigos=[]),
                  dict(id='decreto-legislativo-221-2007', tipo='Decreto Legislativo', numero='221', ano=2007, data=None,
                       ementa=None, link=None, situacao='sem_registro_de_revogacao', revogado_por=None,
                       texto_disponivel=False, fonte_texto=None, artigos=[])],
        vinculos=[dict(lei_id='123', decreto_id='decreto-466-2025', tipo=d.REGULAMENTADA_POR, dispositivo=None,
                       origem='sumula_decreto', nota=ementa),
                  dict(lei_id='123', decreto_id='decreto-404-2025', tipo=d.REGULAMENTADA_POR, dispositivo=None,
                       origem='nota_cml', nota='(Vide Decreto nº 404)'),
                  dict(lei_id='123', decreto_id='decreto-legislativo-221-2007', tipo=d.EFICACIA_SUSPENSA_POR,
                       dispositivo='Art. 99', origem='nota_cml', nota='(Eficácia suspensa)')]))
    with TestClient(create_app(db_api, catalogo_local=True)) as client:
        yield client


@pytest.mark.postgres
def test_chat_junta_lei_e_decreto(api_decretos):
    r = api_decretos.post('/api/perguntar', json={'pergunta': 'Quais documentos preciso para a consulta prévia de parcelamento do solo?'})
    assert r.status_code == 200
    resposta = r.json()
    assert resposta['fontes'][0]['artigo'] == 'Art. 56'
    assert 'O Decreto 466/2025, que regulamenta a Lei nº 48/2026, detalha no Art. 2º' in resposta['resposta']
    papeis = [c['papel'] for c in resposta['camadas']]
    assert papeis[0] == 'lei' and d.REGULAMENTADA_POR in papeis
    alteracao = next(c for c in resposta['camadas'] if c['papel'] == 'alteracao')
    assert alteracao['titulo'] == 'Lei 50/2026' and alteracao['lei_id'] == '124'
    decreto = next(c for c in resposta['camadas'] if c['papel'] == d.REGULAMENTADA_POR)
    assert decreto['titulo'] == 'Decreto 466/2025' and 'croqui' in decreto['trecho'] and decreto['texto_na_base']
    # Revogado e suspensão de outro artigo não entram nesta resposta.
    texto = json.dumps(resposta, ensure_ascii=False)
    assert 'Decreto 404/2025' not in texto and 'Decreto Legislativo 221/2007' not in texto
    assert not any(a.startswith('Atenção') for a in resposta['alertas'])


@pytest.mark.postgres
def test_suspensao_do_artigo_aparece_na_resposta_curta(api_decretos):
    from banco import LeiDecreto
    LeiDecreto.update(dispositivo='Art. 56').where(LeiDecreto.decreto == 'decreto-legislativo-221-2007').execute()
    resposta = api_decretos.post('/api/perguntar', json={'pergunta': 'Quais documentos preciso para a consulta prévia de parcelamento do solo?'}).json()
    assert 'Atenção: a Câmara registra que este artigo' in resposta['resposta']
    assert resposta['alertas'][0].startswith('Atenção')


@pytest.mark.postgres
def test_pagina_da_lei_lista_decretos(api_decretos):
    lei = api_decretos.get('/api/leis/123').json()
    titulos = {x['titulo']: x for x in lei['decretos']}
    assert set(titulos) == {'Decreto 466/2025', 'Decreto 404/2025', 'Decreto Legislativo 221/2007'}
    assert titulos['Decreto 404/2025']['situacao'] == 'revogado'
    assert titulos['Decreto Legislativo 221/2007']['dispositivos'] == ['Art. 99']

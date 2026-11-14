"""Relevância determinística: exemplos sintéticos não representam aconselhamento jurídico."""
import pytest

from busca_documental import avaliar, planejar


@pytest.mark.parametrize('pergunta,texto', [
    ('até que horas posso deixar o som do carro ligado?', 'Carga e descarga entre 8 e 22 horas.'),
    ('até que horas posso deixar o som do carro ligado?', 'Deixar de afixar o alvará gera suspensão.'),
    ('Posso podar uma árvore?', 'O Poder Executivo poderá regulamentar esta lei.'),
    ('Tenho desconto no IPTU?', 'A árvore deverá observar o limite de ruído.'),
    ('Posso criar um ornitorrinco no apartamento?', 'Animais: uma lista genérica sem o assunto perguntado.'),
])
def test_coincidencias_nao_sao_evidencia(pergunta, texto):
    assert avaliar(texto, planejar(pergunta)) is None


@pytest.mark.parametrize('pergunta,texto', [
    ('até que horas posso deixar o som do carro ligado?', 'Os limites de som emitidos pelas fontes móveis obedecerão às normas.'),
    ('Posso podar uma arvore?', 'A poda de árvores depende de autorização.'),
    ('Tenho desconto no IPTU?', 'O desconto do IPTU deverá observar os critérios.'),
    ('Quais regras do Código Ambiental?', 'A fiscalização ambiental observará as normas.'),
])
def test_conceitos_e_sinonimos_explicitos(pergunta, texto):
    assert avaliar(texto, planejar(pergunta)) is not None


def test_exige_conceitos_juntos_no_trecho_e_preserva_literalidade():
    plano = planejar('Tenho desconto no IPTU?')
    assert avaliar('IPTU. ' + 'Anexo irrelevante. ' * 300 + 'Desconto.', plano) is None
    texto = 'Preâmbulo distante. ' * 200 + 'O desconto do IPTU segue critérios.'
    evidencia = avaliar(texto, plano)
    assert evidencia is not None and evidencia['trecho'] in texto
    assert len(evidencia['trecho']) <= 1500


def test_contexto_automotivo_nao_usa_venda_ou_onibus():
    plano = planejar('Até que horas posso usar som no carro?')
    assert avaliar('É proibida a utilização de som em transportes públicos coletivos e veículos escolares.', plano) is None
    assert avaliar('As empresas que comercializam som para veículos devem atestar limites de qualidade.', plano) is None


def test_pergunta_ambigua_pede_contexto():
    assert planejar('Até que horas posso fazer barulho?').esclarecimento
    assert not planejar('Até que horas posso deixar o som do carro ligado?').esclarecimento

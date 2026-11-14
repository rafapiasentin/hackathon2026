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
    plano = planejar('Regras de IPTU e arborização?')
    assert avaliar('IPTU. ' + 'Anexo irrelevante. ' * 300 + 'Árvores.', plano) is None
    plano = planejar('Tenho desconto no IPTU?')
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


@pytest.mark.parametrize('pergunta,texto', [
    ('tem alguma lei sobre cortar arvores na calçada ?', 'A poda de árvores no passeio depende de autorização.'),
    ('posso cortar uma árvore na frente de casa?', 'A poda de árvores depende de autorização.'),
    ('posso podar a árvore em frente de casa?', 'A poda de árvores depende de autorização.'),
    ('corte de árvore em logradouro público', 'A poda ou corte de árvores em logradouros públicos depende de autorização.'),
    ('existe alguma regra para descarte de lixo?', 'Os resíduos devem ter destinação adequada.'),
])
def test_perguntas_coloquiais_preservam_assunto(pergunta, texto):
    plano = planejar(pergunta)
    assert not plano.esclarecimento
    assert avaliar(texto, plano) is not None


def test_palavras_livres_somam_pontos_sem_ser_obrigatorias():
    plano = planejar('corte de árvore em logradouro público')
    assert plano.nomes == ('arborizacao',)
    simples = avaliar('A poda de árvores depende de autorização.', plano)
    contextual = avaliar('A poda de árvores em logradouros públicos depende de autorização.', plano)
    assert contextual['pontos'] == simples['pontos'] + 6
    assert avaliar('Logradouros públicos sem o assunto solicitado.', plano) is None
    assert 'logradouro' not in plano.termos_sql and 'publico' not in plano.termos_sql


def test_sem_dicionario_exige_todas_as_palavras_e_aceita_plural():
    plano = planejar('logradouros municipais')
    assert not plano.complementares
    assert avaliar('Logradouros em outro contexto.', plano) is None
    plano = planejar('logradouro publico')
    assert 'logradouro:*' in plano.termos_sql and 'publico:*' in plano.termos_sql
    assert avaliar('Os logradouros públicos serão cadastrados.', plano) is not None
    assert avaliar('Micrologradouros públicos.', plano) is None


def test_prefixo_nao_se_aplica_a_grupos_ou_palavras_curtas():
    assert avaliar('O Poder Executivo poderá regulamentar esta lei.', planejar('Posso podar uma árvore?')) is None
    assert avaliar('IPTUs suplementares.', planejar('IPTU')) is None
    assert avaliar('Arborizações futuras.', planejar('arborização')) is None
    assert avaliar('Tratores especiais.', planejar('trato')) is not None
    assert avaliar('Casamentos registrados.', planejar('caso')) is None


def test_complemento_distante_nao_soma_pontos_no_trecho():
    plano = planejar('Tenho desconto no IPTU?')
    simples = avaliar('IPTU.', plano)
    distante = avaliar('IPTU. ' + 'Anexo irrelevante. ' * 300 + 'Descontos.', plano)
    assert distante['pontos'] == simples['pontos']


def test_sem_grupo_escolhe_frequencia_real_e_mantem_ausente():
    plano = planejar('benefício habitacional especial', frequencias=lambda grupos: [100, 7, 50])
    assert plano.nomes == ('habitacional',)
    assert avaliar('Programa habitacional.', plano)
    assert avaliar('Benefício especial.', plano) is None
    plano = planejar('benefício inexistente', frequencias=lambda grupos: [100, 0])
    assert plano.nomes == ('inexistente',)
    assert avaliar('Benefício concedido.', plano) is None


def test_isencao_aposentado_flexoes_pontuam_sem_exigir():
    plano = planejar('isenção de IPTU para aposentado')
    a = avaliar('Isenta os aposentados do IPTU.', plano)
    b = avaliar('O IPTU será cobrado.', plano)
    assert a['pontos'] == b['pontos'] + 6


@pytest.mark.parametrize('pergunta,nome', [
    ('onde descartar entulho?', 'residuos'), ('cachorro solto', 'animais'),
    ('fumar em lugar fechado', 'fumo'), ('terreno baldio sujo', 'terreno'),
    ('vendedor ambulante precisa de licença?', 'ambulante'),
    ('estacionamento rotativo', 'estacionamento'), ('calçada quebrada', 'calcada'),
    ('queimada', 'queimada'),
])
def test_novos_grupos_explicitos(pergunta, nome):
    assert nome in planejar(pergunta).nomes


@pytest.mark.parametrize('pergunta', ['som de madrugada', 'som com música', 'som no bar', 'som no carro estacionado'])
def test_contextos_de_ruido_adicionais(pergunta):
    assert not planejar(pergunta).esclarecimento


def test_pergunta_geografica_nao_usa_nome_de_rua_como_evidencia():
    plano = planejar('qual a capital da França?')
    assert not plano.termos_sql
    assert avaliar('Rua França: denominação de logradouro.', plano) is None

"""Relevância determinística: exemplos sintéticos não representam aconselhamento jurídico."""
import pytest

from busca_documental import (administrativa, avaliar, classificar_intencao, ementa_sobre, frase_resposta,
                              planejar, pontos_ementa)


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


@pytest.mark.parametrize('pergunta,intencao', [
    ('Quantos vereadores tem em Londrina?', 'quantidade'), ('qual o prazo para responder o pedido?', 'prazo'),
    ('quem tem direito a passe escolar?', 'direito'), ('posso passear com meu cachorro sem guia?', 'proibicao'),
    ('quais são as regras do código ambiental?', 'requisito'), ('isenção de IPTU para aposentado', 'geral'),
])
def test_classifica_o_tipo_de_pergunta(pergunta, intencao):
    assert classificar_intencao(pergunta) == intencao


@pytest.mark.parametrize('texto,aceito', [
    ('Texto sintético: a Câmara compõe-se de 19 (dezenove) Conselheiros.', True),
    ('Texto sintético: comissão composta de 3 (três) servidores, 2 (dois) Conselheiros.', False),
    ('Texto sintético: aprovação de dois terços dos Conselheiros.', False),
    ('Texto sintético: o subsídio dos Conselheiros será de R$ 10.000,00.', False),
])
def test_quantidade_exige_numero_que_define_o_assunto(texto, aceito):
    assert (avaliar(texto, planejar('Quantos conselheiros existem?')) is not None) is aceito


def test_prazo_exige_numero_com_unidade():
    plano = planejar('qual o prazo para a poda de árvore?')
    assert avaliar('Texto sintético: a poda de árvore será atendida em 45 (quarenta e cinco) dias.', plano)
    assert avaliar('Texto sintético: a poda de árvore depende de autorização.', plano) is None


def test_frase_resposta_nao_corta_no_meio_e_preserva_literalidade():
    plano = planejar('quem tem direito a passe escolar?')
    texto = ('Art. 3º O aluno terá direito ao fornecimento de passes escolares por mês,\npara uso '
             'exclusivo da linha residência-escola. Parágrafo único. Texto sintético sem relação.')
    frase = frase_resposta(texto, plano)
    assert frase.startswith('O aluno terá direito') and 'residência-escola.' in frase
    assert ' '.join(frase.split()) in ' '.join(texto.split())


def test_lei_administrativa_e_assunto_da_ementa():
    assert administrativa('Abre crédito adicional especial no orçamento.')
    assert administrativa('Dispõe sobre as Diretrizes para a Elaboração da Lei Orçamentária.')
    assert not administrativa('Institui o Código Ambiental do Município.')
    plano = planejar('posso passear com meu cachorro na praça sem guia?')
    assert pontos_ementa('Texto sintético: dispõe sobre animais em condomínios.', plano) == 0
    assert pontos_ementa('Texto sintético: circulação de animais com guia.', plano) > 0
    assert ementa_sobre('Institui o Código Ambiental do Município.', planejar('regras do código ambiental'))

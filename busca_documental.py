"""Regras determinísticas e auditáveis de relevância, sem LLM ou serviço externo."""
import re
import unicodedata
from dataclasses import dataclass

VERSAO_BUSCA = '2.2.0'
STOP = set('''a o as os um uma uns umas de da do das dos em no na nos nas ao aos e ou
que se por para pra pro com sem sobre como qual quais quando onde quem eu meu minha
seu sua isso esse essa este esta ser ter tem posso pode podem preciso devo deve existe
existem ha lei leis municipal municipio londrina regra regras artigo artigos saber quero
gostaria ate hora horas horario deixar ligado ligada perto permitido permite vale vigor
atualmente atual hoje funciona fazer quanto quais quais sao esta estao tenho temos
sou estou gostaria queria duvida informacao direito
alguma algum algumas alguns algo alguem qualquer tipo coisa coisas gente voce voces
frente favor ajuda informar explicar quantos quantas quantidade numero'''.split())

NUMERAL = (r'(?:(?<![\w.,])\d+(?![\d,.]*\d)(?![º°ª])|\b(?:um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez|'
           r'onze|doze|treze|quatorze|catorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte|trinta|quarenta|'
           r'cinquenta|sessenta|setenta|oitenta|noventa|cem|cento|duzentos|trezentos|quinhentos|mil)\b)')
UNIDADE_PRAZO = r'(?:dias?|meses|mes|anos?|horas?|minutos?|semanas?)'
PROPORCAO = r'(?:tercos?|quartos?|quintos?|decimos?|centesimos?|metade|maioria|vezes|por|vez|dos|das|de)\b'
DEFINICAO_QUANTIDADE = (r'\b(compost\w*|compo[em]\w*|integrad\w*|constituid\w*|numero de|fixad\w*|sera de|serao de|'
                        r'total de|limite de|maximo de|minimo de|quantidade de)\b')
INTENCOES = (
    ('quantidade', r'\b(quantos|quantas|qual (?:e )?(?:o )?numero de|qual (?:e )?a quantidade)\b'),
    ('prazo', r'\b(prazo|em quantos dias|quanto tempo|ate quando)\b'),
    ('limite', r'\b(limite|maximo|minimo|ate quanto)\b'),
    ('direito', r'\b(quem tem direito|tem direito|direito a|quem pode|beneficio|beneficiad\w*|gratuit\w*)\b'),
    ('procedimento', r'\b(como (?:faco|fazer|solicitar|pedir|conseguir|obter)|onde (?:solicitar|pedir|fazer)|o que fazer)\b'),
    ('proibicao', r'^(?:eu )?(?:posso|pode|podem|e proibido|e permitido|e obrigatorio)\b|\b(proibid\w*|permitid\w*|obrigatori\w*)\b'),
    ('requisito', r'\b(requisitos?|condicoes|regras? (?:de|da|do|para)|quais (?:sao )?as regras)\b'),
)
SINAIS_INTENCAO = {
    'limite': r'\b(maxim\w*|minim\w*|limite\w*|nao (?:podera|pode|poderao) (?:exceder|ultrapassar)|superior a|inferior a)\b',
    'direito': r'\b(isent\w*|isencao|direito|beneficiad\w*|beneficio\w*|gratuit\w*|faz(?:em)? jus|desde que|requisit\w*)\b',
    'requisito': r'\b(requisit\w*|desde que|condic\w*|devera\w*|exig\w*|obrigatori\w*)\b',
    'proibicao': r'\b(proibid\w*|vedad\w*|permitid\w*|obrigatori\w*|desde que|devera\w*|nao sera\w*)\b',
    'procedimento': r'\b(requeriment\w*|protocol\w*|solicit\w*|devera\w*|prazo|autorizacao)\b',
}
ADMINISTRATIVA = re.compile(
    r'^\s*(?:abre\b|autoriza o (?:poder )?executivo(?: municipal)? a (?:abrir|doar|permutar|alienar|adquirir|ceder|'
    r'conceder|desafetar|arrendar|receber|firmar|contratar)|denomina|da denominacao|declara de utilidade|desafeta|'
    r'concede (?:o )?titulo|inscreve)|plano plurianual|diretrizes para a elaboracao|lei orcamentaria|'
    r'(?:orca|estima) a receita|renuncia fiscal|converte os valores')


def classificar_intencao(pergunta):
    normal = normalizar_texto(pergunta).strip()
    for nome, padrao in INTENCOES:
        if re.search(padrao, normal):
            return nome
    return 'geral'


def administrativa(ementa):
    """Crédito, denominação, doação, orçamento: raramente respondem o que uma regra diz."""
    return bool(ADMINISTRATIVA.search(normalizar_texto(ementa or '')))


def refs_numero(texto):
    """Números de lei citados num texto ("Lei nº 14.294" -> {"14294"})."""
    return {n.replace('.', '') for n in re.findall(r'lei\s+(?:complementar\s+)?(?:municipal\s+)?(?:n\W{0,3}\s*)?(\d[\d.]*\d|\d)',
                                                     normalizar_texto(texto))}


def numero_legivel(chave):
    return f'{int(chave):,}'.replace(',', '.') if (chave or '').isdigit() else (chave or '')

# Sinônimos são grupos conceituais: coincidir apenas em "horas" nunca satisfaz o assunto.
GRUPOS = {
    'ruido': ('som', 'sons', 'barulho', 'barulhos', 'ruído', 'ruídos', 'sonora', 'sonoro', 'sossego', 'acústica', 'música', 'músicas'),
    'arborizacao': ('árvore', 'árvores', 'vegetação', 'arborização', 'poda', 'podar', 'supressão'),
    'iptu': ('iptu', 'imposto predial', 'imposto territorial urbano'),
    'alvara': ('alvará', 'licenciamento', 'licença de funcionamento'),
    'residuos': ('lixo', 'resíduos', 'resíduo', 'coleta de lixo', 'descarte', 'entulho', 'entulhos', 'descartar', 'caçamba'),
    'ambiental': ('ambiental', 'ambientais', 'meio ambiente'),
    'animais': ('cachorro', 'cachorros', 'cão', 'cães', 'gato', 'gatos', 'animal', 'animais'),
    'fumo': ('fumar', 'fumo', 'cigarro', 'tabaco', 'fumígeno', 'fumígeros'),
    'terreno': ('terreno baldio', 'terrenos baldios', 'lote', 'lotes', 'limpeza de terreno', 'limpeza de terrenos', 'mato'),
    'ambulante': ('ambulante', 'camelô', 'comércio eventual'),
    'estacionamento': ('estacionamento', 'zona azul', 'rotativo'),
    'calcada': ('calçada', 'calçadas', 'passeio'),
    'queimada': ('queimada', 'queimadas', 'fogo', 'incêndio'),
}
EXTRA = {'cortar': ('corte', 'supressão'), 'calcada': ('calçada', 'passeio'),
         'cachorro': ('cachorro', 'cão', 'cães'), 'cachorros': ('cachorros', 'cão', 'cães'),
         'isencao': ('isenção', 'isenta', 'isento', 'isenções'),
         'passear': ('passear', 'passeio', 'circulação', 'circular', 'conduzidos', 'conduzir')}
GENERICO_CONTEXTO = {'carro', 'carros', 'veiculo', 'veiculos', 'automotivo', 'cortar',
                     'corte', 'podar', 'poda', 'calcada', 'frente', 'residencia', 'casa', 'rua'}


def normalizar_texto(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if not unicodedata.combining(c))


def padrao_termo(palavra, flexivel=False):
    palavra = normalizar_texto(palavra)
    fim = r'\w*' if flexivel and len(palavra) >= 5 else r'(?!\w)'
    return r'(?<!\w)' + re.escape(palavra) + fim


def contem(texto, palavra, flexivel=False):
    return bool(re.search(padrao_termo(palavra, flexivel), texto))


@dataclass(frozen=True)
class PlanoBusca:
    grupos: tuple
    nomes: tuple
    termos_sql: str
    intencao_horario: bool
    veiculo: bool
    esclarecimento: str | None
    complementares: tuple = ()
    intencao: str = 'geral'


def termos_grupo(grupo, livre=False):
    termos = []
    for sinonimo in grupo:
        # Preserva os acentos para o stemmer português do PostgreSQL.
        for p in re.findall(r'[^\W\d_]{3,}', sinonimo.lower()):
            if normalizar_texto(p) not in STOP:
                termos.append(p + ':*' if livre and len(p) >= 5 else p)
    return ' | '.join(dict.fromkeys(termos))


def planejar(pergunta, frequencias=None):
    normal = normalizar_texto(pergunta)
    # Pergunta geográfica não é consulta de legislação municipal: nomes de
    # países também podem aparecer incidentalmente em nomes de ruas.
    if re.search(r'\bqual (?:e )?a capital (?:da|do|de)\b', normal):
        return PlanoBusca((), (), '', False, False, None)
    palavras = list(dict.fromkeys(re.findall(r'[^\W\d_]{3,}', pergunta.lower())))
    grupos, nomes, consumidas = [], [], set()
    for nome, sinonimos in GRUPOS.items():
        if any(contem(normal, p) for p in sinonimos):
            grupos.append(sinonimos)
            nomes.append(nome)
            consumidas.update(normalizar_texto(p) for s in sinonimos for p in re.findall(r'[^\W\d_]{3,}', s))
    # Em perguntas específicas sobre árvores/ruído, "ambiental" é a categoria,
    # não uma segunda palavra obrigatória que todo artigo precise repetir.
    if 'ambiental' in nomes and any(n in nomes for n in ('ruido', 'arborizacao')):
        i = nomes.index('ambiental')
        nomes.pop(i)
        grupos.pop(i)
    # Na pergunta sobre árvores, calçada é localização genérica. O assunto
    # "calçada" continua obrigatório quando a própria calçada é o objeto.
    if 'calcada' in nomes and 'arborizacao' in nomes:
        i = nomes.index('calcada')
        nomes.pop(i)
        grupos.pop(i)
    desconhecidas = [p for p in palavras if normalizar_texto(p) not in STOP | consumidas | GENERICO_CONTEXTO]
    if 'ambiental' in nomes:
        desconhecidas = [p for p in desconhecidas if normalizar_texto(p) != 'codigo']
    if 'ruido' in nomes:
        desconhecidas = [p for p in desconhecidas if normalizar_texto(p) not in {'alto', 'alta', 'volume'}]
    # Com assunto conhecido, palavras livres apenas refinam a ordenação.
    complementares = []
    assunto_conhecido = bool(grupos)
    for p in desconhecidas[:6]:
        sinonimos = EXTRA.get(normalizar_texto(p), (p,))
        if assunto_conhecido:
            complementares.append(sinonimos)
        else:
            grupos.append(sinonimos)
            nomes.append(normalizar_texto(p))
    if not grupos:
        for p in palavras:
            if normalizar_texto(p) not in STOP:
                grupos.append(EXTRA.get(normalizar_texto(p), (p,)))
                nomes.append(normalizar_texto(p))
    if not assunto_conhecido and grupos and frequencias is not None:
        contagens = frequencias(tuple(grupos))
        # Zero ocorrências é o termo mais raro: não trocar um assunto ausente
        # por outra palavra genérica da pergunta. Desempate estável pela ordem.
        indice = min(range(len(grupos)), key=lambda i: (contagens[i], i))
        complementares = [g for i, g in enumerate(grupos) if i != indice]
        grupos, nomes = [grupos[indice]], [nomes[indice]]
    veiculo = bool(re.search(r'\b(carro|carros|veiculo|veiculos|automotivo)\b', normal))
    horario = bool(re.search(r'\b(hora|horas|horario|quando)\b', normal))
    esclarecimento = None
    if 'ruido' in nomes and not veiculo and not re.search(r'\b(casa|vizinho|residencia|bar|festa|estabelecimento|obra|musica|madrugada)\b', normal):
        esclarecimento = 'O som ou barulho vem de um veículo, residência, estabelecimento ou obra? Inclua esse contexto na pergunta.'
    if len(desconhecidas) > 6:
        esclarecimento = 'Há muitos conceitos na pergunta. Separe a dúvida em uma pergunta específica por vez.'
    # Só assuntos obrigatórios geram candidatos. Um complemento comum como
    # "público" não deve ocupar as 100 vagas com artigos de outros assuntos.
    termos = [termos_grupo(g, n not in GRUPOS) for n, g in zip(nomes, grupos)]
    return PlanoBusca(tuple(grupos), tuple(nomes), ' & '.join('(' + t + ')' for t in termos),
                      horario, veiculo, esclarecimento, tuple(complementares), classificar_intencao(pergunta))


def _quantidade_junto(janela, plano):
    """Pergunta de quantidade só é respondida por um número ligado ao próprio assunto (ex.: "19 (dezenove) X")."""
    for nome, grupo in zip(plano.nomes, plano.grupos):
        for termo in grupo:
            alvo = padrao_termo(termo, nome not in GRUPOS)[len(r'(?<!\w)'):]
            if re.search(DEFINICAO_QUANTIDADE + r'[^;:,]{0,60}?' + NUMERAL + r'\s*(?:\([^)]{0,40}\)\s*)?(?:(?!'
                         + PROPORCAO + r')\w+\s+)?' + alvo, janela):
                return True
    return False


def pontos_ementa(ementa, plano):
    """Lei cujo assunto (ementa) é o tema perguntado vale mais que uma menção incidental."""
    normal = normalizar_texto(ementa or '')
    obrigatorios = sum(any(contem(normal, s, n not in GRUPOS) for s in g) for n, g in zip(plano.nomes, plano.grupos))
    extras = sum(any(contem(normal, s, True) for s in g) for g in plano.complementares)
    if plano.complementares and not extras:
        obrigatorios = 0
    return 3 * (obrigatorios + extras)


def ementa_sobre(ementa, plano):
    normal = normalizar_texto(ementa or '')
    return bool(plano.grupos) and all(any(contem(normal, s, n not in GRUPOS) for s in g)
                                      for n, g in zip(plano.nomes, plano.grupos))


def ementa_limpa(ementa):
    texto = re.split(r'\s*\(\s*vide\b|\s*\r?\n', ementa or '', maxsplit=1, flags=re.I)[0].strip()
    return re.sub(r'^s[úu]mula:\s*', '', texto, flags=re.I)


def responde_intencao(janela, plano):
    """Exige o tipo de dado pedido quando ele é objetivo (quantidade, prazo); nos demais casos só pontua."""
    if plano.intencao == 'quantidade':
        return _quantidade_junto(janela, plano), 0
    if plano.intencao == 'prazo':
        return bool(re.search(NUMERAL + r'\s*(?:\([^)]{0,40}\)\s*)?' + UNIDADE_PRAZO + r'\b', janela)), 0
    sinal = SINAIS_INTENCAO.get(plano.intencao)
    return True, (4 if sinal and re.search(sinal, janela) else 0)


def frase_resposta(trecho, plano, inicio_do_artigo=True):
    """Escolhe, sem reescrever, a frase do trecho que mais responde à pergunta."""
    corrido = re.sub(r'\s+', ' ', trecho).strip()
    pedacos = [p.strip() for p in re.split(r'(?<=[.;!?])\s+', corrido) if p.strip()]
    if not inicio_do_artigo and len(pedacos) > 1:
        pedacos = pedacos[1:]
    frases = []
    for pedaco in pedacos:
        if frases and (re.search(r'\b(?:art|arts|inc|n|nº|al)\.$|[:,]$', frases[-1], re.I) or len(frases[-1]) < 60):
            frases[-1] += ' ' + pedaco
        else:
            frases.append(pedaco)
    frases = [re.sub(r'^(?:art\.\s*\d+[º°]?\s*[-–.]?\s*|\d+[º°]\s+)', '', f, flags=re.I) for f in frases]
    frases = [f for f in frases if len(f) > 12]
    if not frases:
        return trecho.strip()[:400]

    def nota(frase):
        normal = normalizar_texto(frase)
        conceitos = sum(any(contem(normal, s, n not in GRUPOS) for s in g) for n, g in zip(plano.nomes, plano.grupos))
        extras = sum(any(contem(normal, s, True) for s in g) for g in plano.complementares)
        ok, bonus = responde_intencao(normal, plano)
        return (ok, conceitos + extras + bonus, -len(frase))

    melhor = max(frases, key=nota)
    return melhor if len(melhor) <= 450 else melhor[:447].rstrip() + '...'


def avaliar(texto, plano):
    """Aceita só conceitos presentes juntos num trecho limitado, nunca em anexos distantes."""
    if not plano.grupos or not texto.strip():
        return None
    normal = normalizar_texto(texto)
    posicoes = [0]
    for nome, grupo in zip(plano.nomes, plano.grupos):
        for termo in grupo:
            padrao = padrao_termo(termo, nome not in GRUPOS)
            posicoes.extend(max(0, m.start() - 200) for m in re.finditer(padrao, normal))
    for grupo in plano.complementares:
        for termo in grupo:
            posicoes.extend(max(0, m.start() - 200)
                            for m in re.finditer(padrao_termo(termo, True), normal))
    melhor = None
    # Limite evita que um artigo/anexo gigantesco domine o custo da consulta.
    for inicio in sorted(set(posicoes))[:100]:
        trecho = texto[inicio:inicio + 1500]
        janela = normalizar_texto(trecho)
        if not all(any(contem(janela, s, nome not in GRUPOS) for s in grupo)
                   for nome, grupo in zip(plano.nomes, plano.grupos)):
            continue
        pontos = 10 * len(plano.grupos)
        if 'ruido' in plano.nomes:
            if not re.search(r'\b(ruido\w*|poluicao|perturb\w*|sossego|decibe\w*|volume|limit\w*|emiss\w*|emitid\w*|proibid\w*)\b', janela):
                continue
            if plano.veiculo:
                # São contextos diferentes; não usar ônibus/escola ou venda de equipamentos
                # para orientar som em veículo particular.
                if re.search(r'transport\w*\s+(public\w*|escolar|coletiv\w*)|empresas que comercializam', janela):
                    continue
                if re.search(r'fontes\s+moveis|automotor\w*', janela):
                    pontos += 8
                if re.search(r'\b(veicul\w*|carros?|automotiv\w*)\b', janela):
                    pontos += 5
        atende, bonus = responde_intencao(janela, plano)
        if not atende:
            continue
        pontos += bonus
        pontos += 3 * sum(any(contem(janela, s, True) for s in grupo)
                          for grupo in plano.complementares)
        # Mantém a literalidade: trecho vem do artigo, sem criar uma redação nova.
        candidato = dict(pontos=pontos, trecho=trecho, conceitos=list(plano.nomes))
        if melhor is None or pontos > melhor['pontos']:
            melhor = candidato
    return melhor

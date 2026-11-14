"""Regras determinísticas e auditáveis de relevância, sem LLM ou serviço externo."""
import re
import unicodedata
from dataclasses import dataclass

VERSAO_BUSCA = '2.1.0'
STOP = set('''a o as os um uma uns umas de da do das dos em no na nos nas ao aos e ou
que se por para pra pro com sem sobre como qual quais quando onde quem eu meu minha
seu sua isso esse essa este esta ser ter tem posso pode podem preciso devo deve existe
existem ha lei leis municipal municipio londrina regra regras artigo artigos saber quero
gostaria ate hora horas horario deixar ligado ligada perto permitido permite vale vigor
atualmente atual hoje funciona fazer quanto quais quais sao esta estao tenho temos
sou estou gostaria queria duvida informacao direito
alguma algum algumas alguns algo alguem qualquer tipo coisa coisas gente voce voces
frente favor ajuda informar explicar'''.split())

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
         'isencao': ('isenção', 'isenta', 'isento', 'isenções')}
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
                      horario, veiculo, esclarecimento, tuple(complementares))


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
        pontos += 3 * sum(any(contem(janela, s, True) for s in grupo)
                          for grupo in plano.complementares)
        # Mantém a literalidade: trecho vem do artigo, sem criar uma redação nova.
        candidato = dict(pontos=pontos, trecho=trecho, conceitos=list(plano.nomes))
        if melhor is None or pontos > melhor['pontos']:
            melhor = candidato
    return melhor

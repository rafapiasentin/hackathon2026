"""Regras determinísticas e auditáveis de relevância, sem LLM ou serviço externo."""
import re
import unicodedata
from dataclasses import dataclass

VERSAO_BUSCA = '2.0.0'
STOP = set('''a o as os um uma uns umas de da do das dos em no na nos nas ao aos e ou
que se por para pra pro com sem sobre como qual quais quando onde quem eu meu minha
seu sua isso esse essa este esta ser ter tem posso pode podem preciso devo deve existe
existem ha lei leis municipal municipio londrina regra regras artigo artigos saber quero
gostaria ate hora horas horario deixar ligado ligada perto permitido permite vale vigor
atualmente atual hoje funciona fazer quanto quais quais sao esta estao tenho temos
sou estou gostaria queria duvida informacao direito'''.split())

# Sinônimos são grupos conceituais: coincidir apenas em "horas" nunca satisfaz o assunto.
GRUPOS = {
    'ruido': ('som', 'sons', 'barulho', 'barulhos', 'ruído', 'ruídos', 'sonora', 'sonoro', 'sossego', 'acústica'),
    'arborizacao': ('árvore', 'árvores', 'vegetação', 'arborização', 'poda', 'podar', 'supressão'),
    'iptu': ('iptu', 'imposto predial', 'imposto territorial urbano'),
    'alvara': ('alvará', 'licenciamento', 'licença de funcionamento'),
    'residuos': ('lixo', 'resíduos', 'resíduo', 'coleta de lixo', 'descarte'),
    'ambiental': ('ambiental', 'ambientais', 'meio ambiente'),
}
EXTRA = {'cortar': ('corte', 'supressão'), 'calcada': ('calçada', 'passeio'),
         'cachorro': ('cachorro', 'cão', 'cães'), 'cachorros': ('cachorros', 'cão', 'cães')}
GENERICO_CONTEXTO = {'carro', 'carros', 'veiculo', 'veiculos', 'automotivo', 'cortar',
                     'corte', 'podar', 'poda', 'calcada', 'residencia', 'casa', 'rua'}


def normalizar_texto(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if not unicodedata.combining(c))


def contem(texto, palavra):
    return bool(re.search(r'(?<!\w)' + re.escape(normalizar_texto(palavra)) + r'(?!\w)', texto))


@dataclass(frozen=True)
class PlanoBusca:
    grupos: tuple
    nomes: tuple
    termos_sql: str
    intencao_horario: bool
    veiculo: bool
    esclarecimento: str | None


def planejar(pergunta):
    normal = normalizar_texto(pergunta)
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
    desconhecidas = [p for p in palavras if normalizar_texto(p) not in STOP | consumidas | GENERICO_CONTEXTO]
    if 'ambiental' in nomes:
        desconhecidas = [p for p in desconhecidas if normalizar_texto(p) != 'codigo']
    if 'ruido' in nomes:
        desconhecidas = [p for p in desconhecidas if normalizar_texto(p) not in {'alto', 'alta', 'volume'}]
    # Exigir os conceitos desconhecidos evita respostas por uma coincidência isolada.
    for p in desconhecidas[:6]:
        grupos.append(EXTRA.get(normalizar_texto(p), (p,)))
        nomes.append(normalizar_texto(p))
    if not grupos:
        for p in palavras:
            if normalizar_texto(p) not in STOP:
                grupos.append(EXTRA.get(normalizar_texto(p), (p,)))
                nomes.append(normalizar_texto(p))
    veiculo = bool(re.search(r'\b(carro|carros|veiculo|veiculos|automotivo)\b', normal))
    horario = bool(re.search(r'\b(hora|horas|horario|quando)\b', normal))
    esclarecimento = None
    if 'ruido' in nomes and not veiculo and not re.search(r'\b(casa|vizinho|residencia|bar|festa|estabelecimento|obra)\b', normal):
        esclarecimento = 'O som ou barulho vem de um veículo, residência, estabelecimento ou obra? Inclua esse contexto na pergunta.'
    if len(desconhecidas) > 6:
        esclarecimento = 'Há muitos conceitos na pergunta. Separe a dúvida em uma pergunta específica por vez.'
    termos = list(dict.fromkeys(p for g in grupos for s in g for p in re.findall(r'[^\W\d_]{3,}', s.lower())
                               if normalizar_texto(p) not in STOP))
    return PlanoBusca(tuple(grupos), tuple(nomes), ' | '.join(termos), horario, veiculo, esclarecimento)


def avaliar(texto, plano):
    """Aceita só conceitos presentes juntos num trecho limitado, nunca em anexos distantes."""
    if not plano.grupos or not texto.strip():
        return None
    normal = normalizar_texto(texto)
    posicoes = [0]
    for grupo in plano.grupos:
        for termo in grupo:
            padrao = r'(?<!\w)' + re.escape(normalizar_texto(termo)) + r'(?!\w)'
            posicoes.extend(max(0, m.start() - 200) for m in re.finditer(padrao, normal))
    melhor = None
    # Limite evita que um artigo/anexo gigantesco domine o custo da consulta.
    for inicio in sorted(set(posicoes))[:100]:
        trecho = texto[inicio:inicio + 1500]
        janela = normalizar_texto(trecho)
        if not all(any(contem(janela, s) for s in grupo) for grupo in plano.grupos):
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
        pontos += min(3, sum(contem(janela, s) for g in plano.grupos for s in g))
        # Mantém a literalidade: trecho vem do artigo, sem criar uma redação nova.
        candidato = dict(pontos=pontos, trecho=trecho, conceitos=list(plano.nomes))
        if melhor is None or pontos > melhor['pontos']:
            melhor = candidato
    return melhor

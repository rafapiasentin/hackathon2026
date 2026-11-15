"""Decretos ligados às leis: leitura das notas da Câmara, do texto do decreto e das camadas da resposta.

Uma lei define a regra; um decreto do prefeito diz como aplicá-la (prazo, documento, valor),
sem poder contrariá-la. O decreto legislativo, da Câmara, pode suspender a eficácia de uma lei.
Este módulo só usa a biblioteca padrão: é importado pela API, que não instala requests nem pymupdf.
"""
import re
import unicodedata

MESES = {'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7,
         'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}

# Tipos de vínculo lei -> decreto (o banco guarda o tipo do ponto de vista da lei).
REGULAMENTADA_POR = 'regulamentada_por'      # "(Vide Decreto nº 466, de 16 de abril de 2025)"
ANEXO_ATUALIZADO_POR = 'anexo_atualizado_por'  # "(Anexo atualizado pelo Decreto nº 1148, de 3/9/2024)"
EFICACIA_SUSPENSA_POR = 'eficacia_suspensa_por'  # "(Eficácia suspensa pelo Decreto-Legislativo nº 221...)"
TIPOS_VINCULO = (REGULAMENTADA_POR, ANEXO_ATUALIZADO_POR, EFICACIA_SUSPENSA_POR)

# "Decreto nº 466", "Decreto 1.341", "Decreto Regulamentar nº 831", "Decreto-Legislativo nº 221",
# "Decreto nº 45/2026". "Decreto-Lei" (federal) não casa: o hífen não é seguido de número.
RE_DECRETO = re.compile(
    r'\bdecreto(?P<leg>[\s-]+legislativo)?(?:\s+(?:regulamentar|municipal))?\s*'
    r'(?:n[º°ª.o]{0,3}s?\s*)?(?P<num>\d[\d.]*\d|\d)(?:\s*/\s*(?P<ano>\d{4}|\d{2})\b)?', re.I)
RE_DATA_EXTENSO = re.compile(r'^\s*,?\s*(?:de\s+)?(\d{1,2})\s*[º°o]?\s+de\s+([a-zç]+)\s+de\s+(\d\.?\d{3})', re.I)
RE_DATA_BARRA = re.compile(r'^\s*,?\s*(?:de\s+)?(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})\b')
RE_ANO_SOLTO = re.compile(r'\b(19\d{2}|20\d{2})\b')
RE_PARENTESE = re.compile(r'\([^()]*\)')
# Separa, numa nota, o decreto de que se fala do decreto que o revogou.
RE_REVOGADO_PELO = re.compile(r'revogad[oa]s?\s+(?:pel[oa]|por)\b', re.I)
RE_QUE_REVOGOU = re.compile(r'\bque\s+revog(?:ou|a)\b', re.I)

# O artigo manda regulamentar por decreto ou ato do Executivo.
RE_PREVE_REGULAMENTACAO = re.compile(
    r'regulamentad[oa]s?\s+(?:por|mediante|atrav[eé]s\s+de|em)\s+decreto|'
    r'decreto\s+(?:municipal\s+|do\s+executivo\s+)?regulamentar[aá]|'
    r'(?:poder\s+)?executivo(?:\s+municipal)?\s+regulamentar[aá]|'
    r'regulamenta[çc][ãa]o\s+(?:por|em)\s+decreto|previst[oa]\s+em\s+decreto', re.I)
# Redação atual dada por outra lei: "(Redação dada pela Lei nº 13.931, de 21 de março de 2025)".
RE_REDACAO_DADA = re.compile(
    r'\((?:reda[çc][ãa]o\s+dada|inclu[ií]d[oa]|acrescid[oa]|acrescentad[oa]|alterad[oa])\s+pel[oa]\s+'
    r'(?:art\.?\s*[\w-]+º?\.?\s+da\s+)?lei\s+(complementar\s+)?(?:municipal\s+)?(?:n[º°ª.o]{0,3}s?\s*)?'
    r'(\d[\d.]*\d|\d)(?:\s*/\s*(\d{4}))?([^()]*)\)', re.I)


def _normal(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if not unicodedata.combining(c))


def _ano(texto):
    ano = texto.replace('.', '')
    return int(ano) + (2000 if int(ano) < 50 else 1900) if len(ano) == 2 else int(ano)


def identificador(tipo, numero, ano):
    """("Decreto", "466", 2025) -> "decreto-466-2025"; legislativo -> "decreto-legislativo-221-2007"."""
    return f"{'decreto-legislativo' if tipo == 'Decreto Legislativo' else 'decreto'}-{numero}-{ano}"


def nome_decreto(tipo, numero, ano):
    numero = f'{int(numero):,}'.replace(',', '.') if str(numero).isdigit() else numero
    return f'{tipo} {numero}/{ano}'


def mencoes(trecho):
    """Decretos citados num trecho, na ordem: [{tipo, numero, ano, data}].
    O ano vem do número ("45/2026"), da data logo depois ("de 16 de abril de 2025", "de 4/4/22")
    ou, sem isso, do primeiro ano solto antes do próximo decreto ("publicado ... de 2014")."""
    achados = list(RE_DECRETO.finditer(trecho))
    resultado = []
    for i, m in enumerate(achados):
        depois = trecho[m.end():achados[i + 1].start() if i + 1 < len(achados) else len(trecho)]
        data = ano = None
        if m['ano']:
            ano = _ano(m['ano'])
        elif d := RE_DATA_EXTENSO.match(depois):
            mes = MESES.get(_normal(d[2]))
            ano = _ano(d[3])
            if mes:
                data = f'{ano:04d}-{mes:02d}-{int(d[1]):02d}'
        elif d := RE_DATA_BARRA.match(depois):
            ano = _ano(d[3])
            data = f'{ano:04d}-{int(d[2]):02d}-{int(d[1]):02d}'
        elif a := RE_ANO_SOLTO.search(depois):
            ano = int(a[1])
        resultado.append(dict(tipo='Decreto Legislativo' if m['leg'] else 'Decreto',
                              numero=m['num'].replace('.', ''), ano=ano, data=data))
    return resultado


def _classificar(nota):
    n = _normal(nota)
    if 'suspens' in n or 'suspende' in n:
        return EFICACIA_SUSPENSA_POR
    if re.match(r'\(\s*vide\b', n):
        return REGULAMENTADA_POR
    if 'anexo atualizado' in n or 'atualizacao em pdf' in n:
        return ANEXO_ATUALIZADO_POR
    return None


def notas_de_decreto(texto):
    """Lê as notas que a Câmara escreve entre parênteses na ementa ou no artigo.

    Ex.: "(Vide Decreto nº 404, de 1º de abril de 2025 - Revogado pelo Art. 69 do Decreto nº 45/2026)"
      -> [{tipo_vinculo: "regulamentada_por", decreto: Decreto 404/2025,
           revogado_por: Decreto 45/2026, nota: "(Vide ...)"}]
    Uma nota "(Revogado pelo Decreto ...)" logo depois de um "(Vide ...)" revoga o decreto do Vide.
    Citações soltas ("constante do Decreto nº 727/82") não viram vínculo.
    """
    resultado, anterior, fim_anterior = [], [], None
    for m in RE_PARENTESE.finditer(texto or ''):
        nota = ' '.join(m.group(0).split())
        if not RE_DECRETO.search(nota):
            anterior = []
            continue
        tipo = _classificar(nota)
        contiguo = fim_anterior is not None and not texto[fim_anterior:m.start()].strip()
        fim_anterior = m.end()
        if tipo is None and re.match(r'\(\s*revogad', _normal(nota)) and contiguo and anterior:
            revogador = next(iter(mencoes(nota)), None)
            for item in anterior:
                item['revogado_por'] = revogador
            anterior = []
            continue
        if tipo is None:
            anterior = []
            continue
        # O decreto da nota é o que vem antes de "revogado pelo"; o de depois é o revogador.
        corte = RE_REVOGADO_PELO.search(nota) or RE_QUE_REVOGOU.search(nota)
        sujeitos = mencoes(nota[:corte.start()] if corte else nota)
        revogador = None
        if corte and RE_REVOGADO_PELO.search(nota):
            revogador = next(iter(mencoes(nota[corte.end():])), None)
        if tipo == EFICACIA_SUSPENSA_POR:
            sujeitos = [d for d in sujeitos if d['tipo'] == 'Decreto Legislativo'] or sujeitos
        itens = [dict(tipo_vinculo=tipo, decreto=d, revogado_por=revogador, nota=nota)
                 for d in sujeitos if d['ano']]
        resultado.extend(itens)
        anterior = itens
    return resultado


def suspensao_em_relacionamento(descricao):
    """Relacionamento "Suspende" da Câmara: "DECRETO LEGISLATIVO Nº 246/2012 Suspende a eficácia da Lei ..."."""
    if not re.match(r'\s*decreto[\s-]+legislativo', _normal(descricao or '')):
        return None
    achados = mencoes(descricao[:80])
    return achados[0] if achados and achados[0]['ano'] else None


def preve_regulamentacao(texto):
    return bool(RE_PREVE_REGULAMENTACAO.search(texto or ''))


def redacoes_dadas(texto):
    """Leis que deram a redação atual do trecho: [(chave, ano ou None)], sem repetir."""
    vistos = []
    for m in RE_REDACAO_DADA.finditer(texto or ''):
        chave = ('LC-' if m[1] else '') + m[2].replace('.', '')
        solto = RE_ANO_SOLTO.search(m[4] or '')
        ano = int(m[3]) if m[3] else int(solto[1]) if solto else None
        if (chave, ano) not in vistos:
            vistos.append((chave, ano))
    return vistos


# --------------------------------------------------------------------------- texto do decreto

RE_TITULO = re.compile(r'DECRETO\s+(LEGISLATIVO\s+)?N[º°ª.O]{0,3}\s*(\d[\d.]*)\s*,?\s*(?:DE\s+)?(\d{1,2})\s*[º°O]?\s+DE\s+'
                       r'([A-ZÇ]+)\s+DE\s+(\d{4})', re.I)
RE_SUMULA = re.compile(r'S[ÚU]MULA:\s*(.+?)\s*(?:O\s+PREFEITO\s+DO\s+MUNIC|A\s+C[ÂA]MARA\s+MUNICIPAL|D\s*E\s*C\s*R\s*E\s*T\s*A)',
                       re.I | re.S)
RE_LEI_CITADA = re.compile(
    r'\blei\s+(complementar\s+)?(?:municipal\s+)?(?:n[º°ª.o]{0,3}s?\s*)?(\d[\d.]*\d|\d)'
    r'(?:\s*/\s*(\d{4})|,?\s+de\s+\d{1,2}\s*[º°o]?\s+de\s+[a-zç]+\s+de\s+(\d{4}))?', re.I)
# Cabeçalho e rodapé que o SEI imprime em cada página do PDF.
RE_LIXO_SEI = re.compile(r'(?m)^.*(?:SEI/PML|https?://sei\.|controlador\.php).*$|^\s*\d{1,3}/\d{1,3}\s*$')


def limpar_texto_pdf(texto):
    texto = RE_LIXO_SEI.sub('', texto.replace('\xa0', ' '))
    return '\n'.join(' '.join(linha.split()) for linha in texto.splitlines() if linha.strip())


def leis_citadas(texto):
    """Leis citadas na súmula do decreto: [(chave, ano ou None)]. Leis federais ("Lei Federal")
    não casam porque o número vem logo depois de "Lei", "Lei Municipal" ou "Lei Complementar"."""
    vistos = []
    for m in RE_LEI_CITADA.finditer(texto or ''):
        chave = ('LC-' if m[1] else '') + m[2].replace('.', '')
        ano = int(m[3] or m[4]) if (m[3] or m[4]) else None
        if (chave, ano) not in vistos:
            vistos.append((chave, ano))
    return vistos


def ler_decreto(texto):
    """Do texto já extraído do PDF: título, número, data, súmula e as leis que ele regulamenta.
    Os artigos são separados por quem chama (extracao_documentos.separar_artigos)."""
    texto = limpar_texto_pdf(texto)
    titulo = RE_TITULO.search(texto)
    if not titulo:
        raise ValueError('Título "DECRETO Nº ... DE ... DE ..." não encontrado no documento.')
    mes = MESES.get(_normal(titulo[4]))
    if not mes:
        raise ValueError(f'Mês inválido no título do decreto: {titulo[4]!r}.')
    sumula = RE_SUMULA.search(texto[titulo.end():])
    ementa = ' '.join(sumula[1].split()) if sumula else None
    return dict(texto=texto, tipo='Decreto Legislativo' if titulo[1] else 'Decreto',
                numero=titulo[2].replace('.', ''), ano=int(titulo[5]),
                data=f'{int(titulo[5]):04d}-{mes:02d}-{int(titulo[3]):02d}',
                ementa=ementa, leis=leis_citadas(ementa or ''))


# --------------------------------------------------------------------------- camadas da resposta

PAPEIS = {
    'lei': 'Lei que traz a regra',
    'alteracao': 'Lei que mudou a redação deste artigo',
    REGULAMENTADA_POR: 'Decreto que detalha como aplicar a lei',
    ANEXO_ATUALIZADO_POR: 'Decreto que atualizou um anexo da lei',
    EFICACIA_SUSPENSA_POR: 'Decreto legislativo da Câmara que suspendeu a eficácia',
}


def montar_camadas(lei, alteradoras=(), decretos=(), artigo_preve_regulamentacao=False,
                   lei_preve_regulamentacao=False):
    """Junta, em ordem, as normas que formam a resposta: lei, leis que a alteraram e decretos.

    lei: {lei_id, chave, ano, ementa, link, situacao, artigo, trecho}
    alteradoras: [{lei_id, chave, ano, link, situacao}]
    decretos: [{id, tipo, numero, ano, ementa, link, situacao, revogado_por, texto_disponivel,
                vinculo, dispositivo, artigo?, trecho?}]
    Devolve (camadas, alertas). Alerta é sempre uma frase curta em linguagem simples.
    """
    numero = f"{int(lei['chave']):,}".replace(',', '.') if str(lei['chave']).isdigit() else lei['chave']
    camadas = [dict(papel='lei', descricao=PAPEIS['lei'], titulo=f"Lei {numero}/{lei['ano']}",
                    lei_id=lei.get('lei_id'), link=lei.get('link'), ementa=lei.get('ementa'),
                    situacao=lei.get('situacao'), artigo=lei.get('artigo'), trecho=lei.get('trecho'),
                    texto_na_base=True)]
    for a in alteradoras:
        n = f"{int(a['chave']):,}".replace(',', '.') if str(a['chave']).isdigit() else a['chave']
        camadas.append(dict(papel='alteracao', descricao=PAPEIS['alteracao'],
                            titulo=f"Lei {n}/{a['ano']}" if a.get('ano') else f'Lei {n}',
                            lei_id=a.get('lei_id'), link=a.get('link'), ementa=a.get('ementa'),
                            situacao=a.get('situacao'), artigo=None, trecho=None,
                            texto_na_base=bool(a.get('lei_id'))))
    alertas = []
    vigentes = [d for d in decretos if d['situacao'] != 'revogado']
    # Suspensão primeiro: muda o que vale hoje.
    ordem = {EFICACIA_SUSPENSA_POR: 0, REGULAMENTADA_POR: 1, ANEXO_ATUALIZADO_POR: 2}
    for d in sorted(vigentes, key=lambda d: (ordem.get(d['vinculo'], 9), not d.get('trecho'),
                                             -(d.get('ano') or 0))):
        camadas.append(dict(papel=d['vinculo'], descricao=PAPEIS.get(d['vinculo'], 'Decreto ligado à lei'),
                            titulo=nome_decreto(d['tipo'], d['numero'], d['ano']), decreto_id=d['id'],
                            link=d.get('link'), ementa=d.get('ementa'), situacao=d['situacao'],
                            artigo=d.get('artigo'), trecho=d.get('trecho'), dispositivo=d.get('dispositivo'),
                            texto_na_base=bool(d.get('texto_disponivel'))))
    suspensos = [d for d in vigentes if d['vinculo'] == EFICACIA_SUSPENSA_POR]
    if suspensos:
        quem = ', '.join(nome_decreto(d['tipo'], d['numero'], d['ano']) for d in suspensos)
        onde = 'este artigo, ou parte dele,' if any(d.get('dispositivo') for d in suspensos) else 'esta lei, ou parte dela,'
        alertas.append(f'Atenção: a Câmara registra que {onde} está com a eficácia suspensa ({quem}).')
    sem_texto = [d for d in vigentes if d['vinculo'] != EFICACIA_SUSPENSA_POR and not d.get('texto_disponivel')]
    com_texto = [d for d in vigentes if d['vinculo'] != EFICACIA_SUSPENSA_POR and d.get('texto_disponivel')]
    if sem_texto:
        quem = ', '.join(nome_decreto(d['tipo'], d['numero'], d['ano']) for d in sem_texto[:4])
        alertas.append(f'Esta lei tem decreto que a regulamenta ({quem}), mas o texto dele ainda não está na nossa base. '
                       'Prazos, valores e documentos podem estar lá: confira no Jornal Oficial do Município.')
    elif artigo_preve_regulamentacao and not com_texto:
        alertas.append('Este artigo depende de regulamentação por decreto. Prazos, valores e documentos podem estar '
                       'em um decreto que ainda não está na nossa base.')
    elif lei_preve_regulamentacao and not vigentes:
        alertas.append('Esta lei prevê regulamentação por decreto em alguns pontos. Nossa base ainda não reúne '
                       'todos os decretos do Município.')
    if any(d['situacao'] == 'revogado' for d in decretos) and not vigentes:
        alertas.append('Os decretos ligados a esta lei que conhecemos foram revogados.')
    return camadas, alertas

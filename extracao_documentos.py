"""Extração local de HTML, PDF textual e PDF escaneado, com proveniência."""
import copy
import hashlib
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, NavigableString

ARTIGO = re.compile(r'(?m)^[ \t]*(Art\.?[ \t]*\d+[º°o]?(?:-[A-Z])?\.?)', re.I)
TESSDATA = Path(__file__).with_name('.data') / 'tessdata'
OCR_SHA256 = 'c4932b937207a9514b7514d518b931a99938c02a28a5a5a553f8599ed58b7deb'


def normal_texto(texto):
    return '\n'.join(' '.join(linha.split()) for linha in texto.splitlines() if linha.strip())


def separar_artigos(texto, riscados):
    marcas = list(ARTIGO.finditer(texto))
    artigos = []
    for i, marca in enumerate(marcas):
        inicio, fim = marca.start(), marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        # Assinaturas e referências finais não integram o último artigo.
        rodape = re.search(r'(?mi)^\s*(?:Londrina,|Ref\.:|Protocolos desta Publicação)', texto[marca.end():fim])
        if rodape:
            fim = marca.end() + rodape.start()
        posicoes = [p for p in range(marca.end(), fim) if not texto[p].isspace()]
        revogado = bool(posicoes) and all(riscados[p] for p in posicoes)
        vigente = ''.join(texto[p] for p in range(inicio, fim) if not riscados[p])
        antigo = ''.join(texto[p] for p in range(inicio, fim) if riscados[p] or texto[p].isspace())
        artigos.append(dict(ordem=i + 1, artigo=normal_texto(marca.group(1)).rstrip('.'),
                            texto='' if revogado else normal_texto(vigente),
                            texto_riscado=normal_texto(antigo) or None, revogado=revogado))
    return artigos


def _montar(texto, riscados, contexto, extracao):
    from coleta_leis import parse_titulo
    registro = copy.deepcopy(contexto or {})
    titulos = [linha.strip() for linha in texto.splitlines() if re.match(r'^\s*LEI\b', linha, re.I)]
    titulo = titulos[0] if titulos else None
    numeros = {parse_titulo(t)[0] for t in titulos if parse_titulo(t)[0]}
    if len(numeros) > 1:
        extracao['conflitos'].append('multiplas_normas_no_mesmo_documento')
    if titulo:
        numero, data_lei, ano, complementar = parse_titulo(titulo)
        if registro.get('numero') and numero and str(registro['numero']) != str(numero):
            extracao['conflitos'].append('numero_do_documento_diverge_do_contexto')
        if registro.get('data_lei') and data_lei and registro['data_lei'] != data_lei:
            extracao['conflitos'].append('data_do_documento_diverge_do_contexto')
        registro.setdefault('titulo', titulo)
        if numero:
            registro.setdefault('numero', numero)
            registro.setdefault('chave', ('LC-' if complementar else '') + numero)
        if data_lei:
            registro.setdefault('data_lei', data_lei)
        if ano:
            registro.setdefault('ano', int(ano))
        registro.setdefault('tipo', 'Lei Complementar' if complementar else 'Lei')
    link = registro.get('link')
    if isinstance(link, str):
        url = urlsplit(link)
        materia = url.path.rstrip('/').split('/')[-1]
        if url.hostname in {'www.cml.pr.gov.br', 'www1.cml.pr.gov.br', 'cml.pr.gov.br'} and materia.isdigit():
            registro.setdefault('id', materia)
    registro['artigos'] = separar_artigos(texto, riscados)
    registro['texto_disponivel'] = bool(registro['artigos'])
    registro.setdefault('relacoes', [])
    registro.setdefault('relacionamentos', [])
    registro.setdefault('anexos', [])
    registro.setdefault('ementa', None)
    registro['extracao'] = dict(extracao, texto_extraido=texto,
                               sha256_texto=hashlib.sha256(texto.encode('utf-8')).hexdigest())
    # Nunca deduz vigência a partir de ter conseguido ler o documento.
    return [registro]


def extrair_html(raw, contexto=None):
    soup = BeautifulSoup(raw, 'html.parser')
    contexto = dict(contexto or {})
    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href'):
        if contexto.get('link') and contexto['link'].split('#')[0] != canonical['href'].split('#')[0]:
            raise ValueError('URL canônica do HTML difere do contexto.')
        contexto.setdefault('link', canonical['href'])
    raiz = (soup.select_one('.pbw_exibir_materia') or soup.select_one('[data-lei]')
            or soup.find('article') or soup.find('main') or soup.body or soup)
    for node in raiz.select('script, style, nav, header, footer, form, noscript, template'):
        node.decompose()
    partes, mascara = [], []
    blocos = {'div', 'p', 'section', 'article', 'main', 'h1', 'h2', 'h3', 'li', 'tr'}
    def adicionar(valor, riscado=False):
        partes.append(valor)
        mascara.extend([riscado] * len(valor))
    def visitar(node, riscado=False):
        if isinstance(node, NavigableString):
            adicionar(str(node).replace('\xa0', ' '), riscado)
            return
        style = re.sub(r'\s+', '', str(node.get('style', '')).lower())
        if node.has_attr('hidden') or 'display:none' in style or 'visibility:hidden' in style:
            return
        riscado = riscado or node.name in {'s', 'strike', 'del'} or bool(re.search(r'text-decoration(?:-line)?:[^;]*line-through', style))
        if node.name in blocos or node.name == 'br':
            adicionar('\n')
        for filho in node.children:
            visitar(filho, riscado)
        if node.name in blocos:
            adicionar('\n')
    visitar(raiz)
    texto = ''.join(partes)
    if not texto.strip():
        raise ValueError('HTML sem conteúdo textual legível.')
    return _montar(texto, mascara, contexto, dict(formato='html', metodo='dom', paginas=[],
        conflitos=[], exige_revisao_extracao=False))


def _tessdata():
    caminho = Path(os.getenv('OCR_TESSDATA', str(TESSDATA)))
    arquivo = caminho / 'por.traineddata'
    if not arquivo.is_file():
        raise ValueError('Modelo OCR português ausente; execute preparar_ocr.py.')
    if hashlib.sha256(arquivo.read_bytes()).hexdigest() != OCR_SHA256:
        raise ValueError('Modelo OCR português diferente da versão homologada.')
    # A biblioteca nativa do Tesseract no Windows não abre alguns caminhos Unicode.
    if os.name == 'nt' and not str(caminho).isascii():
        cache = Path(tempfile.gettempdir()) / 'hackathon_ocr' / OCR_SHA256
        cache.mkdir(parents=True, exist_ok=True)
        destino = cache / 'por.traineddata'
        dados = arquivo.read_bytes()
        if not destino.is_file() or hashlib.sha256(destino.read_bytes()).hexdigest() != OCR_SHA256:
            destino.write_bytes(dados)
        caminho = cache
    return str(caminho)


def extrair_pdf(raw, contexto=None):
    import pymupdf
    texto, mascara, paginas, conflitos = '', [], [], []
    usou_ocr = False
    try:
        documento = pymupdf.open(stream=raw, filetype='pdf')
    except Exception as exc:
        raise ValueError('PDF inválido ou ilegível.') from exc
    with documento:
        if documento.needs_pass:
            raise ValueError('PDF protegido por senha; forneça uma cópia acessível autorizada.')
        if not 0 < documento.page_count <= 200:
            raise ValueError('PDF vazio ou acima do limite de 200 páginas por entrada.')
        for numero, pagina in enumerate(documento, 1):
            inicio = len(texto)
            nativo = pagina.get_text('text', sort=True)
            imagens = pagina.get_image_info()
            area_imagens = sum(pymupdf.Rect(i['bbox']).get_area() for i in imagens)
            necessita_ocr = len(nativo.strip()) < 40 or area_imagens > pagina.rect.get_area() * .15
            if necessita_ocr:
                if pagina.rect.width * pagina.rect.height > 4000000:
                    raise ValueError('Página excede o limite de área para OCR.')
                try:
                    tp = pagina.get_textpage_ocr(language='por', dpi=200, full=True, tessdata=_tessdata())
                    atual = pagina.get_text('text', textpage=tp, sort=True)
                except ValueError:
                    raise
                except Exception as exc:
                    raise ValueError(f'OCR não conseguiu processar a página {numero}.') from exc
                if not atual.strip():
                    raise ValueError(f'Página {numero} sem texto recuperável mesmo após OCR.')
                mask = [False] * len(atual)
                metodo = 'ocr_por'
                usou_ocr = True
            else:
                atual, mask = '', []
                linhas_riscadas = []
                for desenho in pagina.get_drawings():
                    for item in desenho['items']:
                        if item[0] == 'l' and abs(item[1].y - item[2].y) < 1.5:
                            linhas_riscadas.append((min(item[1].x, item[2].x), max(item[1].x, item[2].x), item[1].y))
                anotacoes = [a.rect for a in (pagina.annots() or []) if a.type[1] == 'StrikeOut']
                for bloco in pagina.get_text('rawdict', sort=True)['blocks']:
                    for linha in bloco.get('lines', []):
                        for span in linha['spans']:
                            for char in span['chars']:
                                rect = pymupdf.Rect(char['bbox'])
                                riscado = any((rect & r).get_area() > rect.get_area() * .5 for r in anotacoes)
                                riscado = riscado or any(
                                    rect.y0 + rect.height * .3 <= y <= rect.y0 + rect.height * .7
                                    and min(rect.x1, x1) - max(rect.x0, x0) > rect.width * .5
                                    for x0, x1, y in linhas_riscadas)
                                atual += char['c']
                                mask.extend([riscado] * len(char['c']))
                        atual += '\n'
                        mask.append(False)
                metodo = 'texto_nativo'
            texto += atual + '\n'
            mascara.extend(mask + [False])
            paginas.append(dict(pagina=numero, metodo=metodo, inicio=inicio, fim=len(texto)))
    return _montar(texto, mascara, contexto, dict(formato='pdf', metodo='pdf_com_ocr' if usou_ocr else 'pdf_textual',
        paginas=paginas, conflitos=conflitos, exige_revisao_extracao=usou_ocr))

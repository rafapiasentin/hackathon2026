"""Gera o decretos.json: os decretos ligados às leis de Londrina.

Duas fontes, cada uma registrada no vínculo (campo "origem"):
  1. Notas da Câmara no leis.json, como "(Vide Decreto nº 466, de 16 de abril de 2025)" na ementa ou
     num artigo, "(Eficácia suspensa pelo Decreto-Legislativo nº 221...)" e o relacionamento "Suspende".
     Daí vem a ligação lei -> decreto, mesmo sem o texto do decreto.
  2. O texto dos decretos listados em decretos_fontes.json (PDF do Município). A súmula do decreto
     diz quais leis ele regulamenta ("Regulamenta o Art. 50-A da Lei Municipal nº 13.898...").

Uso:
    python coleta_decretos.py                 # lê leis.json (ou leis.zip) e gera decretos.json
    python coleta_decretos.py --sem-download  # usa só o cache_decretos/ (sem internet)
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZipFile

import decretos as d

PASTA = Path(__file__).parent
CACHE = PASTA / 'cache_decretos'
VERSAO = '1.0'
LIMITE_BYTES = 30 * 1024 * 1024


def ler_leis(caminho):
    caminho = Path(caminho)
    if caminho.suffix == '.zip':
        with ZipFile(caminho) as z:
            nome = next(n for n in z.namelist() if Path(n).name == 'leis.json')
            raw = z.read(nome)
    else:
        raw = caminho.read_bytes()
    return json.loads(raw.decode('utf-8-sig')), hashlib.sha256(raw).hexdigest()


def url_do_municipio(url):
    host = (urlsplit(url).hostname or '').lower()
    return urlsplit(url).scheme == 'https' and (host == 'londrina.pr.gov.br' or host.endswith('.londrina.pr.gov.br'))


def baixar(fonte, sem_download=False):
    """Baixa o PDF uma vez e guarda em cache_decretos/ (o mesmo arquivo serve às próximas coletas)."""
    CACHE.mkdir(exist_ok=True)
    arquivo = CACHE / f"{d.identificador(fonte['tipo'], fonte['numero'], fonte['ano'])}.pdf"
    if not arquivo.exists():
        if sem_download:
            raise ValueError(f'{arquivo.name} não está no cache e --sem-download foi usado.')
        import requests
        r = requests.get(fonte['url'], timeout=60, headers={'User-Agent': 'Mozilla/5.0 (coleta de decretos)'})
        r.raise_for_status()
        if not r.content.startswith(b'%PDF') or len(r.content) > LIMITE_BYTES:
            raise ValueError(f"{fonte['url']} não devolveu um PDF válido.")
        arquivo.write_bytes(r.content)
    return arquivo.read_bytes(), datetime.datetime.fromtimestamp(arquivo.stat().st_mtime).astimezone()


def texto_do_pdf(raw):
    import pymupdf
    with pymupdf.open(stream=raw, filetype='pdf') as documento:
        if not 0 < documento.page_count <= 200:
            raise ValueError('PDF vazio ou com mais de 200 páginas.')
        texto = '\n'.join(pagina.get_text('text', sort=True) for pagina in documento)
    if len(texto.strip()) < 200:
        raise ValueError('PDF sem texto (escaneado): use o OCR do projeto antes de incluir.')
    return texto


def artigos_do_texto(texto):
    from extracao_documentos import separar_artigos
    corpo = texto[texto.upper().find('DECRETA'):] if 'DECRETA' in texto.upper() else texto
    # O título do capítulo seguinte ("CAPÍTULO II / DAS DIRETRIZES...") não faz parte do artigo.
    titulo = re.compile(r'\n(?:CAP[IÍ]TULO|SE[CÇ][AÃ]O|T[IÍ]TULO)\b')
    return [dict(ordem=a['ordem'], artigo=a['artigo'], texto=titulo.split(a['texto'])[0].strip())
            for a in separar_artigos(corpo, [False] * len(corpo)) if a['texto']]


def resolver_lei(chave, ano, por_chave):
    """Lei citada pelo número (e ano, quando há): só liga quando não há dúvida."""
    candidatas = [l for l in por_chave.get(chave, []) if ano is None or l['ano'] == str(ano)]
    return candidatas[0] if len(candidatas) == 1 else None


def coletar(leis, fontes, sem_download=False):
    registro, vinculos = {}, []

    def decreto(info, revogado_por=None):
        chave = d.identificador(info['tipo'], info['numero'], info['ano'])
        atual = registro.setdefault(chave, dict(
            id=chave, tipo=info['tipo'], numero=info['numero'], ano=info['ano'], data=None, ementa=None,
            link=None, situacao='sem_registro_de_revogacao', revogado_por=None, texto_disponivel=False,
            artigos=[], fonte_texto=None))
        atual['data'] = atual['data'] or info.get('data')
        if revogado_por and revogado_por.get('ano'):
            atual['situacao'] = 'revogado'
            atual['revogado_por'] = d.nome_decreto(revogado_por['tipo'], revogado_por['numero'], revogado_por['ano'])
        return atual

    def vincular(lei_id, item, tipo, dispositivo, origem, nota):
        novo = dict(lei_id=lei_id, decreto_id=item['id'], tipo=tipo, dispositivo=dispositivo, origem=origem, nota=nota)
        if novo not in vinculos:
            vinculos.append(novo)

    # 1) Notas da Câmara nas leis
    for lei in leis:
        trechos = [(None, lei.get('ementa') or '')] + [(a['artigo'], a['texto']) for a in lei.get('artigos', [])]
        for dispositivo, texto in trechos:
            for nota in d.notas_de_decreto(texto):
                item = decreto(nota['decreto'], nota['revogado_por'])
                vincular(lei['id'], item, nota['tipo_vinculo'], dispositivo, 'nota_cml', nota['nota'])
        for rel in lei.get('relacionamentos', []):
            if rel.get('tipo') == 'Suspende':
                info = d.suspensao_em_relacionamento(rel.get('descricao'))
                if info:
                    vincular(lei['id'], decreto(info), d.EFICACIA_SUSPENSA_POR, None, 'relacionamento_cml',
                             ' '.join((rel.get('descricao') or '').split())[:300])

    # 2) Texto dos decretos (PDF do Município)
    por_chave = {}
    for lei in leis:
        por_chave.setdefault(lei['chave'], []).append(lei)
    for fonte in fontes:
        if not url_do_municipio(fonte['url']):
            raise ValueError(f"{fonte['url']}: só são aceitos documentos do Município (londrina.pr.gov.br).")
        raw, baixado_em = baixar(fonte, sem_download)
        lido = d.ler_decreto(texto_do_pdf(raw))
        if (lido['tipo'], lido['numero'], lido['ano']) != (fonte['tipo'], str(fonte['numero']), int(fonte['ano'])):
            raise ValueError(f"O PDF de {fonte['url']} é do {d.nome_decreto(lido['tipo'], lido['numero'], lido['ano'])}, "
                             f"não do {d.nome_decreto(fonte['tipo'], fonte['numero'], fonte['ano'])}.")
        item = decreto(lido)
        artigos = artigos_do_texto(lido['texto'])
        if not artigos:
            raise ValueError(f"Nenhum artigo encontrado no {d.nome_decreto(lido['tipo'], lido['numero'], lido['ano'])}.")
        item.update(data=lido['data'], ementa=lido['ementa'], link=fonte['url'], texto_disponivel=True, artigos=artigos,
                    fonte_texto=dict(url=fonte['url'], sha256=hashlib.sha256(raw).hexdigest(),
                                     baixado_em=baixado_em.isoformat(timespec='seconds'), metodo='pdf_textual'))
        for chave, ano in lido['leis']:
            lei = resolver_lei(chave, ano, por_chave)
            if lei:
                vincular(lei['id'], item, d.REGULAMENTADA_POR, None, 'sumula_decreto', lido['ementa'])

    lista = sorted(registro.values(), key=lambda x: (x['tipo'], -x['ano'], int(x['numero'])))
    return lista, vinculos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--leis', default='leis.json' if (PASTA / 'leis.json').exists() else 'leis.zip')
    ap.add_argument('--fontes', default='decretos_fontes.json')
    ap.add_argument('--saida', default='decretos.json')
    ap.add_argument('--sem-download', action='store_true')
    args = ap.parse_args()
    try:
        leis, sha_leis = ler_leis(args.leis)
        fontes = json.loads(Path(args.fontes).read_text(encoding='utf-8'))['decretos']
        lista, vinculos = coletar(leis, fontes, args.sem_download)
    except (ValueError, OSError, KeyError) as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        return 1
    saida = dict(
        versao_formato=VERSAO,
        gerado_em=datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        leis_json_sha256=sha_leis,
        totais=dict(decretos=len(lista), com_texto=sum(x['texto_disponivel'] for x in lista),
                    revogados=sum(x['situacao'] == 'revogado' for x in lista), vinculos=len(vinculos),
                    por_tipo_vinculo={t: sum(v['tipo'] == t for v in vinculos) for t in d.TIPOS_VINCULO}),
        decretos=lista, vinculos=vinculos)
    Path(args.saida).write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{args.saida}: {json.dumps(saida['totais'], ensure_ascii=False)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""Fixtures PDF/HTML sintéticas para extração e integração PostgreSQL."""
import hashlib
import json

import pymupdf
import pytest

from adaptadores import carregar_formato
from banco import Artigo, Lei, VersaoRegistro
from extracao_documentos import extrair_html, extrair_pdf
from governanca import hash_registro, receber, validar_registro, contrato_atual
from test_governanca import lei_sintetica, revisar


HTML = b'''<html><head><title>Menu</title></head><body><nav>Art. 999 Menu</nav>
<article><h1>LEI N. 48, DE 1 DE JANEIRO DE 2026</h1>
<p><strong>Art. 1</strong> Texto atual. <del>Trecho antigo.</del></p>
<p><strong>Art. 2</strong><s>Artigo inteiramente revogado.</s></p>
<p style="display:none">Art. 900 Invisivel</p>
<script>Art. 901 script</script><footer>Art. 902 Rodape</footer></article></body></html>'''


def pdf_sintetico(escaneado=False, riscado=False):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 60), 'LEI N. 48, DE 1 DE JANEIRO DE 2026', fontsize=14)
    page.insert_text((50, 100), 'Art. 1 Texto atual de uma lei sintetica para testes.', fontsize=14)
    page.insert_text((50, 140), 'Art. 2 Artigo antigo inteiramente revogado.', fontsize=14)
    if riscado:
        page.add_strikeout_annot(page.search_for('Artigo antigo inteiramente revogado.')[0]).update()
    if escaneado:
        imagem = page.get_pixmap(dpi=200)
        novo = pymupdf.open()
        p = novo.new_page(width=page.rect.width, height=page.rect.height)
        p.insert_image(p.rect, pixmap=imagem)
        raw = novo.tobytes()
        novo.close()
    else:
        raw = doc.tobytes()
    doc.close()
    return raw


def test_html_extrai_artigos_e_separa_texto_riscado(lei_sintetica):
    registro = extrair_html(HTML, lei_sintetica)[0]
    assert len(registro['artigos']) == 2
    a, b = registro['artigos']
    assert 'Texto atual.' in a['texto'] and 'Trecho antigo' not in a['texto']
    assert a['texto_riscado'] == 'Trecho antigo.'
    assert b['revogado'] and b['texto'] == ''
    assert 'revogado' in b['texto_riscado']


def test_pdf_textual_e_anotacao_riscada(lei_sintetica):
    raw = pdf_sintetico(riscado=True)
    registro = extrair_pdf(raw, lei_sintetica)[0]
    assert len(registro['artigos']) == 2
    assert registro['artigos'][1]['revogado']
    assert registro['artigos'][1]['texto'] == ''
    assert registro['extracao']['paginas'][0]['metodo'] == 'texto_nativo'


def test_pdf_escaneado_ocr_portugues_real(lei_sintetica):
    registro = extrair_pdf(pdf_sintetico(escaneado=True), lei_sintetica)[0]
    assert len(registro['artigos']) == 2
    assert 'Texto atual' in registro['artigos'][0]['texto']
    assert registro['extracao']['paginas'][0]['metodo'] == 'ocr_por'
    assert registro['extracao']['exige_revisao_extracao']
    _, problemas = validar_registro(registro, {'123'}, contrato_atual())
    assert 'ocr_requer_conferencia' in {p['codigo'] for p in problemas}


def test_html_incompleto_nao_e_formato_desconhecido():
    registros, _, _ = carregar_formato(b'<html><main>Art. 1 Texto legivel.</main></html>', 'lei.html')
    assert registros[0]['artigos']
    assert registros[0]['extracao']['formato'] == 'html'
    assert 'situacao' not in registros[0]


@pytest.mark.parametrize('ext', ['html', 'pdf'])
@pytest.mark.postgres
def test_documento_ate_publicacao_no_postgres(db_governanca, tmp_path, lei_sintetica, monkeypatch, ext):
    raw = HTML if ext == 'html' else pdf_sintetico()
    extrair = extrair_html if ext == 'html' else extrair_pdf
    registro = extrair(raw, lei_sintetica)[0]
    revisar(registro, monkeypatch)
    contexto = dict(lei_sintetica, revisao_vigencia=registro['revisao_vigencia'])
    path = tmp_path / ('lei.' + ext)
    path.write_bytes(raw)
    meta = dict(registro=contexto, arquivo=dict(sha256=hashlib.sha256(raw).hexdigest()),
        totais=dict(leis=1, artigos=len(registro['artigos']),
                    artigos_revogados=sum(a['revogado'] for a in registro['artigos']), relacoes=0))
    meta_path = tmp_path / 'lei.meta.json'
    meta_path.write_text(json.dumps(meta), encoding='utf-8')
    resultado = receber(db_governanca, path, lei_sintetica['link'], meta_path)
    assert resultado['estado'] == 'publicado'
    assert Lei.select().count() == 1 and Artigo.select().count() == 2
    assert VersaoRegistro.get().original['extracao']['formato'] == ext

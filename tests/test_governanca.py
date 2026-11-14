"""Dados sintéticos identificados; nenhuma fixture é uma lei real."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import pytest
from peewee import IntegrityError

from adaptadores import ErroEntrada, carregar_formato, padronizar
from banco import (Artigo, DocumentoOriginal, Lei, LoteIngestao, PendenciaIngestao,
                   PublicacaoLei, VersaoRegistro, artigos_para_chatbot)
from governanca import (contrato_atual, hash_registro, receber, url_oficial,
                        validar_registro, verificar_revisao)


@pytest.fixture
def lei_sintetica():
    return dict(id='123', chave='48', tipo='Lei', numero='48', ano=2026,
                data_lei='2026-01-01', titulo='LEI SINTÉTICA PARA TESTES', ementa=None,
                link='https://www.cml.pr.gov.br/proposicoes/0/0/0/0/123',
                situacao='vigente', texto_disponivel=True, fonte_relacoes='cml',
                artigos=[dict(ordem=1, artigo='Art. 1º', texto='Redação vigente sintética.',
                              texto_riscado=None, revogado=False)], relacoes=[], relacionamentos=[], anexos=[])


def revisar(lei, monkeypatch):
    monkeypatch.setenv('GOVERNANCA_REVISORES', 'equipe_teste')
    lei['revisao_vigencia'] = dict(responsavel='equipe_teste', verificado_em='2020-01-01T00:00:00Z',
        fonte=lei['link'], trecho=lei['artigos'][0]['texto'], situacao=lei['situacao'],
        hash_registro=hash_registro(lei))
    return lei


def entrada(tmp_path, leis, nome='leis.json', corromper=False):
    raw = json.dumps(leis, ensure_ascii=False).encode('utf-8')
    meta = dict(arquivo=dict(sha256=hashlib.sha256(raw).hexdigest()), commit='f9be9d4',
                totais=dict(leis=len(leis), artigos=sum(len(l['artigos']) for l in leis),
                    artigos_revogados=sum(a['revogado'] for l in leis for a in l['artigos']),
                    relacoes=sum(len(l['relacoes']) for l in leis)))
    if corromper:
        meta['totais']['artigos'] += 1
    path = tmp_path / nome
    path.write_bytes(raw)
    (tmp_path / 'leis.meta.json').write_text(json.dumps(meta), encoding='utf-8')
    return path


@pytest.mark.parametrize('ext', ['json', 'jsonl', 'csv', 'xml', 'zip'])
def test_adaptadores_equivalentes(ext, lei_sintetica, tmp_path):
    lei = lei_sintetica
    if ext == 'json':
        raw = json.dumps([lei]).encode()
    elif ext == 'jsonl':
        raw = json.dumps(lei).encode()
    elif ext == 'csv':
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=lei)
        writer.writeheader()
        writer.writerow({k: json.dumps(v) if isinstance(v, (list, dict, bool)) else v for k, v in lei.items()})
        raw = buffer.getvalue().encode()
    elif ext == 'xml':
        from xml.etree.ElementTree import Element, SubElement, tostring
        root = Element('leis')
        node = SubElement(root, 'lei')
        for k, v in lei.items():
            SubElement(node, k).text = json.dumps(v) if isinstance(v, (list, dict, bool)) else str(v or '')
        raw = tostring(root)
    else:
        path = tmp_path / 'leis.zip'
        with ZipFile(path, 'w') as z:
            z.writestr('leis.json', json.dumps([lei]))
        raw = path.read_bytes()
    registros, _, _ = carregar_formato(raw, 'dados.' + ext)
    dados, erros = validar_registro(padronizar(registros[0]), {'123'}, contrato_atual())
    assert dados is not None
    assert not [e for e in erros if e['severidade'] == 'erro']


@pytest.mark.parametrize('valor', ['https://evil.example/123', 'https://www.cml.pr.gov.br.evil.example/123',
    'https://usuario:senha@www.cml.pr.gov.br/123', 'https://www.cml.pr.gov.br/123?keysoft=segredo',
    'http://www.cml.pr.gov.br/123', 'https://www.cml.pr.gov.br:123/123'])
def test_rejeita_fontes_invalidas(valor):
    assert not url_oficial(valor, contrato_atual())


@pytest.mark.parametrize('ext,raw', [('pdf', b'%PDF-1.7'),
    ('json', b'{broken'), ('xml', b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///secret">]><leis><lei>&x;</lei></leis>')])
def test_formatos_nao_interpretaveis_geram_erro(ext, raw):
    with pytest.raises(ErroEntrada):
        carregar_formato(raw, 'dados.' + ext)


def test_padroniza_sem_adivinhar(lei_sintetica):
    original = copy.deepcopy(lei_sintetica)
    original['ano'] = '2026'
    original['texto_disponivel'] = 'true'
    original['ementa'] = ''
    original['id_cml'] = original.pop('id')
    convertido = padronizar(original)
    assert convertido['ano'] == 2026 and convertido['texto_disponivel'] is True
    assert convertido['ementa'] is None and convertido['id'] == '123'
    assert original['ano'] == '2026'


def test_revisao_vinculada_ao_conteudo_e_responsavel(lei_sintetica, monkeypatch):
    lei = revisar(lei_sintetica, monkeypatch)
    assert verificar_revisao(lei, contrato_atual())
    lei['artigos'][0]['texto'] = 'Conteúdo mudou'
    assert not verificar_revisao(lei, contrato_atual())
    monkeypatch.delenv('GOVERNANCA_REVISORES')
    assert not verificar_revisao(lei, contrato_atual())


@pytest.mark.parametrize('mudanca,codigo', [
    ({'data_lei': '2026-02-30'}, 'data_invalida'),
    ({'data_lei': '2025-01-01'}, 'ano_divergente'),
    ({'situacao': 'talvez'}, 'valor_nao_permitido'),
    ({'titulo': ''}, 'tipo_invalido'),
    ({'link': 'https://www.cml.pr.gov.br/proposicoes/999'}, 'identidade_divergente'),
])
def test_regras_contrato(lei_sintetica, mudanca, codigo):
    lei_sintetica.update(mudanca)
    dados, problemas = validar_registro(lei_sintetica, {'123'}, contrato_atual())
    assert dados is None
    assert codigo in {p['codigo'] for p in problemas}


@pytest.mark.postgres
def test_publicacao_idempotente_historico_e_chatbot(db_governanca, tmp_path, lei_sintetica, monkeypatch):
    lei = revisar(lei_sintetica, monkeypatch)
    path = entrada(tmp_path, [lei])
    primeiro = receber(db_governanca, path, 'https://www.cml.pr.gov.br/dadosabertos')
    repetido = receber(db_governanca, path, 'https://www.cml.pr.gov.br/dadosabertos')
    assert primeiro['estado'] == 'publicado' and repetido['repetido']
    assert Lei.select().count() == 1 and VersaoRegistro.select().count() == 1
    assert bytes(DocumentoOriginal.get().conteudo) == path.read_bytes()
    assert LoteIngestao.get().metadados['commit'] == 'f9be9d4'
    assert [a.texto for a in artigos_para_chatbot()] == ['Redação vigente sintética.']
    lei['artigos'][0]['texto'] = 'Redação nova sintética.'
    revisar(lei, monkeypatch)
    resultado = receber(db_governanca, entrada(tmp_path, [lei]), 'https://www.cml.pr.gov.br/dadosabertos')
    assert resultado['estado'] == 'publicado'
    assert Artigo.get().texto == 'Redação nova sintética.'
    assert VersaoRegistro.select().count() == 2 and DocumentoOriginal.select().count() == 2


@pytest.mark.postgres
def test_atualizacao_invalida_preserva_texto_e_retira_do_chatbot(db_governanca, tmp_path, lei_sintetica, monkeypatch):
    lei = revisar(lei_sintetica, monkeypatch)
    receber(db_governanca, entrada(tmp_path, [lei]), 'https://www.cml.pr.gov.br/dadosabertos')
    lei['data_lei'] = '2026-02-30'
    resultado = receber(db_governanca, entrada(tmp_path, [lei]), 'https://www.cml.pr.gov.br/dadosabertos')
    assert resultado['estado'] == 'quarentena'
    assert Artigo.get().texto == 'Redação vigente sintética.'
    assert list(artigos_para_chatbot()) == []
    assert PublicacaoLei.get().estado == 'pendente'
    assert PendenciaIngestao.select().where(PendenciaIngestao.codigo == 'data_invalida').exists()


@pytest.mark.postgres
def test_integridade_bloqueia_lote_inteiro(db_governanca, tmp_path, lei_sintetica, monkeypatch):
    lei = revisar(lei_sintetica, monkeypatch)
    resultado = receber(db_governanca, entrada(tmp_path, [lei], corromper=True), 'https://www.cml.pr.gov.br/dadosabertos')
    assert resultado['publicados'] == 0 and Lei.select().count() == 0
    assert PendenciaIngestao.select().where(PendenciaIngestao.codigo == 'integridade_lote').exists()


@pytest.mark.postgres
def test_publica_parcial_e_propaga_dependencia(db_governanca, tmp_path, lei_sintetica, monkeypatch):
    primeira = revisar(copy.deepcopy(lei_sintetica), monkeypatch)
    segunda = copy.deepcopy(lei_sintetica)
    segunda.update(id='456', link='https://www.cml.pr.gov.br/proposicoes/456', situacao='desconhecida')
    terceira = copy.deepcopy(lei_sintetica)
    terceira.update(id='789', link='https://www.cml.pr.gov.br/proposicoes/789')
    terceira['relacoes'] = [dict(id='456', chave='48', tipo='altera')]
    revisar(terceira, monkeypatch)
    resultado = receber(db_governanca, entrada(tmp_path, [primeira, segunda, terceira]), 'https://www.cml.pr.gov.br/dadosabertos')
    assert resultado['estado'] == 'parcial' and resultado['publicados'] == 1
    assert Lei.get().id == '123'
    assert PendenciaIngestao.select().where(PendenciaIngestao.codigo == 'dependencia_pendente').exists()


@pytest.mark.postgres
def test_sem_revisao_retem_e_nao_deduz_vigencia(db_governanca, tmp_path, lei_sintetica, monkeypatch):
    monkeypatch.delenv('GOVERNANCA_REVISORES', raising=False)
    resultado = receber(db_governanca, entrada(tmp_path, [lei_sintetica]), 'https://www.cml.pr.gov.br/dadosabertos')
    assert resultado['publicados'] == 0
    assert PendenciaIngestao.select().where(PendenciaIngestao.codigo == 'vigencia_nao_verificada').exists()


@pytest.mark.postgres
def test_formato_desconhecido_preserva_original(db_governanca, tmp_path):
    path = tmp_path / 'lei.pdf'
    path.write_bytes(b'%PDF-sintetico')
    resultado = receber(db_governanca, path, 'https://www.cml.pr.gov.br/dadosabertos')
    assert resultado['estado'] == 'quarentena'
    assert bytes(DocumentoOriginal.get().conteudo) == b'%PDF-sintetico'


@pytest.mark.postgres
def test_falha_de_banco_reverte_publicacao_mas_audita(db_governanca, tmp_path, lei_sintetica, monkeypatch):
    import governanca
    lei = revisar(lei_sintetica, monkeypatch)
    receber(db_governanca, entrada(tmp_path, [lei]), 'https://www.cml.pr.gov.br/dadosabertos')
    publicar_original = governanca._publicar
    def falhar(db, preparados):
        publicar_original(db, preparados)
        raise IntegrityError('falha sintética após atualização')
    monkeypatch.setattr(governanca, '_publicar', falhar)
    lei['artigos'][0]['texto'] = 'Não deve persistir'
    revisar(lei, monkeypatch)
    resultado = receber(db_governanca, entrada(tmp_path, [lei]), 'https://www.cml.pr.gov.br/dadosabertos')
    assert resultado['publicados'] == 0
    assert Artigo.get().texto == 'Redação vigente sintética.'
    assert PendenciaIngestao.select().where(PendenciaIngestao.codigo == 'publicacao_falhou').exists()

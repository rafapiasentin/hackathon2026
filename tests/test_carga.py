"""Fixtures sintéticas; integração opcional usa exclusivamente DB_TEST_NAME."""
import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from banco import Artigo, Carga, Lei, MODELOS, Relacao, RelacionamentoCml, artigos_para_chatbot, conectar
from carregar_leis import importar, ler_entrada, normalizar, totais_banco, validar_meta


def fixture():
    # Destino do complemento vem depois; chave repetida e rótulos de artigo repetidos são válidos.
    base = dict(chave='48', tipo='Lei', numero='48', ano='2026', titulo='Lei de teste sintética',
                ementa=None, link='https://example.invalid/lei', situacao='vigente',
                texto_disponivel=True, artigos=[], relacoes=[], relacionamentos=[])
    primeira = dict(copy.deepcopy(base), id='1', tipo='Promulgação de partes vetadas', complementa_id='2',
                    data_lei='2010-02-29', hash_texto='a' * 64, anexos=['https://example.invalid/anexo'])
    primeira['artigos'] = [
        dict(ordem=1, artigo='Art. 1º', texto='Redação vigente sintética', texto_riscado='Redação antiga', revogado=False),
        dict(ordem=2, artigo='Art. 1º', texto='', texto_riscado='Revogado integralmente', revogado=True),
    ]
    primeira['relacoes'] = [dict(id='2', chave='48', tipo='altera'), dict(id=None, chave='LC-12', tipo='cita')]
    primeira['relacionamentos'] = [dict(id='999', tipo='Sanção', descricao='Projeto fora da base', data='14/11/2026')]
    segunda = dict(copy.deepcopy(base), id='2', situacao='revogada')
    segunda['artigos'] = [dict(ordem=1, artigo='Art. 1º', texto='Não recuperar', texto_riscado=None, revogado=False)]
    return [primeira, segunda]


class ValidacaoTest(unittest.TestCase):
    def test_formato_novo_e_datas_impossiveis(self):
        dados, totais, corrigido = normalizar(fixture())
        self.assertTrue(corrigido)
        self.assertEqual(totais['artigos_revogados'], 1)
        self.assertIsNone(dados['leis'][0]['data_lei'])
        self.assertEqual(dados['leis'][0]['data_lei_original'], '2010-02-29')
        self.assertIsNone(dados['leis'][0]['ementa'])

    def test_legado_defaults(self):
        leis = fixture()
        for lei in leis:
            for artigo in lei['artigos']:
                artigo.pop('texto_riscado')
                artigo.pop('revogado')
        dados, _, corrigido = normalizar(leis)
        self.assertFalse(corrigido)
        self.assertFalse(dados['artigos'][0]['revogado'])
        self.assertIsNone(dados['artigos'][0]['texto_riscado'])

    def test_rejeita_ids_ordens_referencias_e_texto_revogado(self):
        for alterar in (
            lambda x: x[1].update(id='1'),
            lambda x: x[0]['artigos'][1].update(ordem=1),
            lambda x: x[0].update(complementa_id='999'),
            lambda x: x[0]['relacoes'][0].update(id='999'),
            lambda x: x[0]['relacoes'][0].update(id='1'),
            lambda x: x[0]['artigos'][1].update(texto='texto indevido'),
            lambda x: x[0]['artigos'][1].update(revogado='false'),
        ):
            leis = fixture()
            alterar(leis)
            with self.assertRaises(ValueError):
                normalizar(leis)

    def test_zip_e_metadados_hash_do_json_descompactado(self):
        raw = json.dumps(fixture(), ensure_ascii=False).encode('utf-8')
        sha = hashlib.sha256(raw).hexdigest()
        _, totais, _ = normalizar(fixture())
        meta = dict(sha256=sha, totais=totais)
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / 'leis.zip'
            with ZipFile(zip_path, 'w') as arquivo:
                arquivo.writestr('dados/leis.json', raw)
                arquivo.writestr('dados/leis.meta.json', json.dumps(meta))
            leis, obtido, metadados = ler_entrada(zip_path)
            self.assertEqual(leis, fixture())
            validar_meta(metadados, obtido, totais, obrigatorio=True)
        with self.assertRaises(ValueError):
            validar_meta(meta, 'b' * 64, totais)
        with self.assertRaises(ValueError):
            validar_meta(dict(sha256=sha, totais=dict(totais, artigos=999)), sha, totais)
        with self.assertRaises(ValueError):
            validar_meta(dict(sha256=sha), sha, totais)

    def test_contrato_oficial_arquivo_sha256_e_quatro_totais(self):
        _, totais, _ = normalizar(fixture())
        sha = 'a' * 64
        meta = dict(arquivo=dict(sha256=sha), totais=totais, commit='f9be9d4')
        validar_meta(meta, sha, totais, obrigatorio=True)
        for campo in ('leis', 'artigos', 'artigos_revogados', 'relacoes'):
            errado = copy.deepcopy(meta)
            errado['totais'][campo] += 1
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                validar_meta(errado, sha, totais, obrigatorio=True)
        incompleto = copy.deepcopy(meta)
        del incompleto['totais']['relacoes']
        with self.assertRaises(ValueError):
            validar_meta(incompleto, sha, totais, obrigatorio=True)
        for arquivo in (None, {}, dict(sha256='b' * 64)):
            with self.subTest(arquivo=arquivo), self.assertRaises(ValueError):
                validar_meta(dict(meta, arquivo=arquivo), sha, totais, obrigatorio=True)
        with self.assertRaises(ValueError):
            validar_meta(dict(meta, sha256='b' * 64), sha, totais, obrigatorio=True)


@unittest.skipUnless(os.getenv('DB_TEST_NAME'), 'Defina DB_TEST_NAME para integração PostgreSQL.')
class PostgresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nome = os.environ['DB_TEST_NAME']
        if not nome.endswith('_teste'):
            raise ValueError('DB_TEST_NAME deve terminar em _teste para isolar dados reais.')
        cls.db = conectar(nome)
        cls.db.connect()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        self.dados, self.totais, self.corrigido = normalizar(fixture())
        self.sha = 'a' * 64
        self.meta = dict(arquivo=dict(sha256=self.sha), totais=self.totais, commit='f9be9d4')

    def carregar(self, **kwargs):
        return importar(self.db, self.dados, self.totais, self.sha, self.meta,
                        'fixture-sintetica.json', self.corrigido, **kwargs)

    def test_repeticao_fk_json_nulos_e_filtro_chatbot(self):
        self.carregar(final=True, lote=1)
        self.carregar(final=True, lote=2)
        self.assertEqual(totais_banco(), self.totais)
        self.assertEqual(Carga.select().count(), 1)
        self.assertEqual(Carga.get().metadados['commit'], 'f9be9d4')
        self.assertEqual(Lei.get_by_id('1').complementa_id, '2')
        self.assertIsNone(Lei.get_by_id('1').ementa)
        self.assertEqual(len(Lei.get_by_id('1').anexos), 1)
        self.assertEqual(Relacao.select().where(Relacao.lei_destino.is_null()).count(), 1)
        self.assertEqual(RelacionamentoCml.get().data, '14/11/2026')
        # A flag final da carga legada não substitui aprovação governada.
        with self.assertRaises(ValueError):
            artigos_para_chatbot()
        self.assertEqual(Artigo.get_by_id(('1', 2)).texto, '')

    def test_rollback_restaura_tabelas_e_carga_anterior(self):
        self.carregar(final=True)
        self.dados['leis'][0]['titulo'] = None  # viola NOT NULL após o DROP transacional
        with self.assertRaises(Exception):
            self.carregar(final=True)
        self.assertEqual(totais_banco(), self.totais)
        self.assertEqual(Lei.get_by_id('1').titulo, 'Lei de teste sintética')
        self.assertTrue(Carga.get().final)

    def test_carga_provisoria_bloqueia_chatbot(self):
        self.carregar()
        with self.assertRaises(ValueError):
            artigos_para_chatbot()

    def test_duas_cargas_na_mesma_transacao(self):
        with self.db.atomic():
            self.carregar(final=True)
            self.carregar(final=True)
            self.assertEqual(totais_banco(), self.totais)


if __name__ == '__main__':
    unittest.main()

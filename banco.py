"""Conexão local e modelos da legislação. Nunca usa o número como identidade."""
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit

from dotenv import load_dotenv
from peewee import (
    AutoField, BlobField, BooleanField, CharField, Check, CompositeKey, DatabaseProxy,
    DateField, DateTimeField, ForeignKeyField, IntegerField, Model, TextField,
)
from playhouse.postgres_ext import BinaryJSONField, PostgresqlExtDatabase

load_dotenv(Path(__file__).with_name('.env'))
database = DatabaseProxy()


def conectar(nome=None):
    url = os.getenv('DATABASE_URL') if nome is None else None
    if url:
        partes = urlsplit(url)
        if partes.scheme not in ('postgres', 'postgresql') or not partes.hostname:
            raise ValueError('DATABASE_URL deve ser uma conexão PostgreSQL válida.')
        opcoes = dict(parse_qsl(partes.query))
        opcoes.setdefault('sslmode', 'require')
        opcoes.setdefault('connect_timeout', 10)
        db = PostgresqlExtDatabase(unquote(partes.path.lstrip('/')),
            host=partes.hostname, port=partes.port or 5432,
            user=unquote(partes.username or ''), password=unquote(partes.password or ''), **opcoes)
    else:
        db = PostgresqlExtDatabase(
        nome or os.getenv('DB_NAME', 'hackathon2026'),
        host=os.getenv('DB_HOST', '127.0.0.1'),
        port=int(os.getenv('DB_PORT', '5432')),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        connect_timeout=10,
        )
    database.initialize(db)
    return db


class BaseModel(Model):
    class Meta:
        database = database
        legacy_table_names = False


class Lei(BaseModel):
    id = CharField(primary_key=True)
    chave = CharField(index=True)
    tipo = CharField()
    numero = CharField()
    data_lei = DateField(null=True)
    data_lei_fonte = CharField(null=True)
    data_lei_original = CharField(null=True)
    ano = IntegerField()
    titulo = TextField()
    ementa = TextField(null=True)
    ementa_fonte = CharField(null=True)
    publicado_site = TextField(null=True)
    link = TextField()
    situacao = CharField(index=True)
    revogacao_nota = TextField(null=True)
    complementa = ForeignKeyField('self', null=True, column_name='complementa_id',
                                 backref='complementos', on_delete='RESTRICT')
    texto_disponivel = BooleanField(default=False)
    hash_texto = CharField(max_length=64, null=True,
                           constraints=[Check('hash_texto IS NULL OR length(hash_texto) = 64')])
    anexos = BinaryJSONField(default=list)
    fonte_relacoes = CharField(null=True)


class Artigo(BaseModel):
    lei = ForeignKeyField(Lei, backref='artigos', column_name='lei_id', on_delete='CASCADE')
    ordem = IntegerField(constraints=[Check('ordem > 0')])
    artigo = CharField()
    texto = TextField()
    texto_riscado = TextField(null=True)
    revogado = BooleanField(default=False)

    class Meta:
        primary_key = CompositeKey('lei', 'ordem')


class Relacao(BaseModel):
    id = AutoField()
    lei_origem = ForeignKeyField(Lei, backref='relacoes_saida', on_delete='CASCADE')
    lei_destino = ForeignKeyField(Lei, null=True, backref='relacoes_entrada', on_delete='RESTRICT')
    chave_destino = CharField(null=True)
    tipo = CharField(index=True)


class RelacionamentoCml(BaseModel):
    """Registro oficial cru: o destino também pode ser um projeto fora desta base."""
    id = AutoField()
    lei = ForeignKeyField(Lei, backref='relacionamentos_cml', on_delete='CASCADE')
    tipo = CharField()
    materia_id = CharField(null=True)
    descricao = TextField(null=True)
    data = TextField(null=True)

    class Meta:
        table_name = 'relacionamento_cml'


class Carga(BaseModel):
    """Proveniência da única carga presente, inclusive se os dados são legados."""
    id = AutoField()
    arquivo = TextField()
    sha256 = CharField(max_length=64)
    formato_corrigido = BooleanField()
    final = BooleanField(default=False)
    metadados = BinaryJSONField(null=True)
    totais = BinaryJSONField()


MODELOS = [Lei, Artigo, Relacao, RelacionamentoCml, Carga]


class Decreto(BaseModel):
    """Decreto do prefeito ou decreto legislativo da Câmara. id: "decreto-466-2025"."""
    id = CharField(primary_key=True)
    tipo = CharField()
    numero = CharField()
    ano = IntegerField()
    data = DateField(null=True)
    ementa = TextField(null=True)
    link = TextField(null=True)
    situacao = CharField(index=True)
    revogado_por = CharField(null=True)
    texto_disponivel = BooleanField(default=False)
    fonte_texto = BinaryJSONField(null=True)


class ArtigoDecreto(BaseModel):
    decreto = ForeignKeyField(Decreto, backref='artigos', column_name='decreto_id', on_delete='CASCADE')
    ordem = IntegerField(constraints=[Check('ordem > 0')])
    artigo = CharField()
    texto = TextField()

    class Meta:
        table_name = 'artigo_decreto'
        primary_key = CompositeKey('decreto', 'ordem')


class LeiDecreto(BaseModel):
    # Sem FK para lei: a carga das leis recria a tabela lei, e o vínculo sobrevive a ela.
    id = AutoField()
    lei_id = CharField(index=True)
    decreto = ForeignKeyField(Decreto, backref='vinculos', column_name='decreto_id', on_delete='CASCADE')
    tipo = CharField(index=True)
    dispositivo = CharField(null=True)
    origem = CharField()
    nota = TextField(null=True)

    class Meta:
        table_name = 'lei_decreto'


MODELOS_DECRETOS = [Decreto, ArtigoDecreto, LeiDecreto]


def agora_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class DocumentoOriginal(BaseModel):
    sha256 = CharField(primary_key=True, max_length=64)
    conteudo = BlobField()
    recebido_em = DateTimeField(default=agora_utc)


class LoteIngestao(BaseModel):
    id = AutoField()
    identidade = CharField(unique=True, max_length=64)
    documento = ForeignKeyField(DocumentoOriginal, on_delete='RESTRICT')
    nome_arquivo = TextField()
    fonte = TextField()
    formato = CharField()
    contrato = CharField()
    recebido_em = DateTimeField(default=agora_utc)
    estado = CharField(default='recebido')
    metadados = BinaryJSONField(null=True)
    relatorio = BinaryJSONField(default=dict)


class VersaoRegistro(BaseModel):
    id = AutoField()
    lote = ForeignKeyField(LoteIngestao, backref='registros', on_delete='RESTRICT')
    posicao = IntegerField()
    lei_id = CharField(null=True, index=True)
    original = BinaryJSONField()
    normalizado = BinaryJSONField(null=True)
    estado = CharField()
    vigencia_verificada = BooleanField(default=False)
    criado_em = DateTimeField(default=agora_utc)

    class Meta:
        indexes = ((('lote', 'posicao'), True),)


class PendenciaIngestao(BaseModel):
    id = AutoField()
    lote = ForeignKeyField(LoteIngestao, backref='pendencias', on_delete='RESTRICT')
    registro = ForeignKeyField(VersaoRegistro, null=True, backref='pendencias', on_delete='RESTRICT')
    codigo = CharField(index=True)
    campo = TextField()
    mensagem = TextField()
    valor = BinaryJSONField(null=True)
    severidade = CharField(default='erro')
    estado = CharField(default='aberta')
    criado_em = DateTimeField(default=agora_utc)


class PublicacaoLei(BaseModel):
    # Sem FK para lei: mantém o histórico mesmo em restaurações da base de leitura.
    lei_id = CharField(primary_key=True)
    versao = ForeignKeyField(VersaoRegistro, on_delete='RESTRICT')
    estado = CharField(index=True)
    vigencia_verificada = BooleanField(default=False)
    atualizado_em = DateTimeField(default=agora_utc)


MODELOS_GOVERNANCA = [DocumentoOriginal, LoteIngestao, VersaoRegistro,
                     PendenciaIngestao, PublicacaoLei]


def artigos_para_chatbot():
    """Somente texto vigente. Não expõe uma carga antiga como redação corrigida."""
    if not PublicacaoLei.table_exists():
        raise ValueError('Chatbot indisponível: execute a ingestão governada.')
    aprovadas = PublicacaoLei.select(PublicacaoLei.lei_id).where(
        PublicacaoLei.estado == 'publicado', PublicacaoLei.vigencia_verificada == True)
    return (Artigo.select(Artigo, Lei).join(Lei)
            .where(Lei.situacao.in_(['vigente', 'vigente_com_alteracoes']),
                   Artigo.revogado == False, Artigo.texto != '', Lei.id.in_(aprovadas)))

"""Conexão local e modelos da legislação. Nunca usa o número como identidade."""
import os
from pathlib import Path

from dotenv import load_dotenv
from peewee import (
    AutoField, BooleanField, CharField, Check, CompositeKey, DatabaseProxy,
    DateField, ForeignKeyField, IntegerField, Model, TextField,
)
from playhouse.postgres_ext import BinaryJSONField, PostgresqlExtDatabase

load_dotenv(Path(__file__).with_name('.env'))
database = DatabaseProxy()


def conectar(nome=None):
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


def artigos_para_chatbot():
    """Somente texto vigente. Não expõe uma carga antiga como redação corrigida."""
    carga = Carga.select().first()
    if not carga or not carga.formato_corrigido or not carga.final:
        raise ValueError('Chatbot indisponível: execute a carga final dos dados corrigidos.')
    return (Artigo.select(Artigo, Lei).join(Lei)
            .where(Lei.situacao.in_(['vigente', 'vigente_com_alteracoes']),
                   Artigo.revogado == False, Artigo.texto != ''))

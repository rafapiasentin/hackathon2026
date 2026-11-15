"""PostgreSQL real em schema exclusivo, revertido após cada teste."""
import os
import uuid

import pytest

from banco import MODELOS, MODELOS_DECRETOS, MODELOS_GOVERNANCA, conectar


@pytest.fixture
def db_governanca():
    nome = os.getenv('DB_TEST_NAME')
    if not nome:
        pytest.skip('Defina DB_TEST_NAME terminado em _teste para integração PostgreSQL.')
    if not nome.endswith('_teste'):
        pytest.fail('DB_TEST_NAME deve terminar em _teste.')
    db = conectar(nome)
    db.connect()
    schema = 'pytest_' + uuid.uuid4().hex
    modelos = MODELOS + MODELOS_GOVERNANCA + MODELOS_DECRETOS
    anteriores = {m: m._meta.schema for m in modelos}
    try:
        with db.atomic() as transacao:
            db.execute_sql(f'CREATE SCHEMA "{schema}"')
            db.execute_sql(f'SET LOCAL search_path TO "{schema}"')
            for modelo in modelos:
                modelo._meta.schema = schema
            db.create_tables(modelos)
            yield db
            transacao.rollback()
    finally:
        for modelo, anterior in anteriores.items():
            modelo._meta.schema = anterior
        db.close()


@pytest.fixture
def db_api():
    """HTTP usa outra thread/conexão; o schema precisa estar commitado e visível."""
    nome = os.getenv('DB_TEST_NAME')
    if not nome:
        pytest.skip('Defina DB_TEST_NAME para integração PostgreSQL.')
    if not nome.endswith('_teste'):
        pytest.fail('DB_TEST_NAME deve terminar em _teste.')
    db = conectar(nome)
    db.connect()
    schema = 'pytest_api_' + uuid.uuid4().hex
    modelos = MODELOS + MODELOS_GOVERNANCA + MODELOS_DECRETOS
    anteriores = {m: m._meta.schema for m in modelos}
    try:
        db.execute_sql(f'CREATE SCHEMA "{schema}"')
        for modelo in modelos:
            modelo._meta.schema = schema
        db.create_tables(modelos)
        yield db
    finally:
        # Alvo exclusivo deste teste, formado apenas por prefixo fixo e UUID hexadecimal.
        db.execute_sql(f'DROP SCHEMA "{schema}" CASCADE')
        for modelo, anterior in anteriores.items():
            modelo._meta.schema = anterior
        db.close()

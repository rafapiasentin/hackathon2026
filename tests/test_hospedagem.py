"""Configuração remota preserva os limites da consulta documental."""
import pytest
from banco import conectar
from api_local import create_app


def test_url_postgres_e_ssl(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://leitor:senha%40teste@exemplo.invalid/acervo')
    db = conectar()
    assert db.database == 'acervo'
    assert db.connect_params['password'] == 'senha@teste'
    assert db.connect_params['sslmode'] == 'require'
    assert conectar('isolado_teste').database == 'isolado_teste'


def test_nuvem_rejeita_excecao_local(monkeypatch):
    monkeypatch.setenv('VERCEL', '1')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://u:p@exemplo.invalid/acervo')
    with pytest.raises(RuntimeError, match='local'):
        create_app(catalogo_local=True)


@pytest.mark.postgres
def test_documental_hospedado_mantem_limites(db_api, monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setenv('VERCEL', '1')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://u:p@exemplo.invalid/acervo')
    monkeypatch.setenv('API_MODO', 'documental')
    monkeypatch.setenv('CORS_ORIGINS', 'https://rafapiasentin.github.io')
    with TestClient(create_app(db_api, catalogo_local=False)) as client:
        assert client.get('/api/health').json()['modo'] == 'documental'
        r = client.options('/api/perguntar', headers={'Origin': 'https://rafapiasentin.github.io',
            'Access-Control-Request-Method': 'POST'})
        assert r.headers['access-control-allow-origin'] == 'https://rafapiasentin.github.io'
        assert not client.post('/api/perguntar', json={'pergunta': 'ornitorrinco lunar'}).json()['fontes']

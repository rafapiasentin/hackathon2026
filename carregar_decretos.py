"""Carrega o decretos.json no PostgreSQL, numa transação só; não toca nas tabelas das leis.

Uso:
    python carregar_decretos.py                      # banco do .env (DB_NAME ou DATABASE_URL)
    python carregar_decretos.py --validar            # só confere o arquivo
    python carregar_decretos.py --banco hackathon2026_teste
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from peewee import chunked

from banco import ArtigoDecreto, Decreto, LeiDecreto, MODELOS_DECRETOS, conectar
from decretos import TIPOS_VINCULO

SITUACOES = {'revogado', 'sem_registro_de_revogacao'}
TIPOS = {'Decreto', 'Decreto Legislativo'}
ORIGENS = {'nota_cml', 'sumula_decreto', 'relacionamento_cml'}


def normalizar(dados):
    """Valida tudo antes de abrir a transação. Devolve as linhas das três tabelas."""
    if not isinstance(dados, dict) or not isinstance(dados.get('decretos'), list):
        raise ValueError('decretos.json deve ter a lista "decretos".')
    decretos, artigos, ids = [], [], set()
    for x in dados['decretos']:
        if x['id'] in ids:
            raise ValueError(f"Decreto repetido: {x['id']}.")
        ids.add(x['id'])
        if x['tipo'] not in TIPOS or x['situacao'] not in SITUACOES:
            raise ValueError(f"{x['id']}: tipo ou situação inválidos.")
        link = x.get('link')
        host = (urlsplit(link).hostname or '') if link else ''
        if link and not (host == 'londrina.pr.gov.br' or host.endswith('.londrina.pr.gov.br')):
            raise ValueError(f"{x['id']}: link fora do domínio do Município.")
        if bool(x['texto_disponivel']) != bool(x.get('artigos')):
            raise ValueError(f"{x['id']}: texto_disponivel não confere com os artigos.")
        decretos.append(dict(id=x['id'], tipo=x['tipo'], numero=str(x['numero']), ano=int(x['ano']),
                             data=date.fromisoformat(x['data']) if x.get('data') else None,
                             ementa=x.get('ementa'), link=link, situacao=x['situacao'],
                             revogado_por=x.get('revogado_por'), texto_disponivel=bool(x['texto_disponivel']),
                             fonte_texto=x.get('fonte_texto')))
        ordens = set()
        for a in x.get('artigos', []):
            if int(a['ordem']) < 1 or a['ordem'] in ordens or not a['texto'].strip():
                raise ValueError(f"{x['id']}: artigo {a['ordem']} inválido ou repetido.")
            ordens.add(a['ordem'])
            artigos.append(dict(decreto=x['id'], ordem=int(a['ordem']), artigo=a['artigo'], texto=a['texto']))
    vinculos = []
    for v in dados.get('vinculos', []):
        if v['decreto_id'] not in ids:
            raise ValueError(f"Vínculo com decreto ausente: {v['decreto_id']}.")
        if v['tipo'] not in TIPOS_VINCULO or v['origem'] not in ORIGENS:
            raise ValueError(f"Vínculo {v['lei_id']} -> {v['decreto_id']}: tipo ou origem inválidos.")
        vinculos.append(dict(lei_id=str(v['lei_id']), decreto=v['decreto_id'], tipo=v['tipo'],
                             dispositivo=v.get('dispositivo'), origem=v['origem'], nota=v.get('nota')))
    return decretos, artigos, vinculos


def importar(db, dados, lote=500):
    decretos, artigos, vinculos = normalizar(dados)
    with db.atomic():
        db.create_tables(MODELOS_DECRETOS, safe=True)
        # Substitui por inteiro: o arquivo é a fonte; ordem inversa por causa das FKs.
        for modelo in reversed(MODELOS_DECRETOS):
            modelo.delete().execute()
        for modelo, linhas in ((Decreto, decretos), (ArtigoDecreto, artigos), (LeiDecreto, vinculos)):
            for parte in chunked(linhas, lote):
                modelo.insert_many(parte).execute()
    return dict(decretos=len(decretos), artigos=len(artigos), vinculos=len(vinculos))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('arquivo', nargs='?', default='decretos.json')
    ap.add_argument('--banco', help='Sobrescreve DB_NAME, por exemplo hackathon2026_teste.')
    ap.add_argument('--validar', action='store_true', help='Só confere o arquivo, sem conectar ao banco.')
    args = ap.parse_args()
    try:
        dados = json.loads(Path(args.arquivo).read_text(encoding='utf-8'))
        if args.validar:
            d, a, v = normalizar(dados)
            print(json.dumps(dict(decretos=len(d), artigos=len(a), vinculos=len(v))))
            return 0
        db = conectar(args.banco)
        with db.connection_context():
            print(f'Decretos carregados em {db.database}: {json.dumps(importar(db, dados))}')
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

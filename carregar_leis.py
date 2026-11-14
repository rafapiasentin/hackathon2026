"""Importação transacional em duas passadas; aceita JSON e ZIP sem extrair arquivos."""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from zipfile import ZipFile

from peewee import chunked

from banco import (Artigo, Carga, Lei, MODELOS, Relacao, RelacionamentoCml, conectar)


def ler_entrada(caminho, meta_path=None):
    caminho = Path(caminho)
    meta = None
    if caminho.suffix.lower() == '.zip':
        with ZipFile(caminho) as zip_file:
            candidatos = [n for n in zip_file.namelist() if Path(n).name == 'leis.json']
            if len(candidatos) != 1:
                raise ValueError('O ZIP precisa conter exatamente um leis.json.')
            raw = zip_file.read(candidatos[0])
            metas = [n for n in zip_file.namelist() if Path(n).name == 'leis.meta.json']
            if len(metas) > 1:
                raise ValueError('O ZIP contém metadados ambíguos.')
            if metas:
                meta = json.loads(zip_file.read(metas[0]).decode('utf-8-sig'))
    else:
        raw = caminho.read_bytes()
    externo = Path(meta_path) if meta_path else caminho.with_name('leis.meta.json')
    if meta_path or (meta is None and externo.is_file()):
        meta = json.loads(externo.read_text(encoding='utf-8-sig'))
    leis = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(leis, list) or not leis:
        raise ValueError('A entrada deve ser uma lista não vazia de leis.')
    return leis, hashlib.sha256(raw).hexdigest(), meta


def booleano(valor, campo):
    if type(valor) is not bool:
        raise ValueError(f'{campo} deve ser booleano, recebido {valor!r}.')
    return valor


def normalizar(leis):
    """Valida tudo antes de qualquer DROP. Não tenta adivinhar a redação vigente."""
    ids = [str(lei['id']) for lei in leis]
    if len(set(ids)) != len(ids):
        raise ValueError('IDs da Câmara duplicados.')
    conhecidos = set(ids)
    resultado = {k: [] for k in ('leis', 'artigos', 'relacoes', 'relacionamentos_cml', 'complementos')}
    artigos = [art for lei in leis for art in lei.get('artigos', [])]
    corrigido = bool(artigos) and all('revogado' in art and 'texto_riscado' in art for art in artigos)
    for lei in leis:
        origem = str(lei['id'])
        data_original = lei.get('data_lei_original') or None
        data_lei = lei.get('data_lei') or None
        if data_lei:
            try:
                data_lei = date.fromisoformat(data_lei)
            except (ValueError, TypeError):
                data_original = data_original or str(data_lei)
                data_lei = None
        hash_texto = lei.get('hash_texto') or None
        if hash_texto and not re.fullmatch(r'[0-9a-fA-F]{64}', hash_texto):
            raise ValueError(f'Lei {origem}: hash_texto inválido.')
        anexos = lei.get('anexos') or []
        if not isinstance(anexos, list):
            raise ValueError(f'Lei {origem}: anexos deve ser uma lista.')
        resultado['leis'].append(dict(
            id=origem, chave=str(lei['chave']), tipo=lei['tipo'], numero=str(lei['numero']),
            data_lei=data_lei, data_lei_fonte=lei.get('data_lei_fonte') or None,
            data_lei_original=data_original, ano=int(lei['ano']), titulo=lei['titulo'],
            ementa=lei.get('ementa') or None, ementa_fonte=lei.get('ementa_fonte') or None,
            publicado_site=lei.get('publicado_site') or None, link=lei['link'],
            situacao=lei['situacao'], revogacao_nota=lei.get('revogacao_nota') or None,
            complementa=None, texto_disponivel=booleano(lei.get('texto_disponivel', False), 'texto_disponivel'),
            hash_texto=hash_texto, anexos=anexos, fonte_relacoes=lei.get('fonte_relacoes') or None,
        ))
        # Todas as leis já existirão quando a referência própria for preenchida.
        destino = lei.get('complementa_id')
        if destino is not None:
            destino = str(destino)
            if destino not in conhecidos or destino == origem:
                raise ValueError(f'Lei {origem}: complementa_id inválido: {destino}.')
            resultado['complementos'].append((origem, destino))
        ordens = set()
        for art in lei.get('artigos', []):
            ordem = int(art['ordem'])
            if ordem < 1 or ordem in ordens:
                raise ValueError(f'Lei {origem}: ordem de artigo inválida ou duplicada: {ordem}.')
            ordens.add(ordem)
            texto = art['texto']
            if not isinstance(texto, str):
                raise ValueError(f'Lei {origem}, artigo {ordem}: texto deve ser string (pode ser vazio).')
            revogado = booleano(art.get('revogado', False), 'revogado')
            if revogado and texto:
                raise ValueError(f'Lei {origem}, artigo {ordem}: artigo revogado com texto vigente.')
            resultado['artigos'].append(dict(lei=origem, ordem=ordem, artigo=art['artigo'], texto=texto,
                                            texto_riscado=art.get('texto_riscado'), revogado=revogado))
        for rel in lei.get('relacoes', []):
            destino = str(rel['id']) if rel.get('id') is not None else None
            if destino == origem and corrigido:
                raise ValueError(f'Lei {origem}: autorrelação em relacoes; corrija a fonte.')
            if destino is not None and destino not in conhecidos:
                raise ValueError(f'Lei {origem}: relação com id ausente {destino}; use id null na fonte.')
            resultado['relacoes'].append(dict(lei_origem=origem, lei_destino=destino,
                                              chave_destino=rel.get('chave'), tipo=rel['tipo']))
        for rel in lei.get('relacionamentos', []):
            resultado['relacionamentos_cml'].append(dict(
                lei=origem, tipo=rel['tipo'], materia_id=str(rel['id']) if rel.get('id') is not None else None,
                descricao=rel.get('descricao'), data=rel.get('data') or None,
            ))
    totais = {k: len(resultado[k]) for k in ('leis', 'artigos', 'relacoes', 'relacionamentos_cml')}
    totais['artigos_revogados'] = sum(a['revogado'] for a in resultado['artigos'])
    return resultado, totais, corrigido


def validar_meta(meta, sha256, totais, obrigatorio=False):
    if meta is None:
        if obrigatorio:
            raise ValueError('A carga final exige leis.meta.json.')
        return
    if not isinstance(meta, dict):
        raise ValueError('Metadados devem ser um objeto JSON.')
    esperado = meta.get('sha256') or meta.get('sha256_leis_json')
    if isinstance(esperado, dict):
        esperado = esperado.get('leis.json')
    if not isinstance(esperado, str) or esperado.lower() != sha256:
        raise ValueError('SHA256 de leis.json ausente nos metadados ou diferente do arquivo.')
    # O contrato exato ainda será publicado; formatos desconhecidos falham explicitamente.
    fontes = [meta] + [meta[k] for k in ('totais', 'contagens', 'resumo') if isinstance(meta.get(k), dict)]
    aliases = {
        'leis': ('leis', 'total_leis'), 'artigos': ('artigos', 'total_artigos'),
        'relacoes': ('relacoes', 'total_relacoes'),
        'relacionamentos_cml': ('relacionamentos_cml', 'total_relacionamentos_cml'),
        'artigos_revogados': ('artigos_revogados', 'total_artigos_revogados'),
    }
    verificados = set()
    for campo, nomes in aliases.items():
        for fonte in fontes:
            for nome in nomes:
                if nome in fonte:
                    valor = fonte[nome]
                    if type(valor) is not int or valor != totais[campo]:
                        raise ValueError(f'Total divergente nos metadados: {campo}: {valor!r} != {totais[campo]}.')
                    verificados.add(campo)
    faltantes = {'leis', 'artigos', 'artigos_revogados'} - verificados
    if faltantes:
        raise ValueError('Metadados sem totais reconhecidos: ' + ', '.join(sorted(faltantes)))


def totais_banco():
    return dict(leis=Lei.select().count(), artigos=Artigo.select().count(),
                relacoes=Relacao.select().count(), relacionamentos_cml=RelacionamentoCml.select().count(),
                artigos_revogados=Artigo.select().where(Artigo.revogado == True).count())


def importar(db, dados, totais, sha256, meta, arquivo, corrigido, final=False, lote=500):
    if lote < 1 or lote > 1000:
        raise ValueError('O lote deve estar entre 1 e 1000.')
    if final and not corrigido:
        raise ValueError('Carga final rejeitada: artigos ainda sem os campos corrigidos.')
    validar_meta(meta, sha256, totais, obrigatorio=final)
    with db.atomic():
        # Serializa duas cargas simultâneas. DDL e dados voltam integralmente em caso de falha.
        db.execute_sql('SELECT pg_advisory_xact_lock(2026, 14308)')
        db.drop_tables(MODELOS, safe=True)
        db.create_tables(MODELOS)
        for linhas in chunked(dados['leis'], lote):
            Lei.insert_many(linhas).execute()
        if dados['complementos']:
            db.execute_sql('CREATE TEMP TABLE carga_complemento (origem text, destino text) ON COMMIT DROP')
            for linhas in chunked(dados['complementos'], lote):
                placeholders = ','.join(['(%s,%s)'] * len(linhas))
                db.execute_sql('INSERT INTO carga_complemento VALUES ' + placeholders,
                               [v for par in linhas for v in par])
            db.execute_sql('UPDATE lei SET complementa_id = c.destino FROM carga_complemento c WHERE lei.id = c.origem')
        for modelo, campo in ((Artigo, 'artigos'), (Relacao, 'relacoes'),
                               (RelacionamentoCml, 'relacionamentos_cml')):
            for linhas in chunked(dados[campo], lote):
                modelo.insert_many(linhas).execute()
        obtidos = totais_banco()
        if obtidos != totais:
            raise ValueError(f'Totais do banco divergentes: {obtidos} != {totais}')
        validar_meta(meta, sha256, obtidos, obrigatorio=final)
        Carga.create(arquivo=str(arquivo), sha256=sha256, formato_corrigido=corrigido,
                     final=final, metadados=meta, totais=obtidos)
    return obtidos


def criar_banco(db):
    import psycopg2
    from psycopg2 import sql
    parametros = dict(db.connect_params)
    admin = psycopg2.connect(dbname='postgres', **parametros)
    try:
        admin.autocommit = True
        with admin.cursor() as cursor:
            cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db.database,))
            if cursor.fetchone() is None:
                cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db.database)))
    finally:
        admin.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivo', nargs='?', default='leis.json')
    parser.add_argument('--meta', help='Metadados externos (substituem os do ZIP).')
    parser.add_argument('--banco', help='Sobrescreve DB_NAME, por exemplo hackathon2026_teste.')
    parser.add_argument('--criar-banco', action='store_true')
    parser.add_argument('--criar-tabelas', action='store_true', help='Cria tabelas vazias sem apagar as existentes.')
    parser.add_argument('--validar', action='store_true', help='Valida os arquivos sem conectar ao banco.')
    parser.add_argument('--recriar', action='store_true', help='Apaga e recria somente as tabelas deste projeto.')
    parser.add_argument('--permitir-legado', action='store_true', help='Apenas para testes, bloqueia o chatbot.')
    parser.add_argument('--final', action='store_true', help='Exige artigos corrigidos, hash e totais dos metadados.')
    parser.add_argument('--lote', type=int, default=500)
    args = parser.parse_args()
    try:
        if args.criar_tabelas:
            if args.recriar or args.final or args.validar:
                raise ValueError('--criar-tabelas não pode ser combinado com carga/validação.')
            db = conectar(args.banco)
            if args.criar_banco:
                criar_banco(db)
            with db.connection_context():
                db.create_tables(MODELOS, safe=True)
            print(f'Tabelas criadas em {db.database}. Nenhum dado carregado.')
            return 0
        leis, sha256, meta = ler_entrada(args.arquivo, args.meta)
        dados, totais, corrigido = normalizar(leis)
        validar_meta(meta, sha256, totais, obrigatorio=args.final)
        if args.final and not corrigido:
            raise ValueError('Arquivo legado: a carga final exige os campos novos dos artigos.')
        print(json.dumps(dict(sha256=sha256, formato_corrigido=corrigido, totais=totais), ensure_ascii=False))
        if args.validar:
            return 0
        if not args.recriar:
            raise ValueError('Para carregar, use --recriar: substitui todas as tabelas deste projeto.')
        if not corrigido and not args.permitir_legado:
            raise ValueError('Dados antigos: use --permitir-legado somente no banco de teste.')
        db = conectar(args.banco)
        if args.criar_banco:
            criar_banco(db)
        with db.connection_context():
            resultado = importar(db, dados, totais, sha256, meta, args.arquivo, corrigido,
                                  final=args.final, lote=args.lote)
        print(f'Carga concluída em {db.database}: {json.dumps(resultado)}')
        if not args.final:
            print('Carga de teste; chatbot bloqueado até a carga final dos dados corrigidos.')
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

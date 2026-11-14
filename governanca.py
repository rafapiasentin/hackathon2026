"""Ingestão auditável: originais, versões, pendências e publicação incremental."""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from peewee import DatabaseError, chunked

from adaptadores import ErroEntrada, carregar_formato, padronizar
from banco import (Artigo, DocumentoOriginal, Lei, LoteIngestao, MODELOS,
                   MODELOS_GOVERNANCA, PendenciaIngestao, PublicacaoLei, Relacao,
                   RelacionamentoCml, VersaoRegistro, agora_utc, conectar)
from carregar_leis import normalizar, validar_meta

CONTRATO_PATH = Path(__file__).with_name('contrato_governanca.json')
VERSAO_ADAPTADORES = '1.1.0'


def contrato_atual():
    return json.loads(CONTRATO_PATH.read_text(encoding='utf-8'))


def json_canonico(valor):
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      default=lambda v: v.isoformat() if isinstance(v, (date, datetime)) else str(v))


def hash_registro(registro):
    conteudo = {k: v for k, v in padronizar(registro).items() if k != 'revisao_vigencia'}
    return hashlib.sha256(json_canonico(conteudo).encode('utf-8')).hexdigest()


def url_oficial(valor, contrato):
    if not isinstance(valor, str):
        return False
    try:
        url = urlsplit(valor)
        return (url.scheme == 'https' and url.hostname in contrato['dominios_oficiais']
                and url.port in (None, 443) and not url.username and not url.password
                and not {'keysoft', 'token', 'key', 'password', 'api_key'}
                .intersection(k.lower() for k in parse_qs(url.query)))
    except ValueError:
        return False


def problema(codigo, campo, mensagem, valor=None, severidade='erro'):
    return dict(codigo=codigo, campo=campo, mensagem=mensagem, valor=valor, severidade=severidade)


def validar_registro(registro, conhecidos, contrato):
    """Validação técnica não equivale a aprovação jurídica."""
    erros = []
    extracao = registro.get('extracao')
    if isinstance(extracao, dict):
        for conflito in extracao.get('conflitos', []):
            erros.append(problema('conflito_extracao', 'extracao', str(conflito)))
        if extracao.get('exige_revisao_extracao') and not (
            isinstance(registro.get('revisao_vigencia'), dict)
            and registro['revisao_vigencia'].get('extracao_conferida') is True
        ):
            erros.append(problema('ocr_requer_conferencia', 'extracao',
                                  'Texto extraído por OCR; a revisão deve conferir a extração visualmente.'))
    for campo in contrato['campos_obrigatorios']:
        if campo not in registro or registro[campo] is None:
            erros.append(problema('campo_obrigatorio', campo, 'Campo obrigatório ausente.'))
    for campo in ('id', 'chave', 'numero', 'titulo', 'link', 'tipo', 'situacao'):
        if campo in registro and (not isinstance(registro[campo], str) or not registro[campo].strip()):
            erros.append(problema('tipo_invalido', campo, 'Deve ser texto não vazio.', registro[campo]))
    for campo, permitidos in (('tipo', contrato['tipos']), ('situacao', contrato['situacoes'])):
        if campo in registro and registro[campo] not in permitidos:
            erros.append(problema('valor_nao_permitido', campo, 'Valor fora do contrato.', registro[campo]))
    if not url_oficial(registro.get('link'), contrato):
        erros.append(problema('fonte_nao_oficial', 'link', 'URL deve ser HTTPS de domínio oficial sem credenciais.'))
    elif str(registro.get('id', '')).isdigit() and 'cml.pr.gov.br' in urlsplit(registro['link']).hostname:
        if urlsplit(registro['link']).path.rstrip('/').split('/')[-1] != str(registro['id']):
            erros.append(problema('identidade_divergente', 'link', 'ID da Câmara difere do ID na URL.'))
    if 'id' in registro and not re.fullmatch(r'[0-9]+', str(registro['id'])):
        erros.append(problema('identidade_invalida', 'id', 'Este contrato exige o ID numérico da Câmara.'))
    ano = registro.get('ano')
    if type(ano) is not int or not 1800 <= ano <= 9999:
        erros.append(problema('ano_invalido', 'ano', 'Ano deve ser inteiro entre 1800 e 9999.', ano))
    if registro.get('ementa') is not None and not isinstance(registro['ementa'], str):
        erros.append(problema('tipo_invalido', 'ementa', 'Ementa deve ser texto ou nulo.'))
    for campo in ('artigos', 'relacoes', 'relacionamentos', 'anexos'):
        if campo in registro and not isinstance(registro[campo], list):
            erros.append(problema('tipo_invalido', campo, 'Deve ser uma lista.'))
    data_lei = registro.get('data_lei')
    if data_lei:
        try:
            data = date.fromisoformat(data_lei)
            if data.year != ano:
                erros.append(problema('ano_divergente', 'data_lei', 'Data do ato diverge de ano.', data_lei))
        except (ValueError, TypeError):
            erros.append(problema('data_invalida', 'data_lei', 'Data inválida; não será corrigida por adivinhação.', data_lei))
    elif registro.get('data_lei_original'):
        erros.append(problema('data_original_invalida', 'data_lei_original', 'Data impossível na fonte exige revisão.',
                              registro['data_lei_original']))
    else:
        erros.append(problema('data_ausente', 'data_lei', 'Data do ato ausente; ano preservado.', severidade='aviso'))
    if isinstance(registro.get('relacoes'), list):
        for i, rel in enumerate(registro['relacoes']):
            if not isinstance(rel, dict) or rel.get('tipo') not in contrato['tipos_relacao']:
                erros.append(problema('relacao_invalida', f'relacoes.{i}', 'Tipo de relação fora do contrato.'))
    if isinstance(registro.get('artigos'), list):
        for i, art in enumerate(registro['artigos']):
            if not isinstance(art, dict):
                erros.append(problema('artigo_invalido', f'artigos.{i}', 'Artigo deve ser um objeto.'))
                continue
            if any(c not in art for c in ('ordem', 'artigo', 'texto', 'texto_riscado', 'revogado')):
                erros.append(problema('artigo_legado', f'artigos.{i}', 'Artigo sem contrato de redação vigente.'))
            if type(art.get('ordem')) is not int or art.get('ordem', 0) < 1:
                erros.append(problema('ordem_invalida', f'artigos.{i}.ordem', 'Ordem deve ser inteiro positivo.'))
            if not isinstance(art.get('artigo'), str) or not art['artigo'].strip():
                erros.append(problema('rotulo_invalido', f'artigos.{i}.artigo', 'Rótulo de artigo deve ser texto.'))
            if art.get('texto_riscado') is not None and not isinstance(art['texto_riscado'], str):
                erros.append(problema('tipo_invalido', f'artigos.{i}.texto_riscado', 'Texto histórico deve ser texto ou nulo.'))
            if art.get('revogado') is False and isinstance(art.get('texto'), str) and not art['texto'].strip():
                erros.append(problema('texto_vigente_vazio', f'artigos.{i}.texto', 'Artigo não revogado sem redação vigente.'))
    if registro.get('texto_disponivel') is True and not registro.get('artigos'):
        erros.append(problema('artigos_ausentes', 'artigos', 'Texto declarado disponível sem artigos extraídos.'))
    dados = None
    if not any(e['severidade'] == 'erro' for e in erros):
        try:
            dados, _, _ = normalizar([registro], ids_conhecidos=conhecidos)
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            erros.append(problema('consistencia', 'registro', str(exc)))
    return dados, erros


def verificar_revisao(registro, contrato):
    """Aceita revisão declarada só de responsáveis configurados e vinculada ao conteúdo."""
    revisao = registro.get('revisao_vigencia')
    if not isinstance(revisao, dict):
        return False
    revisores = {r.strip() for r in os.getenv('GOVERNANCA_REVISORES', '').split(',') if r.strip()}
    campos = ('responsavel', 'verificado_em', 'fonte', 'trecho', 'situacao', 'hash_registro')
    if any(not isinstance(revisao.get(k), str) or not revisao[k].strip() for k in campos):
        return False
    if revisao['responsavel'] not in revisores or revisao['situacao'] != registro.get('situacao'):
        return False
    if revisao['hash_registro'] != hash_registro(registro) or not url_oficial(revisao['fonte'], contrato):
        return False
    if revisao['fonte'].split('#')[0] != registro.get('link', '').split('#')[0]:
        return False
    try:
        momento = datetime.fromisoformat(revisao['verificado_em'].replace('Z', '+00:00'))
        if momento.tzinfo is None or momento > datetime.now(timezone.utc):
            return False
    except ValueError:
        return False
    textos = [registro.get('titulo') or '', registro.get('ementa') or '', registro.get('revogacao_nota') or '']
    textos.extend(a.get('texto', '') + '\n' + (a.get('texto_riscado') or '') for a in registro.get('artigos', []))
    normal = lambda s: ' '.join(s.split())
    return normal(revisao['trecho']) in normal('\n'.join(textos))


def _publicar(db, preparados):
    """Substitui apenas os registros aprovados, sem apagar leis ausentes do lote."""
    ids = list(preparados)
    if not ids:
        return
    # Mesma trava do importador legado para impedir concorrência entre os caminhos.
    db.execute_sql('SELECT pg_advisory_xact_lock(2026, 14308)')
    for grupo in chunked(ids, 500):
        linhas = [preparados[i]['leis'][0] for i in grupo]
        campos = [c for c in linhas[0] if c not in ('id', 'complementa')]
        Lei.insert_many(linhas).on_conflict(conflict_target=[Lei.id], preserve=campos).execute()
    for grupo in chunked(ids, 500):
        Artigo.delete().where(Artigo.lei.in_(grupo)).execute()
        Relacao.delete().where(Relacao.lei_origem.in_(grupo)).execute()
        RelacionamentoCml.delete().where(RelacionamentoCml.lei.in_(grupo)).execute()
    for origem, dados in preparados.items():
        destino = dados['complementos'][0][1] if dados['complementos'] else None
        Lei.update(complementa=destino).where(Lei.id == origem).execute()
    for modelo, campo in ((Artigo, 'artigos'), (Relacao, 'relacoes'), (RelacionamentoCml, 'relacionamentos_cml')):
        linhas = (linha for dados in preparados.values() for linha in dados[campo])
        for grupo in chunked(linhas, 500):
            modelo.insert_many(grupo).execute()
    esperados = dict(leis=len(ids), artigos=sum(len(d['artigos']) for d in preparados.values()),
                     relacoes=sum(len(d['relacoes']) for d in preparados.values()),
                     artigos_revogados=sum(a['revogado'] for d in preparados.values() for a in d['artigos']))
    obtidos = dict(leis=0, artigos=0, relacoes=0, artigos_revogados=0)
    for grupo in chunked(ids, 500):
        obtidos['leis'] += Lei.select().where(Lei.id.in_(grupo)).count()
        obtidos['artigos'] += Artigo.select().where(Artigo.lei.in_(grupo)).count()
        obtidos['relacoes'] += Relacao.select().where(Relacao.lei_origem.in_(grupo)).count()
        obtidos['artigos_revogados'] += Artigo.select().where(Artigo.lei.in_(grupo), Artigo.revogado == True).count()
    if obtidos != esperados:
        raise DatabaseError('Totais publicados divergentes; publicação deve ser revertida.')


def receber(db, caminho, fonte, meta_path=None):
    """Publica conformes e registra exceções. Falha de integridade bloqueia o lote inteiro."""
    contrato = contrato_atual()
    raw = Path(caminho).read_bytes()
    sha_original = hashlib.sha256(raw).hexdigest()
    db.create_tables(MODELOS + MODELOS_GOVERNANCA, safe=True)
    registros, conteudo, meta, erro_lote = [], raw, None, None
    try:
        if not url_oficial(fonte, contrato):
            raise ErroEntrada('Fonte de recebimento deve ser uma URL oficial HTTPS sem credenciais.')
        proprio = Path(caminho).with_suffix('.meta.json')
        externo = Path(meta_path) if meta_path else (proprio if proprio.is_file() else Path(caminho).with_name('leis.meta.json'))
        if meta_path or externo.is_file():
            meta = json.loads(externo.read_text(encoding='utf-8-sig'))
        contexto = meta.get('registro') if isinstance(meta, dict) else None
        if contexto is not None and not isinstance(contexto, dict):
            raise ErroEntrada('O campo registro dos metadados deve ser um objeto.')
        registros, conteudo, meta_interno = carregar_formato(raw, caminho, contrato['limite_bytes'], contexto=contexto)
        if meta_interno is not None and not meta_path:
            meta = meta_interno
        elif meta is None:
            meta = meta_interno
    except (ValueError, OSError) as exc:
        erro_lote = str(exc)
    identidade = hashlib.sha256(json_canonico(dict(
        sha256=sha_original, fonte=fonte, meta=meta, contrato=contrato,
        adaptadores=VERSAO_ADAPTADORES, formato=Path(caminho).suffix.lower(), erro=erro_lote,
        revisores=os.getenv('GOVERNANCA_REVISORES', ''),
    )).encode('utf-8')).hexdigest()
    with db.atomic():
        db.execute_sql('SELECT pg_advisory_xact_lock(2026, 14308)')
        existente = LoteIngestao.get_or_none(LoteIngestao.identidade == identidade)
        if existente:
            return dict(lote=existente.id, estado=existente.estado, repetido=True, **existente.relatorio)
        DocumentoOriginal.insert(sha256=sha_original, conteudo=raw).on_conflict_ignore().execute()
        # Fonte inválida nunca é persistida com query string ou credenciais.
        fonte_segura = fonte if url_oficial(fonte, contrato) else 'fonte_invalida'
        lote = LoteIngestao.create(identidade=identidade, documento=sha_original,
                                  nome_arquivo=Path(caminho).name, fonte=fonte_segura,
                                  formato=Path(caminho).suffix.lower().lstrip('.'),
                                  contrato=contrato['versao'], metadados=meta)
        if erro_lote:
            PendenciaIngestao.create(lote=lote, **problema('entrada_invalida', 'arquivo', erro_lote))
            lote.estado = 'quarentena'
            lote.relatorio = dict(recebidos=0, publicados=0, pendentes=0, erros_lote=1)
            lote.save()
            return dict(lote=lote.id, estado=lote.estado, repetido=False, **lote.relatorio)
        padronizados = []
        falhas = {}
        for posicao, original in enumerate(registros):
            try:
                padronizados.append(padronizar(original))
            except (ValueError, TypeError) as exc:
                padronizados.append({})
                falhas[posicao] = [problema('padronizacao', 'registro', str(exc))]
        ids = Counter(r.get('id') for r in padronizados if isinstance(r.get('id'), str))
        existentes = {l.id for l in Lei.select(Lei.id)}
        conhecidos = set(ids) | existentes
        preparados = {}
        por_posicao = {}
        for posicao, registro in enumerate(padronizados):
            dados, problemas = validar_registro(registro, conhecidos, contrato)
            problemas.extend(falhas.get(posicao, []))
            lei_id = registro.get('id') if isinstance(registro.get('id'), str) else None
            if lei_id and ids[lei_id] > 1:
                problemas.append(problema('id_duplicado', 'id', 'ID duplicado dentro do lote.', lei_id))
            verificada = dados is not None and verificar_revisao(registro, contrato)
            if not verificada:
                problemas.append(problema('vigencia_nao_verificada', 'revisao_vigencia',
                                          'Falta revisão válida vinculada a esta versão e responsável configurado.'))
            por_posicao[posicao] = dict(lei_id=lei_id, dados=dados, problemas=problemas,
                                        verificada=verificada)
            if dados and not any(p['severidade'] == 'erro' for p in problemas):
                preparados[lei_id] = dados
        # Integridade é do arquivo inteiro, não só do subconjunto que vai ser publicado.
        totais = dict(leis=len(registros), artigos=sum(len(r.get('artigos', [])) for r in padronizados
                                                     if isinstance(r.get('artigos'), list)),
                      relacoes=sum(len(r.get('relacoes', [])) for r in padronizados
                                   if isinstance(r.get('relacoes'), list)),
                      artigos_revogados=sum(a.get('revogado') is True for r in padronizados
                                            if isinstance(r.get('artigos'), list)
                                            for a in r['artigos'] if isinstance(a, dict)),
                      relacionamentos_cml=sum(len(r.get('relacionamentos', [])) for r in padronizados
                                              if isinstance(r.get('relacionamentos'), list)))
        try:
            validar_meta(meta, hashlib.sha256(conteudo).hexdigest(), totais, obrigatorio=True)
        except ValueError as exc:
            PendenciaIngestao.create(lote=lote, **problema('integridade_lote', 'metadados', str(exc)))
            for item in por_posicao.values():
                item['problemas'].append(problema('integridade_lote', 'metadados', 'Integridade do lote não comprovada.'))
            preparados.clear()
        # Dependências de um registro retido também ficam retidas; propaga até estabilizar.
        mudou = True
        while mudou:
            mudou = False
            for item in por_posicao.values():
                lei_id = item['lei_id']
                if lei_id not in preparados:
                    continue
                dados = item['dados']
                destinos = {r['lei_destino'] for r in dados['relacoes'] if r['lei_destino']}
                destinos.update(d for _, d in dados['complementos'])
                bloqueados = destinos.intersection(ids).difference(preparados)
                if bloqueados:
                    item['problemas'].append(problema('dependencia_pendente', 'relacoes',
                                                      'Dependência do lote está retida.', sorted(bloqueados)))
                    preparados.pop(lei_id)
                    mudou = True
        try:
            with db.atomic():
                _publicar(db, preparados)
        except DatabaseError:
            # O savepoint restaura a base; a falha fica auditada no lote em vez de sumir.
            PendenciaIngestao.create(lote=lote, **problema('publicacao_falhou', 'banco',
                                                         'Falha na persistência; versão publicada foi preservada.'))
            for item in por_posicao.values():
                item['problemas'].append(problema('publicacao_falhou', 'banco', 'Publicação revertida por falha no banco.'))
            preparados.clear()
        for posicao, item in por_posicao.items():
            publicado = item['lei_id'] in preparados
            estado = 'publicado' if publicado else 'pendente'
            versao = VersaoRegistro.create(lote=lote, posicao=posicao, lei_id=item['lei_id'],
                original=registros[posicao], normalizado=json.loads(json_canonico(item['dados'])) if item['dados'] else None,
                estado=estado, vigencia_verificada=item['verificada'])
            for p in item['problemas']:
                PendenciaIngestao.create(lote=lote, registro=versao, **p)
            if item['lei_id']:
                PublicacaoLei.insert(lei_id=item['lei_id'], versao=versao,
                    estado=estado, vigencia_verificada=bool(publicado and item['verificada']), atualizado_em=agora_utc())\
                    .on_conflict(conflict_target=[PublicacaoLei.lei_id], preserve=[
                        PublicacaoLei.versao, PublicacaoLei.estado, PublicacaoLei.vigencia_verificada,
                        PublicacaoLei.atualizado_em]).execute()
        publicados = len(preparados)
        lote.estado = 'publicado' if publicados == len(registros) else 'parcial' if publicados else 'quarentena'
        lote.relatorio = dict(recebidos=len(registros), publicados=publicados,
                              pendentes=len(registros) - publicados, totais_entrada=totais,
                              sha256_original=sha_original, contrato=contrato['versao'])
        lote.save()
        return dict(lote=lote.id, estado=lote.estado, repetido=False, **lote.relatorio)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivo', nargs='?')
    parser.add_argument('--fonte', default='https://www.cml.pr.gov.br/dadosabertos')
    parser.add_argument('--meta')
    parser.add_argument('--banco')
    parser.add_argument('--relatorio', type=int, metavar='LOTE', help='Consulta um lote e suas pendências.')
    args = parser.parse_args()
    db = conectar(args.banco)
    try:
        with db.connection_context():
            if args.relatorio:
                lote = LoteIngestao.get_by_id(args.relatorio)
                resultado = dict(lote=lote.id, estado=lote.estado, resumo=lote.relatorio,
                    pendencias=list(PendenciaIngestao.select(PendenciaIngestao.codigo,
                        PendenciaIngestao.campo, PendenciaIngestao.mensagem,
                        PendenciaIngestao.registro).where(PendenciaIngestao.lote == lote).dicts()))
            else:
                if not args.arquivo:
                    parser.error('Informe um arquivo ou --relatorio LOTE.')
                resultado = receber(db, args.arquivo, args.fonte, args.meta)
        print(json.dumps(resultado, ensure_ascii=False))
        return 0 if resultado['estado'] == 'publicado' else 2
    except (ValueError, OSError) as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

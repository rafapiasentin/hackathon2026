"""Adaptadores explícitos. Formatos não estruturados vão para pendência."""
import csv
import io
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException


class ErroEntrada(ValueError):
    pass


def carregar_formato(raw, nome, limite=209715200, contexto=None):
    """Retorna registros, bytes efetivos do JSON e meta interno, sem extrair ZIP."""
    if len(raw) > limite:
        raise ErroEntrada('Arquivo excede o limite de tamanho do contrato.')
    formato = Path(nome).suffix.lower().lstrip('.')
    meta = None
    if formato in {'html', 'htm', 'pdf'}:
        from extracao_documentos import extrair_html, extrair_pdf
        try:
            registros = extrair_pdf(raw, contexto) if formato == 'pdf' else extrair_html(raw, contexto)
            return registros, raw, None
        except ValueError as exc:
            raise ErroEntrada(str(exc)) from exc
    if formato == 'zip':
        try:
            with ZipFile(io.BytesIO(raw)) as arquivo:
                arquivos = [i for i in arquivo.infolist() if not i.is_dir()]
                if sum(i.file_size for i in arquivos) > limite:
                    raise ErroEntrada('Conteúdo descompactado excede o limite do contrato.')
                jsons = [i for i in arquivos if Path(i.filename).name == 'leis.json']
                metas = [i for i in arquivos if Path(i.filename).name == 'leis.meta.json']
                if len(jsons) != 1 or len(metas) > 1:
                    raise ErroEntrada('ZIP exige exatamente um leis.json e no máximo um leis.meta.json.')
                if metas:
                    meta = json.loads(arquivo.read(metas[0]).decode('utf-8-sig'))
                registros, conteudo, _ = carregar_formato(arquivo.read(jsons[0]), 'leis.json', limite)
                return registros, conteudo, meta
        except (BadZipFile, RuntimeError) as exc:
            raise ErroEntrada('ZIP inválido ou criptografado.') from exc
    if formato not in {'json', 'jsonl', 'csv', 'xml'}:
        raise ErroEntrada(f'Formato {formato or "desconhecido"} sem adaptador estruturado; requer extração revisada.')
    try:
        texto = raw.decode('utf-8-sig')
        if formato == 'json':
            registros = json.loads(texto)
            if isinstance(registros, dict):
                if 'leis' in registros:
                    registros = registros['leis']
                elif 'id' in registros or 'titulo' in registros:
                    registros = [registros]
        elif formato == 'jsonl':
            registros = [json.loads(linha) for linha in texto.splitlines() if linha.strip()]
        elif formato == 'csv':
            leitor = csv.DictReader(io.StringIO(texto), delimiter=';' if ';' in texto.splitlines()[0] else ',')
            registros = list(leitor)
        else:
            raiz = ElementTree.fromstring(texto)
            if raiz.tag != 'leis':
                raise ErroEntrada('XML deve usar raiz <leis> e registros <lei>.')
            registros = []
            for no in raiz:
                if no.tag != 'lei' or len({c.tag for c in no}) != len(no):
                    raise ErroEntrada('XML com registro inválido ou campo repetido.')
                registros.append({campo.tag: campo.text or '' for campo in no})
        if not isinstance(registros, list) or not registros:
            raise ErroEntrada('A entrada deve conter uma lista não vazia de registros.')
        return registros, raw, meta
    except (ValueError, UnicodeError, IndexError, ElementTree.ParseError, DefusedXmlException) as exc:
        if isinstance(exc, ErroEntrada):
            raise
        raise ErroEntrada('Não foi possível interpretar o arquivo no formato declarado.') from exc


def padronizar(registro):
    """Converte somente representações inequívocas, mantendo o original no histórico."""
    if not isinstance(registro, dict):
        raise ErroEntrada('Registro deve ser um objeto com campos nomeados.')
    resultado = dict(registro)
    # Contrato real conferido na API: data é publicação no site, não data do ato.
    if {'titulo', 'ementa', 'data', 'autoria', 'link'} <= resultado.keys() and 'artigos' not in resultado:
        from coleta_leis import parse_titulo
        link = urlsplit(str(resultado.get('link', '')))
        materia = link.path.rstrip('/').split('/')[-1]
        if link.hostname in {'www.cml.pr.gov.br', 'www1.cml.pr.gov.br', 'cml.pr.gov.br'} and materia.isdigit():
            resultado.setdefault('id', materia)
        if isinstance(resultado.get('titulo'), str):
            numero, data_lei, ano, complementar = parse_titulo(resultado['titulo'])
            if numero:
                resultado.setdefault('numero', numero)
                resultado.setdefault('chave', ('LC-' if complementar else '') + numero)
            if data_lei:
                resultado.setdefault('data_lei', data_lei)
            if ano:
                resultado.setdefault('ano', ano)
            if re.match(r'^\s*LEI\b', resultado['titulo'], re.I):
                resultado.setdefault('tipo', 'Lei Complementar' if complementar else 'Lei')
        resultado.setdefault('publicado_site', resultado['data'])
    aliases = {'id_cml': 'id', 'numero_lei': 'numero', 'data_do_ato': 'data_lei'}
    for origem, destino in aliases.items():
        if origem in resultado:
            if destino in resultado and str(resultado[destino]) != str(resultado[origem]):
                raise ErroEntrada(f'Campos {origem} e {destino} divergentes.')
            resultado[destino] = resultado.pop(origem)
    for campo in ('artigos', 'relacoes', 'relacionamentos', 'anexos', 'revisao_vigencia'):
        valor = resultado.get(campo)
        if isinstance(valor, str) and valor.strip():
            try:
                resultado[campo] = json.loads(valor)
            except ValueError as exc:
                raise ErroEntrada(f'{campo} deve conter JSON válido dentro de CSV/XML.') from exc
    valor = resultado.get('texto_disponivel')
    if isinstance(valor, str) and valor.strip().lower() in {'true', 'false'}:
        resultado['texto_disponivel'] = valor.strip().lower() == 'true'
    for campo in ('id', 'chave', 'numero'):
        valor = resultado.get(campo)
        if isinstance(valor, (str, int)) and not isinstance(valor, bool):
            resultado[campo] = str(valor).strip()
    valor = resultado.get('ano')
    if isinstance(valor, str) and valor.strip().isdigit():
        resultado['ano'] = int(valor.strip())
    if resultado.get('ementa') == '':
        resultado['ementa'] = None
    return resultado

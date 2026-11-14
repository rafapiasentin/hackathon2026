"""Confere disponibilidade e estrutura da fonte, sem expor a chave da CML."""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

from dotenv import load_dotenv

PAGINA = 'https://www.cml.pr.gov.br/dadosabertos'
API = 'https://www.cml.pr.gov.br/jsonweb/web-aplicativo.php'


def consultar(url, pasta, nome, params=None, session=None):
    """Nunca registra a URL preparada, parâmetros de autenticação ou texto da exceção."""
    session = session or requests.Session()
    resultado = dict(url=url, consultado_em=datetime.now(timezone.utc).isoformat())
    try:
        resposta = session.get(url, params=params, timeout=25, allow_redirects=False,
                              headers={'User-Agent': 'Mozilla/5.0 (Hackathon-Londrina)'})
        resultado.update(status_http=resposta.status_code, content_type=resposta.headers.get('Content-Type', ''),
                         sha256=hashlib.sha256(resposta.content).hexdigest())
        (pasta / f'{nome}{".json" if params else ".html"}').write_bytes(resposta.content)
        if resposta.status_code == 200:
            if params:
                dados = resposta.json()
                if not isinstance(dados, list):
                    raise ValueError('Contrato inesperado')
                resultado['quantidade'] = len(dados)
                resultado['campos'] = sorted({k for d in dados if isinstance(d, dict) for k in d})
                resultado['contrato_compativel'] = (all(isinstance(d, dict) for d in dados)
                    and (params.get('call') != 'legislacoes' or all(
                        {'titulo', 'ementa', 'data', 'autoria', 'link'} <= d.keys() for d in dados)))
                if params.get('call') == 'legislacoes_tipos':
                    resultado['contratos'] = [d['contract'] for d in dados if isinstance(d, dict) and 'contract' in d]
                    resultado['contrato_compativel'] = len(resultado['contratos']) == len(dados)
            else:
                from bs4 import BeautifulSoup
                texto = BeautifulSoup(resposta.content, 'html.parser').get_text(' ', strip=True).lower()
                resultado['contrato_compativel'] = all(t in texto for t in (
                    'dados abertos', 'web-aplicativo.php', 'legislacoes_tipos', 'legislacoes'))
        else:
            resultado['contrato_compativel'] = False
    except (requests.RequestException, ValueError) as exc:
        resultado.update(contrato_compativel=False, erro=type(exc).__name__)
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', default='dados_recebidos/conferencia_fonte')
    parser.add_argument('--api', action='store_true', help='Também confere tipos e uma página de leis usando CML_TOKEN.')
    args = parser.parse_args()
    load_dotenv(Path(__file__).with_name('.env'))
    pasta = Path(args.saida)
    pasta.mkdir(parents=True, exist_ok=True)
    resultados = [consultar(PAGINA, pasta, 'dadosabertos')]
    if args.api:
        token = os.getenv('CML_TOKEN')
        if not token:
            resultados.append(dict(url=API, contrato_compativel=False, erro='CML_TOKEN_ausente'))
        else:
            tipos = consultar(API, pasta, 'tipos', dict(keysoft=token, call='legislacoes_tipos'))
            resultados.append(tipos)
            if 'Leis' in tipos.get('contratos', []):
                resultados.append(consultar(API, pasta, 'leis_pagina_1',
                    dict(keysoft=token, call='legislacoes', tipo='Leis', pagina=1)))
            else:
                resultados.append(dict(url=API, contrato_compativel=False, erro='contract_Leis_nao_confirmado'))
    (pasta / 'resultado.json').write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(resultados, ensure_ascii=False))
    return 0 if all(r['contrato_compativel'] for r in resultados) else 2


if __name__ == '__main__':
    raise SystemExit(main())

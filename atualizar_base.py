"""Consome automaticamente arquivos concluídos de uma pasta de entrada."""
import argparse
import json
import time
from pathlib import Path

from banco import conectar
from governanca import receber


def processar_pasta(db, pasta, fonte, estaveis=None):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    resultados = []
    arquivos = [p for p in sorted(pasta.iterdir()) if p.is_file()
                and not p.name.endswith(('.meta.json', '.part', '.tmp'))
                and not p.name.startswith('.')]
    for path in arquivos:
        assinatura = (path.stat().st_size, path.stat().st_mtime_ns)
        if estaveis is not None:
            anterior = estaveis.get(str(path))
            estaveis[str(path)] = assinatura
            if anterior != assinatura:
                continue
        meta = path.with_suffix('.meta.json')
        try:
            resultados.append(receber(db, path, fonte, meta if meta.is_file() else None))
        except (ValueError, OSError) as exc:
            resultados.append(dict(arquivo=path.name, estado='falha', erro=type(exc).__name__))
    return resultados


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pasta', default='dados_entrada')
    parser.add_argument('--fonte', default='https://www.cml.pr.gov.br/dadosabertos')
    parser.add_argument('--banco')
    parser.add_argument('--uma-vez', action='store_true', help='Para agendadores externos; arquivos devem estar completos.')
    parser.add_argument('--intervalo', type=int, default=60)
    args = parser.parse_args()
    if args.intervalo < 1:
        parser.error('--intervalo deve ser positivo.')
    db = conectar(args.banco)
    estaveis = {}
    try:
        while True:
            with db.connection_context():
                resultados = processar_pasta(db, args.pasta, args.fonte,
                                             None if args.uma_vez else estaveis)
            print(json.dumps(resultados, ensure_ascii=False), flush=True)
            if args.uma_vez:
                return 2 if any(r['estado'] in ('quarentena', 'parcial', 'falha') for r in resultados) else 0
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    raise SystemExit(main())

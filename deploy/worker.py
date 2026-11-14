"""Execução hospedada dos comandos completos de coleta e governança."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


def executar(acao):
    from banco import conectar
    from carregar_leis import ler_entrada, normalizar, validar_meta
    from governanca import receber
    from preparar_ocr import main as preparar_ocr
    pasta = RAIZ / 'dados_recebidos' / 'pipeline'
    pasta.mkdir(parents=True, exist_ok=True)
    preparar_ocr()
    if acao == 'coletar':
        saida = pasta / 'leis.json'
        subprocess.run([sys.executable, str(RAIZ / 'coleta_leis.py'), '--texto',
                        '--paralelo', '3', '--saida', str(saida)], cwd=RAIZ, check=True)
        leis, sha, meta = ler_entrada(saida)
        _, totais, corrigido = normalizar(leis)
        validar_meta(meta, sha, totais, obrigatorio=True)
        if not corrigido:
            raise ValueError('Coleta sem o formato corrigido; publicação cancelada.')
        with ZipFile(pasta / 'coleta.zip', 'w', ZIP_DEFLATED) as z:
            z.write(saida, 'leis.json')
            z.write(saida.with_suffix('.meta.json'), 'leis.meta.json')
        subprocess.run([sys.executable, str(RAIZ / 'relatorio_problemas.py')], cwd=pasta, check=True)
        db = conectar()
        with db.connection_context():
            resultado = receber(db, saida, 'https://www.cml.pr.gov.br/dadosabertos')
    else:
        # Valida o snapshot real e os mesmos adaptadores sem alterar o acervo público.
        leis, sha, meta = ler_entrada(RAIZ / 'leis.zip')
        _, totais, corrigido = normalizar(leis)
        validar_meta(meta, sha, totais, obrigatorio=True)
        db = conectar()
        with db.connection_context():
            from banco import Lei, Artigo
            resultado = dict(acao='validar', banco='conectado', leis=Lei.select().count(),
                              artigos=Artigo.select().count(), sha256=sha, formato_corrigido=corrigido)
            if resultado['leis'] != totais['leis'] or resultado['artigos'] != totais['artigos']:
                raise ValueError('Totais do banco diferentes do snapshot validado.')
        subprocess.run([sys.executable, str(RAIZ / 'conferir_fonte.py'), '--api'], cwd=RAIZ, check=True)
    (pasta / 'resultado.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(resultado, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acao', choices=['validar', 'coletar'], default='validar')
    raise SystemExit(executar(parser.parse_args().acao))

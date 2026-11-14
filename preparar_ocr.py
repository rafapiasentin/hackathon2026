"""Instala somente os dados de idioma oficiais; OCR executado localmente."""
import hashlib

import requests

from extracao_documentos import OCR_SHA256, TESSDATA


def main():
    TESSDATA.mkdir(parents=True, exist_ok=True)
    destino = TESSDATA / 'por.traineddata'
    if destino.is_file() and hashlib.sha256(destino.read_bytes()).hexdigest() == OCR_SHA256:
        print('Modelo OCR português já validado.')
        return 0
    resposta = requests.get('https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/por.traineddata', timeout=60)
    resposta.raise_for_status()
    if hashlib.sha256(resposta.content).hexdigest() != OCR_SHA256:
        raise ValueError('Hash do modelo diferente da versão homologada; arquivo não instalado.')
    destino.write_bytes(resposta.content)
    print('Modelo OCR português instalado e validado.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

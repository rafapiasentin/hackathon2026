"""Inicia a API somente na interface local, com catálogo real identificado."""
import os

import uvicorn

if __name__ == '__main__':
    os.environ['API_MODO_DOCUMENTAL_LOCAL'] = 'true'
    from api_local import preparar_indices
    from banco import conectar
    preparar_indices(conectar())
    uvicorn.run('api_local:app', host='127.0.0.1', port=8000)

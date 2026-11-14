# Produção

O frontend permanece em https://rafapiasentin.github.io/hackathon2026/.
Não renomear o repositório, proprietário ou caminho base do Pages.

O PostgreSQL completo foi migrado para a branch `producao` do projeto Neon
`hackathon2026-londrina`. A migração usa backup integral e compara os hashes
de todas as tabelas, incluindo os registros de governança.

A API Python usa os mesmos `api_local.py`, `busca_documental.py` e `banco.py`
da execução local, em https://londrina-conecta-api.vercel.app. Sua credencial
é somente de leitura. `API_MODO=documental` mantém o catálogo documental
com a situação da fonte, sem afirmar revisão institucional. O modo
`governado` continua exigindo publicação aprovada. Não há LLM.

O workflow `backend.yml` executa o backend de coleta e governança no GitHub
Actions diariamente às 06:00 UTC. Usa todos os módulos e dependências Python
do repositório, incluindo OCR português, adaptadores, validação de hash,
metadados, quarentena e histórico. Os segredos `NEON_DATABASE_URL` e
`CML_TOKEN` ficam criptografados no GitHub. Coletas não substituem a aprovação
institucional exigida pelo contrato. Relatórios e originais são preservados
no banco e em artefatos do workflow. A ação manual `validar` confere o
snapshot e a fonte sem escrever no acervo; `coletar` executa o fluxo completo.

Revisores devem ser configurados em `GOVERNANCA_REVISORES` pelo responsável,
seguindo o contrato existente. Não preencher automaticamente nem declarar
leis aprovadas para contornar essa regra.

Para atualizar a API, publicar os módulos de consulta com `app.py`,
`requirements-api.txt` como `requirements.txt` e `deploy/api/vercel.json`.
Para atualizar o site, executar o build Pages e `exportar-pages.mjs` antes
do push. As tarefas de coleta executam a versão de `main`, sem o computador local.

# Busca documental sem LLM

O sistema não usa LLM, embeddings nem serviço externo de interpretação.
`busca_documental.py` contém as regras determinísticas e sua versão. O filtro
de vigência e a revisão institucional continuam independentes da relevância.

## Fluxo

1. Remove palavras de conversa e identifica grupos de sinônimos explícitos.
2. Perguntas ambíguas pedem contexto antes da busca. Perguntas extensas demais
   pedem divisão em dúvidas específicas, sem descartar conceitos silenciosamente.
3. PostgreSQL full-text recupera até 100 candidatos não revogados.
4. O filtro exige todos os conceitos no mesmo trecho de até 1.500 caracteres.
   Uma ocorrência distante em anexo não pode completar a evidência de outro trecho.
5. Regras de escopo evitam usar comércio de equipamentos ou transporte coletivo
   para orientar som em veículo particular. Os critérios são explícitos, testáveis.
6. Os resultados aceitos são ordenados por cobertura dos conceitos, contexto,
   ano como desempate e tamanho. Recência não é tratada como prova de vigência.
7. A resposta cita trechos literais. Não transforma semelhança em interpretação
   jurídica e não deduz um horário-limite a partir de fragmentos relacionados.

Estados retornados em `evidencia.estado`:

- `precisa_contexto`: a pergunta precisa ser mais específica;
- `insuficiente`: nenhum candidato satisfez os critérios;
- `trechos_relacionados`: existem trechos relacionados, sem promessa de resposta conclusiva.

O relatório inclui conceitos, número de candidatos e número de aceitos.
Não há porcentagem de confiança inventada. Os pesos são critérios de ordenação,
não probabilidades. Artigos e leis revogados continuam excluídos do chat.

## Regressões

As fixtures sintéticas cobrem ruído, arborização, IPTU, coincidências de palavras,
conceitos distantes e perguntas ambíguas. `tests/casos_consulta.json` registra
casos sobre o snapshot real e fontes relacionadas/inadequadas. Esses casos
avaliam recuperação, não substituem revisão jurídica das normas.

```powershell
$env:DB_TEST_NAME = 'hackathon2026_teste'
$env:TEST_ACERVO_DB = 'hackathon2026'
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:DB_TEST_NAME
Remove-Item Env:TEST_ACERVO_DB
```

A suíte de acervo executa apenas leituras. Deve crescer com perguntas reais,
acompanhadas das evidências esperadas. Uma alteração no dicionário ou ranking
precisa preservar os casos anteriores. Sinônimos ainda exigem manutenção;
sem LLM, perguntas novas podem ser recusadas por falta de vocabulário ou contexto.

## Publicação

Esta evolução é testada localmente. Não modifica o endereço nem a configuração
do GitHub Pages: https://rafapiasentin.github.io/hackathon2026/

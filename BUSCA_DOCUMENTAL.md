# Busca documental sem LLM

O sistema não usa LLM, embeddings nem serviço externo de interpretação.
`busca_documental.py` contém as regras determinísticas e sua versão. O filtro
de vigência e a revisão institucional continuam independentes da relevância.

A versão **2.1.0** distingue assuntos conhecidos de palavras livres: termos
coloquiais como “alguma” e “frente” não bloqueiam a recuperação. O dicionário
inclui ruído, arborização, IPTU, alvará, resíduos/entulho, meio ambiente,
animais, fumo, terrenos, ambulantes, estacionamento, calçadas e queimadas.
“Calçada” é localização genérica numa pergunta sobre árvores, mas assunto
próprio em perguntas sobre conservação de calçadas. “Ambiental” também não
vira uma exigência adicional quando ruído ou arborização já define o assunto.

## Fluxo

1. Remove palavras de conversa e identifica grupos de sinônimos explícitos.
2. Perguntas ambíguas pedem contexto antes da busca. Perguntas extensas demais
   pedem divisão em dúvidas específicas, sem descartar conceitos silenciosamente.
3. PostgreSQL full-text recupera até 100 candidatos não revogados. Exige os
   grupos obrigatórios já nesta etapa, com `AND` entre grupos e `OR` entre
   sinônimos. Complementos pontuam na ordenação antes do limite de 100:
   isso evita perder a lei específica antes da avaliação dos trechos.
4. O filtro exige todos os grupos conhecidos no mesmo trecho de até 1.500 caracteres.
   Havendo um grupo conhecido, palavras livres apenas somam três pontos por
   conceito encontrado nesse trecho. Sem grupos conhecidos, a API consulta
   a frequência documental no mesmo escopo de artigos elegíveis: a palavra
   com menos artigos é obrigatória; as demais apenas pontuam. Zero ocorrências
   também conta, impedindo trocar um assunto ausente por coincidências genéricas.
   O desempate segue a ordem da pergunta. A função pura `planejar` recebe
   esse consultor de frequências; sem ele, conserva a exigência de todas as
   palavras livres, sem inventar frequências nem acessar o banco implicitamente.
   Uma ocorrência distante em anexo não pode completar a evidência de outro trecho.
   Palavras livres com cinco letras ou mais aceitam sufixos por prefixo de palavra
   (por exemplo, `logradouro` encontra `logradouros` e `público` encontra `públicos`).
   Sem grupo conhecido, isso vale também para a recuperação full-text (`:*`).
   Havendo grupo conhecido, apenas seus termos recuperam os candidatos;
   complementos como “público” não ocupam as 100 vagas com outros assuntos.
   Grupos do dicionário e
   palavras curtas mantêm a comparação exata: `poda` não encontra `poderá`.
   Flexões que não compartilham um prefixo literal precisam de família explícita:
   `isenção` inclui `isenta` e `isento`; `aposentado` encontra `aposentados` por prefixo.
5. Regras de escopo evitam usar comércio de equipamentos ou transporte coletivo
   para orientar som em veículo particular. Os critérios são explícitos, testáveis.
6. Os resultados aceitos são ordenados por cobertura dos conceitos, contexto,
   ano como desempate e tamanho. Recência não é tratada como prova de vigência.
   Sinônimos de um mesmo grupo representam um conceito; repetir sinônimos não
   soma pontos. Perguntas geográficas sobre a capital de um país ficam sem
   evidência: um nome de país numa lei de denominação de rua não é resposta.
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
Incluem as cinco perguntas coloquiais de arborização/resíduos e os casos de
entulho, animais, fumo, terrenos, ambulantes, estacionamento, calçadas,
queimadas e isenção de IPTU. A consulta de logradouro exige a Lei 14.279 entre
as fontes; a de isenção aceita a Lei 6.009 ou as normas relacionadas à sua alteração.

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

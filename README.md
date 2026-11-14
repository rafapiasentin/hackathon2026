# Londrina Conecta: as leis de Londrina em linguagem simples

Projeto do **Hackathon Smart Cities Londrina 2026**. Um assistente em que o cidadão e os servidores perguntam sobre as leis municipais de Londrina e recebem a resposta com base **só nas leis em vigor**, citando a lei, o artigo e o link oficial da Câmara.

- **Site:** https://rafapiasentin.github.io/hackathon2026/
- **API pública:** https://londrina-conecta-api.vercel.app (saúde e totais em [`/api/health`](https://londrina-conecta-api.vercel.app/api/health))
- **Repositório:** https://github.com/rafapiasentin/hackathon2026

> Este README é o ponto de partida do projeto, tanto para a equipe quanto para quem (ou qual assistente de IA) for usá-lo como contexto. As seções do começo dão a visão geral; os detalhes de cada parte estão nas seções seguintes e nos documentos indicados.

## Sumário

1. [Introdução: o problema e a solução](#introdução-o-problema-e-a-solução)
2. [Arquitetura](#arquitetura)
3. [Mapa do repositório](#mapa-do-repositório)
4. [Estado atual](#estado-atual-14112026)
5. [Como rodar](#como-rodar-escolha-um-caminho)
6. [Regras do projeto](#regras-do-projeto-não-quebrar)
7. [Produção](#produção-onde-cada-parte-roda)
8. [Decisões em aberto](#decisões-em-aberto)
9. Detalhes: [coleta](#coleta-dos-dados-como-rodar), [fonte](#fonte-dos-dados), [formato do `leis.json`](#formato-do-leisjson), [vigência](#como-a-vigência-é-calculada), [problemas nos dados](#problemas-encontrados-nos-dados-e-como-foram-resolvidos), [banco](#banco-local-com-peewee)

## Introdução: o problema e a solução

**O problema.** Londrina tem mais de 14 mil leis municipais. Muitas já foram revogadas ou alteradas, e quem consulta (cidadão ou servidor) acaba usando uma lei que não vale mais. A responsável pelas leis relatou exatamente essa dor.

> Exemplo que motivou o projeto: a Lei nº 14.294, de 29/10/2026, instituiu o novo Código Ambiental de Londrina e revogou a Lei nº 11.471/2012. Uma pergunta sobre regra ambiental precisa ser respondida com a lei de 2026, não com a de 2012.

**A solução.**

1. **Coletamos todas as leis** da API oficial da Câmara Municipal (14.308 leis, 74.630 artigos), com o texto completo e as relações oficiais (quem altera e quem revoga quem).
2. **Calculamos a vigência** de cada lei e de cada artigo. A página da Câmara mostra o texto compilado, com a redação antiga riscada; separamos a redação vigente da revogada (1.492 artigos revogados identificados).
3. **Guardamos tudo num banco** (PostgreSQL), com conferência de integridade (hash e totais) e um fluxo de governança para publicação.
4. **O assistente** busca só em leis vigentes e artigos não revogados, responde citando lei, artigo e link, e avisa quando uma lei sobre o assunto foi revogada (e por qual).
5. **O site** (React) tem conversa, busca, página da lei com histórico, comparação "o que mudou" e um **validador de leis** (padrão da LC 95/1998), além de recursos de acessibilidade.

## Arquitetura

```
 API da Câmara (CML)                         coleta_leis.py
 + página de cada lei      ───────────────►  (texto, artigos, riscado, relações, vigência)
                                                     │
                                                     ▼
                                       leis.zip  =  leis.json + leis.meta.json (SHA-256 e totais)
                                                     │
                                                     ▼
                       carregar_leis.py / governanca.py  ──►  PostgreSQL (banco.py, Peewee)
                       (valida hash e totais, contrato,          tabelas: lei, artigo, relacao,
                        publicação governada)                    relacionamento_cml, carga...
                                                     │
                                                     ▼
                       api_local.py (FastAPI)  ◄── busca_documental.py (full-text em português)
                       GET /api/leis · GET /api/leis/{id} · POST /api/perguntar · GET /api/health
                                                     │
                                                     ▼
                       frontend/ (React + Vite)  ──►  GitHub Pages
```

Em produção, o PostgreSQL roda no **Neon**, a API na **Vercel** e o site no **GitHub Pages**; a coleta é refeita todo dia pelo **GitHub Actions**. Ver [Produção](#produção-onde-cada-parte-roda).

## Mapa do repositório

| Área | Arquivo | O que é |
|---|---|---|
| **Coleta** | `coleta_leis.py` | Baixa as leis da API e das páginas da Câmara; marca texto riscado; calcula vigência; gera `leis.json` e `leis.meta.json`. Explicado em [docs/COMO_FUNCIONA.md](docs/COMO_FUNCIONA.md) |
| | `relatorio_problemas.py` | Gera [docs/PROBLEMAS_NOS_DADOS.md](docs/PROBLEMAS_NOS_DADOS.md) e `docs/leis_com_problemas.csv` (1.490 leis com problemas na fonte e a solução de cada um) |
| | `conferir_fonte.py` | Confere disponibilidade e estrutura da API da Câmara sem expor o token |
| **Dados** | `leis.zip` | `leis.json` + `leis.meta.json` da coleta completa de 14/11/2026 (formato 2.0) |
| | `leis.meta.json` | Hash SHA-256, totais e commit do coletor; usado para conferir a carga |
| **Banco e governança** | `banco.py` | Modelos Peewee (PostgreSQL) e filtro `artigos_para_chatbot()` |
| | `carregar_leis.py` | Carga do `leis.zip` no PostgreSQL, conferindo hash e totais |
| | `governanca.py`, `contrato_governanca.json` | Publicação governada: contrato versionado, pendências, revisão de vigência. Ver [GOVERNANCA.md](GOVERNANCA.md) |
| | `adaptadores.py`, `extracao_documentos.py`, `atualizar_base.py`, `preparar_ocr.py` | Entrada de novos dados em vários formatos (JSON, CSV, XML, HTML, PDF com OCR) e pasta de entrada automática |
| **API** | `api_local.py` | API sobre o PostgreSQL, com busca documental (sem IA) e governança |
| | `busca_documental.py` | Regras de busca e relevância, sem IA. Ver [BUSCA_DOCUMENTAL.md](BUSCA_DOCUMENTAL.md) |
| | `iniciar_local.py` | Sobe o `api_local.py` em modo local (127.0.0.1:8000). Ver [RODAR_LOCAL.md](RODAR_LOCAL.md) |
| **Front** | `frontend/` | React + Vite + TypeScript + Tailwind. Telas, contrato da API e Pages em [frontend/README.md](frontend/README.md) |
| | `index.html`, `assets/`, `.nojekyll`, `.github/workflows/pages.yml` | Build publicado no GitHub Pages |
| **Produção** | `deploy/api/` (`app.py`, `vercel.json`), `requirements-api.txt` | Publicação da API na Vercel (usa o mesmo `api_local.py`) |
| | `deploy/worker.py`, `.github/workflows/backend.yml` | Coleta e governança diárias no GitHub Actions, gravando no banco de produção. Ver [deploy/README.md](deploy/README.md) |
| **Testes** | `tests/`, `pytest.ini` | Carga, governança, API, busca e casos de consulta reais (`tests/casos_consulta.json`) |
| **Documentação** | `ATUALIZACAO.md` | Resumo para o grupo |
| | `docs/REVISAO_INTEGRACAO_FRONT.md` | Revisão técnica da integração do front |
| **Configuração** | `.env.example`, `frontend/.env.example` | Modelos de configuração (token da CML, banco, endereço da API) |

Não vão para o git: `.env` (token e senha do banco), `leis.json` descompactado, `cache_textos/` e `frontend/.env.local`.

## Estado atual (14/11/2026)

| Parte | Situação |
|---|---|
| Coleta completa, texto riscado, vigência, relatório de problemas | ✅ Pronta (`leis.zip`, hash `459d6a82…`) |
| Carga no PostgreSQL com conferência de hash e totais | ✅ Feita, local e em produção (Neon) |
| API (`api_local.py`) com busca documental | ✅ Publicada na Vercel, em modo `documental` |
| Front no GitHub Pages ligado à API pública | ✅ No ar, com os dados reais |
| Coleta e governança automáticas | ✅ GitHub Actions, todo dia às 06:00 UTC (03:00 em Brasília) |
| Busca 2.2.0: tipo de pergunta, resposta direta citando lei e artigo, fontes só quando sustentam a resposta | ✅ No código e nos testes · ⏳ aguarda deploy da API na Vercel (produção ainda na 2.1.0) |
| IA gerando a resposta em linguagem natural | ⏳ Não implementado; a resposta é extrativa (cita trechos literais) |
| Lei Orgânica, leis complementares e emendas | ⏳ Ainda não coletadas |
| Revisão institucional de vigência (governança) | ⏳ Aguarda o fluxo oficial do órgão |

## Como rodar (escolha um caminho)

**A. Completo, com PostgreSQL (recomendado):** siga [RODAR_LOCAL.md](RODAR_LOCAL.md). Resumo: carregar o `leis.zip` no PostgreSQL ([Banco local com Peewee](#banco-local-com-peewee)), `python iniciar_local.py` e, em outro terminal, `cd frontend && npm ci && npm run dev`, com `VITE_API_URL=http://127.0.0.1:8000` em `frontend/.env.local`.

**B. Front local usando a API pública:** `cd frontend && npm install && npm run dev`, com `VITE_API_URL=https://londrina-conecta-api.vercel.app` em `frontend/.env.local`. Não precisa de banco.

**C. Só o front, com dados de exemplo:** `cd frontend && npm install && npm run dev` (sem `VITE_API_URL`).

**D. Refazer a coleta dos dados:** [Coleta dos dados: como rodar](#coleta-dos-dados-como-rodar) (precisa do token da Câmara no `.env`).

## Regras do projeto (não quebrar)

Estas regras valem para qualquer código novo, inclusive gerado por IA:

1. **O identificador de uma lei é o `id` da Câmara.** `chave`/`numero` se repetem (ex.: duas Leis nº 48 de 1949) e não podem ser chave primária nem `UNIQUE`.
2. **Responder só com o que está vigente:** leis com `situacao IN ('vigente', 'vigente_com_alteracoes')` e artigos com `revogado = false`, usando apenas o campo `texto`. `texto_riscado` é histórico ("como era antes").
3. **"Revogada por" nos relacionamentos não significa revogação total.** A revogação total vem da anotação "(REVOGADA pelo ...)" na ementa; a parcial aparece só nos relacionamentos.
4. **Nunca inventar dados.** Data, ementa, vigência e revogador ausentes ficam nulos, com o campo de fonte indicando a origem (`data_lei_fonte`, `ementa_fonte`, `revogacao_nota`).
5. **Toda resposta cita lei, artigo e link oficial**, e avisa que não substitui orientação jurídica. Quando a base não responde, o assistente diz que não sabe.
6. **Toda carga confere o SHA-256 e os totais** do `leis.meta.json`.
7. **Segredos nunca vão para o git:** token da Câmara (`CML_TOKEN`), senha do banco e chaves de API de IA ficam só no `.env` ou nas variáveis de ambiente da hospedagem; nunca no front.

## Produção: onde cada parte roda

| Parte | Onde | Detalhes |
|---|---|---|
| Site | GitHub Pages: https://rafapiasentin.github.io/hackathon2026/ | Build com `VITE_API_URL` da API pública (`frontend/.env.pages`). **Não renomear** o repositório, o dono nem o caminho base |
| API | Vercel: https://londrina-conecta-api.vercel.app | Mesmo `api_local.py`, `busca_documental.py` e `banco.py` da execução local; credencial do banco **somente leitura**; `API_MODO=documental` |
| Banco | Neon (PostgreSQL), projeto `hackathon2026-londrina`, branch `producao` | Migração integral conferida por hash de todas as tabelas |
| Coleta e governança | GitHub Actions (`backend.yml`), diário às 06:00 UTC | Ações manuais: `validar` (só confere) e `coletar` (fluxo completo). Segredos `NEON_DATABASE_URL` e `CML_TOKEN` criptografados no GitHub |

Como atualizar cada parte: [deploy/README.md](deploy/README.md). O modo `documental` mostra a situação informada pela Câmara e avisa que a revisão institucional está pendente; o modo `governado` só expõe publicações com revisão de vigência aprovada (ver [GOVERNANCA.md](GOVERNANCA.md)).

## Decisões em aberto

| Tema | Opções | Observações |
|---|---|---|
| **Usar IA (LLM) na resposta** | Manter a busca documental sem IA ou adicionar um modelo (ex.: Gemini, pelo Google AI Studio) | Sem IA, perguntas de fato ("quantos vereadores…") não são respondidas. Com IA, ela deve ler **só** os artigos encontrados, citar a fonte e, se falhar, voltar à resposta extrativa. A chave fica nas variáveis de ambiente da Vercel, nunca no front |
| **Revisores da governança** | Definir com o órgão quem pode declarar a revisão de vigência (`GOVERNANCA_REVISORES`) | Sem revisores, a API continua em modo `documental`; não preencher automaticamente |
| **Ampliar a base** | Lei Orgânica, leis complementares e emendas (outros tipos da API da Câmara) | Perguntas sobre a composição da Câmara, por exemplo, dependem da Lei Orgânica |

## Coleta dos dados: como rodar

Requisitos: Python 3.10 ou superior.

```bash
pip install requests beautifulsoup4 python-dotenv
cp .env.example .env    # depois coloque o token real da CML no .env
```

```bash
python coleta_leis.py --paginas 2 --texto   # teste rápido: 100 leis com texto (~1 min)
python coleta_leis.py                        # lista completa, só ementas (~5 min)
python coleta_leis.py --texto                # tudo com texto e relações oficiais (~1h10; ~50 min com --paralelo 5)
python relatorio_problemas.py                # depois da coleta: atualiza docs/PROBLEMAS_NOS_DADOS.md
```

| Opção | Efeito |
|---|---|
| `--paginas N` | Limita a N páginas da API (50 leis por página) |
| `--texto` | Baixa também o texto e os "Relacionamentos desta Matéria" de cada lei |
| `--paralelo N` | Downloads simultâneos de texto (padrão 3) |
| `--saida ARQ` | Nome do arquivo de saída (padrão `leis.json`) |

A coleta com texto guarda cada lei em `cache_textos/<id>.json`. Se ela parar no meio, rode o mesmo comando de novo e ela continua de onde parou.

## Fonte dos dados

### API da CML (precisa do token `keysoft`)

```
https://www.cml.pr.gov.br/jsonweb/web-aplicativo.php?keysoft=TOKEN&call=legislacoes&tipo=Leis&pagina=1
```

- A API tem 8 tipos de legislação. Usamos `Leis`, que traz as leis ordinárias: 14.308 em novembro de 2026, em umas 290 páginas. A Lei Orgânica, as Emendas à Lei Orgânica e as leis complementares estão em outros tipos e ainda não foram incluídas.
- Vêm 50 leis por página, da mais nova para a mais antiga. Quando a página volta vazia, acabou.
- Cada item vem assim:

```json
{
  "data": "2026-11-04 18:44:30",
  "titulo": "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026",
  "ementa": "SÚMULA: Institui o Código Ambiental do Município de Londrina.",
  "autoria": "",
  "link": "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/296902#pesquisa"
}
```

- `data` é quando a lei foi publicada no site, **não** a data da lei.
- O título tem dois formatos. As leis recentes (umas 420) vêm como `LEI N.º 14294, DE 29 DE OUTUBRO DE 2026`, com a data completa. As antigas vêm como `LEI ORDINÁRIA Nº 11341/2011`, só com o ano; nesse caso a data é tirada da assinatura no fim do texto ("Londrina, 5 de janeiro de 2012." ou "EDIFÍCIO DA PREFEITURA... aos 3 de julho de 1970.") ou, se a lei só tiver PDF, da data do anexo. A data só é aceita se o ano bater com o do título. Algumas leis antigas têm letra no número (`520 - A`, `1666 A`).
- **Revogação total vem anotada na ementa** pela própria CML: `... (REVOGADA pelo art. 270. da Lei nº 12.236, de 29 de janeiro de 2015)`. Cerca de 1.300 leis têm essa anotação.

### Página de cada lei (`link`)

- Traz o texto completo em HTML (não precisa de PDF). É o **texto compilado**: a redação antiga aparece **riscada** (`<strike>`) ao lado da redação nova. O script marca o riscado e separa a redação vigente da antiga.
- Leis antigas podem ter só um PDF anexado; o link fica em `anexos`.
- Traz a seção oficial **"Relacionamentos desta Matéria"**, com os rótulos `Altera`, `Alterada por`, `Revoga`, `Revogada por`, `Cita`, `Citada por`, `Sanção`, `Promulgação` e `Vínculo`. Cada item aponta para o `id` da outra matéria.
- Atenção: `Revogada por` inclui **revogação parcial**. A Lei 11.471 aparece "Revogada por" a 13.529/2022, que só revogou os §§ 1º e 2º do art. 23. A revogação total é só a da 14.294/2026, e é ela que aparece anotada na ementa.

## Formato do `leis.json`

```json
{
  "id": "296902",
  "chave": "14294",
  "tipo": "Lei",
  "numero": "14294",
  "data_lei": "2026-10-29",
  "ano": "2026",
  "titulo": "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026",
  "ementa": "Institui o Código Ambiental do Município de Londrina.",
  "publicado_site": "2026-11-04 18:44:30",
  "link": "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/296902",
  "data_lei_fonte": "titulo",
  "data_lei_original": null,
  "ementa_fonte": "api",
  "situacao": "vigente",
  "revogacao_nota": null,
  "complementa_id": null,
  "texto_disponivel": true,
  "hash_texto": "9f2c…",
  "altera": [],
  "alterada_por": [],
  "revoga": ["11471"],
  "revogada_por": [],
  "relacoes": [
    { "tipo": "revoga", "id": "35210", "chave": "11471" }
  ],
  "fonte_relacoes": "cml",
  "relacionamentos": [
    { "tipo": "Revoga", "data": "05/01/2012 00:00", "id": "35210", "descricao": "LEI ORDINÁRIA Nº 11471/2012 Institui o Código Ambiental ..." }
  ],
  "anexos": [],
  "artigos": [
    { "ordem": 1, "artigo": "Art. 1º", "texto": "Art. 1º ...", "texto_riscado": null, "revogado": false }
  ]
}
```

- `id` é o identificador da CML e é único. `chave` é o número legível: `14294`, `520-A` ou, para lei complementar, `LC-12`. Existem 4 casos de leis diferentes com o mesmo número (por exemplo, duas Leis nº 48 de 1949).
- `altera`, `alterada_por`, `revoga` e `revogada_por` são listas de `chave`, para leitura humana.
- `relacoes` traz as mesmas relações **por `id`**, para o banco: `tipo` é `altera`, `alterada_por`, `revoga` ou `revogada_por`. `id` é `null` quando a lei citada não está no arquivo (por exemplo, uma lei complementar).
- `relacionamentos` é a lista crua da seção oficial da CML, com todos os rótulos (inclusive `Cita`, `Sanção`, `Vínculo`). As relações da lei com ela mesma, que existem na fonte por erro, ficam aqui mas **não** entram em `relacoes`.
- `tipo` é `Lei` ou `Promulgação de partes vetadas`: trechos vetados pelo prefeito que a Câmara promulgou depois, publicados à parte com o **mesmo número** da lei. Nesse caso, `complementa_id` aponta para a lei principal, e os artigos fazem parte dela.
- `situacao` pode ser `vigente`, `vigente_com_alteracoes`, `revogada` ou `inexistente` (número que ficou vago: "LEI INEXISTENTE").
- `revogacao_nota` guarda a anotação original "(REVOGADA pelo ...)". Serve de evidência quando o revogador não é identificável (decreto ou erro de digitação na fonte).
- `data_lei` só recebe datas que existem no calendário, e pode ser `null`. `data_lei_fonte` diz de onde veio: `titulo`, `assinatura` ou `anexo`. `data_lei_original` guarda uma data impossível encontrada na fonte (ex.: `2010-02-29`) para revisão. `ano` está sempre preenchido.
- `ementa` é `null` quando não existe; `ementa_fonte` é `api`, `texto` (súmula tirada do texto quando a API veio vazia) ou `null`.
- `texto_disponivel` é `false` quando a lei só tem PDF anexado ou é inexistente. `anexos` traz os links dos PDFs.
- `hash_texto` é o SHA-256 do texto baixado: numa coleta futura, um hash diferente indica que a página da lei mudou.
- `fonte_relacoes` é `cml` quando as relações vieram da seção oficial e `ementa` quando foram deduzidas da ementa (coleta sem `--texto`).
- `relacionamentos`, `anexos`, `artigos` e `hash_texto` só são preenchidos com `--texto`.

### Artigos e texto riscado

As páginas mostram o **texto compilado**: quando um artigo muda, a redação antiga continua lá, riscada, e a nova vem logo depois. Cada artigo traz:

- `ordem`: posição do artigo no texto, **única dentro da lei** (use como chave no banco).
- `texto`: só a redação **vigente** (sem o riscado). Fica `""` se o artigo inteiro está riscado.
- `texto_riscado`: a redação antiga, que não vale mais (`null` se não houver).
- `revogado`: `true` quando o artigo inteiro está riscado.
- `artigo`: o rótulo ("Art. 3º"). **Pode se repetir**: o "Art. 3º" antigo (riscado, `revogado: true`) seguido do "Art. 3º" com a redação nova.

> Para o chatbot: indexe e mostre só `texto` de artigos com `revogado = false`. O `texto_riscado` serve para responder "como era antes".

### Metadados (`leis.meta.json`)

Arquivo gerado ao lado do `leis.json`, sem mudar a estrutura dele (que continua sendo uma lista). Traz `versao_formato`, `gerado_em`, `textos_baixados_entre`, a fonte, o `commit` do script, os totais e o `sha256` do `leis.json`, que permite conferir se o arquivo é exatamente o que foi gerado.

### Sugestão de tabelas (Postgres)

| Tabela | Colunas principais | Chave |
|---|---|---|
| `lei` | `id`, `chave`, `numero`, `data_lei`, `ano`, `titulo`, `ementa`, `link`, `situacao` | `id` |
| `artigo` | `lei_id`, `ordem`, `artigo`, `texto`, `texto_riscado`, `revogado` | `(lei_id, ordem)` |
| `relacao` | `lei_origem_id`, `lei_destino_id` (aceita nulo), `chave_destino`, `tipo` | — |
| `relacionamento_cml` | `lei_id`, `tipo`, `data`, `id_destino`, `descricao` (lista crua, inclui Sanção, Cita, Vínculo) | — |

- Não use `chave`/`numero` como chave primária nem com `UNIQUE`: existem leis diferentes com o mesmo número.
- `data_lei` deve aceitar nulo; `ano` nunca é nulo.
- Para a busca, filtre leis com `situacao IN ('vigente', 'vigente_com_alteracoes')` e artigos com `revogado = false`, e não indexe leis com `texto_disponivel = false`.

## Como a vigência é calculada

1. **Revogada:** a ementa tem a anotação oficial `(REVOGADA pelo ... Lei nº X ...)`. A lei X vai para `revogada_por`.
2. **Relações:** com `--texto`, vêm da seção oficial "Relacionamentos desta Matéria". Sem `--texto`, são deduzidas da ementa: quando ela começa com "Altera", "Insere", "Acrescenta", "Introduz alterações", "Dá nova redação", "Modifica" ou "Revoga", as leis citadas entram em `altera`, e o lado inverso (`alterada_por`) é preenchido automaticamente.
3. **Vigente com alterações:** a lei não está revogada, mas tem `alterada_por` ou `revogada_por` (revogação parcial).
4. **Vigente:** nenhum dos casos acima.

Resultado da coleta completa (14/11/2026, `leis.meta.json`): **14.308 leis**, **74.630 artigos** (1.492 revogados por inteiro e 1.471 com algum trecho riscado) e **9.612 relações**, com 11.974 vigentes, 1.031 vigentes com alterações, 1.298 revogadas e 5 inexistentes. O caso da demo sai certo: a 11.471 fica `revogada`, com `revogada_por: ["14294", "13529"]` (revogação total pela 14.294 e parcial pela 13.529).

## Problemas encontrados nos dados (e como foram resolvidos)

Os dados de origem (site e API da Câmara) têm problemas. O script **não corrige a fonte nem inventa dados**: ele trata cada caso e registra de onde veio cada informação. Na coleta de 14/11/2026, **1.490 das 14.308 leis** tinham pelo menos um problema. Uma lei pode estar em mais de uma categoria.

| Problema | Leis | O que aconteceu na fonte | Como resolvemos |
|---|---|---|---|
| Redação antiga riscada | 633 | A página mostra o **texto compilado**: quando um artigo muda, a redação antiga continua lá, riscada, e a nova vem depois. O script antigo pegava as duas como válidas. São 1.492 artigos revogados por inteiro e 1.471 com algum trecho riscado. | Cada trecho riscado é separado: `texto` traz só a redação vigente, `texto_riscado` a antiga, e `revogado = true` quando o artigo inteiro está riscado. Ex.: Lei 1.457/1969, art. 3º. |
| Lei sem data | 837 | Título antigo só com o ano (`LEI ORDINÁRIA Nº 1234/1965`) e texto sem assinatura datada nem anexo. | `data_lei = null`, sem inventar. O `ano` está sempre preenchido. |
| Data impossível | 1 | O texto da Lei 10.887 diz "29 de fevereiro de 2010" (2010 não foi bissexto). | Fica em `data_lei_original` para revisão; a data usada (29/03/2010) veio do anexo (`data_lei_fonte = "anexo"`). |
| Relação da lei com ela mesma | 25 | Nos "Relacionamentos", a Câmara lista a lei como "Revoga" / "Altera" / "Revogada por" ela mesma (27 relações). | Descartadas em `relacoes`; continuam na lista crua `relacionamentos`. |
| Anotação de revogação cita a própria lei | 2 | Ex.: a Lei 9.265 diz "(REVOGADA pelo Art. 14 da Lei nº 9.265 de 8 de dezembro de 2018)": número errado na fonte. | A lei continua `revogada`, o número errado não vira relação, a anotação fica em `revogacao_nota`. O revogador correto (Lei 12.232), listado pela Câmara nos Relacionamentos, entra em `revogada_por`. |
| Revogada sem revogador identificável | 3 | Revogada por **decreto** (Lei 13.905), anotação quebrada na fonte (Lei 6.884: "Lei nº de de de 20") ou anotação que cita a própria lei sem outro revogador listado (Lei 6.135). | `situacao = revogada`, `revogada_por` vazio e a anotação original em `revogacao_nota`. |
| Ementa vazia na API | 3 | A API devolveu a ementa em branco. | Usa a "SÚMULA:" do texto quando existe (`ementa_fonte = "texto"`); senão `ementa = null`. |
| Promulgação de partes vetadas | 1 | A "Lei 13.960" aparecia duas vezes: a segunda é a promulgação, pela Câmara, dos trechos que o prefeito vetou. | `tipo = "Promulgação de partes vetadas"` e `complementa_id` apontando para a lei principal. |
| Leis diferentes com o mesmo número | 7 | Ex.: duas Leis nº 48 de 1949, duas nº 1.041 de 1965, duas nº 1.641 de 1970. | Identificador é o `id` da Câmara; `chave`/`numero` sem `UNIQUE`. |
| Lei só com PDF | 18 | A página não tem o texto em HTML, só um PDF anexado. | `texto_disponivel = false` e link do PDF em `anexos`. Ler os PDFs é um próximo passo. |
| Número inexistente | 5 | A página diz "LEI INEXISTENTE" (número vago). | `situacao = "inexistente"`; fica fora da busca. |

A lista completa, **lei por lei** (com link para a página oficial e o detalhe de cada caso), está em [`docs/PROBLEMAS_NOS_DADOS.md`](docs/PROBLEMAS_NOS_DADOS.md) e em [`docs/leis_com_problemas.csv`](docs/leis_com_problemas.csv). Os dois são gerados por `python relatorio_problemas.py` a partir do `leis.json`.

## Limitações conhecidas

- Sem `--texto`, as alterações são deduzidas da ementa e podem ter falsos positivos ou negativos. Com `--texto`, valem as relações oficiais da CML.
- Artigos revogados por inteiro são identificados pelo texto riscado (`revogado`). Trechos menores riscados (um inciso, um parágrafo) ficam em `texto_riscado` do artigo.
- Algumas leis revogadas ficam com `revogada_por` vazio, porque o revogador é um decreto ou a anotação da CML tem erro de digitação. A anotação original fica em `revogacao_nota`.
- A fonte tem erros que o script não corrige, só sinaliza: datas impossíveis (`data_lei_original`) e relações de uma lei com ela mesma (ficam só em `relacionamentos`).
- 18 leis só têm o texto em PDF anexado, que ainda não é lido (os links estão em `anexos`).
- Requisições com `curl` são bloqueadas pelo site (406 Not Acceptable). O script em Python funciona normalmente; se ele receber 406, mostra um aviso.

## Próximos passos

- [x] Verificar "Relacionamentos desta Matéria" como fonte oficial das relações
- [x] Rodar a coleta completa com texto, separar o texto riscado e documentar os problemas da fonte
- [x] Carregar o `leis.json` no PostgreSQL local (Peewee), conferindo hash e totais
- [x] Busca por palavras em português (full-text do PostgreSQL) com filtro de vigência
- [x] Front ligado à API local (conversa, busca, página da lei, comparação, validador)
- [x] Publicar a API (Vercel) e o banco (Neon) e ligar o front do Pages a eles
- [x] Coleta e governança automáticas diárias (GitHub Actions)
- [ ] Decidir e, se for o caso, integrar uma IA para responder em linguagem natural (a partir dos artigos encontrados)
- [ ] Incluir leis complementares, Lei Orgânica e Emendas à Lei Orgânica (outros tipos da API)
- [ ] Ler o texto das 18 leis que só têm PDF
- [ ] Definir com o órgão o fluxo de revisão institucional de vigência (governança)

## Banco local com Peewee

O fluxo atual de publicação é documentado em [GOVERNANCA.md](GOVERNANCA.md).
`governanca.py` preserva originais, valida diferentes formatos, registra pendências
e publica somente versões conformes com evidência de revisão de vigência.
`atualizar_base.py` consome automaticamente uma pasta de entrada. O caminho
`carregar_leis.py --final` também usa esse fluxo; a flag não concede aprovação.
HTML e PDF (textual ou escaneado com OCR português) também são extraídos.
Para habilitar OCR após instalar as dependências, execute
`.\.venv\Scripts\python.exe preparar_ocr.py`.

Os modelos estão em `banco.py` e a importação em `carregar_leis.py`. A estrutura
aceita o JSON antigo e os novos campos informados pela equipe. O `leis.zip`
publicado já está no formato final (2.0) e foi carregado e conferido (ver [RODAR_LOCAL.md](RODAR_LOCAL.md)).

### Preparação (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Configure `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e `DB_PASSWORD` no `.env`,
usando `.env.example` como referência. A senha fica somente no `.env` ignorado
pelo Git. O banco padrão é `hackathon2026`; o banco de testes é
`hackathon2026_teste`. O usuário precisa de permissão de criação de bancos apenas
quando usar `--criar-banco`.

```powershell
# Cria o banco, se necessário, e as tabelas vazias. Não apaga tabelas existentes.
.\.venv\Scripts\python.exe carregar_leis.py --criar-banco --criar-tabelas

# Confere a entrada sem conectar ao PostgreSQL.
.\.venv\Scripts\python.exe carregar_leis.py leis.zip --validar

# Testa o ZIP antigo exclusivamente no banco de testes.
.\.venv\Scripts\python.exe carregar_leis.py leis.zip --banco hackathon2026_teste --criar-banco --recriar --permitir-legado

# Quando a equipe publicar o ZIP corrigido e os metadados:
.\.venv\Scripts\python.exe carregar_leis.py leis.zip --validar --final
.\.venv\Scripts\python.exe governanca.py leis.zip
```

O argumento também aceita `leis.json`. O ZIP é lido sem extrair arquivos. Os
metadados são procurados no ZIP ou como `leis.meta.json` ao lado da entrada;
`--meta caminho` seleciona explicitamente um arquivo externo.

**No modo legado de teste, `--recriar` substitui as cinco tabelas abaixo.**
Na carga final governada, usa atualização incremental, preservando histórico;
`--recriar` não apaga dados quando combinado com `--final`.
O modo legado não apaga o banco
nem outras tabelas e não usa `CASCADE` para derrubar dependências externas.
Valida o arquivo antes de alterar o banco. O DROP, a criação das tabelas, as
inserções e as verificações dos totais ocorrem na mesma transação: uma falha
restaura a carga anterior. Uma trava de transação impede cargas concorrentes.

### Tabelas e regras

| Tabela | Regras |
|---|---|
| `lei` | `id` da Câmara como PK; `chave` e `numero` podem repetir; `ementa` aceita nulo; `ano` inteiro; campos de fonte, nota de revogação, hash e anexos JSONB; `complementa_id` é FK anulável para `lei.id` |
| `artigo` | PK composta `(lei_id, ordem)`; rótulo pode repetir; `texto` pode ser vazio; `texto_riscado` anulável e `revogado` booleano |
| `relacao` | Origem obrigatória, destino anulável, chave legível e tipo; destinos fora do conjunto devem vir com `id: null` |
| `relacionamento_cml` | Relação oficial original: tipo, `materia_id`, descrição e `data` textual; o destino pode ser projeto fora da base e não tem FK |
| `carga` | Arquivo, SHA256 do JSON descompactado, totais, metadados e indicação de carga corrigida/final |

As leis são inseridas primeiro, em lotes; depois são preenchidos os
`complementa_id`, os artigos e as relações. Assim, a ordem das leis na entrada
não interfere nas FKs. O tamanho padrão do lote é 500 (`--lote`, máximo 1000).
IDs de lei duplicados, ordens duplicadas dentro da lei e FKs inválidas impedem
a carga. No modo legado, datas impossíveis são preservadas em
`data_lei_original`, com `data_lei` nula. Na governança, geram pendência para
revisão. O campo de banco é texto, mas a governança valida `tipo` pela lista do
contrato, que inclui `Promulgação de partes vetadas`.

### Artigos e texto riscado

Na coleta corrigida, `artigo.texto` contém somente a redação vigente e fica
vazio quando o artigo inteiro foi revogado. A redação anterior fica em
`texto_riscado`. O importador preserva esses campos e rejeita um artigo marcado
como revogado que ainda tenha conteúdo em `texto`.

No formato antigo, usa `art.get('texto_riscado')` e
`art.get('revogado', False)`. Esses valores padrão **não comprovam que o texto
antigo esteja vigente**. Por isso a importação antiga exige
`--permitir-legado`; `artigos_para_chatbot()` bloqueia qualquer carga provisória.
As autorrelações antigas são preservadas apenas para compatibilidade e totais;
autorrelações em `relacoes` no formato corrigido causam erro.

`artigos_para_chatbot()` exige publicação governada com revisão de vigência
vinculada à versão. A flag de carga final não basta. Restringe os resultados a leis com
`situacao IN ('vigente', 'vigente_com_alteracoes')`, artigos com `revogado = false`
e `texto` não vazio. O chatbot deve usar somente `texto` como evidência vigente;
`texto_riscado` é histórico.

### Metadados e totais

A carga final exige SHA256 e totais de leis, artigos, artigos revogados e relações. O hash
é calculado sobre os bytes originais de `leis.json` descompactado. Exemplo
**sintético** do contrato informado pela equipe (commit do coletor `f9be9d4`):

```json
{
  "arquivo": {"sha256": "HASH_SHA256_DO_LEIS_JSON"},
  "commit": "f9be9d4",
  "totais": {"leis": 2, "artigos": 3, "artigos_revogados": 1, "relacoes": 2}
}
```

O objeto original dos metadados, incluindo o commit do coletor, é preservado
em `lote_ingestao.metadados` (e em `carga.metadados` no modo legado).
O commit identifica o código que gerou o arquivo; não é
fixado como requisito para permitir coletas futuras com novas versões.

Também aceita `sha256` na raiz, `sha256_leis_json` ou
`sha256: {"leis.json": "HASH"}`. Se houver vários hashes declarados, todos devem
conferir. Os totais
podem estar na raiz, em `totais`, `contagens` ou `resumo`, usando os nomes acima
ou `total_leis`, `total_artigos`, `total_artigos_revogados`, `total_relacoes`.
Se fornecido, `relacionamentos_cml` também é conferido (ou seu nome com
prefixo `total_`). Campos de metadados desconhecidos não são adivinhados:
se o arquivo final usar outro contrato, será necessário ajustar o leitor antes
da carga. Os totais são comparados com a entrada e novamente com o banco antes
do commit. A verificação com o arquivo real aguarda o término da coleta.

### Verificação

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q

# Integração: substitui as tabelas do banco de testes por fixtures sintéticas.
$env:DB_TEST_NAME = 'hackathon2026_teste'
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:DB_TEST_NAME
```

Os testes cobrem os formatos antigo/novo, hash do ZIP, divergência de totais,
FKs, números e rótulos repetidos, ementa nula, artigo revogado, filtro do chatbot,
repetição da carga e rollback após falha. Fixtures são sintéticas e identificadas.

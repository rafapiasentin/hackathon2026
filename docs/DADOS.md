# Dados das leis: fonte, formato, vigência e problemas

Referência técnica do `leis.json`, gerado por `coleta_leis.py`. Para a explicação passo a passo do coletor, veja [COMO_FUNCIONA.md](COMO_FUNCIONA.md). Voltar ao [README](../README.md).

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
- `revogacao_nota` guarda a anotação original "(REVOGADA pelo ...)". Serve de evidência quando o revogador não é identificável (erro de digitação na fonte). Uma anotação que cita só decreto não conta como revogação: decreto não revoga lei (ver [Decretos](DECRETOS.md)).
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

1. **Revogada:** a ementa tem a anotação oficial `(REVOGADA pelo ... Lei nº X ...)`. A lei X vai para `revogada_por`. Anotação que cita só decreto, como `(Revogado pelo Decreto 1.341...)` logo depois de `(Vide Decreto nº 413...)`, fala do decreto e não revoga a lei.
2. **Relações:** com `--texto`, vêm da seção oficial "Relacionamentos desta Matéria". Sem `--texto`, são deduzidas da ementa: quando ela começa com "Altera", "Insere", "Acrescenta", "Introduz alterações", "Dá nova redação", "Modifica" ou "Revoga", as leis citadas entram em `altera`, e o lado inverso (`alterada_por`) é preenchido automaticamente.
3. **Vigente com alterações:** a lei não está revogada, mas tem `alterada_por` ou `revogada_por` (revogação parcial).
4. **Vigente:** nenhum dos casos acima.

Resultado da coleta completa (14/11/2026, `leis.meta.json`): **14.308 leis**, **74.630 artigos** (1.492 revogados por inteiro e 1.471 com algum trecho riscado) e **9.612 relações**, com 11.975 vigentes, 1.031 vigentes com alterações, 1.297 revogadas e 5 inexistentes (após o reprocessamento que corrigiu a Lei 13.905). O caso da demo sai certo: a 11.471 fica `revogada`, com `revogada_por: ["14294", "13529"]` (revogação total pela 14.294 e parcial pela 13.529).

## Problemas encontrados nos dados (e como foram resolvidos)

Os dados de origem (site e API da Câmara) têm problemas. O script **não corrige a fonte nem inventa dados**: ele trata cada caso e registra de onde veio cada informação. Na coleta de 14/11/2026, **1.490 das 14.308 leis** tinham pelo menos um problema. Uma lei pode estar em mais de uma categoria.

| Problema | Leis | O que aconteceu na fonte | Como resolvemos |
|---|---|---|---|
| Redação antiga riscada | 633 | A página mostra o **texto compilado**: quando um artigo muda, a redação antiga continua lá, riscada, e a nova vem depois. O script antigo pegava as duas como válidas. São 1.492 artigos revogados por inteiro e 1.471 com algum trecho riscado. | Cada trecho riscado é separado: `texto` traz só a redação vigente, `texto_riscado` a antiga, e `revogado = true` quando o artigo inteiro está riscado. Ex.: Lei 1.457/1969, art. 3º. |
| Lei sem data | 837 | Título antigo só com o ano (`LEI ORDINÁRIA Nº 1234/1965`) e texto sem assinatura datada nem anexo. | `data_lei = null`, sem inventar. O `ano` está sempre preenchido. |
| Data impossível | 1 | O texto da Lei 10.887 diz "29 de fevereiro de 2010" (2010 não foi bissexto). | Fica em `data_lei_original` para revisão; a data usada (29/03/2010) veio do anexo (`data_lei_fonte = "anexo"`). |
| Relação da lei com ela mesma | 25 | Nos "Relacionamentos", a Câmara lista a lei como "Revoga" / "Altera" / "Revogada por" ela mesma (27 relações). | Descartadas em `relacoes`; continuam na lista crua `relacionamentos`. |
| Anotação de revogação cita a própria lei | 2 | Ex.: a Lei 9.265 diz "(REVOGADA pelo Art. 14 da Lei nº 9.265 de 8 de dezembro de 2018)": número errado na fonte. | A lei continua `revogada`, o número errado não vira relação, a anotação fica em `revogacao_nota`. O revogador correto (Lei 12.232), listado pela Câmara nos Relacionamentos, entra em `revogada_por`. |
| Revogada sem revogador identificável | 2 | Anotação quebrada na fonte (Lei 6.884: "Lei nº de de de 20") ou anotação que cita a própria lei sem outro revogador listado (Lei 6.135). | `situacao = revogada`, `revogada_por` vazio e a anotação original em `revogacao_nota`. |
| Nota de decreto lida como revogação da lei | 1 | A ementa da Lei 13.905/2024 (Uso e Ocupação do Solo) traz "(Vide Decreto nº 413...) (Revogado pelo Decreto 1.341...)": quem foi revogado é o **Decreto 413**. A versão anterior do coletor marcou a lei como revogada. | A anotação só conta se citar uma lei. `python coleta_leis.py --reprocessar leis.json` corrigiu o arquivo sem nova coleta: a lei voltou a `vigente`. |
| Ementa vazia na API | 3 | A API devolveu a ementa em branco. | Usa a "SÚMULA:" do texto quando existe (`ementa_fonte = "texto"`); senão `ementa = null`. |
| Promulgação de partes vetadas | 1 | A "Lei 13.960" aparecia duas vezes: a segunda é a promulgação, pela Câmara, dos trechos que o prefeito vetou. | `tipo = "Promulgação de partes vetadas"` e `complementa_id` apontando para a lei principal. |
| Leis diferentes com o mesmo número | 7 | Ex.: duas Leis nº 48 de 1949, duas nº 1.041 de 1965, duas nº 1.641 de 1970. | Identificador é o `id` da Câmara; `chave`/`numero` sem `UNIQUE`. |
| Lei só com PDF | 18 | A página não tem o texto em HTML, só um PDF anexado. | `texto_disponivel = false` e link do PDF em `anexos`. Ler os PDFs é um próximo passo. |
| Número inexistente | 5 | A página diz "LEI INEXISTENTE" (número vago). | `situacao = "inexistente"`; fica fora da busca. |

A lista completa, **lei por lei** (com link para a página oficial e o detalhe de cada caso), está em [`docs/PROBLEMAS_NOS_DADOS.md`](PROBLEMAS_NOS_DADOS.md) e em [`docs/leis_com_problemas.csv`](leis_com_problemas.csv). Os dois são gerados por `python relatorio_problemas.py` a partir do `leis.json`.

## Limitações conhecidas

- Sem `--texto`, as alterações são deduzidas da ementa e podem ter falsos positivos ou negativos. Com `--texto`, valem as relações oficiais da CML.
- Artigos revogados por inteiro são identificados pelo texto riscado (`revogado`). Trechos menores riscados (um inciso, um parágrafo) ficam em `texto_riscado` do artigo.
- Algumas leis revogadas ficam com `revogada_por` vazio, porque a anotação da CML tem erro de digitação. A anotação original fica em `revogacao_nota`.
- Só 3 decretos têm o texto na base. Os outros 117 citados pela Câmara aparecem como "texto ainda fora da base", com aviso na resposta. A suspensão de eficácia por decreto legislativo vira aviso, mas não muda a `situacao` da lei.
- A fonte tem erros que o script não corrige, só sinaliza: datas impossíveis (`data_lei_original`) e relações de uma lei com ela mesma (ficam só em `relacionamentos`).
- 18 leis só têm o texto em PDF anexado, que ainda não é lido (os links estão em `anexos`).
- Requisições com `curl` são bloqueadas pelo site (406 Not Acceptable). O script em Python funciona normalmente; se ele receber 406, mostra um aviso.

# Problemas encontrados nos dados das leis

Relatório gerado por `relatorio_problemas.py` a partir do `leis.json` de 2026-11-14 (SHA-256 `08c3203f4638…`).
Os problemas abaixo estão **na fonte** (site e API da Câmara). O script não corrige a fonte: ele trata cada caso e deixa registrado de onde veio cada informação.

**1.490 de 14.308 leis** têm pelo menos um problema tratado. Uma lei pode aparecer em mais de uma categoria.

## Resumo

| Problema | Leis afetadas | Como foi resolvido |
|---|---|---|
| [Redação antiga riscada no texto compilado](#texto-riscado) | 633 | Cada trecho riscado é separado: `texto` traz só a redação vigente, `texto_riscado` a antiga, e `revogado = true` quando o artigo inteiro está riscado. O chatbot usa só `texto` de artigos não revogados. |
| [Lei sem data](#sem-data) | 837 | `data_lei = null`. Nada é inventado; o `ano` (tirado do título) está sempre preenchido e pode ser usado para filtrar por período. |
| [Data impossível no texto](#data-impossivel) | 1 | A data impossível não entra em `data_lei`: fica em `data_lei_original` para revisão. O script tenta a próxima fonte (anexo); `data_lei_fonte` diz de onde veio a data usada. |
| [Relação da lei com ela mesma](#autorrelacao) | 25 | A relação é descartada em `relacoes` (usada para a vigência). A lista crua `relacionamentos` continua como veio da fonte. |
| [Anotação de revogação cita a própria lei](#anotacao-numero-errado) | 2 | A lei continua `revogada` (a anotação existe), mas o número errado não vira relação. A anotação original fica em `revogacao_nota`; o revogador correto, quando a Câmara o lista nos Relacionamentos, entra em `revogada_por`. |
| [Revogada sem lei revogadora identificável](#revogada-sem-revogador) | 2 | `situacao = revogada` e `revogada_por` vazio. A anotação original fica em `revogacao_nota` como evidência. |
| [Ementa vazia na API](#ementa-vazia) | 3 | Quando o texto traz "SÚMULA:", ela é usada (`ementa_fonte = "texto"`). Senão, `ementa = null` (`ementa_fonte = null`). |
| [Promulgação de partes vetadas com o mesmo número](#promulgacao-veto) | 1 | `tipo = "Promulgação de partes vetadas"` e `complementa_id` apontando para a lei principal. Os artigos fazem parte da lei principal e seguem a situação dela. |
| [Leis diferentes com o mesmo número](#numero-repetido) | 7 | O identificador é o `id` da Câmara (único). `chave`/`numero` não podem ser chave primária nem `UNIQUE`. |
| [Lei só com PDF (sem texto em HTML)](#so-pdf) | 18 | `texto_disponivel = false`, `artigos` vazio e o link do PDF em `anexos`. Não entra na busca por artigo; a leitura dos PDFs é um próximo passo. |
| [Número de lei inexistente](#inexistente) | 5 | `situacao = "inexistente"` e `texto_disponivel = false`. Não entra na busca. |

Só no texto riscado: **1.492 artigos revogados por inteiro** e **1.471 artigos com algum trecho riscado**.

<a id="texto-riscado"></a>
## Redação antiga riscada no texto compilado (633 leis)

**O que aconteceu:** A página da Câmara mostra o texto compilado: quando um artigo muda, a redação antiga continua lá, riscada, e a nova vem logo depois. O script antigo extraía as duas como se valessem.

**Solução:** Cada trecho riscado é separado: `texto` traz só a redação vigente, `texto_riscado` a antiga, e `revogado = true` quando o artigo inteiro está riscado. O chatbot usa só `texto` de artigos não revogados.

| Lei | id | Detalhe |
|---|---|---|
| [LEI N.º 14040, DE 04 DE DEZEMBRO DE 2025](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/262340) | 262340 | 1 com trecho riscado: Art. 3 |
| [LEI N.º 13969, DE 22 DE JULHO DE 2025](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/243400) | 243400 | 2 com trecho riscado: Art. 1, Art. 2 |
| [LEI N.º 13961, DE 15 DE JULHO DE 2025](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/242561) | 242561 | 6 artigo(s) revogado(s): Art. 1º, Art. 3º, Art. 4º, Art. 5, Art. 19, Art. 20; 1 com trecho riscado: Art. 2º |
| [LEI N.º 13960, DE 14 DE JULHO DE 2025](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/242406) | 242406 | 2 com trecho riscado: Art. 3, Art. 4 |
| [LEI N.º 13941, DE 06 DE MAIO DE 2025](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/232586) | 232586 | 3 com trecho riscado: Art. 1, Art. 9, Art. 2 |
| [LEI N.º 13905, DE 27 DE DEZEMBRO DE 2024](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/222790) | 222790 | 6 com trecho riscado: Art. 14, Art. 16, Art. 20, Art. 30, Art. 48, Art. 93 |
| [LEI ORDINÁRIA Nº 13783/2024](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/41045) | 41045 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13748/2024](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/41081) | 41081 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 13699/2023](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/41070) | 41070 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13683/2023](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/41043) | 41043 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 13659/2023](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40931) | 40931 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 13622/2023](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40968) | 40968 | 6 artigo(s) revogado(s): Art. 1º, Art. 3º, Art. 4º, Art. 5º, Art. 6º, Art. 7°; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 13581/2023](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40908) | 40908 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 13504/2022](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40807) | 40807 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13469/2022](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40781) | 40781 | 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 13442/2022](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40740) | 40740 | 2 artigo(s) revogado(s): Art. 3º, Art. 5º; 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 13419/2022](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40704) | 40704 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13405/2022](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40706) | 40706 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 13403/2022](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40727) | 40727 | 10 com trecho riscado: Art. 14, Art. 15, Art. 16, Art. 17, Art. 18, Art. 19… |
| [LEI ORDINÁRIA Nº 13354/2022](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40664) | 40664 | 1 artigo(s) revogado(s): Art. 28 |
| [LEI ORDINÁRIA Nº 13339/2022](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40719) | 40719 | 1 artigo(s) revogado(s): Art. 4º; 1 com trecho riscado: Art. 154 |
| [LEI ORDINÁRIA Nº 13289/2021](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40559) | 40559 | 1 artigo(s) revogado(s): Art. 7º |
| [LEI ORDINÁRIA Nº 13260/2021](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40721) | 40721 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 13259/2021](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40579) | 40579 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 13249/2021](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40563) | 40563 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13220/2021](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40524) | 40524 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13196/2021](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40508) | 40508 | 1 artigo(s) revogado(s): Art. 7º |
| [LEI ORDINÁRIA Nº 13191/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40473) | 40473 | 6 artigo(s) revogado(s): Art. 3º, Art. 4º, Art. 6º, Art. 7º, Art. 10, Art. 11 |
| [LEI ORDINÁRIA Nº 13143/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27543) | 27543 | 2 artigo(s) revogado(s): Art. 2º, Art. 4º |
| [LEI ORDINÁRIA Nº 13137/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27555) | 27555 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13117/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27512) | 27512 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13090/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27446) | 27446 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13074/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27293) | 27293 | 1 artigo(s) revogado(s): Art. 4º |
| [LEI ORDINÁRIA Nº 13068/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27391) | 27391 | 1 artigo(s) revogado(s): Art. 1º; 3 com trecho riscado: Art. 7º, Art. 9º, Art. 10 |
| [LEI ORDINÁRIA Nº 13055/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27236) | 27236 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 13034/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27331) | 27331 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 13015/2020](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27620) | 27620 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12993/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27179) | 27179 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12992/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27148) | 27148 | 1 artigo(s) revogado(s): Art. 10; 2 com trecho riscado: Art. 5º, Art. 12 |
| [LEI ORDINÁRIA Nº 12987/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27362) | 27362 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 12976/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27130) | 27130 | 2 artigo(s) revogado(s): Art. 4º, Art. 15º; 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 12968/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27101) | 27101 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 12955/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27044) | 27044 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 12938/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27574) | 27574 | 1 artigo(s) revogado(s): Art. 4º |
| [LEI ORDINÁRIA Nº 12914/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27530) | 27530 | 4 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 5º, Art. 6º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 12867/2019](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27478) | 27478 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 12827/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27386) | 27386 | 1 com trecho riscado: Art. 7º |
| [LEI ORDINÁRIA Nº 12817/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27369) | 27369 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12785/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27298) | 27298 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 12744/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27284) | 27284 | 4 artigo(s) revogado(s): Art. 4º, Art. 5º, Art. 8º, Art. 10; 3 com trecho riscado: Art. 5°, Art. 9º, Art. 10 |
| [LEI ORDINÁRIA Nº 12738/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27203) | 27203 | 1 artigo(s) revogado(s): Art. 38 |
| [LEI ORDINÁRIA Nº 12735/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27281) | 27281 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 12718/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27257) | 27257 | 3 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 12700/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27225) | 27225 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 12695/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27218) | 27218 | 2 com trecho riscado: Art. 7º, Art. 8º |
| [LEI ORDINÁRIA Nº 12656/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27123) | 27123 | 1 artigo(s) revogado(s): Art. 5° |
| [LEI ORDINÁRIA Nº 12652/2018](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27113) | 27113 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12625/2017](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27088) | 27088 | 2 com trecho riscado: Art. 17, Art. 19 |
| [LEI ORDINÁRIA Nº 12613/2017](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27018) | 27018 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12575/2017](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26982) | 26982 | 4 artigo(s) revogado(s): Art. 11, Art. 12, Art. 12, Art. 13; 4 com trecho riscado: Art. 8º, Art. 8º, Art. 9º, Art.15 |
| [LEI ORDINÁRIA Nº 12541/2017](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26962) | 26962 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 12527/2017](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26940) | 26940 | 1 artigo(s) revogado(s): Art. 4º |
| [LEI ORDINÁRIA Nº 12523/2017](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26891) | 26891 | 2 com trecho riscado: Art. 5º, Art. 6º |
| [LEI ORDINÁRIA Nº 12481/2016](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26900) | 26900 | 2 com trecho riscado: Art. 1º, Art. 18 |
| [LEI ORDINÁRIA Nº 12480/2016](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26878) | 26878 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 12477/2016](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26885) | 26885 | 3 artigo(s) revogado(s): Art. 1°, Art. 4°, Art.15; 3 com trecho riscado: Art.13, Art.14, Art. 16 |
| [LEI ORDINÁRIA Nº 12434/2016](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26761) | 26761 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12423/2016](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26750) | 26750 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 12422/2016](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26749) | 26749 | 3 artigo(s) revogado(s): Art. 2º, Art. 3º, Art. 4º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 12399/2016](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26697) | 26697 | 1 com trecho riscado: Art. 31 |
| [LEI ORDINÁRIA Nº 12361/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26693) | 26693 | 3 artigo(s) revogado(s): Art. 2º, Art. 8º, Art. 11; 2 com trecho riscado: Art. 1º, Art. 9º |
| [LEI ORDINÁRIA Nº 12354/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26581) | 26581 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 12348/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26668) | 26668 | 4 artigo(s) revogado(s): Art. 3º, Art. 6º, Art. 8º, Art. 11; 5 com trecho riscado: Art. 4º, Art. 5º, Art. 6º, Art. 8º, Art. 10 |
| [LEI ORDINÁRIA Nº 12344/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26664) | 26664 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12332/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26663) | 26663 | 2 com trecho riscado: Art. 4º, Art. 6º |
| [LEI ORDINÁRIA Nº 12308/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27153) | 27153 | 2 com trecho riscado: Art. 2º, Art. 271 |
| [LEI ORDINÁRIA Nº 12237/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26610) | 26610 | 2 com trecho riscado: Art. 12, Art. 13 |
| [LEI ORDINÁRIA Nº 12236/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26635) | 26635 | 5 artigo(s) revogado(s): Art. 113, Art. 115, Art. 117, Art. 200, Art. 201; 26 com trecho riscado: Art. 11, Art. 116, Art. 126, Art. 129, Art. 132, Art. 135… |
| [LEI ORDINÁRIA Nº 12233/2015](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29937) | 29937 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 12230/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27692) | 27692 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 12199/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29946) | 29946 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12194/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34642) | 34642 | 6 artigo(s) revogado(s): Art. 1º, Art. 8º, Art. 11, Art. 15, Art. 16, Art. 19; 17 com trecho riscado: Art. 1º, Art. 1º-A, Art. 1º-B, Art. 2º, Art. 3º, Art. 3º-A… |
| [LEI ORDINÁRIA Nº 12184/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34633) | 34633 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 12158/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34609) | 34609 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12149/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34603) | 34603 | 1 artigo(s) revogado(s): Art. 14; 3 com trecho riscado: Art. 3º, Art. 4º, Art. 7º |
| [LEI ORDINÁRIA Nº 12125/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34576) | 34576 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 12096/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27155) | 27155 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 12092/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27154) | 27154 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 12084/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35351) | 35351 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 12079/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27580) | 27580 | 10 artigo(s) revogado(s): Art. 9º, Art. 22, Art. 23, Art. 24, Art. 25, Art. 26…; 4 com trecho riscado: Art. 9º, Art. 11, Art. 21, Art. 30 |
| [LEI ORDINÁRIA Nº 12075/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35339) | 35339 | 2 artigo(s) revogado(s): Art. 2º, Art. 3º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 12074/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34557) | 34557 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 12037/2014](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30804) | 30804 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 11996/2013](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39279) | 39279 | 1 com trecho riscado: Art. 59-A |
| [LEI ORDINÁRIA Nº 11990/2013](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39274) | 39274 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 11902/2013](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26813) | 26813 | 3 artigo(s) revogado(s): Art. 4º, Art. 5º, Art. 6º |
| [LEI ORDINÁRIA Nº 11901/2013](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26325) | 26325 | 2 artigo(s) revogado(s): Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 11899/2013](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26830) | 26830 | 3 artigo(s) revogado(s): Art. 3º, Art. 5º, Art. 6º |
| [LEI ORDINÁRIA Nº 11885/2013](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26338) | 26338 | 1 artigo(s) revogado(s): Art. 69 |
| [LEI ORDINÁRIA Nº 11873/2013](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26360) | 26360 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 11777/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26404) | 26404 | 2 artigo(s) revogado(s): Art. 5º, Art. 17; 3 com trecho riscado: Art. 4º, Art. 5º, Art. 18 |
| [LEI ORDINÁRIA Nº 11699/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26509) | 26509 | 1 artigo(s) revogado(s): Art. 4º |
| [LEI ORDINÁRIA Nº 11672/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26342) | 26342 | 19 artigo(s) revogado(s): Art. 39, Art. 39, Art. 43, Art. 44, Art. 68, Art. 71…; 16 com trecho riscado: Art. 4º, Art. 5º, Art. 9º, Art. 10, Art. 24, Art. 33… |
| [LEI ORDINÁRIA Nº 11632/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26496) | 26496 | 1 artigo(s) revogado(s): Art. 2ºVETADO |
| [LEI ORDINÁRIA Nº 11538/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35189) | 35189 | 5 com trecho riscado: Art. 1º, Art. 2º, Art. 3º, Art. 4º, Art. 5º |
| [LEI ORDINÁRIA Nº 11535/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35215) | 35215 | 1 artigo(s) revogado(s): Art. 48; 1 com trecho riscado: Art. 71 |
| [LEI ORDINÁRIA Nº 11531/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35214) | 35214 | 2 artigo(s) revogado(s): Art. 9º, Art. 16; 3 com trecho riscado: Art. 9º, Art. 16, Art. 24 |
| [LEI ORDINÁRIA Nº 11491/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35261) | 35261 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 11471/2012](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35210) | 35210 | 17 artigo(s) revogado(s): Art. 34, Art. 43, Art. 58, Art. 66, Art. 77, Art. 82…; 7 com trecho riscado: Art. 19, Art. 21, Art. 23, Art. 44, Art. 47, Art. 65… |
| [LEI ORDINÁRIA Nº 11468/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35262) | 35262 | 28 artigo(s) revogado(s): Art. 9º, Art. 38, Art. 39, Art. 46, Art. 77, Art. 97…; 20 com trecho riscado: Art. 8º, Art. 9º, Art. 16, Art. 49, Art. 66, Art. 76… |
| [LEI ORDINÁRIA Nº 11467/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35271) | 35271 | 1 artigo(s) revogado(s): Art. 2º; 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 11445/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35248) | 35248 | 18 artigo(s) revogado(s): Art. 4º, Art. 5º, Art. 6º, Art. 7º, Art. 8º, Art. 9º…; 17 com trecho riscado: Art. 1º, Art. 6º, Art. 7º, Art. 8º, Art. 9º, Art. 10… |
| [LEI ORDINÁRIA Nº 11414/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27939) | 27939 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 11381/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28194) | 28194 | 12 artigo(s) revogado(s): Art. 199, Art. 200, Art. 201, Art. 202, Art. 203, Art. 204…; 1 com trecho riscado: Art. 209 |
| [LEI ORDINÁRIA Nº 11374/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28002) | 28002 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 11348/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27937) | 27937 | 48 artigo(s) revogado(s): Art. 1º, Art. 7º, Art. 11, Art. 15, Art. 16, Art. 17…; 57 com trecho riscado: Art. 4º, Art. 13, Art. 18, Art. 27, Art. 28, Art. 29… |
| [LEI ORDINÁRIA Nº 11317/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28110) | 28110 | 3 com trecho riscado: Art. 2º, Art. 3º, Art. 6º |
| [LEI ORDINÁRIA Nº 11315/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28063) | 28063 | 2 com trecho riscado: Art. 6º, Art. 7° |
| [LEI ORDINÁRIA Nº 11314/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28062) | 28062 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 11303/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28059) | 28059 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 11301/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28051) | 28051 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 11265/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28085) | 28085 | 1 artigo(s) revogado(s): Art. 6º |
| [LEI ORDINÁRIA Nº 11240/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28093) | 28093 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 11221/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28148) | 28148 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 11215/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28137) | 28137 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 11157/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28283) | 28283 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 11141/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28287) | 28287 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 11117/2011](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33161) | 33161 | 2 artigo(s) revogado(s): Art. 30, Art. 32; 2 com trecho riscado: Art. 9º, Art. 12 |
| [LEI ORDINÁRIA Nº 11090/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28179) | 28179 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 11081/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35162) | 35162 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 11054/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33764) | 33764 | 2 com trecho riscado: Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 10986/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39420) | 39420 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 10981/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33796) | 33796 | 49 artigo(s) revogado(s): Art. 14, Art. 29, Art. 37, Art. 49, Art. 61, Art. 66…; 16 com trecho riscado: Art. 14, Art. 30, Art. 36, Art. 37, Art. 44, Art. 61… |
| [LEI ORDINÁRIA Nº 10969/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39253) | 39253 | 10 artigo(s) revogado(s): Art. 6º, Art. 7º, Art. 9º, Art. 19, Art. 24, Art. 37…; 12 com trecho riscado: Art. 8º, Art. 11, Art. 14, Art. 15, Art. 19, Art. 26… |
| [LEI ORDINÁRIA Nº 10967/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39436) | 39436 | 7 artigo(s) revogado(s): Art. 36, Art. 37, Art. 39, Art. 40, Art. 41, Art. 45…; 6 com trecho riscado: Art. 35, Art. 38, Art. 36, Art. 38, Art. 42, Art. 40 |
| [LEI ORDINÁRIA Nº 10966/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39412) | 39412 | 8 artigo(s) revogado(s): Art. 8º, Art. 9º, Art. 17, Art. 19, Art. 20, Art. 24…; 25 com trecho riscado: Art. 2º, Art. 3º, Art. 4º, Art. 6º, Art. 6º, Art. 7º… |
| [LEI ORDINÁRIA Nº 10914/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39460) | 39460 | 3 artigo(s) revogado(s): Art. 2º, Art. 5º, Art. 6º; 3 com trecho riscado: Art. 1º, Art. 5º, Art. 7º |
| [LEI ORDINÁRIA Nº 10849/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39400) | 39400 | 5 artigo(s) revogado(s): Art. 6º, Art. 10, Art. 14, Art. 14, Art. 17; 3 com trecho riscado: Art. 7º, Art. 10, Art. 29 |
| [LEI ORDINÁRIA Nº 10842/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39489) | 39489 | 3 artigo(s) revogado(s): Art. 2º, Art. 3º, Art. 5º; 2 com trecho riscado: Art. 2°, Art. 2° |
| [LEI ORDINÁRIA Nº 10781/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32569) | 32569 | 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 10774/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32605) | 32605 | 8 artigo(s) revogado(s): Art. 9º, Art. 12, Art. 13, Art. 19, Art. 23, Art. 23-A…; 7 com trecho riscado: Art. 6º, Art. 12, Art. 13, Art. 18, Art. 19, Art. 20… |
| [LEI ORDINÁRIA Nº 10773/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32657) | 32657 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 10765/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39473) | 39473 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 10746/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39414) | 39414 | 2 com trecho riscado: Art. 3º, Art. 5º |
| [LEI ORDINÁRIA Nº 10734/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36143) | 36143 | 1 artigo(s) revogado(s): Art. 8º; 2 com trecho riscado: Art. 2º, Art. 8º |
| [LEI ORDINÁRIA Nº 10730/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28251) | 28251 | 4 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º, Art. 4º; 3 com trecho riscado: Art. 2º, Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 10715/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32534) | 32534 | 2 artigo(s) revogado(s): Art. 2º, Art. 2º; 2 com trecho riscado: Art. 1º, Art.3º |
| [LEI ORDINÁRIA Nº 10706/2009](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32519) | 32519 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 10665/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32482) | 32482 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 10660/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32503) | 32503 | 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 10659/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32485) | 32485 | 2 artigo(s) revogado(s): Art. 7º, Art. 8º |
| [LEI ORDINÁRIA Nº 10656/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28234) | 28234 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 10648/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34136) | 34136 | 3 artigo(s) revogado(s): Art. 2º, Art. 4º, Art. 6º |
| [LEI ORDINÁRIA Nº 10637/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32487) | 32487 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 10629/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28852) | 28852 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 10607/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34106) | 34106 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 10577/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34099) | 34099 | 5 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 4°, Art.6º, Art. 8º |
| [LEI ORDINÁRIA Nº 10561/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36107) | 36107 | 4 artigo(s) revogado(s): Art. 5º, Art. 13, Art. 18, Art. 19; 2 com trecho riscado: Art. 2º, Art. 13 |
| [LEI ORDINÁRIA Nº 10560/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34070) | 34070 | 7 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º, Art. 10, Art. 11, Art. 14…; 3 com trecho riscado: Art. 9º, Art. 12, Art. 15 |
| [LEI ORDINÁRIA Nº 10558/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28257) | 28257 | 1 artigo(s) revogado(s): Art. 2º; 2 com trecho riscado: Art. 6º, Art. 12 |
| [LEI ORDINÁRIA Nº 10543/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36133) | 36133 | 2 com trecho riscado: Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 10541/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36094) | 36094 | 2 com trecho riscado: Art. 10, Art. 11 |
| [LEI ORDINÁRIA Nº 10499/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36058) | 36058 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 10440/2008](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34200) | 34200 | 1 artigo(s) revogado(s): Art. 4º; 7 com trecho riscado: Art. 1º, Art. 1º, Art. 1º, Art. 1º, Art. 1º, Art. 2º-A… |
| [LEI ORDINÁRIA Nº 10433/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40753) | 40753 | 3 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 4º |
| [LEI ORDINÁRIA Nº 10427/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39714) | 39714 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 10420/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34202) | 34202 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 10419/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34501) | 34501 | 4 artigo(s) revogado(s): Art. 23, Art. 24, Art. 28, Art. 29 |
| [LEI ORDINÁRIA Nº 10418/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34201) | 34201 | 23 artigo(s) revogado(s): Art. 5º, Art. 10, Art. 13, Art. 14, Art. 17, Art. 25…; 2 com trecho riscado: Art. 1º, Art. 2° |
| [LEI ORDINÁRIA Nº 10414/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34175) | 34175 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 10392/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34185) | 34185 | 1 artigo(s) revogado(s): Art. 2º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 10388/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39976) | 39976 | 1 artigo(s) revogado(s): Art. 8º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 10381/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34152) | 34152 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 10373/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34144) | 34144 | 1 artigo(s) revogado(s): Art. 2º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 10372/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40762) | 40762 | 2 com trecho riscado: Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 10346/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34068) | 34068 | 2 com trecho riscado: Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 10323/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36191) | 36191 | 1 artigo(s) revogado(s): Art. 6º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 10315/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36180) | 36180 | 2 com trecho riscado: Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 10313/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36185) | 36185 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 10295/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36222) | 36222 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 10290/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36251) | 36251 | 1 artigo(s) revogado(s): Art. 3º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 10278/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36212) | 36212 | 6 artigo(s) revogado(s): Art. 8º, Art. 10, Art. 11, Art. 15, Art. 16, Art. 20; 7 com trecho riscado: Art. 1º, Art. 1º, Art. 4º, Art. 6º, Art. 12, Art. 16… |
| [LEI ORDINÁRIA Nº 10275/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36259) | 36259 | 4 artigo(s) revogado(s): Art. 14, Art. 17, Art. 18, Art. 21; 3 com trecho riscado: Art. 21, Art. 27, Art. 30 |
| [LEI ORDINÁRIA Nº 10272/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36228) | 36228 | 1 artigo(s) revogado(s): Art. 8º; 7 com trecho riscado: Art. 1º, Art. 2º, Art. 3º, Art. 4º, Art. 5º, Art. 6º… |
| [LEI ORDINÁRIA Nº 10249/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36350) | 36350 | 1 artigo(s) revogado(s): Art. 4°; 3 com trecho riscado: Art. 4º, Art. 5°, Art. 6° |
| [LEI ORDINÁRIA Nº 10247/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36354) | 36354 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 10214/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39686) | 39686 | 9 com trecho riscado: Art. 6º, Art. 7º, Art. 8º, Art. 9º, Art. 10, Art. 11… |
| [LEI ORDINÁRIA Nº 10185/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39649) | 39649 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 10184/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39648) | 39648 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 10147/2007](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39621) | 39621 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 9954/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34433) | 34433 | 2 artigo(s) revogado(s): Art. 2º, Art. 3º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 9945/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36193) | 36193 | 2 com trecho riscado: Art.10, Art. 11 |
| [LEI ORDINÁRIA Nº 9934/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34343) | 34343 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 10130/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29882) | 29882 | 1 artigo(s) revogado(s): Art. 9º; 2 com trecho riscado: Art. 4º, Art. 9º |
| [LEI ORDINÁRIA Nº 10128/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29899) | 29899 | 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 10117/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29370) | 29370 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 10113/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29889) | 29889 | 1 artigo(s) revogado(s): Art. 3º; 4 com trecho riscado: Art. 4º, Art. 5º, Art. 6º, Art. 7º |
| [LEI ORDINÁRIA Nº 10098/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29903) | 29903 | 2 artigo(s) revogado(s): Art. 2º, Art. 3º; 4 com trecho riscado: Art. 1º, Art. 6º, Art. 12, Art. 13 |
| [LEI ORDINÁRIA Nº 10084/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29917) | 29917 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 10073/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29728) | 29728 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 10050/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29805) | 29805 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 10019/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29824) | 29824 | 4 com trecho riscado: Art. 4º, Art. 5º, Art. 6º, Art. 7º |
| [LEI ORDINÁRIA Nº 10004/2006](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32191) | 32191 | 1 artigo(s) revogado(s): Art. 2º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 9879/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29809) | 29809 | 2 artigo(s) revogado(s): Art. 4°, Art. 5°; 1 com trecho riscado: Art. 19 |
| [LEI ORDINÁRIA Nº 9873/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34233) | 34233 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 9869/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34224) | 34224 | 2 artigo(s) revogado(s): Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 9866/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34208) | 34208 | 5 artigo(s) revogado(s): Art. 6º, Art. 6º, Art. 17, Art. 17, Art. 17; 12 com trecho riscado: Art. 1º, Art. 2º, Art. 3º, Art. 4º, Art. 5º, Art. 10… |
| [LEI ORDINÁRIA Nº 9864/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34223) | 34223 | 33 artigo(s) revogado(s): Art. 2º, Art. 6º, Art. 11, Art. 16, Art. 17, Art. 20…; 17 com trecho riscado: Art. 1º, Art. 5º, Art. 9º, Art. 11, Art. 17, Art. 29… |
| [LEI ORDINÁRIA Nº 9837/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29839) | 29839 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9831/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29855) | 29855 | 1 artigo(s) revogado(s): Art. 3º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 9810/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29943) | 29943 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 9749/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34386) | 34386 | 4 artigo(s) revogado(s): Art. 6º, Art. 8º, Art. 9º, Art. 10; 2 com trecho riscado: Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 9704/2005](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29722) | 29722 | 1 artigo(s) revogado(s): Art. 9º |
| [LEI ORDINÁRIA Nº 9699/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29732) | 29732 | 6 com trecho riscado: Art. 3º, Art. 4º, Art. 5º, Art. 6º, Art. 7º, Art. 8º |
| [LEI ORDINÁRIA Nº 9684/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29738) | 29738 | 5 com trecho riscado: Art. 3º, Art. 4º, Art. 5º, Art. 6º, Art. 7º |
| [LEI ORDINÁRIA Nº 9679/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29747) | 29747 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9678/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29737) | 29737 | 5 artigo(s) revogado(s): Art. 14, Art. 16, Art. 22, Art. 26, Art. 32; 55 com trecho riscado: Art. 21, Art. 22, Art. 23, Art. 24, Art. 25, Art. 26… |
| [LEI ORDINÁRIA Nº 9676/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29745) | 29745 | 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 9637/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36176) | 36176 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9625/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36165) | 36165 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9538/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36322) | 36322 | 1 artigo(s) revogado(s): Art. 11; 1 com trecho riscado: Art. 11 |
| [LEI ORDINÁRIA Nº 9536/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33801) | 33801 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 9516/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36304) | 36304 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 9478/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36332) | 36332 | 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 9461/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36318) | 36318 | 1 artigo(s) revogado(s): Art. 4º |
| [LEI ORDINÁRIA Nº 9446/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33844) | 33844 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 9414/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36065) | 36065 | 1 com trecho riscado: Art. 28 |
| [LEI ORDINÁRIA Nº 9406/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27656) | 27656 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 9337/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32766) | 32766 | 16 artigo(s) revogado(s): Art. 1º, Art. 9º, Art. 10, Art. 11, Art. 13, Art. 14…; 54 com trecho riscado: Art. 5º, Art. 7º, Art. 8º, Art. 8º, Art. 8º, Art. 8º… |
| [LEI ORDINÁRIA Nº 9334/2004](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29616) | 29616 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 9294/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32715) | 32715 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 9293/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32589) | 32589 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9291/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32540) | 32540 | 10 artigo(s) revogado(s): Art. 5º, Art. 6º, Art. 6º, Art. 6º-A, Art. 7º, Art. 10…; 6 com trecho riscado: Art. 5º, Art. 6º, Art. 6º-A, Art. 8º, Art. 9º, Art. 16 |
| [LEI ORDINÁRIA Nº 9245/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32831) | 32831 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 9243/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32825) | 32825 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9237/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32818) | 32818 | 3 artigo(s) revogado(s): Art. 1º, Art. 3º, Art. 3º |
| [LEI ORDINÁRIA Nº 9215/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32798) | 32798 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9188/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32951) | 32951 | 2 artigo(s) revogado(s): Art. 4º-A, Art. 4º-B; 5 com trecho riscado: Art. 1º, Art. 2°, Art. 3°, Art. 4°, Art. 4º-C |
| [LEI ORDINÁRIA Nº 9153/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32938) | 32938 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9141/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32877) | 32877 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9111/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33056) | 33056 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9101/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33041) | 33041 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 9084/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33013) | 33013 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 9057/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32979) | 32979 | 2 artigo(s) revogado(s): Art. 1º, Art. 2º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 9021/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33093) | 33093 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 9013/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33116) | 33116 | 6 com trecho riscado: Art. 4º, Art. 6º, Art. 7º, Art. 8º, Art. 9º, Art. 10 |
| [LEI ORDINÁRIA Nº 9012/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33147) | 33147 | 1 artigo(s) revogado(s): Art. 9º |
| [LEI ORDINÁRIA Nº 8985/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33297) | 33297 | 4 com trecho riscado: Art. 3º, Art. 7º, Art. 9º, Art. 11 |
| [LEI ORDINÁRIA Nº 8955/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33221) | 33221 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 8924/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33435) | 33435 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 8888/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33365) | 33365 | 1 artigo(s) revogado(s): Art. 10 |
| [LEI ORDINÁRIA Nº 8871/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33352) | 33352 | 4 artigo(s) revogado(s): Art. 3º, Art. 4º, Art. 8º, Art. 14 |
| [LEI ORDINÁRIA Nº 8834/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33555) | 33555 | 4 artigo(s) revogado(s): Art. 7º, Art. 17, Art. 21, Art. 23; 21 com trecho riscado: Art. 4º, Art. 5º, Art. 6º, Art. 7º, Art. 8º, Art. 9°… |
| [LEI ORDINÁRIA Nº 8822/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31961) | 31961 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 8815/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33539) | 33539 | 5 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º, Art. 5º, Art. 7º |
| [LEI ORDINÁRIA Nº 8802/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33326) | 33326 | 3 artigo(s) revogado(s): Art. 2º, Art. 3º, Art. 3º |
| [LEI ORDINÁRIA Nº 8798/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33487) | 33487 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 8786/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33467) | 33467 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 8730/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33605) | 33605 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 8709/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33575) | 33575 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 8693/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29478) | 29478 | 15 artigo(s) revogado(s): Art. 2º, Art. 3º, Art. 5º, Art. 6°, Art. 7°, Art. 8°…; 4 com trecho riscado: Art. 4º, Art. 5º, Art. 6°, Art. 15 |
| [LEI ORDINÁRIA Nº 8684/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29459) | 29459 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 8674/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33697) | 33697 | 2 artigo(s) revogado(s): Art. 2º, Art. 5º |
| [LEI ORDINÁRIA Nº 8673/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33713) | 33713 | 5 com trecho riscado: Art. 1º, Art. 1º, Art. 2º, Art. 2º, Art. 2º-A |
| [LEI ORDINÁRIA Nº 8672/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29519) | 29519 | 2 artigo(s) revogado(s): Art. 9º, Art. 10; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 8554/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29472) | 29472 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 8539/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29240) | 29240 | 2 com trecho riscado: Art. 4º, Art. 5º |
| [LEI ORDINÁRIA Nº 8462/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29322) | 29322 | 1 artigo(s) revogado(s): Art. 1º; 3 com trecho riscado: Art. 7º, Art. 15, Art. 16 |
| [LEI ORDINÁRIA Nº 8370/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29017) | 29017 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 8369/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29003) | 29003 | 2 artigo(s) revogado(s): Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 8312/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28067) | 28067 | 3 artigo(s) revogado(s): Art. 36, Art. 2º, Art. 37; 2 com trecho riscado: Art. 1º, Art. 4º |
| [LEI ORDINÁRIA Nº 8305/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29091) | 29091 | 2 artigo(s) revogado(s): Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 8294/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28919) | 28919 | 3 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 5°; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 8233/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28990) | 28990 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 8223/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28997) | 28997 | 2 artigo(s) revogado(s): Art. 2º, Art. 8º |
| [LEI ORDINÁRIA Nº 8196/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28826) | 28826 | 4 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 4º, Art. 6º |
| [LEI ORDINÁRIA Nº 8143/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28674) | 28674 | 2 artigo(s) revogado(s): Art. 15, Art. 15; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 8137/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28545) | 28545 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 8136/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27793) | 27793 | 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 8086/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28712) | 28712 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 8078/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28863) | 28863 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 8064/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27695) | 27695 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 8035/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28623) | 28623 | 3 artigo(s) revogado(s): Art. 1º, Art. 3º, Art. 11; 2 com trecho riscado: Art. 1º, Art. 1º |
| [LEI ORDINÁRIA Nº 8033/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28581) | 28581 | 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 8030/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28729) | 28729 | 2 com trecho riscado: Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 8023/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28608) | 28608 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7999/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28583) | 28583 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 7955/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28417) | 28417 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7941/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28457) | 28457 | 2 artigo(s) revogado(s): Art. 2º, Art. 3º; 1 com trecho riscado: Art. 9º |
| [LEI ORDINÁRIA Nº 7921/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28476) | 28476 | 3 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 7916/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28498) | 28498 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 7898/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35085) | 35085 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7842/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35108) | 35108 | 4 artigo(s) revogado(s): Art. 2º, Art. 3º, Art. 4º, Art. 6º |
| [LEI ORDINÁRIA Nº 7841/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35105) | 35105 | 3 com trecho riscado: Art. 3º, Art. 5º, Art. 6º |
| [LEI ORDINÁRIA Nº 7780/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28406) | 28406 | 1 artigo(s) revogado(s): Art. 3º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7759/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34988) | 34988 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7756/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34981) | 34981 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º; 3 com trecho riscado: Art. 1º, Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 7744/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34720) | 34720 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7705/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35052) | 35052 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7656/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34876) | 34876 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 7647/1999](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34893) | 34893 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7631/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34891) | 34891 | 2 artigo(s) revogado(s): Art. 6º, Art. 7º; 3 com trecho riscado: Art. 3º, Art. 8º-B, Art. 8º-C |
| [LEI ORDINÁRIA Nº 7630/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34858) | 34858 | 1 artigo(s) revogado(s): Art. 8º |
| [LEI ORDINÁRIA Nº 7629/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27678) | 27678 | 1 artigo(s) revogado(s): Art. 4º; 9 com trecho riscado: Art. 1º, Art. 2º, Art. 3º, Art. 4º, Art. 5º, Art. 6º… |
| [LEI ORDINÁRIA Nº 7614/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31586) | 31586 | 2 artigo(s) revogado(s): Art. 1º, Art. 5º |
| [LEI ORDINÁRIA Nº 7596/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33889) | 33889 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7594/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33903) | 33903 | 2 artigo(s) revogado(s): Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 7586/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33910) | 33910 | 4 artigo(s) revogado(s): Art. 1º, Art. 5º, Art. 6º, Art. 8º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 7582/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33929) | 33929 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7562/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33930) | 33930 | 2 artigo(s) revogado(s): Art. 3º, Art. 3º |
| [LEI ORDINÁRIA Nº 7486/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34000) | 34000 | 3 com trecho riscado: Art. 5º, Art. 9º, Art. 10 |
| [LEI ORDINÁRIA Nº 7485/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33936) | 33936 | 8 artigo(s) revogado(s): Art. 29, Art. 36, Art. 37, Art. 47, Art. 65, Art. 70…; 13 com trecho riscado: Art. 4º, Art. 14, Art. 15, Art. 16, Art. 25, Art. 27… |
| [LEI ORDINÁRIA Nº 7483/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34001) | 34001 | 2 artigo(s) revogado(s): Art. 43, Art. 56; 2 com trecho riscado: Art. 9º, Art. 55 |
| [LEI ORDINÁRIA Nº 7482/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34048) | 34048 | 3 artigo(s) revogado(s): Art. 16, Art. 21, Art. 22; 4 com trecho riscado: Art. 19, Art. 21, Art. 22, Art. 22 |
| [LEI ORDINÁRIA Nº 7476/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39560) | 39560 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7443/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39590) | 39590 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7439/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39570) | 39570 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7434/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39607) | 39607 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 7431/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39578) | 39578 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 7423/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39596) | 39596 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7397/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39717) | 39717 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7396/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39726) | 39726 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7392/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39740) | 39740 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7373/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39744) | 39744 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 7352/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39779) | 39779 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 7350/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39804) | 39804 | 4 artigo(s) revogado(s): Art. 1º, Art. 12, Art. 15, Art. 17 |
| [LEI ORDINÁRIA Nº 7349/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39783) | 39783 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7347/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39778) | 39778 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7333/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39775) | 39775 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7322/1998](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39797) | 39797 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 7303/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39849) | 39849 | 81 artigo(s) revogado(s): Art. 63, Art. 68, Art. 97, Art. 107, Art. 107, Art. 110…; 65 com trecho riscado: Art. 14, Art. 16, Art. 20, Art. 39, Art. 71, Art. 94… |
| [LEI ORDINÁRIA Nº 7302/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39785) | 39785 | 9 com trecho riscado: Art. 1º, Art. 2º, Art. 12, Art. 13, Art. 14, Art. 15… |
| [LEI ORDINÁRIA Nº 7301/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39786) | 39786 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 7299/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39848) | 39848 | 1 artigo(s) revogado(s): Art. 9º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 7292/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39839) | 39839 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 7279/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39855) | 39855 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 7176/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39833) | 39833 | 6 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º, Art. 3º, Art. 4º, Art. 5º; 2 com trecho riscado: Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 7169/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39969) | 39969 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 7133/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39980) | 39980 | 2 artigo(s) revogado(s): Art. 2°, Art. 2° |
| [LEI ORDINÁRIA Nº 7122/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39991) | 39991 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 7118/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40037) | 40037 | 2 artigo(s) revogado(s): Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 7110/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40048) | 40048 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6994/1997](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39789) | 39789 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6935/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40257) | 40257 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6858/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26210) | 26210 | 3 artigo(s) revogado(s): Art. 4º, Art. 10, Art. 32 |
| [LEI ORDINÁRIA Nº 6831/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40347) | 40347 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6819/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40330) | 40330 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6809/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40326) | 40326 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6793/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40346) | 40346 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 6706/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40455) | 40455 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6697/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40424) | 40424 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6685/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40459) | 40459 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6680/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30178) | 30178 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 6666/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26156) | 26156 | 2 artigo(s) revogado(s): Art. 5º, Art. 6º |
| [LEI ORDINÁRIA Nº 6643/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38595) | 38595 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6628/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40146) | 40146 | 1 artigo(s) revogado(s): Art. 4º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 6554/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26236) | 26236 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 6552/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26289) | 26289 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 6542/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34269) | 34269 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6531/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26274) | 26274 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6521/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26309) | 26309 | 1 artigo(s) revogado(s): Art. 9º; 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 6512/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26316) | 26316 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6511/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26315) | 26315 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6465/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35984) | 35984 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6437/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35979) | 35979 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6436/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35975) | 35975 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6420/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35495) | 35495 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 6387/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35534) | 35534 | 1 artigo(s) revogado(s): Art. 3º; 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 6370/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35438) | 35438 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 6369/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35448) | 35448 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 6361/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35437) | 35437 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 6325/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35642) | 35642 | 3 artigo(s) revogado(s): Art. 1º, Art. 6º, Art. 7º |
| [LEI ORDINÁRIA Nº 6315/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35503) | 35503 | 16 com trecho riscado: Art. 1º, Art. 1º, Art. 2º, Art. 2º, Art. 2º, Art. 3º… |
| [LEI ORDINÁRIA Nº 6309/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35467) | 35467 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 6277/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34978) | 34978 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 6235/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35535) | 35535 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 6221/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35740) | 35740 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6196/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35580) | 35580 | 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 6168/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35741) | 35741 | 5 artigo(s) revogado(s): Art. 2º, Art. 2º, Art. 3º, Art. 3º, Art. 3º; 1 com trecho riscado: Art. 6º |
| [LEI ORDINÁRIA Nº 6151/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35662) | 35662 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6120/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35781) | 35781 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6106/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35656) | 35656 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 6105/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35802) | 35802 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 6090/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35743) | 35743 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6021/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35759) | 35759 | 1 com trecho riscado: Art. 18 |
| [LEI ORDINÁRIA Nº 6017/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35749) | 35749 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6009/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35772) | 35772 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 6007/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35773) | 35773 | 12 artigo(s) revogado(s): Art. 2º, Art. 3º, Art. 4º, Art. 6º, Art. 6º, Art. 7º…; 2 com trecho riscado: Art. 5º, Art. 12 |
| [LEI ORDINÁRIA Nº 6001/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35823) | 35823 | 1 artigo(s) revogado(s): Art. 3º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 5981/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35839) | 35839 | 2 com trecho riscado: Art. 1º, Art. 1º |
| [LEI ORDINÁRIA Nº 5971/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35852) | 35852 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 5937/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35890) | 35890 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 5932/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36009) | 36009 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 5913/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30593) | 30593 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 5906/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30635) | 30635 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 5874/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30661) | 30661 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 5836/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30044) | 30044 | 4 artigo(s) revogado(s): Art. 6º, Art. 23, Art. 37, Art. 38 |
| [LEI ORDINÁRIA Nº 5834/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30026) | 30026 | 2 artigo(s) revogado(s): Art. 14, Art. 38; 2 com trecho riscado: Art. 5º, Art. 6º |
| [LEI ORDINÁRIA Nº 5833/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30041) | 30041 | 5 artigo(s) revogado(s): Art. 6º, Art. 7º, Art. 23, Art. 37, Art. 38; 3 com trecho riscado: Art. 4º, Art. 5º, Art. 11 |
| [LEI ORDINÁRIA Nº 5832/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30040) | 30040 | 13 artigo(s) revogado(s): Art. 9°, Art. 10, Art. 12, Art. 28, Art. 29, Art. 30…; 5 com trecho riscado: Art. 5º, Art. 8º, Art. 20, Art. 44, Art. 68 |
| [LEI ORDINÁRIA Nº 5761/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30085) | 30085 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 5696/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30493) | 30493 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 5684/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30584) | 30584 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 5669/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30521) | 30521 | 5 artigo(s) revogado(s): Art. 19, Art. 20, Art. 22, Art. 29, Art. 41; 9 com trecho riscado: Art. 1º, Art. 3º, Art. 17, Art. 18, Art. 24, Art. 41… |
| [LEI ORDINÁRIA Nº 5500/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30331) | 30331 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 5497/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30334) | 30334 | 5 artigo(s) revogado(s): Art. 2º, Art. 2º, Art. 6º, Art. 10, Art. 10; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 5496/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29685) | 29685 | 3 artigo(s) revogado(s): Art. 5º, Art. 9º, Art. 51; 13 com trecho riscado: Art. 5º, Art. 9º, Art. 13, Art. 36, Art. 36, Art. 36… |
| [LEI ORDINÁRIA Nº 5387/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30273) | 30273 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 5316/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27863) | 27863 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 5314/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32690) | 32690 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 5313/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27828) | 27828 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º; 2 com trecho riscado: Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 5305/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28120) | 28120 | 2 artigo(s) revogado(s): Art. 2º, Art. 3º; 2 com trecho riscado: Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 5268/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27886) | 27886 | 57 artigo(s) revogado(s): Art. 5º, Art. 8º, Art. 15, Art. 16, Art. 17, Art. 18…; 60 com trecho riscado: Art. 5º, Art. 8º, Art. 9º, Art. 10, Art. 11, Art. 14… |
| [LEI ORDINÁRIA Nº 5257/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27893) | 27893 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 5254/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27891) | 27891 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 5252/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27898) | 27898 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 5241/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27900) | 27900 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 5237/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27899) | 27899 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 5232/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27911) | 27911 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 5131/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27710) | 27710 | 1 artigo(s) revogado(s): Art. 42 |
| [LEI ORDINÁRIA Nº 5127/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32747) | 32747 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 5118/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27804) | 27804 | 1 com trecho riscado: Art. 43 |
| [LEI ORDINÁRIA Nº 5117/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34488) | 34488 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 5067/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34731) | 34731 | 1 artigo(s) revogado(s): Art. 2º; 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 5003/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36399) | 36399 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4935/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32401) | 32401 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 4928/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27817) | 27817 | 140 artigo(s) revogado(s): Art. 4º, Art. 9º, Art. 16, Art. 37, Art. 38, Art. 41…; 117 com trecho riscado: Art. 8º, Art. 13, Art. 24, Art. 38, Art. 42, Art. 51… |
| [LEI ORDINÁRIA Nº 4912/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34486) | 34486 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 4911/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33081) | 33081 | 9 artigo(s) revogado(s): Art. 2º, Art. 2º, Art. 3º, Art. 3º, Art. 4º, Art. 5º…; 2 com trecho riscado: Art. 5º, Art. 10 |
| [LEI ORDINÁRIA Nº 4907/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29808) | 29808 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 4878/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36512) | 36512 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 4874/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34974) | 34974 | 1 artigo(s) revogado(s): Art. 4º |
| [LEI ORDINÁRIA Nº 4871/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34885) | 34885 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4865/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31508) | 31508 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 4861/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32820) | 32820 | 2 artigo(s) revogado(s): Art. 7º, Art. 25; 4 com trecho riscado: Art. 1º, Art. 5º, Art. 31, Art. 32 |
| [LEI ORDINÁRIA Nº 4853/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36503) | 36503 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4846/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36523) | 36523 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 4840/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36522) | 36522 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 4835/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30905) | 30905 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4822/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36461) | 36461 | 1 com trecho riscado: Art. 18 |
| [LEI ORDINÁRIA Nº 4818/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32659) | 32659 | 1 artigo(s) revogado(s): Art. 4º; 2 com trecho riscado: Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 4809/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33064) | 33064 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 4806/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27979) | 27979 | 3 artigo(s) revogado(s): Art. 6º, Art. 17, Art. 18; 2 com trecho riscado: Art. 5º, Art. 18 |
| [LEI ORDINÁRIA Nº 4742/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27662) | 27662 | 2 artigo(s) revogado(s): Art. 23, Art. 24; 1 com trecho riscado: Art. 17 |
| [LEI ORDINÁRIA Nº 4644/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30814) | 30814 | 1 artigo(s) revogado(s): Art. 5º; 3 com trecho riscado: Art. 1º, Art. 4º, Art. 4º |
| [LEI ORDINÁRIA Nº 4632/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29807) | 29807 | 6 artigo(s) revogado(s): Art. 1º, Art. 4º, Art. 5º, Art. 8º, Art. 10, Art. 11 |
| [LEI ORDINÁRIA Nº 4607/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27696) | 27696 | 28 artigo(s) revogado(s): Art. 4º, Art. 5º, Art. 24, Art. 26, Art. 34, Art. 46…; 31 com trecho riscado: Art. 4º, Art. 18, Art. 24, Art. 26, Art. 34, Art. 34… |
| [LEI ORDINÁRIA Nº 4536/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31081) | 31081 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 4508/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28075) | 28075 | 1 artigo(s) revogado(s): Art. 3º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 4501/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30958) | 30958 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4471/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30973) | 30973 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4450/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30954) | 30954 | 1 com trecho riscado: Art. 6º |
| [LEI ORDINÁRIA Nº 4410/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27965) | 27965 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 4406/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30886) | 30886 | 2 artigo(s) revogado(s): Art. 1º, Art. 2º; 3 com trecho riscado: Art. 1º, Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 4405/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31265) | 31265 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 4395/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31255) | 31255 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4382/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31225) | 31225 | 1 com trecho riscado: Art. 25 |
| [LEI ORDINÁRIA Nº 4377/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31229) | 31229 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 4369/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31217) | 31217 | 2 artigo(s) revogado(s): Art. 2º, Art. 4º; 2 com trecho riscado: Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 4363/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31215) | 31215 | 2 artigo(s) revogado(s): Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 4336/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31212) | 31212 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 4331/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31173) | 31173 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4313/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31154) | 31154 | 1 artigo(s) revogado(s): Art. 2º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 4253/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31109) | 31109 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4248/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31100) | 31100 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 4202/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36478) | 36478 | 1 artigo(s) revogado(s): Art. 8º; 2 com trecho riscado: Art. 7º, Art. 8º |
| [LEI ORDINÁRIA Nº 4197/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31665) | 31665 | 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 4195/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36603) | 36603 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 4193/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36685) | 36685 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 4186/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28090) | 28090 | 1 com trecho riscado: Art. 10 |
| [LEI ORDINÁRIA Nº 4184/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31382) | 31382 | 1 artigo(s) revogado(s): Art. 7º; 1 com trecho riscado: Art. 9º |
| [LEI ORDINÁRIA Nº 4169/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31343) | 31343 | 1 artigo(s) revogado(s): Art. 3º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 4162/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31288) | 31288 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 4156/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31275) | 31275 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 4120/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36646) | 36646 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 4113/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34692) | 34692 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 4055/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36662) | 36662 | 3 artigo(s) revogado(s): Art. 1º, Art. 5º, Art. 6º |
| [LEI ORDINÁRIA Nº 4048/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28390) | 28390 | 4 artigo(s) revogado(s): Art. 12, Art. 19, Art. 21, Art. 25; 1 com trecho riscado: Art. 14 |
| [LEI ORDINÁRIA Nº 4040/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28494) | 28494 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 4021/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28327) | 28327 | 1 artigo(s) revogado(s): Art. 7º; 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 4011/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29202) | 29202 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3981/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31357) | 31357 | 3 artigo(s) revogado(s): Art. 16, Art. 19, Art. 21 |
| [LEI ORDINÁRIA Nº 3979/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31345) | 31345 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 3964/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31373) | 31373 | 6 artigo(s) revogado(s): Art. 7º, Art. 9º, Art. 29, Art. 119, Art. 137, Art. 195; 8 com trecho riscado: Art. 3º, Art. 7º, Art. 9º, Art. 18, Art. 63, Art. 85… |
| [LEI ORDINÁRIA Nº 3951/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31314) | 31314 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 3948/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31336) | 31336 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 3941/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30851) | 30851 | 5 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º, Art. 4º, Art. 6; 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 3940/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30649) | 30649 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3937/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31461) | 31461 | 1 artigo(s) revogado(s): Art. 5º; 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 3924/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31395) | 31395 | 2 artigo(s) revogado(s): Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 3917/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36766) | 36766 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3911/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36713) | 36713 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3878/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36678) | 36678 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3875/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28459) | 28459 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 3872/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31446) | 31446 | 1 artigo(s) revogado(s): Art. 18; 3 com trecho riscado: Art. 6º, Art. 15, Art. 18 |
| [LEI ORDINÁRIA Nº 3855/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31406) | 31406 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3854/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31393) | 31393 | 3 artigo(s) revogado(s): Art. 1º, Art. 5º, Art. 8º |
| [LEI ORDINÁRIA Nº 3846/1985](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35985) | 35985 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3840/1985](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36786) | 36786 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3785/1985](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36783) | 36783 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3767/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36781) | 36781 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3749/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36721) | 36721 | 1 artigo(s) revogado(s): Art. 8º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 3742/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36808) | 36808 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3736/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36677) | 36677 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3707/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36790) | 36790 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 3706/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27511) | 27511 | 1 artigo(s) revogado(s): Art. 44; 11 com trecho riscado: Art. 2º, Art. 16, Art. 17, Art. 18, Art. 22, Art. 30… |
| [LEI ORDINÁRIA Nº 3645/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31574) | 31574 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3630/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26181) | 26181 | 1 artigo(s) revogado(s): Art. 8º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 3629/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26207) | 26207 | 21 artigo(s) revogado(s): Art. 20, Art. 21, Art. 26, Art. 27, Art. 41, Art. 42…; 28 com trecho riscado: Art. 5º, Art. 7º, Art. 13, Art. 14, Art. 16, Art. 19… |
| [LEI ORDINÁRIA Nº 3627/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36840) | 36840 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3612/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36833) | 36833 | 2 com trecho riscado: Art. 1º, Art. 5º |
| [LEI ORDINÁRIA Nº 3610/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36830) | 36830 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3608/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31570) | 31570 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3573/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31483) | 31483 | 2 artigo(s) revogado(s): Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 3548/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31594) | 31594 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3510/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36874) | 36874 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3489/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28246) | 28246 | 1 com trecho riscado: Art. 8º |
| [LEI ORDINÁRIA Nº 3483/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36897) | 36897 | 4 artigo(s) revogado(s): Art. 8º, Art. 9º, Art. 11, Art. 20 |
| [LEI ORDINÁRIA Nº 3478/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36842) | 36842 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 3475/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36814) | 36814 | 1 artigo(s) revogado(s): Art. 2º; 1 com trecho riscado: Art. 14 |
| [LEI ORDINÁRIA Nº 3474/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36829) | 36829 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3445/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36847) | 36847 | 4 com trecho riscado: Art. 2º, Art. 3º, Art. 4º, Art. 5º |
| [LEI ORDINÁRIA Nº 3410/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31544) | 31544 | 3 artigo(s) revogado(s): Art. 2º, Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 3395/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32780) | 32780 | 2 com trecho riscado: Art. 4º, Art. 8º |
| [LEI ORDINÁRIA Nº 3380/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29960) | 29960 | 2 com trecho riscado: Art. 2º, Art. 6º |
| [LEI ORDINÁRIA Nº 3358/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36993) | 36993 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3354/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36954) | 36954 | 3 com trecho riscado: Art. 2º, Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 3345/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36972) | 36972 | 5 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º, Art. 4º, Art. 7º |
| [LEI ORDINÁRIA Nº 3341/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36730) | 36730 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3335/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36948) | 36948 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3325/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36958) | 36958 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3320/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36910) | 36910 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3318/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36933) | 36933 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3310/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36923) | 36923 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3295/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31590) | 31590 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 3243/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37063) | 37063 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 3237/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36991) | 36991 | 13 artigo(s) revogado(s): Art. 107, Art. 108, Art. 109, Art. 110, Art. 111, Art. 112…; 4 com trecho riscado: Art. 87, Art. 109, Art. 114, Art. 117 |
| [LEI ORDINÁRIA Nº 3223/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33541) | 33541 | 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 3222/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37014) | 37014 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3202/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31687) | 31687 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3188/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35640) | 35640 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 3166/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31670) | 31670 | 3 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º |
| [LEI ORDINÁRIA Nº 3143/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34951) | 34951 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 3142/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33400) | 33400 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3139/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34927) | 34927 | 3 artigo(s) revogado(s): Art. 3º, Art. 4º, Art. 5º |
| [LEI ORDINÁRIA Nº 3118/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31784) | 31784 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3117/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28482) | 28482 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3116/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31783) | 31783 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 3112/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28145) | 28145 | 4 com trecho riscado: Art. 5º, Art. 6º, Art. 7º, Art. 8º |
| [LEI ORDINÁRIA Nº 3103/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31732) | 31732 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 3079/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31739) | 31739 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 2988/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37080) | 37080 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 2983/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37055) | 37055 | 2 artigo(s) revogado(s): Art. 1º, Art. 10; 1 com trecho riscado: Art. 11 |
| [LEI ORDINÁRIA Nº 2982/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37083) | 37083 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 2930/1978](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39134) | 39134 | 1 com trecho riscado: Art. 9º |
| [LEI ORDINÁRIA Nº 2864/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39128) | 39128 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 2857/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39044) | 39044 | 25 artigo(s) revogado(s): Art. 77, Art. 78, Art. 79, Art. 80, Art. 81, Art. 82…; 6 com trecho riscado: Art. 31, Art. 64, Art. 127, Art. 136, Art. 153, Art. 161 |
| [LEI ORDINÁRIA Nº 2837/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29984) | 29984 | 6 artigo(s) revogado(s): Art. 5º, Art. 6º, Art. 8º, Art. 23, Art. 24, Art. 30; 10 com trecho riscado: Art. 2º, Art. 2º, Art. 6º, Art. 7º, Art. 13, Art. 24… |
| [LEI ORDINÁRIA Nº 2836/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39107) | 39107 | 1 com trecho riscado: Art. 8º |
| [LEI ORDINÁRIA Nº 2827/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39101) | 39101 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 2813/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39092) | 39092 | 1 artigo(s) revogado(s): Art. 4º; 1 com trecho riscado: Art. 4º |
| [LEI ORDINÁRIA Nº 2782/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28775) | 28775 | 3 artigo(s) revogado(s): Art. 2º, Art. 2º, Art. 3º; 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 2776/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39041) | 39041 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 2763/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39019) | 39019 | 8 artigo(s) revogado(s): Art. 9º, Art. 10, Art. 11, Art. 12, Art. 13, Art. 14…; 8 com trecho riscado: Art. 9º, Art. 10, Art. 10, Art. 12, Art. 13, Art. 15… |
| [LEI ORDINÁRIA Nº 2749/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39016) | 39016 | 4 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 4º, Art. 5º |
| [LEI ORDINÁRIA Nº 2731/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38942) | 38942 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 2706/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38956) | 38956 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 2692/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38932) | 38932 | 14 artigo(s) revogado(s): Art. 66, Art. 86, Art. 89, Art. 114, Art. 183, Art. 187…; 24 com trecho riscado: Art. 40, Art. 74, Art. 86, Art. 112, Art. 113, Art. 116… |
| [LEI ORDINÁRIA Nº 2682/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38934) | 38934 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 2670/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38926) | 38926 | 13 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º, Art. 7º, Art. 8º, Art. 2º… |
| [LEI ORDINÁRIA Nº 2653/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38891) | 38891 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 2608/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38890) | 38890 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 2594/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38872) | 38872 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 2576/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38849) | 38849 | 2 artigo(s) revogado(s): Art. 37, Art. 180; 10 com trecho riscado: Art. 37, Art. 37, Art. 82, Art. 136, Art. 143, Art. 177… |
| [LEI ORDINÁRIA Nº 2568/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38847) | 38847 | 1 com trecho riscado: Art. 6º |
| [LEI ORDINÁRIA Nº 2536/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38818) | 38818 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 2534/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38808) | 38808 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 2518/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38760) | 38760 | 1 artigo(s) revogado(s): Art. 40; 6 com trecho riscado: Art. 8º, Art. 9º, Art. 11, Art. 22, Art. 31, Art. 40 |
| [LEI ORDINÁRIA Nº 2517/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38759) | 38759 | 1 artigo(s) revogado(s): Art. 36 |
| [LEI ORDINÁRIA Nº 2516/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38810) | 38810 | 1 com trecho riscado: Art. 5º |
| [LEI ORDINÁRIA Nº 2512/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38492) | 38492 | 1 artigo(s) revogado(s): Art. 5º |
| [LEI ORDINÁRIA Nº 2492/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38793) | 38793 | 2 com trecho riscado: Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 2464/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38032) | 38032 | 1 artigo(s) revogado(s): Art. 4º |
| [LEI ORDINÁRIA Nº 2463/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38194) | 38194 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 2428/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38715) | 38715 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 2406/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38700) | 38700 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 2402/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38621) | 38621 | 2 artigo(s) revogado(s): Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 2401/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38676) | 38676 | 1 artigo(s) revogado(s): Art. 5º; 2 com trecho riscado: Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 2394/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38690) | 38690 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 2387/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38694) | 38694 | 3 artigo(s) revogado(s): Art. 3º, Art. 7º, Art. 8 |
| [LEI ORDINÁRIA Nº 2380/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38679) | 38679 | 2 artigo(s) revogado(s): Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 2364/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38697) | 38697 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 2337/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36042) | 36042 | 2 com trecho riscado: Art. 3º, Art. 8º |
| [LEI ORDINÁRIA Nº 2271/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38580) | 38580 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 2223/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38554) | 38554 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 2212/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35541) | 35541 | 17 artigo(s) revogado(s): Art. 1º, Art. 6º, Art. 7º, Art. 8º, Art. 10, Art. 14…; 13 com trecho riscado: Art. 5º, Art. 16, Art. 18, Art. 23, Art. 25, Art. 42… |
| [LEI ORDINÁRIA Nº 2134/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38456) | 38456 | 1 artigo(s) revogado(s): Art. 1º; 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 2126/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38451) | 38451 | 2 artigo(s) revogado(s): Art. 2º, Art. 4º |
| [LEI ORDINÁRIA Nº 2046/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38407) | 38407 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 2027/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38343) | 38343 | 2 com trecho riscado: Art. 20, Art. 21 |
| [LEI ORDINÁRIA Nº 1954/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38301) | 38301 | 2 artigo(s) revogado(s): Art. 1º, Art. 3º |
| [LEI ORDINÁRIA Nº 1847/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38202) | 38202 | 2 artigo(s) revogado(s): Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 1743/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38122) | 38122 | 4 artigo(s) revogado(s): Art. 2º, Art. 3º, Art. 4º, Art. 7º |
| [LEI ORDINÁRIA Nº 1686/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38048) | 38048 | 2 artigo(s) revogado(s): Art. 3º, Art. 4º |
| [LEI ORDINÁRIA Nº 1618/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37951) | 37951 | 1 com trecho riscado: Art. 41 |
| [LEI ORDINÁRIA Nº 1578/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37921) | 37921 | 4 artigo(s) revogado(s): Art. 1º, Art. 1º, Art. 2º, Art. 5º; 2 com trecho riscado: Art. 2º, Art. 5º |
| [LEI ORDINÁRIA Nº 1543/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37935) | 37935 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 1457/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37869) | 37869 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 1443/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37814) | 37814 | 5 artigo(s) revogado(s): Art. 1º, Art. 2º, Art. 3º, Art. 4º, Art. 5º; 8 com trecho riscado: Art. 1º, Art. 2º, Art. 2º, Art. 2º, Art. 3º, Art. 4º… |
| [LEI ORDINÁRIA Nº 1391/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37483) | 37483 | 1 artigo(s) revogado(s): Art. 3º |
| [LEI ORDINÁRIA Nº 1326/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37741) | 37741 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 1154/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37594) | 37594 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 1153/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37570) | 37570 | 2 com trecho riscado: Art. 1º, Art. 5º |
| [LEI ORDINÁRIA Nº 1151/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37569) | 37569 | 9 artigo(s) revogado(s): Art. 29, Art. 59, Art. 87, Art. 174, Art. 179, Art. 232…; 9 com trecho riscado: Art. 2º, Art. 74, Art. 87, Art. 150, Art. 180, Art. 185… |
| [LEI ORDINÁRIA Nº 1108/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37481) | 37481 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 1091/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37491) | 37491 | 3 com trecho riscado: Art. 1º, Art. 1º, Art. 2º |
| [LEI ORDINÁRIA Nº 1052/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37443) | 37443 | 1 com trecho riscado: Art. 7º |
| [LEI ORDINÁRIA Nº 1030/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37437) | 37437 | 2 artigo(s) revogado(s): Art. 8º, Art. 8º; 2 com trecho riscado: Art. 9º, Art. 10 |
| [LEI ORDINÁRIA Nº 1008/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37402) | 37402 | 3 com trecho riscado: Art. 6º, Art. 10, Art. 11 |
| [LEI ORDINÁRIA Nº 880/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37313) | 37313 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 804/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37197) | 37197 | 1 artigo(s) revogado(s): Art. 2º |
| [LEI ORDINÁRIA Nº 700/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37141) | 37141 | 1 com trecho riscado: Art. 3º |
| [LEI ORDINÁRIA Nº 696/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33029) | 33029 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 682/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37136) | 37136 | 2 com trecho riscado: Art. 42, Art. 44 |
| [LEI ORDINÁRIA Nº 617/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37075) | 37075 | 1 com trecho riscado: Art. 2º |
| [LEI ORDINÁRIA Nº 528/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34265) | 34265 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 508/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28361) | 28361 | 2 artigo(s) revogado(s): Art. 7º, Art. 15; 1 com trecho riscado: Art. 17 |
| [LEI ORDINÁRIA Nº 281/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26849) | 26849 | 20 artigo(s) revogado(s): Art. 11, Art. 15, Art. 31, Art. 33, Art. 37, Art. 39…; 13 com trecho riscado: Art. 11, Art. 13, Art. 52, Art. 52, Art. 70, Art. 85… |
| [LEI ORDINÁRIA Nº 244/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28518) | 28518 | 1 artigo(s) revogado(s): Art. 1º; 3 com trecho riscado: Art. 1º, Art. 1º, Art. 1º |
| [LEI ORDINÁRIA Nº 233/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28734) | 28734 | 1 artigo(s) revogado(s): Art. 1º |
| [LEI ORDINÁRIA Nº 219/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28522) | 28522 | 5 com trecho riscado: Art. 41, Art. 64, Art. 99, Art. 173, Art. 547 |
| [LEI ORDINÁRIA Nº 216/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33892) | 33892 | 1 com trecho riscado: Art. 1º |
| [LEI ORDINÁRIA Nº 133/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28331) | 28331 | 5 artigo(s) revogado(s): Art. 22, Art. 35, Art. 35, Art. 39, Art. 146; 7 com trecho riscado: Art. 20, Art. 20, Art. 37, Art. 60, Art. 137, Art. 146… |

<a id="sem-data"></a>
## Lei sem data (837 leis)

**O que aconteceu:** Leis antigas têm título no formato `LEI ORDINÁRIA Nº 1234/1965`, só com o ano, e o texto não traz assinatura com data nem anexo datado.

**Solução:** `data_lei = null`. Nada é inventado; o `ano` (tirado do título) está sempre preenchido e pode ser usado para filtrar por período.

| Lei | id | Detalhe |
|---|---|---|
| [LEI ORDINÁRIA Nº 6935/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40257) | 40257 | ano 1996 |
| [LEI ORDINÁRIA Nº 6916/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33470) | 33470 | ano 1996 |
| [LEI ORDINÁRIA Nº 6915/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40277) | 40277 | ano 1996 |
| [LEI ORDINÁRIA Nº 6911/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40312) | 40312 | ano 1996 |
| [LEI ORDINÁRIA Nº 6884/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40348) | 40348 | ano 1996 |
| [LEI ORDINÁRIA Nº 6876/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40323) | 40323 | ano 1996 |
| [LEI ORDINÁRIA Nº 6875/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40319) | 40319 | ano 1996 |
| [LEI ORDINÁRIA Nº 6848/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37045) | 37045 | ano 1996 |
| [LEI ORDINÁRIA Nº 6847/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40366) | 40366 | ano 1996 |
| [LEI ORDINÁRIA Nº 6844/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40349) | 40349 | ano 1996 |
| [LEI ORDINÁRIA Nº 6825/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40378) | 40378 | ano 1996 |
| [LEI ORDINÁRIA Nº 6822/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40398) | 40398 | ano 1996 |
| [LEI ORDINÁRIA Nº 6821/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40421) | 40421 | ano 1996 |
| [LEI ORDINÁRIA Nº 6811/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40355) | 40355 | ano 1996 |
| [LEI ORDINÁRIA Nº 6810/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40369) | 40369 | ano 1996 |
| [LEI ORDINÁRIA Nº 6795/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40453) | 40453 | ano 1996 |
| [LEI ORDINÁRIA Nº 6794/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26150) | 26150 | ano 1996 |
| [LEI ORDINÁRIA Nº 6757/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36448) | 36448 | ano 1996 |
| [LEI ORDINÁRIA Nº 6726/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26202) | 26202 | ano 1996 |
| [LEI ORDINÁRIA Nº 6725/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26227) | 26227 | ano 1996 |
| [LEI ORDINÁRIA Nº 6719/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40436) | 40436 | ano 1996 |
| [LEI ORDINÁRIA Nº 6716/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36423) | 36423 | ano 1996 |
| [LEI ORDINÁRIA Nº 6641/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36463) | 36463 | ano 1996 |
| [LEI ORDINÁRIA Nº 6583/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30182) | 30182 | ano 1996 |
| [LEI ORDINÁRIA Nº 6582/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26304) | 26304 | ano 1996 |
| [LEI ORDINÁRIA Nº 6581/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26299) | 26299 | ano 1996 |
| [LEI ORDINÁRIA Nº 6516/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36437) | 36437 | ano 1996 |
| [LEI ORDINÁRIA Nº 6481/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36421) | 36421 | ano 1996 |
| [LEI ORDINÁRIA Nº 6480/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36435) | 36435 | ano 1996 |
| [LEI ORDINÁRIA Nº 6479/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36428) | 36428 | ano 1996 |
| [LEI ORDINÁRIA Nº 6478/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36408) | 36408 | ano 1996 |
| [LEI ORDINÁRIA Nº 6477/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35986) | 35986 | ano 1996 |
| [LEI ORDINÁRIA Nº 6475/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36426) | 36426 | ano 1996 |
| [LEI ORDINÁRIA Nº 6473/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36424) | 36424 | ano 1996 |
| [LEI ORDINÁRIA Nº 6472/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36174) | 36174 | ano 1996 |
| [LEI ORDINÁRIA Nº 6423/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35398) | 35398 | ano 1995 |
| [LEI ORDINÁRIA Nº 6422/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35847) | 35847 | ano 1995 |
| [LEI ORDINÁRIA Nº 6395/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35442) | 35442 | ano 1995 |
| [LEI ORDINÁRIA Nº 6360/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35577) | 35577 | ano 1995 |
| [LEI ORDINÁRIA Nº 6330/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35508) | 35508 | ano 1995 |
| [LEI ORDINÁRIA Nº 6270/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35690) | 35690 | ano 1995 |
| [LEI ORDINÁRIA Nº 6265/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35540) | 35540 | ano 1995 |
| [LEI ORDINÁRIA Nº 6264/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35497) | 35497 | ano 1995 |
| [LEI ORDINÁRIA Nº 6263/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35553) | 35553 | ano 1995 |
| [LEI ORDINÁRIA Nº 6262/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35599) | 35599 | ano 1995 |
| [LEI ORDINÁRIA Nº 6261/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35586) | 35586 | ano 1995 |
| [LEI ORDINÁRIA Nº 6260/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35579) | 35579 | ano 1995 |
| [LEI ORDINÁRIA Nº 6259/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35603) | 35603 | ano 1995 |
| [LEI ORDINÁRIA Nº 6231/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35546) | 35546 | ano 1995 |
| [LEI ORDINÁRIA Nº 6212/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35636) | 35636 | ano 1995 |
| [LEI ORDINÁRIA Nº 6199/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35611) | 35611 | ano 1995 |
| [LEI ORDINÁRIA Nº 6198/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35756) | 35756 | ano 1995 |
| [LEI ORDINÁRIA Nº 6186/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35644) | 35644 | ano 1995 |
| [LEI ORDINÁRIA Nº 6185/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35654) | 35654 | ano 1995 |
| [LEI ORDINÁRIA Nº 6183/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35653) | 35653 | ano 1995 |
| [LEI ORDINÁRIA Nº 6182/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35666) | 35666 | ano 1995 |
| [LEI ORDINÁRIA Nº 6181/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35816) | 35816 | ano 1995 |
| [LEI ORDINÁRIA Nº 6180/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35651) | 35651 | ano 1995 |
| [LEI ORDINÁRIA Nº 6179/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35734) | 35734 | ano 1995 |
| [LEI ORDINÁRIA Nº 6150/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35801) | 35801 | ano 1995 |
| [LEI ORDINÁRIA Nº 6142/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35676) | 35676 | ano 1995 |
| [LEI ORDINÁRIA Nº 6135/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35691) | 35691 | ano 1995 |
| [LEI ORDINÁRIA Nº 6101/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35718) | 35718 | ano 1995 |
| [LEI ORDINÁRIA Nº 6095/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35746) | 35746 | ano 1995 |
| [LEI ORDINÁRIA Nº 6085/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35796) | 35796 | ano 1995 |
| [LEI ORDINÁRIA Nº 6053/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35835) | 35835 | ano 1995 |
| [LEI ORDINÁRIA Nº 6052/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35803) | 35803 | ano 1995 |
| [LEI ORDINÁRIA Nº 6047/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35695) | 35695 | ano 1995 |
| [LEI ORDINÁRIA Nº 6006/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35873) | 35873 | ano 1994 |
| [LEI ORDINÁRIA Nº 6005/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35926) | 35926 | ano 1994 |
| [LEI ORDINÁRIA Nº 5980/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35845) | 35845 | ano 1994 |
| [LEI ORDINÁRIA Nº 5927/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30627) | 30627 | ano 1994 |
| [LEI ORDINÁRIA Nº 5926/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30691) | 30691 | ano 1994 |
| [LEI ORDINÁRIA Nº 5859/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35999) | 35999 | ano 1994 |
| [LEI ORDINÁRIA Nº 5851/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32438) | 32438 | ano 1994 |
| [LEI ORDINÁRIA Nº 5838/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30630) | 30630 | ano 1994 |
| [LEI ORDINÁRIA Nº 5806/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30072) | 30072 | ano 1994 |
| [LEI ORDINÁRIA Nº 5752/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30115) | 30115 | ano 1994 |
| [LEI ORDINÁRIA Nº 5696/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30493) | 30493 | ano 1994 |
| [LEI ORDINÁRIA Nº 5691/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30550) | 30550 | ano 1994 |
| [LEI ORDINÁRIA Nº 5690/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30488) | 30488 | ano 1994 |
| [LEI ORDINÁRIA Nº 5689/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30533) | 30533 | ano 1994 |
| [LEI ORDINÁRIA Nº 5688/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30240) | 30240 | ano 1994 |
| [LEI ORDINÁRIA Nº 5687/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30266) | 30266 | ano 1994 |
| [LEI ORDINÁRIA Nº 5590/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30330) | 30330 | ano 1993 |
| [LEI ORDINÁRIA Nº 5575/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30429) | 30429 | ano 1993 |
| [LEI ORDINÁRIA Nº 5516/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30401) | 30401 | ano 1993 |
| [LEI ORDINÁRIA Nº 5509/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30017) | 30017 | ano 1993 |
| [LEI ORDINÁRIA Nº 5499/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30338) | 30338 | ano 1993 |
| [LEI ORDINÁRIA Nº 5498/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30284) | 30284 | ano 1993 |
| [LEI ORDINÁRIA Nº 5494/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30322) | 30322 | ano 1993 |
| [LEI ORDINÁRIA Nº 5493/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30308) | 30308 | ano 1993 |
| [LEI ORDINÁRIA Nº 5468/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30350) | 30350 | ano 1993 |
| [LEI ORDINÁRIA Nº 5467/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30340) | 30340 | ano 1993 |
| [LEI ORDINÁRIA Nº 5466/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30232) | 30232 | ano 1993 |
| [LEI ORDINÁRIA Nº 5465/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30253) | 30253 | ano 1993 |
| [LEI ORDINÁRIA Nº 5464/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30258) | 30258 | ano 1993 |
| [LEI ORDINÁRIA Nº 5428/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30268) | 30268 | ano 1993 |
| [LEI ORDINÁRIA Nº 5427/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30239) | 30239 | ano 1993 |
| [LEI ORDINÁRIA Nº 5415/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30263) | 30263 | ano 1993 |
| [LEI ORDINÁRIA Nº 5374/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30245) | 30245 | ano 1993 |
| [LEI ORDINÁRIA Nº 5373/1993](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30269) | 30269 | ano 1993 |
| [LEI ORDINÁRIA Nº 5346/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32637) | 32637 | ano 1992 |
| [LEI ORDINÁRIA Nº 5345/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33307) | 33307 | ano 1992 |
| [LEI ORDINÁRIA Nº 5344/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34387) | 34387 | ano 1992 |
| [LEI ORDINÁRIA Nº 5343/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36488) | 36488 | ano 1992 |
| [LEI ORDINÁRIA Nº 5342/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32916) | 32916 | ano 1992 |
| [LEI ORDINÁRIA Nº 5341/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33425) | 33425 | ano 1992 |
| [LEI ORDINÁRIA Nº 5340/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34442) | 34442 | ano 1992 |
| [LEI ORDINÁRIA Nº 5339/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36493) | 36493 | ano 1992 |
| [LEI ORDINÁRIA Nº 5338/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36492) | 36492 | ano 1992 |
| [LEI ORDINÁRIA Nº 5337/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33070) | 33070 | ano 1992 |
| [LEI ORDINÁRIA Nº 5336/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36491) | 36491 | ano 1992 |
| [LEI ORDINÁRIA Nº 5335/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36505) | 36505 | ano 1992 |
| [LEI ORDINÁRIA Nº 5334/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33162) | 33162 | ano 1992 |
| [LEI ORDINÁRIA Nº 5333/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34681) | 34681 | ano 1992 |
| [LEI ORDINÁRIA Nº 5332/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34973) | 34973 | ano 1992 |
| [LEI ORDINÁRIA Nº 5331/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34405) | 34405 | ano 1992 |
| [LEI ORDINÁRIA Nº 5330/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29355) | 29355 | ano 1992 |
| [LEI ORDINÁRIA Nº 5329/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33693) | 33693 | ano 1992 |
| [LEI ORDINÁRIA Nº 5328/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34317) | 34317 | ano 1992 |
| [LEI ORDINÁRIA Nº 5327/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29557) | 29557 | ano 1992 |
| [LEI ORDINÁRIA Nº 5326/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29297) | 29297 | ano 1992 |
| [LEI ORDINÁRIA Nº 5325/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27879) | 27879 | ano 1992 |
| [LEI ORDINÁRIA Nº 5324/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34694) | 34694 | ano 1992 |
| [LEI ORDINÁRIA Nº 5323/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34337) | 34337 | ano 1992 |
| [LEI ORDINÁRIA Nº 5322/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33694) | 33694 | ano 1992 |
| [LEI ORDINÁRIA Nº 5289/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33427) | 33427 | ano 1992 |
| [LEI ORDINÁRIA Nº 5279/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33644) | 33644 | ano 1992 |
| [LEI ORDINÁRIA Nº 5278/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30005) | 30005 | ano 1992 |
| [LEI ORDINÁRIA Nº 5270/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33482) | 33482 | ano 1992 |
| [LEI ORDINÁRIA Nº 5247/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29434) | 29434 | ano 1992 |
| [LEI ORDINÁRIA Nº 5245/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33491) | 33491 | ano 1992 |
| [LEI ORDINÁRIA Nº 5244/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27908) | 27908 | ano 1992 |
| [LEI ORDINÁRIA Nº 5243/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27902) | 27902 | ano 1992 |
| [LEI ORDINÁRIA Nº 5240/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34518) | 34518 | ano 1992 |
| [LEI ORDINÁRIA Nº 5236/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32639) | 32639 | ano 1992 |
| [LEI ORDINÁRIA Nº 5229/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27910) | 27910 | ano 1992 |
| [LEI ORDINÁRIA Nº 5223/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27909) | 27909 | ano 1992 |
| [LEI ORDINÁRIA Nº 5222/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33597) | 33597 | ano 1992 |
| [LEI ORDINÁRIA Nº 5213/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27906) | 27906 | ano 1992 |
| [LEI ORDINÁRIA Nº 5206/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29287) | 29287 | ano 1992 |
| [LEI ORDINÁRIA Nº 5203/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27652) | 27652 | ano 1992 |
| [LEI ORDINÁRIA Nº 5196/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29440) | 29440 | ano 1992 |
| [LEI ORDINÁRIA Nº 5191/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33192) | 33192 | ano 1992 |
| [LEI ORDINÁRIA Nº 5188/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33166) | 33166 | ano 1992 |
| [LEI ORDINÁRIA Nº 5187/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33163) | 33163 | ano 1992 |
| [LEI ORDINÁRIA Nº 5186/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29666) | 29666 | ano 1992 |
| [LEI ORDINÁRIA Nº 5183/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33175) | 33175 | ano 1992 |
| [LEI ORDINÁRIA Nº 5182/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33040) | 33040 | ano 1992 |
| [LEI ORDINÁRIA Nº 5180/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27884) | 27884 | ano 1992 |
| [LEI ORDINÁRIA Nº 5179/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32943) | 32943 | ano 1992 |
| [LEI ORDINÁRIA Nº 5178/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33214) | 33214 | ano 1992 |
| [LEI ORDINÁRIA Nº 5176/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36509) | 36509 | ano 1992 |
| [LEI ORDINÁRIA Nº 5175/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32824) | 32824 | ano 1992 |
| [LEI ORDINÁRIA Nº 5172/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33250) | 33250 | ano 1992 |
| [LEI ORDINÁRIA Nº 5166/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34680) | 34680 | ano 1992 |
| [LEI ORDINÁRIA Nº 5164/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34287) | 34287 | ano 1992 |
| [LEI ORDINÁRIA Nº 5162/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36451) | 36451 | ano 1992 |
| [LEI ORDINÁRIA Nº 5158/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29663) | 29663 | ano 1992 |
| [LEI ORDINÁRIA Nº 5157/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36497) | 36497 | ano 1992 |
| [LEI ORDINÁRIA Nº 5151/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33167) | 33167 | ano 1992 |
| [LEI ORDINÁRIA Nº 5150/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31786) | 31786 | ano 1992 |
| [LEI ORDINÁRIA Nº 5148/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31789) | 31789 | ano 1992 |
| [LEI ORDINÁRIA Nº 5147/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31788) | 31788 | ano 1992 |
| [LEI ORDINÁRIA Nº 5145/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31760) | 31760 | ano 1992 |
| [LEI ORDINÁRIA Nº 5144/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31787) | 31787 | ano 1992 |
| [LEI ORDINÁRIA Nº 5143/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31772) | 31772 | ano 1992 |
| [LEI ORDINÁRIA Nº 5142/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31731) | 31731 | ano 1992 |
| [LEI ORDINÁRIA Nº 5141/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31769) | 31769 | ano 1992 |
| [LEI ORDINÁRIA Nº 5140/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34985) | 34985 | ano 1992 |
| [LEI ORDINÁRIA Nº 5138/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33390) | 33390 | ano 1992 |
| [LEI ORDINÁRIA Nº 5137/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33216) | 33216 | ano 1992 |
| [LEI ORDINÁRIA Nº 5136/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36405) | 36405 | ano 1992 |
| [LEI ORDINÁRIA Nº 5135/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31775) | 31775 | ano 1992 |
| [LEI ORDINÁRIA Nº 5133/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33215) | 33215 | ano 1992 |
| [LEI ORDINÁRIA Nº 5132/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34842) | 34842 | ano 1992 |
| [LEI ORDINÁRIA Nº 5129/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33565) | 33565 | ano 1992 |
| [LEI ORDINÁRIA Nº 5128/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33157) | 33157 | ano 1992 |
| [LEI ORDINÁRIA Nº 5126/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33486) | 33486 | ano 1992 |
| [LEI ORDINÁRIA Nº 5122/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32680) | 32680 | ano 1992 |
| [LEI ORDINÁRIA Nº 5104/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36407) | 36407 | ano 1992 |
| [LEI ORDINÁRIA Nº 5101/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33379) | 33379 | ano 1992 |
| [LEI ORDINÁRIA Nº 5098/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33621) | 33621 | ano 1992 |
| [LEI ORDINÁRIA Nº 5089/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33600) | 33600 | ano 1992 |
| [LEI ORDINÁRIA Nº 5088/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35005) | 35005 | ano 1992 |
| [LEI ORDINÁRIA Nº 5085/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36394) | 36394 | ano 1992 |
| [LEI ORDINÁRIA Nº 5084/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33126) | 33126 | ano 1992 |
| [LEI ORDINÁRIA Nº 5083/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29565) | 29565 | ano 1992 |
| [LEI ORDINÁRIA Nº 5082/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34406) | 34406 | ano 1992 |
| [LEI ORDINÁRIA Nº 5081/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34232) | 34232 | ano 1992 |
| [LEI ORDINÁRIA Nº 5062/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29571) | 29571 | ano 1992 |
| [LEI ORDINÁRIA Nº 5061/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34345) | 34345 | ano 1992 |
| [LEI ORDINÁRIA Nº 5051/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33412) | 33412 | ano 1992 |
| [LEI ORDINÁRIA Nº 5050/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33619) | 33619 | ano 1992 |
| [LEI ORDINÁRIA Nº 5049/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34560) | 34560 | ano 1992 |
| [LEI ORDINÁRIA Nº 5048/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33618) | 33618 | ano 1992 |
| [LEI ORDINÁRIA Nº 5047/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33622) | 33622 | ano 1992 |
| [LEI ORDINÁRIA Nº 5046/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33234) | 33234 | ano 1992 |
| [LEI ORDINÁRIA Nº 5040/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28970) | 28970 | ano 1992 |
| [LEI ORDINÁRIA Nº 5038/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33664) | 33664 | ano 1992 |
| [LEI ORDINÁRIA Nº 5030/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33454) | 33454 | ano 1992 |
| [LEI ORDINÁRIA Nº 5029/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33654) | 33654 | ano 1992 |
| [LEI ORDINÁRIA Nº 5028/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28339) | 28339 | ano 1992 |
| [LEI ORDINÁRIA Nº 5024/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30712) | 30712 | ano 1992 |
| [LEI ORDINÁRIA Nº 5023/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33639) | 33639 | ano 1992 |
| [LEI ORDINÁRIA Nº 5022/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34904) | 34904 | ano 1992 |
| [LEI ORDINÁRIA Nº 5012/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33178) | 33178 | ano 1992 |
| [LEI ORDINÁRIA Nº 5011/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29627) | 29627 | ano 1992 |
| [LEI ORDINÁRIA Nº 4999/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32742) | 32742 | ano 1992 |
| [LEI ORDINÁRIA Nº 4998/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36498) | 36498 | ano 1992 |
| [LEI ORDINÁRIA Nº 4997/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32514) | 32514 | ano 1992 |
| [LEI ORDINÁRIA Nº 4996/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32732) | 32732 | ano 1992 |
| [LEI ORDINÁRIA Nº 4995/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32809) | 32809 | ano 1992 |
| [LEI ORDINÁRIA Nº 4974/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36580) | 36580 | ano 1992 |
| [LEI ORDINÁRIA Nº 4973/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36568) | 36568 | ano 1992 |
| [LEI ORDINÁRIA Nº 4972/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36553) | 36553 | ano 1992 |
| [LEI ORDINÁRIA Nº 4971/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32828) | 32828 | ano 1992 |
| [LEI ORDINÁRIA Nº 4967/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32897) | 32897 | ano 1992 |
| [LEI ORDINÁRIA Nº 4947/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32776) | 32776 | ano 1992 |
| [LEI ORDINÁRIA Nº 4946/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36569) | 36569 | ano 1992 |
| [LEI ORDINÁRIA Nº 4942/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33197) | 33197 | ano 1992 |
| [LEI ORDINÁRIA Nº 4941/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36566) | 36566 | ano 1992 |
| [LEI ORDINÁRIA Nº 4932/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36532) | 36532 | ano 1992 |
| [LEI ORDINÁRIA Nº 4930/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36527) | 36527 | ano 1992 |
| [LEI ORDINÁRIA Nº 4929/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32921) | 32921 | ano 1992 |
| [LEI ORDINÁRIA Nº 4927/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36561) | 36561 | ano 1992 |
| [LEI ORDINÁRIA Nº 4926/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32912) | 32912 | ano 1992 |
| [LEI ORDINÁRIA Nº 4925/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34422) | 34422 | ano 1992 |
| [LEI ORDINÁRIA Nº 4923/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34497) | 34497 | ano 1992 |
| [LEI ORDINÁRIA Nº 4922/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32881) | 32881 | ano 1992 |
| [LEI ORDINÁRIA Nº 4921/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33024) | 33024 | ano 1992 |
| [LEI ORDINÁRIA Nº 4920/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34197) | 34197 | ano 1992 |
| [LEI ORDINÁRIA Nº 4919/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32876) | 32876 | ano 1992 |
| [LEI ORDINÁRIA Nº 4918/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29796) | 29796 | ano 1992 |
| [LEI ORDINÁRIA Nº 4917/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34454) | 34454 | ano 1992 |
| [LEI ORDINÁRIA Nº 4916/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33173) | 33173 | ano 1992 |
| [LEI ORDINÁRIA Nº 4915/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32861) | 32861 | ano 1992 |
| [LEI ORDINÁRIA Nº 4914/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36550) | 36550 | ano 1992 |
| [LEI ORDINÁRIA Nº 4913/1992](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32956) | 32956 | ano 1992 |
| [LEI ORDINÁRIA Nº 4900/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36545) | 36545 | ano 1991 |
| [LEI ORDINÁRIA Nº 4881/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32957) | 32957 | ano 1991 |
| [LEI ORDINÁRIA Nº 4871/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34885) | 34885 | ano 1991 |
| [LEI ORDINÁRIA Nº 4870/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32761) | 32761 | ano 1991 |
| [LEI ORDINÁRIA Nº 4869/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33417) | 33417 | ano 1991 |
| [LEI ORDINÁRIA Nº 4860/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36526) | 36526 | ano 1991 |
| [LEI ORDINÁRIA Nº 4854/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33069) | 33069 | ano 1991 |
| [LEI ORDINÁRIA Nº 4840/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36522) | 36522 | ano 1991 |
| [LEI ORDINÁRIA Nº 4838/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32967) | 32967 | ano 1991 |
| [LEI ORDINÁRIA Nº 4827/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36489) | 36489 | ano 1991 |
| [LEI ORDINÁRIA Nº 4816/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36617) | 36617 | ano 1991 |
| [LEI ORDINÁRIA Nº 4807/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30004) | 30004 | ano 1991 |
| [LEI ORDINÁRIA Nº 4777/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34805) | 34805 | ano 1991 |
| [LEI ORDINÁRIA Nº 4765/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34683) | 34683 | ano 1991 |
| [LEI ORDINÁRIA Nº 4764/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36593) | 36593 | ano 1991 |
| [LEI ORDINÁRIA Nº 4756/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35012) | 35012 | ano 1991 |
| [LEI ORDINÁRIA Nº 4746/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36517) | 36517 | ano 1991 |
| [LEI ORDINÁRIA Nº 4700/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39211) | 39211 | ano 1991 |
| [LEI ORDINÁRIA Nº 4693/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30853) | 30853 | ano 1991 |
| [LEI ORDINÁRIA Nº 4684/1991](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39200) | 39200 | ano 1991 |
| [LEI ORDINÁRIA Nº 4609/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39585) | 39585 | ano 1990 |
| [LEI ORDINÁRIA Nº 4445/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30916) | 30916 | ano 1990 |
| [LEI ORDINÁRIA Nº 4437/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30910) | 30910 | ano 1990 |
| [LEI ORDINÁRIA Nº 4436/1990](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30932) | 30932 | ano 1990 |
| [LEI ORDINÁRIA Nº 4371/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31219) | 31219 | ano 1989 |
| [LEI ORDINÁRIA Nº 4326/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31179) | 31179 | ano 1989 |
| [LEI ORDINÁRIA Nº 4249/1989](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31101) | 31101 | ano 1989 |
| [LEI ORDINÁRIA Nº 4116/1988](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28945) | 28945 | ano 1988 |
| [LEI ORDINÁRIA Nº 3985/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30197) | 30197 | ano 1987 |
| [LEI ORDINÁRIA Nº 3967/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31354) | 31354 | ano 1987 |
| [LEI ORDINÁRIA Nº 3945/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31286) | 31286 | ano 1987 |
| [LEI ORDINÁRIA Nº 3928/1986](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31155) | 31155 | ano 1986 |
| [LEI ORDINÁRIA Nº 3848/1985](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26296) | 26296 | ano 1985 |
| [LEI ORDINÁRIA Nº 3785/1985](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36783) | 36783 | ano 1985 |
| [LEI ORDINÁRIA Nº 3761/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28080) | 28080 | ano 1984 |
| [LEI ORDINÁRIA Nº 3743/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36744) | 36744 | ano 1984 |
| [LEI ORDINÁRIA Nº 3742/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36808) | 36808 | ano 1984 |
| [LEI ORDINÁRIA Nº 3702/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36762) | 36762 | ano 1984 |
| [LEI ORDINÁRIA Nº 3701/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36779) | 36779 | ano 1984 |
| [LEI ORDINÁRIA Nº 3670/1984](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31506) | 31506 | ano 1984 |
| [LEI ORDINÁRIA Nº 3646/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31580) | 31580 | ano 1983 |
| [LEI ORDINÁRIA Nº 3606/1983](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31434) | 31434 | ano 1983 |
| [LEI ORDINÁRIA Nº 3538/1982](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31386) | 31386 | ano 1982 |
| [LEI ORDINÁRIA Nº 3419/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40076) | 40076 | ano 1981 |
| [LEI ORDINÁRIA Nº 3418/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26832) | 26832 | ano 1981 |
| [LEI ORDINÁRIA Nº 3357/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36960) | 36960 | ano 1981 |
| [LEI ORDINÁRIA Nº 3282/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31521) | 31521 | ano 1981 |
| [LEI ORDINÁRIA Nº 3273/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29218) | 29218 | ano 1981 |
| [LEI ORDINÁRIA Nº 3262/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36825) | 36825 | ano 1981 |
| [LEI ORDINÁRIA Nº 3254/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32262) | 32262 | ano 1981 |
| [LEI ORDINÁRIA Nº 3253/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29449) | 29449 | ano 1981 |
| [LEI ORDINÁRIA Nº 3197/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36989) | 36989 | ano 1980 |
| [LEI ORDINÁRIA Nº 3191/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33483) | 33483 | ano 1980 |
| [LEI ORDINÁRIA Nº 3161/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31650) | 31650 | ano 1980 |
| [LEI ORDINÁRIA Nº 3160/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31643) | 31643 | ano 1980 |
| [LEI ORDINÁRIA Nº 3159/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31631) | 31631 | ano 1980 |
| [LEI ORDINÁRIA Nº 3152/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31637) | 31637 | ano 1980 |
| [LEI ORDINÁRIA Nº 3124/1980](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32721) | 32721 | ano 1980 |
| [LEI ORDINÁRIA Nº 3093/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31762) | 31762 | ano 1979 |
| [LEI ORDINÁRIA Nº 3077/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31738) | 31738 | ano 1979 |
| [LEI ORDINÁRIA Nº 3076/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31707) | 31707 | ano 1979 |
| [LEI ORDINÁRIA Nº 2924/1978](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39181) | 39181 | ano 1978 |
| [LEI ORDINÁRIA Nº 2857/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39044) | 39044 | ano 1977 |
| [LEI ORDINÁRIA Nº 2838/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39075) | 39075 | ano 1977 |
| [LEI ORDINÁRIA Nº 2837/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29984) | 29984 | ano 1977 |
| [LEI ORDINÁRIA Nº 2822/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39097) | 39097 | ano 1977 |
| [LEI ORDINÁRIA Nº 2821/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39010) | 39010 | ano 1977 |
| [LEI ORDINÁRIA Nº 2734/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39045) | 39045 | ano 1977 |
| [LEI ORDINÁRIA Nº 2700/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38948) | 38948 | ano 1976 |
| [LEI ORDINÁRIA Nº 2698/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38963) | 38963 | ano 1976 |
| [LEI ORDINÁRIA Nº 2677/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40861) | 40861 | ano 1976 |
| [LEI ORDINÁRIA Nº 2562/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38837) | 38837 | ano 1975 |
| [LEI ORDINÁRIA Nº 2554/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38829) | 38829 | ano 1975 |
| [LEI ORDINÁRIA Nº 2540/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38824) | 38824 | ano 1975 |
| [LEI ORDINÁRIA Nº 2534/1975](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38808) | 38808 | ano 1975 |
| [LEI ORDINÁRIA Nº 2485/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38821) | 38821 | ano 1974 |
| [LEI ORDINÁRIA Nº 2466/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38730) | 38730 | ano 1974 |
| [LEI ORDINÁRIA Nº 2434/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38718) | 38718 | ano 1974 |
| [LEI ORDINÁRIA Nº 2424/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30173) | 30173 | ano 1974 |
| [LEI ORDINÁRIA Nº 2421/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38662) | 38662 | ano 1974 |
| [LEI ORDINÁRIA Nº 2410/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38702) | 38702 | ano 1974 |
| [LEI ORDINÁRIA Nº 2407/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38671) | 38671 | ano 1974 |
| [LEI ORDINÁRIA Nº 2338/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36060) | 36060 | ano 1973 |
| [LEI ORDINÁRIA Nº 2314/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38605) | 38605 | ano 1973 |
| [LEI ORDINÁRIA Nº 2296/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38598) | 38598 | ano 1973 |
| [LEI ORDINÁRIA Nº 2262/1973](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38566) | 38566 | ano 1973 |
| [LEI ORDINÁRIA Nº 2181/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38524) | 38524 | ano 1972 |
| [LEI ORDINÁRIA Nº 2109/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38481) | 38481 | ano 1972 |
| [LEI ORDINÁRIA Nº 2108/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38444) | 38444 | ano 1972 |
| [LEI ORDINÁRIA Nº 2107/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36018) | 36018 | ano 1972 |
| [LEI ORDINÁRIA Nº 2106/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38389) | 38389 | ano 1972 |
| [LEI ORDINÁRIA Nº 2105/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38384) | 38384 | ano 1972 |
| [LEI ORDINÁRIA Nº 2104/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38047) | 38047 | ano 1972 |
| [LEI ORDINÁRIA Nº 2103/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30702) | 30702 | ano 1972 |
| [LEI ORDINÁRIA Nº 2102/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38434) | 38434 | ano 1972 |
| [LEI ORDINÁRIA Nº 2101/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38397) | 38397 | ano 1972 |
| [LEI ORDINÁRIA Nº 2100/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38420) | 38420 | ano 1972 |
| [LEI ORDINÁRIA Nº 2099/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33280) | 33280 | ano 1972 |
| [LEI ORDINÁRIA Nº 2098/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38437) | 38437 | ano 1972 |
| [LEI ORDINÁRIA Nº 2097/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38349) | 38349 | ano 1972 |
| [LEI ORDINÁRIA Nº 2095/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38436) | 38436 | ano 1972 |
| [LEI ORDINÁRIA Nº 2094/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38410) | 38410 | ano 1972 |
| [LEI ORDINÁRIA Nº 2093/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38409) | 38409 | ano 1972 |
| [LEI ORDINÁRIA Nº 2092/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38335) | 38335 | ano 1972 |
| [LEI ORDINÁRIA Nº 2091/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38419) | 38419 | ano 1972 |
| [LEI ORDINÁRIA Nº 2090/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38417) | 38417 | ano 1972 |
| [LEI ORDINÁRIA Nº 2089/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39556) | 39556 | ano 1972 |
| [LEI ORDINÁRIA Nº 2088/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34178) | 34178 | ano 1972 |
| [LEI ORDINÁRIA Nº 2041/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38361) | 38361 | ano 1972 |
| [LEI ORDINÁRIA Nº 1980/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37645) | 37645 | ano 1971 |
| [LEI ORDINÁRIA Nº 1963/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38334) | 38334 | ano 1971 |
| [LEI ORDINÁRIA Nº 1935/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38319) | 38319 | ano 1971 |
| [LEI ORDINÁRIA Nº 1894/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38260) | 38260 | ano 1971 |
| [LEI ORDINÁRIA Nº 1889/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34059) | 34059 | ano 1971 |
| [LEI ORDINÁRIA Nº 1888/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38261) | 38261 | ano 1971 |
| [LEI ORDINÁRIA Nº 1887/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38229) | 38229 | ano 1971 |
| [LEI ORDINÁRIA Nº 1886/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38228) | 38228 | ano 1971 |
| [LEI ORDINÁRIA Nº 1885/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38227) | 38227 | ano 1971 |
| [LEI ORDINÁRIA Nº 1884/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38257) | 38257 | ano 1971 |
| [LEI ORDINÁRIA Nº 1883/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38250) | 38250 | ano 1971 |
| [LEI ORDINÁRIA Nº 1882/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38249) | 38249 | ano 1971 |
| [LEI ORDINÁRIA Nº 1881/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38256) | 38256 | ano 1971 |
| [LEI ORDINÁRIA Nº 1880/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38248) | 38248 | ano 1971 |
| [LEI ORDINÁRIA Nº 1879/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38255) | 38255 | ano 1971 |
| [LEI ORDINÁRIA Nº 1878/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38216) | 38216 | ano 1971 |
| [LEI ORDINÁRIA Nº 1877/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38221) | 38221 | ano 1971 |
| [LEI ORDINÁRIA Nº 1819/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38177) | 38177 | ano 1971 |
| [LEI ORDINÁRIA Nº 1805/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38154) | 38154 | ano 1970 |
| [LEI ORDINÁRIA Nº 1803/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27616) | 27616 | ano 1970 |
| [LEI ORDINÁRIA Nº 1801/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38153) | 38153 | ano 1970 |
| [LEI ORDINÁRIA Nº 1781/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38102) | 38102 | ano 1970 |
| [LEI ORDINÁRIA Nº 1780/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38103) | 38103 | ano 1970 |
| [LEI ORDINÁRIA Nº 1772/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31560) | 31560 | ano 1970 |
| [LEI ORDINÁRIA Nº 1764/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38129) | 38129 | ano 1970 |
| [LEI ORDINÁRIA Nº 1762/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37098) | 37098 | ano 1970 |
| [LEI ORDINÁRIA Nº 1717/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38099) | 38099 | ano 1970 |
| [LEI ORDINÁRIA Nº 1712/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38055) | 38055 | ano 1970 |
| [LEI ORDINÁRIA Nº 1711/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38068) | 38068 | ano 1970 |
| [LEI ORDINÁRIA Nº 1710/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38063) | 38063 | ano 1970 |
| [LEI ORDINÁRIA Nº 1689/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38051) | 38051 | ano 1970 |
| [LEI ORDINÁRIA Nº 1616/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37973) | 37973 | ano 1969 |
| [LEI ORDINÁRIA Nº 1537/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37928) | 37928 | ano 1969 |
| [LEI ORDINÁRIA Nº 1533/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37920) | 37920 | ano 1969 |
| [LEI ORDINÁRIA Nº 1532/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37919) | 37919 | ano 1969 |
| [LEI ORDINÁRIA Nº 1531/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37917) | 37917 | ano 1969 |
| [LEI ORDINÁRIA Nº 1530/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37916) | 37916 | ano 1969 |
| [LEI ORDINÁRIA Nº 1529/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37864) | 37864 | ano 1969 |
| [LEI ORDINÁRIA Nº 1528/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37896) | 37896 | ano 1969 |
| [LEI ORDINÁRIA Nº 1527/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37914) | 37914 | ano 1969 |
| [LEI ORDINÁRIA Nº 1526/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37906) | 37906 | ano 1969 |
| [LEI ORDINÁRIA Nº 1525/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37913) | 37913 | ano 1969 |
| [LEI ORDINÁRIA Nº 1524/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37911) | 37911 | ano 1969 |
| [LEI ORDINÁRIA Nº 1523/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37905) | 37905 | ano 1969 |
| [LEI ORDINÁRIA Nº 1522/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37910) | 37910 | ano 1969 |
| [LEI ORDINÁRIA Nº 1521/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37909) | 37909 | ano 1969 |
| [LEI ORDINÁRIA Nº 1520/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37904) | 37904 | ano 1969 |
| [LEI ORDINÁRIA Nº 1519/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37899) | 37899 | ano 1969 |
| [LEI ORDINÁRIA Nº 1452/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26868) | 26868 | ano 1969 |
| [LEI ORDINÁRIA Nº 1451/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37833) | 37833 | ano 1969 |
| [LEI ORDINÁRIA Nº 1450/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37494) | 37494 | ano 1969 |
| [LEI ORDINÁRIA Nº 1449/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37825) | 37825 | ano 1969 |
| [LEI ORDINÁRIA Nº 1448/1969](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37823) | 37823 | ano 1969 |
| [LEI ORDINÁRIA Nº 1407/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37789) | 37789 | ano 1968 |
| [LEI ORDINÁRIA Nº 1406/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37788) | 37788 | ano 1968 |
| [LEI ORDINÁRIA Nº 1399/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37776) | 37776 | ano 1968 |
| [LEI ORDINÁRIA Nº 1374/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30172) | 30172 | ano 1968 |
| [LEI ORDINÁRIA Nº 1360/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37742) | 37742 | ano 1968 |
| [LEI ORDINÁRIA Nº 1359/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37762) | 37762 | ano 1968 |
| [LEI ORDINÁRIA Nº 1358/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37709) | 37709 | ano 1968 |
| [LEI ORDINÁRIA Nº 1357/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37761) | 37761 | ano 1968 |
| [LEI ORDINÁRIA Nº 1355/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37755) | 37755 | ano 1968 |
| [LEI ORDINÁRIA Nº 1354/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37596) | 37596 | ano 1968 |
| [LEI ORDINÁRIA Nº 1353/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37750) | 37750 | ano 1968 |
| [LEI ORDINÁRIA Nº 1352/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37760) | 37760 | ano 1968 |
| [LEI ORDINÁRIA Nº 1351/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37758) | 37758 | ano 1968 |
| [LEI ORDINÁRIA Nº 1350/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37723) | 37723 | ano 1968 |
| [LEI ORDINÁRIA Nº 1349/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37757) | 37757 | ano 1968 |
| [LEI ORDINÁRIA Nº 1347/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37733) | 37733 | ano 1968 |
| [LEI ORDINÁRIA Nº 1346/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37752) | 37752 | ano 1968 |
| [LEI ORDINÁRIA Nº 1328/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33243) | 33243 | ano 1968 |
| [LEI ORDINÁRIA Nº 1317/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37702) | 37702 | ano 1968 |
| [LEI ORDINÁRIA Nº 1291/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30171) | 30171 | ano 1967 |
| [LEI ORDINÁRIA Nº 1284/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37654) | 37654 | ano 1967 |
| [LEI ORDINÁRIA Nº 1218/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37608) | 37608 | ano 1967 |
| [LEI ORDINÁRIA Nº 1217/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37456) | 37456 | ano 1967 |
| [LEI ORDINÁRIA Nº 1216/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37600) | 37600 | ano 1967 |
| [LEI ORDINÁRIA Nº 1215/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37395) | 37395 | ano 1967 |
| [LEI ORDINÁRIA Nº 1214/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37597) | 37597 | ano 1967 |
| [LEI ORDINÁRIA Nº 1213/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37607) | 37607 | ano 1967 |
| [LEI ORDINÁRIA Nº 1168/1967](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34117) | 34117 | ano 1967 |
| [LEI ORDINÁRIA Nº 1154/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37594) | 37594 | ano 1966 |
| [LEI ORDINÁRIA Nº 1152/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37544) | 37544 | ano 1966 |
| [LEI ORDINÁRIA Nº 1151/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37569) | 37569 | ano 1966 |
| [LEI ORDINÁRIA Nº 1145/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37515) | 37515 | ano 1966 |
| [LEI ORDINÁRIA Nº 1136/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37562) | 37562 | ano 1966 |
| [LEI ORDINÁRIA Nº 1122/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37558) | 37558 | ano 1966 |
| [LEI ORDINÁRIA Nº 1114/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37514) | 37514 | ano 1966 |
| [LEI ORDINÁRIA Nº 1113/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37505) | 37505 | ano 1966 |
| [LEI ORDINÁRIA Nº 1109/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37482) | 37482 | ano 1966 |
| [LEI ORDINÁRIA Nº 1108/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37481) | 37481 | ano 1966 |
| [LEI ORDINÁRIA Nº 1090/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37487) | 37487 | ano 1966 |
| [LEI ORDINÁRIA Nº 1084/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37472) | 37472 | ano 1966 |
| [LEI ORDINÁRIA Nº 1083/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37477) | 37477 | ano 1966 |
| [LEI ORDINÁRIA Nº 1070/1966](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37452) | 37452 | ano 1966 |
| [LEI ORDINÁRIA Nº 989/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34041) | 34041 | ano 1965 |
| [LEI ORDINÁRIA Nº 1064/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37405) | 37405 | ano 1965 |
| [LEI ORDINÁRIA Nº 1061/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37451) | 37451 | ano 1965 |
| [LEI ORDINÁRIA Nº 1028/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37426) | 37426 | ano 1965 |
| [LEI ORDINÁRIA Nº 1010/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37414) | 37414 | ano 1965 |
| [LEI ORDINÁRIA Nº 1009/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28211) | 28211 | ano 1965 |
| [LEI ORDINÁRIA Nº 1008/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37402) | 37402 | ano 1965 |
| [LEI ORDINÁRIA Nº 1007/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35174) | 35174 | ano 1965 |
| [LEI ORDINÁRIA Nº 929/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37375) | 37375 | ano 1964 |
| [LEI ORDINÁRIA Nº 927/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37318) | 37318 | ano 1964 |
| [LEI ORDINÁRIA Nº 926/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37348) | 37348 | ano 1964 |
| [LEI ORDINÁRIA Nº 925/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37347) | 37347 | ano 1964 |
| [LEI ORDINÁRIA Nº 924/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37317) | 37317 | ano 1964 |
| [LEI ORDINÁRIA Nº 923/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37310) | 37310 | ano 1964 |
| [LEI ORDINÁRIA Nº 922/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37329) | 37329 | ano 1964 |
| [LEI ORDINÁRIA Nº 921/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37285) | 37285 | ano 1964 |
| [LEI ORDINÁRIA Nº 877/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39288) | 39288 | ano 1963 |
| [LEI ORDINÁRIA Nº 875/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37250) | 37250 | ano 1963 |
| [LEI ORDINÁRIA Nº 839/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37224) | 37224 | ano 1963 |
| [LEI ORDINÁRIA Nº 838/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37240) | 37240 | ano 1963 |
| [LEI ORDINÁRIA Nº 833/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37203) | 37203 | ano 1963 |
| [LEI ORDINÁRIA Nº 832/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37253) | 37253 | ano 1963 |
| [LEI ORDINÁRIA Nº 831/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37252) | 37252 | ano 1963 |
| [LEI ORDINÁRIA Nº 830/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37222) | 37222 | ano 1963 |
| [LEI ORDINÁRIA Nº 829/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37231) | 37231 | ano 1963 |
| [LEI ORDINÁRIA Nº 825/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37216) | 37216 | ano 1963 |
| [LEI ORDINÁRIA Nº 824/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37243) | 37243 | ano 1963 |
| [LEI ORDINÁRIA Nº 811/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37167) | 37167 | ano 1963 |
| [LEI ORDINÁRIA Nº 810/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32838) | 32838 | ano 1963 |
| [LEI ORDINÁRIA Nº 805/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28391) | 28391 | ano 1963 |
| [LEI ORDINÁRIA Nº 804/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37197) | 37197 | ano 1963 |
| [LEI ORDINÁRIA Nº 797/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33651) | 33651 | ano 1963 |
| [LEI ORDINÁRIA Nº 796/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37137) | 37137 | ano 1963 |
| [LEI ORDINÁRIA Nº 793/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32873) | 32873 | ano 1963 |
| [LEI ORDINÁRIA Nº 788/1963](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27989) | 27989 | ano 1963 |
| [LEI ORDINÁRIA Nº 784/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37247) | 37247 | ano 1962 |
| [LEI ORDINÁRIA Nº 783/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37246) | 37246 | ano 1962 |
| [LEI ORDINÁRIA Nº 781/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30016) | 30016 | ano 1962 |
| [LEI ORDINÁRIA Nº 777/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33021) | 33021 | ano 1962 |
| [LEI ORDINÁRIA Nº 766/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32872) | 32872 | ano 1962 |
| [LEI ORDINÁRIA Nº 762/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32917) | 32917 | ano 1962 |
| [LEI ORDINÁRIA Nº 761/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37209) | 37209 | ano 1962 |
| [LEI ORDINÁRIA Nº 760/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37182) | 37182 | ano 1962 |
| [LEI ORDINÁRIA Nº 751/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37034) | 37034 | ano 1962 |
| [LEI ORDINÁRIA Nº 750/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37198) | 37198 | ano 1962 |
| [LEI ORDINÁRIA Nº 749/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37195) | 37195 | ano 1962 |
| [LEI ORDINÁRIA Nº 747/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32949) | 32949 | ano 1962 |
| [LEI ORDINÁRIA Nº 746/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32983) | 32983 | ano 1962 |
| [LEI ORDINÁRIA Nº 745/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37164) | 37164 | ano 1962 |
| [LEI ORDINÁRIA Nº 744/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37177) | 37177 | ano 1962 |
| [LEI ORDINÁRIA Nº 743/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37163) | 37163 | ano 1962 |
| [LEI ORDINÁRIA Nº 736/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37189) | 37189 | ano 1962 |
| [LEI ORDINÁRIA Nº 733/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33209) | 33209 | ano 1962 |
| [LEI ORDINÁRIA Nº 729/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33001) | 33001 | ano 1962 |
| [LEI ORDINÁRIA Nº 728/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37148) | 37148 | ano 1962 |
| [LEI ORDINÁRIA Nº 725/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37132) | 37132 | ano 1962 |
| [LEI ORDINÁRIA Nº 724/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37116) | 37116 | ano 1962 |
| [LEI ORDINÁRIA Nº 723/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37185) | 37185 | ano 1962 |
| [LEI ORDINÁRIA Nº 721/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37184) | 37184 | ano 1962 |
| [LEI ORDINÁRIA Nº 714/1962](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37176) | 37176 | ano 1962 |
| [LEI ORDINÁRIA Nº 706/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37078) | 37078 | ano 1961 |
| [LEI ORDINÁRIA Nº 702/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34069) | 34069 | ano 1961 |
| [LEI ORDINÁRIA Nº 697/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37121) | 37121 | ano 1961 |
| [LEI ORDINÁRIA Nº 696/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33029) | 33029 | ano 1961 |
| [LEI ORDINÁRIA Nº 684/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37120) | 37120 | ano 1961 |
| [LEI ORDINÁRIA Nº 681/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26833) | 26833 | ano 1961 |
| [LEI ORDINÁRIA Nº 662/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37155) | 37155 | ano 1961 |
| [LEI ORDINÁRIA Nº 661/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33019) | 33019 | ano 1961 |
| [LEI ORDINÁRIA Nº 660/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37154) | 37154 | ano 1961 |
| [LEI ORDINÁRIA Nº 659/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37127) | 37127 | ano 1961 |
| [LEI ORDINÁRIA Nº 656/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33063) | 33063 | ano 1961 |
| [LEI ORDINÁRIA Nº 655/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37126) | 37126 | ano 1961 |
| [LEI ORDINÁRIA Nº 647/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33059) | 33059 | ano 1961 |
| [LEI ORDINÁRIA Nº 646/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33206) | 33206 | ano 1961 |
| [LEI ORDINÁRIA Nº 645/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33186) | 33186 | ano 1961 |
| [LEI ORDINÁRIA Nº 644/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37030) | 37030 | ano 1961 |
| [LEI ORDINÁRIA Nº 643/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37062) | 37062 | ano 1961 |
| [LEI ORDINÁRIA Nº 642/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33240) | 33240 | ano 1961 |
| [LEI ORDINÁRIA Nº 637/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33054) | 33054 | ano 1961 |
| [LEI ORDINÁRIA Nº 635/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37113) | 37113 | ano 1961 |
| [LEI ORDINÁRIA Nº 626/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37077) | 37077 | ano 1961 |
| [LEI ORDINÁRIA Nº 620/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26821) | 26821 | ano 1961 |
| [LEI ORDINÁRIA Nº 615/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33354) | 33354 | ano 1961 |
| [LEI ORDINÁRIA Nº 610/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33135) | 33135 | ano 1961 |
| [LEI ORDINÁRIA Nº 609/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33158) | 33158 | ano 1961 |
| [LEI ORDINÁRIA Nº 608/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26887) | 26887 | ano 1961 |
| [LEI ORDINÁRIA Nº 603/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29851) | 29851 | ano 1960 |
| [LEI ORDINÁRIA Nº 600/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35144) | 35144 | ano 1960 |
| [LEI ORDINÁRIA Nº 590/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29645) | 29645 | ano 1960 |
| [LEI ORDINÁRIA Nº 587/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29441) | 29441 | ano 1960 |
| [LEI ORDINÁRIA Nº 579/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34773) | 34773 | ano 1960 |
| [LEI ORDINÁRIA Nº 578/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29086) | 29086 | ano 1960 |
| [LEI ORDINÁRIA Nº 573/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34693) | 34693 | ano 1960 |
| [LEI ORDINÁRIA Nº 572/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27913) | 27913 | ano 1960 |
| [LEI ORDINÁRIA Nº 571/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33535) | 33535 | ano 1960 |
| [LEI ORDINÁRIA Nº 570/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34663) | 34663 | ano 1960 |
| [LEI ORDINÁRIA Nº 556/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34690) | 34690 | ano 1960 |
| [LEI ORDINÁRIA Nº 552/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34703) | 34703 | ano 1960 |
| [LEI ORDINÁRIA Nº 551/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34702) | 34702 | ano 1960 |
| [LEI ORDINÁRIA Nº 540/1960](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34686) | 34686 | ano 1960 |
| [LEI ORDINÁRIA Nº 528/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34265) | 34265 | ano 1959 |
| [LEI ORDINÁRIA Nº 527/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29298) | 29298 | ano 1959 |
| [LEI ORDINÁRIA Nº 526/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34264) | 34264 | ano 1959 |
| [LEI ORDINÁRIA Nº 511/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33538) | 33538 | ano 1959 |
| [LEI ORDINÁRIA Nº 491/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29046) | 29046 | ano 1959 |
| [LEI ORDINÁRIA Nº 490/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28513) | 28513 | ano 1959 |
| [LEI ORDINÁRIA Nº 488/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34716) | 34716 | ano 1959 |
| [LEI ORDINÁRIA Nº 487/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34485) | 34485 | ano 1959 |
| [LEI ORDINÁRIA Nº 482/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29369) | 29369 | ano 1959 |
| [LEI ORDINÁRIA Nº 476/1958](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30198) | 30198 | ano 1958 |
| [LEI ORDINÁRIA Nº 472/1958](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34253) | 34253 | ano 1958 |
| [LEI ORDINÁRIA Nº 464/1958](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26562) | 26562 | ano 1958 |
| [LEI ORDINÁRIA Nº 448/1958](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34742) | 34742 | ano 1958 |
| [LEI ORDINÁRIA Nº 447/1958](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34741) | 34741 | ano 1958 |
| [LEI ORDINÁRIA Nº 446/1958](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34948) | 34948 | ano 1958 |
| [LEI ORDINÁRIA Nº 445/1958](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29460) | 29460 | ano 1958 |
| [LEI ORDINÁRIA Nº 412/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29315) | 29315 | ano 1957 |
| [LEI ORDINÁRIA Nº 404/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29125) | 29125 | ano 1957 |
| [LEI ORDINÁRIA Nº 401/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34782) | 34782 | ano 1957 |
| [LEI ORDINÁRIA Nº 383/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29036) | 29036 | ano 1957 |
| [LEI ORDINÁRIA Nº 382/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29212) | 29212 | ano 1957 |
| [LEI ORDINÁRIA Nº 381/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29639) | 29639 | ano 1957 |
| [LEI ORDINÁRIA Nº 379/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28599) | 28599 | ano 1957 |
| [LEI ORDINÁRIA Nº 378/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29094) | 29094 | ano 1957 |
| [LEI ORDINÁRIA Nº 377/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34763) | 34763 | ano 1957 |
| [LEI ORDINÁRIA Nº 376/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34762) | 34762 | ano 1957 |
| [LEI ORDINÁRIA Nº 363/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34759) | 34759 | ano 1957 |
| [LEI ORDINÁRIA Nº 360/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34945) | 34945 | ano 1956 |
| [LEI ORDINÁRIA Nº 359/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29135) | 29135 | ano 1956 |
| [LEI ORDINÁRIA Nº 358/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28713) | 28713 | ano 1956 |
| [LEI ORDINÁRIA Nº 357/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34794) | 34794 | ano 1956 |
| [LEI ORDINÁRIA Nº 355/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34793) | 34793 | ano 1956 |
| [LEI ORDINÁRIA Nº 354/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28562) | 28562 | ano 1956 |
| [LEI ORDINÁRIA Nº 353/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28703) | 28703 | ano 1956 |
| [LEI ORDINÁRIA Nº 352/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29317) | 29317 | ano 1956 |
| [LEI ORDINÁRIA Nº 351/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34791) | 34791 | ano 1956 |
| [LEI ORDINÁRIA Nº 350/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29259) | 29259 | ano 1956 |
| [LEI ORDINÁRIA Nº 349/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28903) | 28903 | ano 1956 |
| [LEI ORDINÁRIA Nº 348/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34790) | 34790 | ano 1956 |
| [LEI ORDINÁRIA Nº 347/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28770) | 28770 | ano 1956 |
| [LEI ORDINÁRIA Nº 346/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29137) | 29137 | ano 1956 |
| [LEI ORDINÁRIA Nº 345/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28857) | 28857 | ano 1956 |
| [LEI ORDINÁRIA Nº 344/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34777) | 34777 | ano 1956 |
| [LEI ORDINÁRIA Nº 343/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34775) | 34775 | ano 1956 |
| [LEI ORDINÁRIA Nº 342/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29012) | 29012 | ano 1956 |
| [LEI ORDINÁRIA Nº 341/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29767) | 29767 | ano 1956 |
| [LEI ORDINÁRIA Nº 340/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34774) | 34774 | ano 1956 |
| [LEI ORDINÁRIA Nº 339/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34252) | 34252 | ano 1956 |
| [LEI ORDINÁRIA Nº 338/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28791) | 28791 | ano 1956 |
| [LEI ORDINÁRIA Nº 336/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29216) | 29216 | ano 1956 |
| [LEI ORDINÁRIA Nº 335/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28949) | 28949 | ano 1956 |
| [LEI ORDINÁRIA Nº 334/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28609) | 28609 | ano 1956 |
| [LEI ORDINÁRIA Nº 333/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28462) | 28462 | ano 1956 |
| [LEI ORDINÁRIA Nº 332/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28704) | 28704 | ano 1956 |
| [LEI ORDINÁRIA Nº 331/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34771) | 34771 | ano 1956 |
| [LEI ORDINÁRIA Nº 330/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29790) | 29790 | ano 1956 |
| [LEI ORDINÁRIA Nº 329/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29213) | 29213 | ano 1956 |
| [LEI ORDINÁRIA Nº 328/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29276) | 29276 | ano 1956 |
| [LEI ORDINÁRIA Nº 327/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29290) | 29290 | ano 1956 |
| [LEI ORDINÁRIA Nº 326/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28984) | 28984 | ano 1956 |
| [LEI ORDINÁRIA Nº 325/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29037) | 29037 | ano 1956 |
| [LEI ORDINÁRIA Nº 324/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34770) | 34770 | ano 1956 |
| [LEI ORDINÁRIA Nº 323/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34746) | 34746 | ano 1956 |
| [LEI ORDINÁRIA Nº 322/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28758) | 28758 | ano 1956 |
| [LEI ORDINÁRIA Nº 321/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29123) | 29123 | ano 1956 |
| [LEI ORDINÁRIA Nº 320/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28790) | 28790 | ano 1956 |
| [LEI ORDINÁRIA Nº 318/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34803) | 34803 | ano 1956 |
| [LEI ORDINÁRIA Nº 316/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28724) | 28724 | ano 1956 |
| [LEI ORDINÁRIA Nº 315/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28611) | 28611 | ano 1956 |
| [LEI ORDINÁRIA Nº 314/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34919) | 34919 | ano 1956 |
| [LEI ORDINÁRIA Nº 313/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34802) | 34802 | ano 1956 |
| [LEI ORDINÁRIA Nº 312/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29827) | 29827 | ano 1956 |
| [LEI ORDINÁRIA Nº 311/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28828) | 28828 | ano 1956 |
| [LEI ORDINÁRIA Nº 310/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28659) | 28659 | ano 1956 |
| [LEI ORDINÁRIA Nº 309/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29706) | 29706 | ano 1956 |
| [LEI ORDINÁRIA Nº 308/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28893) | 28893 | ano 1956 |
| [LEI ORDINÁRIA Nº 307/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28426) | 28426 | ano 1956 |
| [LEI ORDINÁRIA Nº 306/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28517) | 28517 | ano 1956 |
| [LEI ORDINÁRIA Nº 305/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34801) | 34801 | ano 1956 |
| [LEI ORDINÁRIA Nº 304/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29047) | 29047 | ano 1956 |
| [LEI ORDINÁRIA Nº 303/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28830) | 28830 | ano 1956 |
| [LEI ORDINÁRIA Nº 302/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34800) | 34800 | ano 1956 |
| [LEI ORDINÁRIA Nº 301/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28744) | 28744 | ano 1956 |
| [LEI ORDINÁRIA Nº 300/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29191) | 29191 | ano 1956 |
| [LEI ORDINÁRIA Nº 299/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28817) | 28817 | ano 1956 |
| [LEI ORDINÁRIA Nº 298/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34799) | 34799 | ano 1956 |
| [LEI ORDINÁRIA Nº 297/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34283) | 34283 | ano 1956 |
| [LEI ORDINÁRIA Nº 296/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34798) | 34798 | ano 1956 |
| [LEI ORDINÁRIA Nº 295/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29559) | 29559 | ano 1956 |
| [LEI ORDINÁRIA Nº 293/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29107) | 29107 | ano 1956 |
| [LEI ORDINÁRIA Nº 292/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34781) | 34781 | ano 1956 |
| [LEI ORDINÁRIA Nº 291/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28838) | 28838 | ano 1956 |
| [LEI ORDINÁRIA Nº 290/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28195) | 28195 | ano 1955 |
| [LEI ORDINÁRIA Nº 289/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29705) | 29705 | ano 1955 |
| [LEI ORDINÁRIA Nº 288/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35088) | 35088 | ano 1955 |
| [LEI ORDINÁRIA Nº 287/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29020) | 29020 | ano 1955 |
| [LEI ORDINÁRIA Nº 286/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28590) | 28590 | ano 1955 |
| [LEI ORDINÁRIA Nº 285/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29939) | 29939 | ano 1955 |
| [LEI ORDINÁRIA Nº 284/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31387) | 31387 | ano 1955 |
| [LEI ORDINÁRIA Nº 283/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28551) | 28551 | ano 1955 |
| [LEI ORDINÁRIA Nº 282/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31168) | 31168 | ano 1955 |
| [LEI ORDINÁRIA Nº 281/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26849) | 26849 | ano 1955 |
| [LEI ORDINÁRIA Nº 280/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28471) | 28471 | ano 1955 |
| [LEI ORDINÁRIA Nº 279/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34776) | 34776 | ano 1955 |
| [LEI ORDINÁRIA Nº 278/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34553) | 34553 | ano 1955 |
| [LEI ORDINÁRIA Nº 277/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28628) | 28628 | ano 1955 |
| [LEI ORDINÁRIA Nº 276/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32614) | 32614 | ano 1955 |
| [LEI ORDINÁRIA Nº 275/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28714) | 28714 | ano 1955 |
| [LEI ORDINÁRIA Nº 274/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28818) | 28818 | ano 1955 |
| [LEI ORDINÁRIA Nº 273/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34780) | 34780 | ano 1955 |
| [LEI ORDINÁRIA Nº 272/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28577) | 28577 | ano 1955 |
| [LEI ORDINÁRIA Nº 271/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28664) | 28664 | ano 1955 |
| [LEI ORDINÁRIA Nº 270/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28797) | 28797 | ano 1955 |
| [LEI ORDINÁRIA Nº 269/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28408) | 28408 | ano 1955 |
| [LEI ORDINÁRIA Nº 268/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28690) | 28690 | ano 1955 |
| [LEI ORDINÁRIA Nº 267/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34792) | 34792 | ano 1955 |
| [LEI ORDINÁRIA Nº 266/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29730) | 29730 | ano 1955 |
| [LEI ORDINÁRIA Nº 265/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28926) | 28926 | ano 1955 |
| [LEI ORDINÁRIA Nº 264/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28644) | 28644 | ano 1955 |
| [LEI ORDINÁRIA Nº 263/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29567) | 29567 | ano 1955 |
| [LEI ORDINÁRIA Nº 262/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28610) | 28610 | ano 1955 |
| [LEI ORDINÁRIA Nº 261/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35118) | 35118 | ano 1955 |
| [LEI ORDINÁRIA Nº 260/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34812) | 34812 | ano 1955 |
| [LEI ORDINÁRIA Nº 259/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34294) | 34294 | ano 1955 |
| [LEI ORDINÁRIA Nº 258/1955](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28700) | 28700 | ano 1955 |
| [LEI ORDINÁRIA Nº 257/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34811) | 34811 | ano 1954 |
| [LEI ORDINÁRIA Nº 256/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28531) | 28531 | ano 1954 |
| [LEI ORDINÁRIA Nº 255/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28563) | 28563 | ano 1954 |
| [LEI ORDINÁRIA Nº 252/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34934) | 34934 | ano 1954 |
| [LEI ORDINÁRIA Nº 251/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34810) | 34810 | ano 1954 |
| [LEI ORDINÁRIA Nº 250/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28645) | 28645 | ano 1954 |
| [LEI ORDINÁRIA Nº 248/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34809) | 34809 | ano 1954 |
| [LEI ORDINÁRIA Nº 246/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34808) | 34808 | ano 1954 |
| [LEI ORDINÁRIA Nº 245/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28762) | 28762 | ano 1954 |
| [LEI ORDINÁRIA Nº 244/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28518) | 28518 | ano 1954 |
| [LEI ORDINÁRIA Nº 243/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34807) | 34807 | ano 1954 |
| [LEI ORDINÁRIA Nº 242/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28595) | 28595 | ano 1954 |
| [LEI ORDINÁRIA Nº 241/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28831) | 28831 | ano 1954 |
| [LEI ORDINÁRIA Nº 240/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29435) | 29435 | ano 1954 |
| [LEI ORDINÁRIA Nº 239/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28715) | 28715 | ano 1954 |
| [LEI ORDINÁRIA Nº 238/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28805) | 28805 | ano 1954 |
| [LEI ORDINÁRIA Nº 237/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34761) | 34761 | ano 1954 |
| [LEI ORDINÁRIA Nº 236/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28981) | 28981 | ano 1954 |
| [LEI ORDINÁRIA Nº 235/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28600) | 28600 | ano 1954 |
| [LEI ORDINÁRIA Nº 234/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28627) | 28627 | ano 1954 |
| [LEI ORDINÁRIA Nº 233/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28734) | 28734 | ano 1954 |
| [LEI ORDINÁRIA Nº 232/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29725) | 29725 | ano 1954 |
| [LEI ORDINÁRIA Nº 231/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29132) | 29132 | ano 1954 |
| [LEI ORDINÁRIA Nº 230/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36420) | 36420 | ano 1954 |
| [LEI ORDINÁRIA Nº 229/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33885) | 33885 | ano 1954 |
| [LEI ORDINÁRIA Nº 228/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34827) | 34827 | ano 1954 |
| [LEI ORDINÁRIA Nº 227/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28504) | 28504 | ano 1954 |
| [LEI ORDINÁRIA Nº 226/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28557) | 28557 | ano 1954 |
| [LEI ORDINÁRIA Nº 225/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28779) | 28779 | ano 1954 |
| [LEI ORDINÁRIA Nº 224/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28925) | 28925 | ano 1954 |
| [LEI ORDINÁRIA Nº 223/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28445) | 28445 | ano 1954 |
| [LEI ORDINÁRIA Nº 222/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29034) | 29034 | ano 1954 |
| [LEI ORDINÁRIA Nº 221/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28819) | 28819 | ano 1954 |
| [LEI ORDINÁRIA Nº 220/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28692) | 28692 | ano 1954 |
| [LEI ORDINÁRIA Nº 219/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28522) | 28522 | ano 1953 |
| [LEI ORDINÁRIA Nº 218/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29158) | 29158 | ano 1953 |
| [LEI ORDINÁRIA Nº 217/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29656) | 29656 | ano 1953 |
| [LEI ORDINÁRIA Nº 216/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33892) | 33892 | ano 1953 |
| [LEI ORDINÁRIA Nº 215/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34963) | 34963 | ano 1953 |
| [LEI ORDINÁRIA Nº 214/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28666) | 28666 | ano 1953 |
| [LEI ORDINÁRIA Nº 213/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29619) | 29619 | ano 1953 |
| [LEI ORDINÁRIA Nº 212/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34816) | 34816 | ano 1953 |
| [LEI ORDINÁRIA Nº 211/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35080) | 35080 | ano 1953 |
| [LEI ORDINÁRIA Nº 210/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28976) | 28976 | ano 1953 |
| [LEI ORDINÁRIA Nº 209/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34789) | 34789 | ano 1953 |
| [LEI ORDINÁRIA Nº 208/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34282) | 34282 | ano 1953 |
| [LEI ORDINÁRIA Nº 207/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28761) | 28761 | ano 1953 |
| [LEI ORDINÁRIA Nº 206/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28951) | 28951 | ano 1953 |
| [LEI ORDINÁRIA Nº 205/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28931) | 28931 | ano 1953 |
| [LEI ORDINÁRIA Nº 204/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34415) | 34415 | ano 1953 |
| [LEI ORDINÁRIA Nº 203/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34787) | 34787 | ano 1953 |
| [LEI ORDINÁRIA Nº 202/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28923) | 28923 | ano 1953 |
| [LEI ORDINÁRIA Nº 201/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35069) | 35069 | ano 1953 |
| [LEI ORDINÁRIA Nº 200/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28455) | 28455 | ano 1953 |
| [LEI ORDINÁRIA Nº 199/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28456) | 28456 | ano 1953 |
| [LEI ORDINÁRIA Nº 198/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28631) | 28631 | ano 1953 |
| [LEI ORDINÁRIA Nº 197/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28420) | 28420 | ano 1953 |
| [LEI ORDINÁRIA Nº 196/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28464) | 28464 | ano 1953 |
| [LEI ORDINÁRIA Nº 195/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28691) | 28691 | ano 1953 |
| [LEI ORDINÁRIA Nº 194/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34825) | 34825 | ano 1953 |
| [LEI ORDINÁRIA Nº 193/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34824) | 34824 | ano 1953 |
| [LEI ORDINÁRIA Nº 192/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34820) | 34820 | ano 1953 |
| [LEI ORDINÁRIA Nº 191/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34819) | 34819 | ano 1953 |
| [LEI ORDINÁRIA Nº 190/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28735) | 28735 | ano 1953 |
| [LEI ORDINÁRIA Nº 189/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32660) | 32660 | ano 1953 |
| [LEI ORDINÁRIA Nº 188/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29331) | 29331 | ano 1953 |
| [LEI ORDINÁRIA Nº 187/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28422) | 28422 | ano 1953 |
| [LEI ORDINÁRIA Nº 186/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28667) | 28667 | ano 1953 |
| [LEI ORDINÁRIA Nº 185/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28763) | 28763 | ano 1953 |
| [LEI ORDINÁRIA Nº 184/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28368) | 28368 | ano 1953 |
| [LEI ORDINÁRIA Nº 183/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28725) | 28725 | ano 1953 |
| [LEI ORDINÁRIA Nº 182/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34955) | 34955 | ano 1953 |
| [LEI ORDINÁRIA Nº 181/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29724) | 29724 | ano 1953 |
| [LEI ORDINÁRIA Nº 180/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28010) | 28010 | ano 1953 |
| [LEI ORDINÁRIA Nº 179/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32624) | 32624 | ano 1953 |
| [LEI ORDINÁRIA Nº 178/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34818) | 34818 | ano 1953 |
| [LEI ORDINÁRIA Nº 177/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29789) | 29789 | ano 1953 |
| [LEI ORDINÁRIA Nº 175/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29757) | 29757 | ano 1953 |
| [LEI ORDINÁRIA Nº 174/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34219) | 34219 | ano 1952 |
| [LEI ORDINÁRIA Nº 164/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34186) | 34186 | ano 1952 |
| [LEI ORDINÁRIA Nº 163/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34214) | 34214 | ano 1952 |
| [LEI ORDINÁRIA Nº 162/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34207) | 34207 | ano 1952 |
| [LEI ORDINÁRIA Nº 161/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34211) | 34211 | ano 1952 |
| [LEI ORDINÁRIA Nº 160/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28239) | 28239 | ano 1952 |
| [LEI ORDINÁRIA Nº 159/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28322) | 28322 | ano 1952 |
| [LEI ORDINÁRIA Nº 158/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28307) | 28307 | ano 1952 |
| [LEI ORDINÁRIA Nº 157/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28020) | 28020 | ano 1952 |
| [LEI ORDINÁRIA Nº 156/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28333) | 28333 | ano 1952 |
| [LEI ORDINÁRIA Nº 155/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28049) | 28049 | ano 1952 |
| [LEI ORDINÁRIA Nº 154/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28026) | 28026 | ano 1952 |
| [LEI ORDINÁRIA Nº 153/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33737) | 33737 | ano 1952 |
| [LEI ORDINÁRIA Nº 152/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33736) | 33736 | ano 1952 |
| [LEI ORDINÁRIA Nº 151/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28363) | 28363 | ano 1952 |
| [LEI ORDINÁRIA Nº 150/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28356) | 28356 | ano 1952 |
| [LEI ORDINÁRIA Nº 149/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28362) | 28362 | ano 1952 |
| [LEI ORDINÁRIA Nº 148/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28277) | 28277 | ano 1952 |
| [LEI ORDINÁRIA Nº 147/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28360) | 28360 | ano 1952 |
| [LEI ORDINÁRIA Nº 146/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28376) | 28376 | ano 1952 |
| [LEI ORDINÁRIA Nº 145/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28353) | 28353 | ano 1952 |
| [LEI ORDINÁRIA Nº 144/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27735) | 27735 | ano 1952 |
| [LEI ORDINÁRIA Nº 143/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28359) | 28359 | ano 1952 |
| [LEI ORDINÁRIA Nº 142/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28352) | 28352 | ano 1952 |
| [LEI ORDINÁRIA Nº 141/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28358) | 28358 | ano 1952 |
| [LEI ORDINÁRIA Nº 140/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28260) | 28260 | ano 1952 |
| [LEI ORDINÁRIA Nº 139/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28375) | 28375 | ano 1952 |
| [LEI ORDINÁRIA Nº 138/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28357) | 28357 | ano 1952 |
| [LEI ORDINÁRIA Nº 137/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28374) | 28374 | ano 1952 |
| [LEI ORDINÁRIA Nº 136/1952](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28373) | 28373 | ano 1952 |
| [LEI ORDINÁRIA Nº 134/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28332) | 28332 | ano 1951 |
| [LEI ORDINÁRIA Nº 133/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28331) | 28331 | ano 1951 |
| [LEI ORDINÁRIA Nº 132/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28330) | 28330 | ano 1951 |
| [LEI ORDINÁRIA Nº 131/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28329) | 28329 | ano 1951 |
| [LEI ORDINÁRIA Nº 130/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28355) | 28355 | ano 1951 |
| [LEI ORDINÁRIA Nº 129/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28354) | 28354 | ano 1951 |
| [LEI ORDINÁRIA Nº 128/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28351) | 28351 | ano 1951 |
| [LEI ORDINÁRIA Nº 127/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28350) | 28350 | ano 1951 |
| [LEI ORDINÁRIA Nº 126/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28348) | 28348 | ano 1951 |
| [LEI ORDINÁRIA Nº 125/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28345) | 28345 | ano 1951 |
| [LEI ORDINÁRIA Nº 124/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28268) | 28268 | ano 1951 |
| [LEI ORDINÁRIA Nº 123/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28157) | 28157 | ano 1951 |
| [LEI ORDINÁRIA Nº 122/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28224) | 28224 | ano 1951 |
| [LEI ORDINÁRIA Nº 121/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28343) | 28343 | ano 1951 |
| [LEI ORDINÁRIA Nº 120/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28342) | 28342 | ano 1951 |
| [LEI ORDINÁRIA Nº 119/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35183) | 35183 | ano 1951 |
| [LEI ORDINÁRIA Nº 118/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35182) | 35182 | ano 1951 |
| [LEI ORDINÁRIA Nº 117/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35181) | 35181 | ano 1951 |
| [LEI ORDINÁRIA Nº 116/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28341) | 28341 | ano 1951 |
| [LEI ORDINÁRIA Nº 115/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36373) | 36373 | ano 1951 |
| [LEI ORDINÁRIA Nº 114/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35184) | 35184 | ano 1951 |
| [LEI ORDINÁRIA Nº 113/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35180) | 35180 | ano 1951 |
| [LEI ORDINÁRIA Nº 112/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36372) | 36372 | ano 1951 |
| [LEI ORDINÁRIA Nº 111/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35179) | 35179 | ano 1951 |
| [LEI ORDINÁRIA Nº 110/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35119) | 35119 | ano 1951 |
| [LEI ORDINÁRIA Nº 109/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35164) | 35164 | ano 1951 |
| [LEI ORDINÁRIA Nº 108/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35176) | 35176 | ano 1951 |
| [LEI ORDINÁRIA Nº 107/1951](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35175) | 35175 | ano 1951 |
| [LEI ORDINÁRIA Nº 99/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35194) | 35194 | ano 1950 |
| [LEI ORDINÁRIA Nº 98/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30797) | 30797 | ano 1950 |
| [LEI ORDINÁRIA Nº 97/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30772) | 30772 | ano 1950 |
| [LEI ORDINÁRIA Nº 96/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36384) | 36384 | ano 1950 |
| [LEI ORDINÁRIA Nº 95/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36375) | 36375 | ano 1950 |
| [LEI ORDINÁRIA Nº 94/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36248) | 36248 | ano 1950 |
| [LEI ORDINÁRIA Nº 93/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36347) | 36347 | ano 1950 |
| [LEI ORDINÁRIA Nº 92/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36241) | 36241 | ano 1950 |
| [LEI ORDINÁRIA Nº 91/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36348) | 36348 | ano 1950 |
| [LEI ORDINÁRIA Nº 90/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36366) | 36366 | ano 1950 |
| [LEI ORDINÁRIA Nº 89/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30802) | 30802 | ano 1950 |
| [LEI ORDINÁRIA Nº 88/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36158) | 36158 | ano 1950 |
| [LEI ORDINÁRIA Nº 87/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36367) | 36367 | ano 1950 |
| [LEI ORDINÁRIA Nº 86/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36365) | 36365 | ano 1950 |
| [LEI ORDINÁRIA Nº 85/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36346) | 36346 | ano 1950 |
| [LEI ORDINÁRIA Nº 84/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36358) | 36358 | ano 1950 |
| [LEI ORDINÁRIA Nº 83/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36364) | 36364 | ano 1950 |
| [LEI ORDINÁRIA Nº 82/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30673) | 30673 | ano 1950 |
| [LEI ORDINÁRIA Nº 81/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30798) | 30798 | ano 1950 |
| [LEI ORDINÁRIA Nº 80/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30042) | 30042 | ano 1950 |
| [LEI ORDINÁRIA Nº 79/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30800) | 30800 | ano 1950 |
| [LEI ORDINÁRIA Nº 78/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30784) | 30784 | ano 1950 |
| [LEI ORDINÁRIA Nº 106/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/36370) | 36370 | ano 1950 |
| [LEI ORDINÁRIA Nº 105/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35163) | 35163 | ano 1950 |
| [LEI ORDINÁRIA Nº 104/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35178) | 35178 | ano 1950 |
| [LEI ORDINÁRIA Nº 103/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34873) | 34873 | ano 1950 |
| [LEI ORDINÁRIA Nº 102/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35200) | 35200 | ano 1950 |
| [LEI ORDINÁRIA Nº 101/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35199) | 35199 | ano 1950 |
| [LEI ORDINÁRIA Nº 100/1950](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35198) | 35198 | ano 1950 |
| [LEI ORDINÁRIA Nº 61/1949](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30780) | 30780 | ano 1949 |
| [LEI ORDINÁRIA Nº 5/1948](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30709) | 30709 | ano 1948 |
| [LEI ORDINÁRIA Nº 42/1948](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30703) | 30703 | ano 1948 |

<a id="data-impossivel"></a>
## Data impossível no texto (1 leis)

**O que aconteceu:** O texto traz uma data que não existe no calendário (ex.: "29 de fevereiro de 2010").

**Solução:** A data impossível não entra em `data_lei`: fica em `data_lei_original` para revisão. O script tenta a próxima fonte (anexo); `data_lei_fonte` diz de onde veio a data usada.

| Lei | id | Detalhe |
|---|---|---|
| [LEI ORDINÁRIA Nº 10887/2010](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39337) | 39337 | texto: 2010-02-29 → usada: 2010-03-29 (anexo) |

<a id="autorrelacao"></a>
## Relação da lei com ela mesma (25 leis)

**O que aconteceu:** Na seção "Relacionamentos desta Matéria", a própria Câmara lista a lei como "Revoga", "Altera" ou "Revogada por" ela mesma.

**Solução:** A relação é descartada em `relacoes` (usada para a vigência). A lista crua `relacionamentos` continua como veio da fonte.

| Lei | id | Detalhe |
|---|---|---|
| [LEI ORDINÁRIA Nº 9282/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32854) | 32854 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8942/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33184) | 33184 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8877/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33358) | 33358 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8843/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33529) | 33529 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8792/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33510) | 33510 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8749/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33671) | 33671 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8734/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33602) | 33602 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8733/2002](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/33612) | 33612 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8681/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29503) | 29503 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8679/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29505) | 29505 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8678/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29524) | 29524 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8677/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29508) | 29508 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8676/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29518) | 29518 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8675/2001](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29514) | 29514 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8267/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28930) | 28930 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8253/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28892) | 28892 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8106/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28662) | 28662 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8104/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28673) | 28673 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8096/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/27999) | 27999 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8095/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32612) | 32612 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 8081/2000](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/28698) | 28698 | Câmara lista: Revoga: ela mesma |
| [LEI ORDINÁRIA Nº 2851/1977](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/39118) | 39118 | Câmara lista: Altera: ela mesma |
| [LEI ORDINÁRIA Nº 1927/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38279) | 38279 | Câmara lista: Altera: ela mesma |
| [LEI ORDINÁRIA Nº 1359/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37762) | 37762 | Câmara lista: Altera: ela mesma |
| [LEI ORDINÁRIA Nº 374/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29087) | 29087 | Câmara lista: Altera: ela mesma |

<a id="anotacao-numero-errado"></a>
## Anotação de revogação cita a própria lei (2 leis)

**O que aconteceu:** A anotação "(REVOGADA pelo ... da Lei nº X ...)" traz como revogador o número da própria lei (erro de digitação na fonte).

**Solução:** A lei continua `revogada` (a anotação existe), mas o número errado não vira relação. A anotação original fica em `revogacao_nota`; o revogador correto, quando a Câmara o lista nos Relacionamentos, entra em `revogada_por`.

| Lei | id | Detalhe |
|---|---|---|
| [LEI ORDINÁRIA Nº 9265/2003](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/32757) | 32757 | (REVOGADA pelo Art. 14 da Lei nº 9.265 de 8 de dezembro de 2018) → revogada_por: ['12232'] |
| [LEI ORDINÁRIA Nº 6135/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35691) | 35691 | (REVOGADA pelo art. 1º da Lei nº 6.135, de 10 de maio de 1995) → revogada_por: — |

<a id="revogada-sem-revogador"></a>
## Revogada sem lei revogadora identificável (2 leis)

**O que aconteceu:** A anotação de revogação veio quebrada da fonte (ex.: "Lei nº de de de 20") ou cita a própria lei. Anotações que citam só decreto não contam: decreto não revoga lei, e essas notas falam de outro decreto citado na ementa (caso da Lei 13.905/2024, que continua vigente).

**Solução:** `situacao = revogada` e `revogada_por` vazio. A anotação original fica em `revogacao_nota` como evidência.

| Lei | id | Detalhe |
|---|---|---|
| [LEI ORDINÁRIA Nº 6884/1996](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40348) | 40348 | (REVOGADA pelo Art. da Lei nº de de de 20) |
| [LEI ORDINÁRIA Nº 6135/1995](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/35691) | 35691 | (REVOGADA pelo art. 1º da Lei nº 6.135, de 10 de maio de 1995) |

<a id="ementa-vazia"></a>
## Ementa vazia na API (3 leis)

**O que aconteceu:** A API devolveu a ementa (súmula) em branco.

**Solução:** Quando o texto traz "SÚMULA:", ela é usada (`ementa_fonte = "texto"`). Senão, `ementa = null` (`ementa_fonte = null`).

| Lei | id | Detalhe |
|---|---|---|
| [LEI N.º 13960, DE 14 DE JULHO DE 2025](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/249902) | 249902 | ementa = null |
| [LEI N.º 13883, DE 03 DE DEZEMBRO DE 2024](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/221928) | 221928 | súmula tirada do texto |
| [LEI ORDINÁRIA Nº 2677/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40861) | 40861 | ementa = null |

<a id="promulgacao-veto"></a>
## Promulgação de partes vetadas com o mesmo número (1 leis)

**O que aconteceu:** Trechos vetados pelo prefeito e promulgados depois pela Câmara aparecem como outra "lei" com o mesmo número, o que parecia duplicata.

**Solução:** `tipo = "Promulgação de partes vetadas"` e `complementa_id` apontando para a lei principal. Os artigos fazem parte da lei principal e seguem a situação dela.

| Lei | id | Detalhe |
|---|---|---|
| [LEI N.º 13960, DE 14 DE JULHO DE 2025](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/249902) | 249902 | complementa_id: 242406 |

<a id="numero-repetido"></a>
## Leis diferentes com o mesmo número (7 leis)

**O que aconteceu:** Duas matérias distintas registradas com o mesmo número e ano.

**Solução:** O identificador é o `id` da Câmara (único). `chave`/`numero` não podem ser chave primária nem `UNIQUE`.

| Lei | id | Detalhe |
|---|---|---|
| [LEI N.º 13960, DE 14 DE JULHO DE 2025](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/242406) | 242406 | mesmo número que id 249902 |
| [LEI ORDINÁRIA Nº 1641/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37980) | 37980 | mesmo número que id 38011 |
| [LEI ORDINÁRIA Nº 1641/1970](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38011) | 38011 | mesmo número que id 37980 |
| [LEI ORDINÁRIA Nº 1041/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37446) | 37446 | mesmo número que id 37467 |
| [LEI ORDINÁRIA Nº 1041/1965](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37467) | 37467 | mesmo número que id 37446 |
| [LEI ORDINÁRIA Nº 48/1949](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30755) | 30755 | mesmo número que id 30749 |
| [LEI ORDINÁRIA Nº 48/1949](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30749) | 30749 | mesmo número que id 30755 |

<a id="so-pdf"></a>
## Lei só com PDF (sem texto em HTML) (18 leis)

**O que aconteceu:** A página não tem o texto da lei, só um PDF anexado.

**Solução:** `texto_disponivel = false`, `artigos` vazio e o link do PDF em `anexos`. Não entra na busca por artigo; a leitura dos PDFs é um próximo passo.

| Lei | id | Detalhe |
|---|---|---|
| [LEI ORDINÁRIA Nº 5933/1994](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26540) | 26540 | https://www.cloudsoftcam.com.br/PR/LONDRINA/importacao/1994/236_lei_ordinaria_n_5933_1994.pdf |
| [LEI ORDINÁRIA Nº 3419/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40076) | 40076 | sem link de PDF |
| [LEI ORDINÁRIA Nº 3418/1981](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26832) | 26832 | sem link de PDF |
| [LEI ORDINÁRIA Nº 3078/1979](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/31742) | 31742 | https://www.cloudsoftcam.com.br/PR/LONDRINA/importacao/1979/200_lei_ordinaria_n_3078_1979.pdf |
| [LEI ORDINÁRIA Nº 2694/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38968) | 38968 | https://www.cloudsoftcam.com.br/PR/LONDRINA/importacao/1976/196_lei_ordinaria_n_2694_1976.pdf |
| [LEI ORDINÁRIA Nº 2677/1976](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/40861) | 40861 | sem link de PDF |
| [LEI ORDINÁRIA Nº 2176/1972](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38518) | 38518 | https://www.cloudsoftcam.com.br/PR/LONDRINA/importacao/1972/194_lei_ordinaria_n_2176_1972.pdf |
| [LEI ORDINÁRIA Nº 1819/1971](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/38177) | 38177 | sem link de PDF |
| [LEI ORDINÁRIA Nº 927/1964](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/37318) | 37318 | sem link de PDF |
| [LEI ORDINÁRIA Nº 670/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26925) | 26925 | https://www.cloudsoftcam.com.br/PR/LONDRINA/importacao/1961/177_lei_ordinaria_n_670_1961.pdf |
| [LEI ORDINÁRIA Nº 526/1959](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34264) | 34264 | sem link de PDF |
| [LEI ORDINÁRIA Nº 412/1957](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29315) | 29315 | sem link de PDF |
| [LEI ORDINÁRIA Nº 360/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34945) | 34945 | sem link de PDF |
| [LEI ORDINÁRIA Nº 355/1956](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/34793) | 34793 | sem link de PDF |
| [LEI ORDINÁRIA Nº 247/1954](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26681) | 26681 | https://www.cloudsoftcam.com.br/PR/LONDRINA/importacao/1954/168_lei_ordinaria_n_247_1954.pdf |
| [LEI ORDINÁRIA Nº 175/1953](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/29757) | 29757 | sem link de PDF |
| [LEI ORDINÁRIA Nº 68/1949](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30791) | 30791 | sem link de PDF |
| [LEI ORDINÁRIA Nº 21/1948](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30729) | 30729 | sem link de PDF |

<a id="inexistente"></a>
## Número de lei inexistente (5 leis)

**O que aconteceu:** A página diz "LEI INEXISTENTE": o número ficou vago.

**Solução:** `situacao = "inexistente"` e `texto_disponivel = false`. Não entra na busca.

| Lei | id | Detalhe |
|---|---|---|
| [LEI ORDINÁRIA Nº 3985/1987](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30197) | 30197 | LEI INEXISTENTE |
| [LEI ORDINÁRIA Nº 2424/1974](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30173) | 30173 | LEI INEXISTENTE |
| [LEI ORDINÁRIA Nº 1374/1968](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30172) | 30172 | LEI INEXISTENTE |
| [LEI ORDINÁRIA Nº 681/1961](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/26833) | 26833 | LEI INEXISTENTE |
| [LEI ORDINÁRIA Nº 476/1958](https://www.cml.pr.gov.br/proposicoes/0/0/0/0/30198) | 30198 | LEI INEXISTENTE |

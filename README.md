# hackathon2026

Projeto do Hackathon Smart Cities Londrina 2026: um assistente de consulta à legislação municipal de Londrina que responde sempre com base na **lei vigente mais recente**, e não em uma lei já revogada ou alterada.

> Exemplo que motivou o projeto: a Lei nº 14.294, de 29/10/2026, instituiu o novo Código Ambiental de Londrina e revogou a Lei nº 11.471/2012. Uma pergunta sobre regra ambiental precisa ser respondida com a lei de 2026, não com a de 2012.

## Estrutura

| Arquivo | O que é |
|---|---|
| `coleta_leis.py` | Baixa as leis da API da Câmara Municipal de Londrina (CML), extrai texto, artigos e relações "altera/revoga" e salva em `leis.json` |
| `.env.example` | Modelo do arquivo de configuração com o token da API |
| `hello.py` | Arquivo de teste |

Arquivos gerados que não vão para o git: `.env`, `leis.json` e `cache_textos/`.

## Como rodar

Requisitos: Python 3.10 ou superior.

```bash
pip install requests beautifulsoup4 python-dotenv
cp .env.example .env    # depois coloque o token real da CML no .env
```

```bash
python coleta_leis.py --paginas 2 --texto   # teste rápido: 100 leis com texto (~1 min)
python coleta_leis.py                        # lista completa, só ementas (~5 min)
python coleta_leis.py --texto                # tudo com texto e relações oficiais (~2 h)
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
- O título tem dois formatos. As leis recentes (umas 420) vêm como `LEI N.º 14294, DE 29 DE OUTUBRO DE 2026`, com a data completa. As antigas vêm como `LEI ORDINÁRIA Nº 11341/2011`, só com o ano; nesse caso a data é tirada do texto da lei. Algumas leis antigas têm letra no número (`520 - A`, `1666 A`).
- **Revogação total vem anotada na ementa** pela própria CML: `... (REVOGADA pelo art. 270. da Lei nº 12.236, de 29 de janeiro de 2015)`. Cerca de 1.300 leis têm essa anotação.

### Página de cada lei (`link`)

- Traz o texto completo em HTML (não precisa de PDF).
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
  "situacao": "vigente",
  "altera": [],
  "alterada_por": [],
  "revoga": ["11471"],
  "revogada_por": [],
  "relacoes": [
    { "tipo": "revoga", "id": "35210", "chave": "11471" }
  ],
  "fonte_relacoes": "cml",
  "relacionamentos": [
    { "tipo": "Revoga", "id": "35210", "descricao": "LEI ORDINÁRIA Nº 11471/2012 Institui o Código Ambiental ..." }
  ],
  "artigos": [{ "ordem": 1, "artigo": "Art. 1º", "texto": "Art. 1º ..." }]
}
```

- `id` é o identificador da CML e é único. `chave` é o número legível: `14294`, `520-A` ou, para lei complementar, `LC-12`. Existem 4 casos de leis diferentes com o mesmo número (por exemplo, duas Leis nº 48 de 1949).
- `altera`, `alterada_por`, `revoga` e `revogada_por` são listas de `chave`, para leitura humana.
- `relacoes` traz as mesmas relações **por `id`**, para o banco: `tipo` é `altera`, `alterada_por`, `revoga` ou `revogada_por`. `id` é `null` quando a lei citada não está no arquivo (por exemplo, uma lei complementar).
- `artigos[].ordem` é a posição do artigo no texto e é única dentro da lei. O rótulo `artigo` pode se repetir, porque leis que alteram outras citam o artigo novo entre aspas.
- `relacionamentos` é a lista crua da seção oficial da CML, com todos os rótulos (inclusive `Cita`, `Sanção`, `Vínculo`).

### Sugestão de tabelas (Postgres)

| Tabela | Colunas principais | Chave |
|---|---|---|
| `lei` | `id`, `chave`, `numero`, `data_lei`, `ano`, `titulo`, `ementa`, `link`, `situacao` | `id` |
| `artigo` | `lei_id`, `ordem`, `artigo`, `texto` | `(lei_id, ordem)` |
| `relacao` | `lei_origem_id`, `lei_destino_id` (aceita nulo), `chave_destino`, `tipo` | — |

Não use `chave`/`numero` como chave primária: existem leis diferentes com o mesmo número.
- `situacao` pode ser `vigente`, `vigente_com_alteracoes` ou `revogada`.
- `fonte_relacoes` é `cml` quando as relações vieram da seção oficial e `ementa` quando foram deduzidas da ementa (coleta sem `--texto`).
- `relacionamentos` e `artigos` só são preenchidos com `--texto`.

## Como a vigência é calculada

1. **Revogada:** a ementa tem a anotação oficial `(REVOGADA pelo ... Lei nº X ...)`. A lei X vai para `revogada_por`.
2. **Relações:** com `--texto`, vêm da seção oficial "Relacionamentos desta Matéria". Sem `--texto`, são deduzidas da ementa: quando ela começa com "Altera", "Insere", "Acrescenta", "Introduz alterações", "Dá nova redação", "Modifica" ou "Revoga", as leis citadas entram em `altera`, e o lado inverso (`alterada_por`) é preenchido automaticamente.
3. **Vigente com alterações:** a lei não está revogada, mas tem `alterada_por` ou `revogada_por` (revogação parcial).
4. **Vigente:** nenhum dos casos acima.

Resultado com a lista completa (só ementas): 12.335 vigentes, 675 vigentes com alterações e 1.298 revogadas. O caso da demo já sai certo: a 11.471 fica `revogada` com `revogada_por: ["14294"]`.

## Limitações conhecidas

- Sem `--texto`, as alterações são deduzidas da ementa e podem ter falsos positivos ou negativos. Com `--texto`, valem as relações oficiais da CML.
- A situação é da lei inteira. O sistema ainda não sabe **quais artigos** foram alterados ou revogados parcialmente.
- Em 3 leis revogadas, `revogada_por` fica vazio: uma cita um decreto como revogador e duas têm erro de digitação na anotação da CML (por exemplo, "Lei nº de 10.037").
- Requisições com `curl` são bloqueadas pelo site (406 Not Acceptable). O script em Python funciona normalmente; se ele receber 406, mostra um aviso.

## Próximos passos

- [x] Verificar "Relacionamentos desta Matéria" como fonte oficial das relações
- [ ] Rodar a coleta completa com texto
- [ ] Incluir leis complementares, Lei Orgânica e Emendas à Lei Orgânica (outros tipos da API)
- [ ] Montar a busca e o assistente em cima do `leis.json`, filtrando leis revogadas

# Como funciona a coleta de leis

Guia passo a passo do [`coleta_leis.py`](../coleta_leis.py), para quem precisar entender ou mexer no código. As funções citadas aqui têm o mesmo nome no script, e o próprio script é comentado etapa por etapa.

## Sumário

0. [Visão geral](#0-visão-geral)
1. [Configuração](#1-configuração)
2. [Etapa 1: listar as leis pela API](#2-etapa-1-listar-as-leis-pela-api)
3. [Etapa 2: ler o título e a ementa](#3-etapa-2-ler-o-título-e-a-ementa)
4. [Etapa 3: baixar a página de cada lei](#4-etapa-3-baixar-a-página-de-cada-lei)
5. [Etapa 4: tratar o texto](#5-etapa-4-tratar-o-texto)
6. [Etapa 5: ligar as leis e calcular a vigência](#6-etapa-5-ligar-as-leis-e-calcular-a-vigência)
7. [Etapa 6: juntar tudo (`main`)](#7-etapa-6-juntar-tudo-main)
8. [Problemas encontrados e soluções](#8-problemas-encontrados-e-soluções)
9. [Como isso se conecta ao resto do projeto](#9-como-isso-se-conecta-ao-resto-do-projeto)
10. [Perguntas frequentes](#10-perguntas-frequentes)

---

## 0. Visão geral

**O problema:** quem consulta leis municipais muitas vezes acaba usando uma lei que já foi revogada ou alterada. O chatbot do projeto precisa responder sempre com a lei **que vale hoje**.

**O que o script faz:** baixa todas as leis de Londrina, descobre quem alterou ou revogou quem e salva tudo num formato organizado (`leis.json`). Esse arquivo é a base do banco e do chatbot.

```
API da Câmara ──► lista das 14.308 leis (número, título, ementa, link)     [Etapa 1]
                          │
                          ▼
Título e ementa ──► número, data, ano, "(REVOGADA pelo ...)"              [Etapa 2]
                          │
                          ▼
Página de cada lei ──► texto completo + "Relacionamentos desta Matéria"   [Etapa 3]
                          │
                          ▼
Tratamento ──► rodapé removido, data da lei, artigos separados            [Etapa 4]
                          │
                          ▼
Ligação entre as leis ──► quem altera/revoga quem + situação              [Etapa 5]
                          │
                          ▼
                     leis.json  (→ leis.zip no repositório)               [Etapa 6]
```

---

## 1. Configuração

| Arquivo | Para que serve |
|---|---|
| `.env` | Guarda o token da API (`CML_TOKEN=...`). **Não vai para o git**, porque funciona como uma senha. |
| `.env.example` | Modelo do `.env` com um valor de exemplo no lugar do token. Quem clonar copia para `.env` e preenche. |
| `.gitignore` | Diz ao git o que ignorar: `.env`, `leis.json`, `cache_textos/` e `*.zip` (o `leis.zip` foi adicionado com `git add -f`). |

| Biblioteca | Para que serve |
|---|---|
| `requests` | Faz as requisições HTTP: chama a API e baixa as páginas. |
| `beautifulsoup4` | Lê o HTML das páginas e permite buscar partes dele. |
| `python-dotenv` | Lê o arquivo `.env`. |

```python
load_dotenv()                      # lê o arquivo .env
TOKEN = os.getenv("CML_TOKEN")     # pega o token
PAUSA = 0.5                        # meio segundo entre requisições, para não sobrecarregar o site
CACHE = Path("cache_textos")       # cada lei baixada fica salva aqui
```

---

## 2. Etapa 1: listar as leis pela API

### `baixar()`: download com novas tentativas

Na primeira coleta completa, o site demorou a responder e o script inteiro caiu. Por isso todo download passa por uma função que **tenta de novo** quando dá erro de rede:

```python
def baixar(url, tentativas=5, **kwargs):
    for n in range(tentativas):
        try:
            r = requests.get(url, headers=HEADERS, timeout=90, **kwargs)
            if r.status_code == 406:          # firewall bloqueou: não adianta tentar de novo
                raise SystemExit("O site respondeu 406 ...")
            if r.status_code < 500:           # deu certo (ou erro "definitivo", como 404)
                r.raise_for_status()
                return r
            erro = requests.HTTPError(...)    # erro 5xx: problema no servidor, tenta de novo
        except (requests.ConnectionError, requests.Timeout) as e:
            erro = e                          # caiu a conexão ou passou do tempo limite
        if n < tentativas - 1:
            time.sleep(5 * 2 ** n)            # espera 5s, 10s, 20s, 40s
    raise erro
```

A espera dobra a cada falha. Isso se chama **backoff exponencial**: dá tempo para o servidor se recuperar sem ficar martelando.

### `listar_leis()`: percorrer as páginas

A API devolve **50 leis por página**, da mais nova para a mais antiga. O script pede a página 1, 2, 3... até vir uma página vazia:

```python
def listar_leis(tipo="Leis", max_paginas=None):
    pagina, leis, vistos = 1, [], set()
    while True:
        dados = chamar_api("legislacoes", tipo=tipo, pagina=pagina)
        if not dados:                        # página vazia = acabou
            break
        for item in dados:
            if item["link"] not in vistos:   # evita duplicar
                vistos.add(item["link"])
                leis.append(item)
        pagina += 1
        time.sleep(PAUSA)
    return leis
```

**Por que o `vistos`?** Se a Câmara publicar uma lei nova **durante** a coleta, todas as leis "andam" uma posição, e a última da página 5 reaparece na página 6.

Cada item da API vem assim:

```json
{
  "data": "2026-11-04 18:44:30",
  "titulo": "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026",
  "ementa": "SÚMULA: Institui o Código Ambiental do Município de Londrina.",
  "autoria": "",
  "link": "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/296902#pesquisa"
}
```

O campo `data` é quando a lei **entrou no site**, não a data da lei. A data real vem do título ou do texto.

---

## 3. Etapa 2: ler o título e a ementa

Aqui entram as **expressões regulares** (regex): padrões para encontrar pedaços de texto. Um lembrete rápido:

| Símbolo | Significa |
|---|---|
| `\d` | um dígito |
| `\s` | um espaço (ou quebra de linha) |
| `*` / `+` / `?` | zero ou mais / um ou mais / opcional |
| `[abc]` | um dos caracteres a, b ou c |
| `(...)` | **grupo**: o pedaço que queremos capturar |
| `(?:...)` | grupo que só agrupa, sem capturar |
| `^` | começo da linha |
| `re.I` | ignora maiúsculas e minúsculas |

### `parse_titulo()`: os dois formatos de título

| Formato | Quantas | Exemplo |
|---|---|---|
| Recente | ~420 | `LEI N.º 14294, DE 29 DE OUTUBRO DE 2026` |
| Antigo | ~13.900 | `LEI ORDINÁRIA Nº 11341/2011` |
| Com letra | poucas | `LEI N.º 520 - A, DE 8 DE DEZEMBRO DE 1959` |

```python
RE_NUMERO = re.compile(r"\bN[\.º°o\s]*\s*(\d[\d\.]*\d|\d)(?:\s*-?\s*([A-Z])\b)?", re.I)
```

- `\bN[\.º°o\s]*` encontra "N", "Nº", "N.º" ou "No".
- `(\d[\d\.]*\d|\d)` é o **grupo 1**: o número, que pode ter ponto ("13.939").
- `(?:\s*-?\s*([A-Z])\b)?` é o **grupo 2**, opcional: a letra (" - A", "- A", " A").

| Entrada | Saída `(numero, data, ano, complementar)` |
|---|---|
| `LEI N.º 14294, DE 29 DE OUTUBRO DE 2026` | `("14294", "2026-10-29", "2026", False)` |
| `LEI ORDINÁRIA Nº 11341/2011` | `("11341", None, "2011", False)`: a data vem do texto na Etapa 4 |
| `LEI N.º 520 - B, DE 8 DE DEZEMBRO DE 1959` | `("520-B", "1959-12-08", "1959", False)` |

### `revogacao_na_ementa()`: a revogação vem escrita na ementa

A própria Câmara escreve na ementa quando uma lei foi revogada **por inteiro**:

> Institui o Código Ambiental do Município de Londrina. **(REVOGADA pelo Art. 225. da Lei nº 14.294, de 29 de outubro de 2026)**

```python
RE_ANOTACAO_REVOGADA = re.compile(r"\(\s*REVOGAD[AO]\b([^()]*)\)", re.I)

def revogacao_na_ementa(ementa):
    m = RE_ANOTACAO_REVOGADA.search(ementa)   # acha o "(REVOGADA ...)"
    if not m:
        return None                           # não está revogada
    return sorted(refs_leis(m.group(1)))      # "Lei nº 14.294" → ["14294"]
```

O `RE_REF_LEI` (usado por `refs_leis`) encontra menções como "Lei nº 14.294", "Lei Municipal nº 11.054" e "Lei 13.106". O "nº" é opcional porque muitas anotações escrevem "da Lei 13.106".

### `altera_pela_ementa()`: plano B

Sem baixar o texto, dá para deduzir as alterações pela ementa. Se ela **começa** com "Altera", "Insere", "Acrescenta" etc., as leis citadas são as alteradas:

- `"Altera a Lei Municipal nº 11.054, de 2010"` → `["11054"]`
- `"Institui o Código Ambiental"` → `[]`

### `montar_registro()`: o registro inicial

Junta tudo isso num dicionário por lei. O ponto mais importante:

> **`id` (ex.: `"296902"`, tirado do fim do link) é o identificador único.** `chave` e `numero` **não** são únicos: existem leis diferentes com o mesmo número, como duas Leis nº 48 de 1949. No banco, a chave primária deve ser o `id`.

---

## 4. Etapa 3: baixar a página de cada lei

A página de cada lei traz o que a API não traz: o **texto completo** e a seção oficial **"Relacionamentos desta Matéria"**.

### `extrair_texto()`

O texto da lei fica entre o botão "pasta digital" e o trecho "Protocolos desta Publicação":

```python
texto = limpar(soup.get_text("\n"))           # todo o texto visível da página
texto = texto[texto.find("pasta digital") + len("pasta digital"):]
texto = texto[:texto.find("Protocolos desta Publicação")]
```

A `limpar()` troca o `\xa0`, um espaço especial que o site usa, por espaço normal.

### `extrair_relacionamentos()`

No HTML, cada relação é um link assim:

```html
<a href=".../proposicoes/0/0/1/0/35210" class="menu-opcoes__items">
  <strong>05/01/2012 00:00 - Revoga: </strong>LEI ORDINÁRIA Nº 11471/2012 ...
</a>
```

```python
for a in soup.select("#menu_opcao_proposicao_relacionamentos a.menu-opcoes__items"):
    cabecalho = a.find("strong").get_text(" ", strip=True)   # "05/01/2012 00:00 - Revoga:"
    tipo = cabecalho.split(" - ", 1)[-1].rstrip(":")         # "Revoga"
    id_ = a["href"].rstrip("/").split("/")[-1]                # "35210", o id da outra lei
```

O `soup.select(...)` usa **seletores CSS**: `#id a.classe` quer dizer "links com essa classe dentro do elemento com esse id". Os rótulos que aparecem são Altera, Alterada por, Revoga, Revogada por, Cita, Citada por, Sanção, Promulgação e Vínculo.

### `baixar_pagina()`: o cache

```python
arq = CACHE / f"{id_}.json"
if arq.exists():                    # já baixei antes? usa o arquivo salvo
    return json.loads(arq.read_text(encoding="utf-8"))
r = baixar(link)
...
arq.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")   # salva
```

Cada lei vira `cache_textos/<id>.json`. Isso permite:
1. **retomar** a coleta se ela cair no meio;
2. **mudar o tratamento** do texto (Etapas 4 e 5) e gerar o `leis.json` de novo em ~5 min, sem baixar as 14 mil páginas outra vez.

### Três downloads ao mesmo tempo

```python
with ThreadPoolExecutor(max_workers=3) as pool:
    for i, _ in enumerate(pool.map(adicionar_texto, leis), 1):
        ...
```

Com 3 downloads simultâneos, a coleta completa cai de ~6 h para **~1h10**. Não usamos mais que 3 para não sobrecarregar o site da Câmara.

---

## 5. Etapa 4: tratar o texto

### `processar_texto()`: rodapé e data da lei

Dois problemas apareceram ao conferir o resultado:

- Nas páginas antigas, o **rodapé do site** ("Certidão de Utilidade Pública, Pautas, LGPD...") entrava no texto da lei.
- **Leis antigas não têm data no título.** A primeira tentativa pegava "a primeira data do texto", e na 11.471 isso dava 2026, a data da anotação de revogação. Errado.

A data passou a vir da **assinatura** no fim da lei, que aparece em vários formatos:

| Formato | Exemplo |
|---|---|
| Recente | `Londrina, 5 de janeiro de 2012.` |
| Antigo | `EDIFÍCIO DA PREFEITURA DO MUNICÍPIO DE LONDRINA, aos 3 de julho de 1970.` |
| Ano com ponto | `Londrina, 14 de novembro de 1.991.` |
| Só PDF | `Anexos (1)` seguido de `18/10/1994 00:00 -` |

Por segurança, a data só é aceita **se o ano bater com o do título** (em `adicionar_texto`):

```python
for data in (data_assinatura, data_anexo):
    if data and (not registro["ano"] or data[:4] == registro["ano"]):
        registro["data_lei"] = data
        break
```

A regra foi testada nas 425 leis que já têm data no título: acertou 418 (~98%). As leis sem data caíram de 9.879 para 837, e todas têm pelo menos o `ano`.

### `separar_artigos()`

```python
RE_ARTIGO = re.compile(r"(?m)^\s*(Art\.\s*\d+[º°o]?[A-Z\-]*\.?)")   # "Art. 1º", "Art. 225.", "Art. 5º-A"
```

- `(?m)^` exige que "Art." esteja **no começo de uma linha**. Assim, "conforme o art. 5º" no meio de uma frase não vira um artigo novo.
- Algumas leis vieram com o texto todo numa linha só. Antes de separar, o script quebra a linha antes de "Art. N" quando ele vem depois de ".", ":" ou ";".
- `RE_ARTIGO.split(texto)` devolve `[antes, "Art. 1º", corpo1, "Art. 2º", corpo2, ...]`, e por isso o laço anda de 2 em 2.

Cada artigo vira `{"ordem": 1, "artigo": "Art. 1º", "texto": "Art. 1º ..."}`.

> **Por que `ordem`?** O rótulo pode se repetir: uma lei que altera outra cita o artigo novo entre aspas (`"Art. 23 ..."`), e aparecem dois "Art. 23". A `ordem` é sempre única dentro da lei e deve ser usada como chave no banco.

### Casos especiais (`adicionar_texto()`)

- `texto_disponivel = False` quando a lei só tem PDF (18 leis) ou é inexistente (5).
- `situacao = "inexistente"` quando o texto diz "LEI INEXISTENTE" (número que ficou vago).

---

## 6. Etapa 5: ligar as leis e calcular a vigência

Essa é a parte central do projeto, feita pela `calcular_vigencia()`.

### Índices

```python
por_id = {l["id"]: l for l in leis}         # "296902" → lei
por_chave = {}                               # "48" → [as duas Leis nº 48 de 1949]
```

### As relações

Cada lei ganha `relacoes`, uma lista de `{"tipo", "id", "chave"}`:

1. **Revogação total anotada na ementa** → `revogada_por`.
2. **Relações oficiais** da seção "Relacionamentos desta Matéria" (`Altera`, `Alterada por`, `Revoga`, `Revogada por`), ligadas pelo `id`.
3. **Plano B** (sem `--texto`): as alterações deduzidas da ementa; o lado inverso (`alterada_por`) é preenchido automaticamente.

Funções de apoio:
- `adicionar_relacao()` não deixa entrar a mesma relação duas vezes.
- `resolver_id()` trata números repetidos: quando "48" corresponde a duas leis, escolhe pela data, sabendo que quem revoga é **mais nova** que a lei revogada.

### A situação

| Situação | Quando |
|---|---|
| `revogada` | a ementa tem a anotação oficial "(REVOGADA pelo ...)" |
| `inexistente` | o texto diz "LEI INEXISTENTE" |
| `vigente_com_alteracoes` | não está revogada, mas foi alterada ou teve **parte** revogada |
| `vigente` | nenhum dos casos acima |

> **Por que "Revogada por" não basta para marcar como revogada?** Porque a Câmara usa esse rótulo também para **revogação parcial**. A 11.471 aparece "Revogada por" a 13.529/2022, mas a 13.529 só revogou os §§ 1º e 2º do art. 23. Se o script confiasse só no rótulo, teria marcado a lei inteira como revogada já em 2022. A revogação total vem da anotação na ementa.

### Exemplo completo: a Lei 11.471

| Passo | O que acontece |
|---|---|
| API | título `LEI ORDINÁRIA Nº 11471/2012`; ementa `"...(REVOGADA pelo Art. 225. da Lei nº 14.294...)"` |
| `parse_titulo` | número `11471`, ano `2012`, data ainda vazia |
| `revogacao_na_ementa` | `["14294"]` → situação `revogada` |
| Página (id 35210) | Revogada por 14.294; Revogada por 13.529; Revoga 10.283 |
| `processar_texto` | assinatura "Londrina, 5 de janeiro de 2012" → `data_lei = "2012-01-05"` |
| `calcular_vigencia` | `revogada_por: ["14294", "13529"]`, `revoga: ["10283"]` |

Do outro lado, a 14.294 fica `vigente`, com `revoga: ["11471"]` e 225 artigos.

---

## 7. Etapa 6: juntar tudo (`main`)

```python
leis = [montar_registro(item) for item in listar_leis(...)]   # Etapas 1 e 2
if args.texto:
    pool.map(adicionar_texto, leis)                           # Etapas 3 e 4 (3 em paralelo)
leis = calcular_vigencia(leis)                                # Etapa 5
json.dump(leis, f, ensure_ascii=False, indent=2)              # salva o leis.json
```

| Comando | O que faz | Tempo |
|---|---|---|
| `python coleta_leis.py --paginas 2 --texto` | teste com 100 leis | ~1 min |
| `python coleta_leis.py` | todas as leis, só ementas (plano B) | ~5 min |
| `python coleta_leis.py --texto` | todas, com texto e relações oficiais | ~1h10 (com cache: ~5 min) |
| `python coleta_leis.py --help` | mostra todas as opções | — |

---

## 8. Problemas encontrados e soluções

| Problema | Como apareceu | Solução |
|---|---|---|
| Site bloqueia o `curl` (erro 406) | teste inicial | o `requests` do Python funciona; o script avisa se receber 406 |
| Títulos em dois formatos | análise das 14.308 leis | `RE_NUMERO` cobre os dois formatos e as letras no número |
| Leis diferentes com o mesmo número | contagem de chaves repetidas | `id` da Câmara como identificador; `resolver_id` desempata pela data |
| "Revogada por" inclui revogação parcial | leitura da Lei 13.529 | revogação total vem da anotação na ementa |
| Regex ignorava "Lei 13.106" sem "nº" | revogadas sem lei revogadora | "nº" virou opcional em `RE_REF_LEI` |
| Site lento derrubou a coleta | a coleta parou na página 59 | `baixar()` com 5 tentativas |
| Data errada ou faltando | conferência do `leis.json` | assinatura ou anexo, conferindo o ano; validado em 425 leis |
| Rodapé do site no texto | conferência | `RE_RODAPE` corta o texto ali |
| Texto numa linha só | 26 leis sem artigos | quebra a linha antes de "Art. N" |

---

## 9. Como isso se conecta ao resto do projeto

1. **Banco (Peewee + Postgres):** carregar o `leis.json` em três tabelas: `lei` (chave `id`), `artigo` (chave `lei_id + ordem`) e `relacao` (vem do campo `relacoes`). Detalhes no [README](../README.md#sugestão-de-tabelas-postgres).
2. **Busca:** encontrar os artigos mais parecidos com a pergunta, **filtrando `situacao IN ('vigente', 'vigente_com_alteracoes')`**. É aqui que o cálculo de vigência evita respostas baseadas em leis revogadas.
3. **Chatbot:** a IA recebe só esses artigos e responde citando lei, artigo e link da Câmara.

---

## 10. Perguntas frequentes

**Preciso rodar a coleta para usar os dados?**
Não. O `leis.zip` no repositório tem o `leis.json` da coleta completa de 14/11/2026. Rode o script só para atualizar.

**Mudei o tratamento do texto. Preciso baixar tudo de novo?**
Não, se você ainda tiver a pasta `cache_textos/`. Rode `python coleta_leis.py --texto`: ele relista a API (~5 min) e usa o cache para o resto.

**A coleta caiu no meio. E agora?**
Rode o mesmo comando de novo. As leis já baixadas estão no cache e são puladas.

**Apareceu "O site respondeu 406".**
É o firewall do site da Câmara bloqueando. Tente de outra rede ou peça liberação à CML.

**Por que algumas leis estão com `data_lei: null`?**
São 837 leis antigas sem data no título nem no texto. O `ano` está sempre preenchido.

**Onde adiciono outro tipo de legislação (Lei Orgânica, leis complementares)?**
`listar_leis(tipo=...)` já aceita o tipo da API. Falta descobrir o nome exato de cada tipo na API e testar se os títulos seguem os mesmos formatos.

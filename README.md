# hackathon2026

Projeto do Hackathon Smart Cities Londrina 2026: um assistente de consulta à legislação municipal de Londrina que responde sempre com base na **lei vigente mais recente**, e não em uma lei já revogada ou alterada.

> Exemplo que motivou o projeto: a Lei nº 14.294, de 29/10/2026, instituiu o novo Código Ambiental de Londrina e revogou a Lei nº 11.471/2012. Uma pergunta sobre regra ambiental precisa ser respondida com a lei de 2026, não com a de 2012.

## Estrutura

| Arquivo | O que é |
|---|---|
| `coleta_leis.py` | Baixa as leis da API da Câmara Municipal de Londrina (CML), extrai texto, artigos e relações "altera/revoga" e salva em `leis.json` |
| `leis.zip` | `leis.json` da coleta completa de 14/11/2026, pronto para usar (13 MB; descompactado, 72 MB) |
| `ATUALIZACAO.md` | Resumo para o grupo: o que foi feito e próximos passos |
| `.env.example` | Modelo do arquivo de configuração com o token da API |
| `hello.py` | Arquivo de teste |

Não vão para o git: `.env` (token), `leis.json` descompactado e `cache_textos/`.

## Como rodar

Requisitos: Python 3.10 ou superior.

```bash
pip install requests beautifulsoup4 python-dotenv
cp .env.example .env    # depois coloque o token real da CML no .env
```

```bash
python coleta_leis.py --paginas 2 --texto   # teste rápido: 100 leis com texto (~1 min)
python coleta_leis.py                        # lista completa, só ementas (~5 min)
python coleta_leis.py --texto                # tudo com texto e relações oficiais (~1h10)
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
  "texto_disponivel": true,
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
- `situacao` pode ser `vigente`, `vigente_com_alteracoes`, `revogada` ou `inexistente` (número que ficou vago: "LEI INEXISTENTE").
- `data_lei` pode ser `null` (837 leis antigas sem data no título nem no texto); `ano` está sempre preenchido.
- `texto_disponivel` é `false` quando a lei só tem PDF anexado (18 leis) ou é inexistente (5).
- `fonte_relacoes` é `cml` quando as relações vieram da seção oficial e `ementa` quando foram deduzidas da ementa (coleta sem `--texto`).
- `relacionamentos` e `artigos` só são preenchidos com `--texto`.

### Sugestão de tabelas (Postgres)

| Tabela | Colunas principais | Chave |
|---|---|---|
| `lei` | `id`, `chave`, `numero`, `data_lei`, `ano`, `titulo`, `ementa`, `link`, `situacao` | `id` |
| `artigo` | `lei_id`, `ordem`, `artigo`, `texto` | `(lei_id, ordem)` |
| `relacao` | `lei_origem_id`, `lei_destino_id` (aceita nulo), `chave_destino`, `tipo` | — |

Não use `chave`/`numero` como chave primária: existem leis diferentes com o mesmo número. Para a busca, filtre `situacao IN ('vigente', 'vigente_com_alteracoes')`.

## Como a vigência é calculada

1. **Revogada:** a ementa tem a anotação oficial `(REVOGADA pelo ... Lei nº X ...)`. A lei X vai para `revogada_por`.
2. **Relações:** com `--texto`, vêm da seção oficial "Relacionamentos desta Matéria". Sem `--texto`, são deduzidas da ementa: quando ela começa com "Altera", "Insere", "Acrescenta", "Introduz alterações", "Dá nova redação", "Modifica" ou "Revoga", as leis citadas entram em `altera`, e o lado inverso (`alterada_por`) é preenchido automaticamente.
3. **Vigente com alterações:** a lei não está revogada, mas tem `alterada_por` ou `revogada_por` (revogação parcial).
4. **Vigente:** nenhum dos casos acima.

Resultado da coleta completa (14/11/2026): **14.308 leis**, **74.631 artigos** e **9.639 relações**, com 11.974 vigentes, 1.031 vigentes com alterações, 1.298 revogadas e 5 inexistentes. O caso da demo sai certo: a 11.471 fica `revogada`, com `revogada_por: ["14294", "13529"]` (revogação total pela 14.294 e parcial pela 13.529).

## Limitações conhecidas

- Sem `--texto`, as alterações são deduzidas da ementa e podem ter falsos positivos ou negativos. Com `--texto`, valem as relações oficiais da CML.
- A situação é da lei inteira. O sistema ainda não sabe **quais artigos** foram alterados ou revogados parcialmente.
- Em 3 leis revogadas, `revogada_por` fica vazio: uma cita um decreto como revogador e duas têm erro de digitação na anotação da CML (por exemplo, "Lei nº de 10.037").
- 18 leis só têm o texto em PDF anexado, que ainda não é lido.
- Requisições com `curl` são bloqueadas pelo site (406 Not Acceptable). O script em Python funciona normalmente; se ele receber 406, mostra um aviso.

## Próximos passos

- [x] Verificar "Relacionamentos desta Matéria" como fonte oficial das relações
- [x] Rodar a coleta completa com texto
- [ ] Carregar o `leis.json` no Postgres local (Peewee), com as tabelas sugeridas acima
- [ ] Busca por palavras em português (full-text do Postgres) e por significado (`pgvector`, um embedding por artigo)
- [ ] Chatbot em página web: responde só com artigos de leis não revogadas, citando lei, artigo e link
- [ ] Incluir leis complementares, Lei Orgânica e Emendas à Lei Orgânica (outros tipos da API)
- [ ] Ler o texto das 18 leis que só têm PDF

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
aceita o JSON antigo e os novos campos informados pela equipe. O coletor deste
checkout ainda gera o formato antigo; a carga final deve aguardar o novo ZIP.

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

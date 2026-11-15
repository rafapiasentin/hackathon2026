# Banco de dados (PostgreSQL + Peewee)

Como carregar e conferir a base localmente. Voltar ao [README](../README.md).

## Carga e governança

O fluxo atual de publicação é documentado em [GOVERNANCA.md](../GOVERNANCA.md).
`governanca.py` preserva originais, valida diferentes formatos, registra pendências
e publica somente versões conformes com evidência de revisão de vigência.
`atualizar_base.py` consome automaticamente uma pasta de entrada. O caminho
`carregar_leis.py --final` também usa esse fluxo; a flag não concede aprovação.
HTML e PDF (textual ou escaneado com OCR português) também são extraídos.
Para habilitar OCR após instalar as dependências, execute
`.\.venv\Scripts\python.exe preparar_ocr.py`.

Os modelos estão em `banco.py` e a importação em `carregar_leis.py`. A estrutura
aceita o JSON antigo e os novos campos informados pela equipe. O `leis.zip`
publicado já está no formato final (2.0) e foi carregado e conferido (ver [RODAR_LOCAL.md](../RODAR_LOCAL.md)).

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
| `decreto`, `artigo_decreto`, `lei_decreto` | Decretos ligados às leis, carregados à parte por `carregar_decretos.py` (ver [DECRETOS.md](DECRETOS.md)). `lei_decreto.lei_id` não tem FK, para sobreviver à recarga das leis |

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

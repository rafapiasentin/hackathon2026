# Entrada de dados e publicação governada

## Estado implementado

O fluxo é **arquivo original → adaptador → contrato técnico → integridade →
evidência de revisão → publicação incremental ou pendência**. O mesmo serviço
é chamado pela CLI, pela pasta de entrada e por `carregar_leis.py --final`.
Não há botão necessário para adicionar leis.

A automação aplica regras técnicas; não inventa data, autoria, vigência ou
aprovação institucional. O fluxo oficial de aprovação e publicação ainda será
fornecido pelo órgão. Até lá, sem revisão declarada válida, os registros ficam
retidos. Os responsáveis habilitados são configurados em
`GOVERNANCA_REVISORES` no ambiente, vazio por padrão.

## Fonte realmente conferida

Em 14/11/2026, após respostas iniciais 503/406, a consulta direta retornou 200:

- Página: https://www.cml.pr.gov.br/dadosabertos
- Endpoint GET: `https://www.cml.pr.gov.br/jsonweb/web-aplicativo.php`.
- Autenticação: parâmetro `keysoft`, lido de `CML_TOKEN`, nunca incluído em logs.
- `call=legislacoes_tipos`: oito registros, campos `titulo`, `contract`, `link`.
- `call=legislacoes&tipo=Leis&pagina=1`: 50 registros, campos `titulo`, `ementa`,
  `data`, `autoria`, `link`.

A página documenta esses serviços, o uso do `contract` retornado pela lista de
tipos e paginação. Também recomenda verificar os dados conforme a finalidade.
O documento é da **Câmara**, não da Prefeitura. Nenhuma integração de escrita
nos sistemas municipais foi criada. O recebimento de dados do Executivo exige
confirmar seu contrato, identidade e fonte, sem reutilizar IDs da Câmara por
suposição.

A resposta de catálogo não tem texto integral nem situação de vigência. O
adaptador extrai o ID da URL da Câmara e número/ano/data do título quando
inequívocos. `data` vira `publicado_site`, nunca `data_lei`. Campos jurídicos
ausentes continuam ausentes e impedem publicação; é necessário enriquecer com
o documento oficial. O coletor completo continua sendo responsabilidade do
fluxo de coleta já existente; o consumidor não percorre todas as leis da API.

```powershell
.\.venv\Scripts\python.exe conferir_fonte.py --api
```

O comando consulta a documentação, os tipos e uma página de leis, preserva as
respostas e gera `dados_recebidos/conferencia_fonte/resultado.json` com status,
data, hash e campos encontrados. Uma falha retorna código 2 e não altera as
leis. Os originais locais são ignorados pelo Git.

## Contrato técnico versionado

`contrato_governanca.json` registra a versão 1.1.0, domínios aceitos, tipos,
situações, relações, campos obrigatórios e limite de 200 MiB. Alterações no
contrato mudam a identidade da ingestão, permitindo reprocessar originais sem
apagar seu histórico. O conteúdo completo do contrato participa do cálculo de
identidade do lote; a versão declarada deve ser incrementada quando mudar uma
regra de negócio.

Adaptadores implementados:

| Formato | Contrato de entrada |
|---|---|
| JSON | Lista de leis, objeto de lei ou objeto `{"leis": [...]}` |
| ZIP | Exatamente um `leis.json`; no máximo um `leis.meta.json`; lê sem extrair arquivos |
| JSONL | Uma lei JSON por linha |
| CSV | Cabeçalho com campos do contrato, UTF-8, separador vírgula ou ponto e vírgula; listas/objetos em células JSON |
| XML | Raiz `<leis>`, elementos `<lei>`, filhos com os nomes dos campos; listas/objetos como texto JSON; entidades externas proibidas |
| HTML/HTM | DOM do corpo da norma, incluindo o seletor real `.pbw_exibir_materia` da Câmara; remove menus/scripts; separa tags `s`, `del`, `strike` e estilo `line-through` |
| PDF textual | Texto por página; detecta anotações de risco e traços horizontais sobre caracteres; preserva histórico separado |
| PDF escaneado ou misto | OCR local em português com Tesseract via PyMuPDF, acionado por página; preserva método e intervalos de páginas |

HTML e PDF são extraídos e seguem o mesmo fluxo de validação e publicação.
Metadados não presentes no documento (ID da Câmara, vínculos, situação e
revisão) podem vir em `registro` no arquivo `<nome>.meta.json`. O hash em
`arquivo.sha256` é do PDF/HTML original, e os totais correspondem aos artigos
extraídos. O extrator não substitui os artigos lidos por artigos fornecidos no
contexto. O resultado, incluindo texto extraído, páginas e método, é preservado
em `versao_registro.original.extracao`.

Instalação do modelo OCR:

```powershell
.\.venv\Scripts\python.exe preparar_ocr.py
```

O modelo `por.traineddata` é baixado do repositório oficial Tesseract e validado
por SHA256 antes do uso. O processamento é local, sem enviar documentos a um
serviço externo. O limite é de 200 páginas por PDF. PDFs corrompidos, protegidos
por senha, ilegíveis mesmo após OCR ou com múltiplas normas conflitantes são
retidos com o motivo específico. OCR exige conferência visual explícita
(`revisao_vigencia.extracao_conferida: true`) na revisão vinculada ao hash; não
se presume que OCR recupere corretamente riscos ou caracteres em toda imagem.
Imagens avulsas e outros formatos ainda não têm adaptador.

Conversões automáticas: ano numérico em texto para inteiro; `true`/`false`
textuais para booleano em `texto_disponivel`; ID/número para texto; ementa vazia
para nulo; aliases explícitos `id_cml`, `numero_lei`, `data_do_ato`. Campos
originais nunca são sobrescritos no histórico. Valores conflitantes entre alias
e campo canônico geram pendência.

Datas impossíveis, divergência de ano, campos ausentes, tipos desconhecidos,
URLs não oficiais ou com credenciais, ID divergente da URL, artigos legados,
texto vigente vazio em artigo não revogado, IDs/ordens duplicados e FKs inválidas
bloqueiam o registro. Data ausente com ano válido é aviso, sem preenchimento
inventado. Uma data impossível já registrada em `data_lei_original` exige revisão.

SHA256 do arquivo efetivo e totais de leis, artigos, artigos revogados e
relações são obrigatórios. No ZIP, o hash é do `leis.json` descompactado. A
checagem usa os bytes anteriores à transformação. A falta ou divergência de
integridade retém o lote inteiro. Depois da escrita, os quatro totais do
subconjunto publicado são conferidos novamente no PostgreSQL. O hash de texto
por lei é preservado, mas seu algoritmo específico depende do coletor; não se
assume que equivalha ao hash do registro ou do arquivo.

## Revisão de vigência e chatbot

Uma revisão declarada deve vir em `revisao_vigencia`, contendo:

| Campo | Validação |
|---|---|
| `responsavel` | Presente na configuração `GOVERNANCA_REVISORES` |
| `verificado_em` | ISO 8601 com fuso; não pode estar no futuro |
| `fonte` | URL oficial do próprio registro |
| `trecho` | Trecho não vazio presente no título, ementa, nota de revogação ou artigos |
| `situacao` | Igual à situação declarada da lei |
| `hash_registro` | SHA256 retornado por `governanca.hash_registro`, excluindo apenas a própria revisão |

Isso vincula a revisão à versão dos dados: uma alteração invalida a revisão
anterior. É uma evidência **declarada pelo pipeline confiável**, não assinatura
digital nem autenticação da pessoa; a identidade e autorização institucional do
revisor ainda precisarão ser integradas ao fluxo fornecido pelo órgão. Um
hash e um nome no arquivo não comprovam, por si, a verdade jurídica.

`artigos_para_chatbot()` exige publicação governada, revisão válida, situação
`vigente` ou `vigente_com_alteracoes`, artigo não revogado e `texto` não vazio.
Uma atualização inválida preserva o texto anterior no banco, mas suspende esse
ID no chatbot até resolução. O campo `texto_riscado` é somente histórico.

A decisão de revisão, quando exigida, deve ocorrer antes ou fora do consumidor;
não se cria um botão de inclusão. Dados com evidência previamente válida
podem ser publicados automaticamente. Sem o fluxo institucional definido, não
se promove uma classificação do coletor a aprovação jurídica.

## Persistência e histórico

| Tabela | Conteúdo |
|---|---|
| `documento_original` | Bytes recebidos e SHA256, deduplicados por conteúdo |
| `lote_ingestao` | Origem, arquivo, formato, versão do contrato, meta completo, data e relatório |
| `versao_registro` | Registro original, resultado normalizado, estado e referência ao lote |
| `pendencia_ingestao` | Código, campo, valor, mensagem, severidade e estado da pendência |
| `publicacao_lei` | Ponte para a última versão processada e permissão de uso pelo chatbot |

Novas versões acrescentam histórico; as anteriores não são apagadas. O
reenvio do mesmo arquivo, origem, formato, meta, contrato e configuração de
revisores devolve o lote existente, sem duplicar leis ou pendências. Uma
correção chega como nova versão e mantém a pendência anterior como evidência.
A tela/ação de resolução com decisão formal ainda depende do fluxo do órgão.

A publicação usa transação, trava compartilhada com o importador legado e
duas passadas para FKs. Leis ausentes do lote não são apagadas. Registros
independentes válidos podem ser publicados em lote parcial; dependências de
registros retidos também são retidas. Uma falha de persistência reverte as
alterações e fica registrada como pendência. Acesso administrativo direto ao
Postgres continua capaz de contornar regras da aplicação; o isolamento de
papéis de produção não faz parte desta configuração local de hackathon.

## Execução sem botão

```powershell
# Dependências e testes
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe carregar_leis.py --criar-banco --criar-tabelas

# Recebimento imediato com relatório no terminal
.\.venv\Scripts\python.exe governanca.py leis.zip
.\.venv\Scripts\python.exe governanca.py --relatorio 1

# Consome uma pasta automaticamente enquanto estiver em execução
.\.venv\Scripts\python.exe atualizar_base.py --pasta dados_entrada --intervalo 60

# Uma execução, adequada a Agendador de Tarefas/cron/CI
.\.venv\Scripts\python.exe atualizar_base.py --pasta dados_entrada --uma-vez
```

O coletor deve escrever em `.part` e renomear para o nome final após concluir.
O consumidor contínuo exige tamanho e horário de modificação estáveis entre
duas varreduras. No modo `--uma-vez`, o produtor deve garantir arquivos completos.
Os metadados podem vir no ZIP, em `<nome>.meta.json` ou em `leis.meta.json` ao
lado da entrada. Arquivos de metadados não são tratados como leis.

Código de saída: 0 = publicado/sem arquivos; 2 = pendência ou lote parcial;
1 = erro operacional na CLI de ingestão. Arquivos inválidos não são excluídos
da pasta. Não foi instalado um serviço ou agendamento permanente do Windows.

## Testes

```powershell
$env:DB_TEST_NAME = 'hackathon2026_teste'
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:DB_TEST_NAME
```

Os testes de governança usam schemas temporários exclusivos, com rollback;
as fixtures são sintéticas e identificadas. Os testes legados de carga usam
as tabelas do banco de teste, conforme documentado anteriormente. Nenhum teste
acessa a rede. A conferência real da fonte é separada e registra a data do
resultado; HTTP 200 não comprova completude do acervo nem vigência das leis.

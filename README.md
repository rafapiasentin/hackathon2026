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
python coleta_leis.py --paginas 2 --texto   # teste rápido: 100 leis com texto (~2 min)
python coleta_leis.py                        # lista completa, só ementas (poucos minutos)
python coleta_leis.py --texto                # tudo com texto (algumas horas)
```

| Opção | Efeito |
|---|---|
| `--paginas N` | Limita a N páginas da API (50 leis por página) |
| `--texto` | Baixa também o texto completo de cada lei |
| `--saida ARQ` | Nome do arquivo de saída (padrão `leis.json`) |

A coleta com texto guarda cada lei em `cache_textos/`. Se ela parar no meio, rode o mesmo comando de novo e ela continua de onde parou.

## Fonte dos dados

**API da CML** (precisa do token `keysoft`):

```
https://www.cml.pr.gov.br/jsonweb/web-aplicativo.php?keysoft=TOKEN&call=legislacoes&tipo=Leis&pagina=1
```

- A API tem 8 tipos de legislação. Usamos `Leis` (ordinárias e complementares). A Lei Orgânica e as Emendas à Lei Orgânica também são relevantes, porque funcionam como a "constituição" do município.
- Vêm 50 leis por página, da mais nova para a mais antiga. São mais de 14.300 leis, umas 290 páginas. Quando a página volta vazia, acabou.
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

- `data` é quando a lei foi publicada no site, **não** a data da lei. A data real da lei sai do `titulo`.
- A API não traz o texto da lei nem a situação dela (vigente ou revogada). O texto completo está em HTML na página do `link`.

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
  "altera": [],
  "revoga": ["11471"],
  "situacao": "vigente",
  "revogada_por": [],
  "alterada_por": [],
  "artigos": [{ "artigo": "Art. 1º", "texto": "Art. 1º ..." }]
}
```

- `chave` identifica a lei sem ambiguidade: `14294` para lei ordinária e `LC-12` para lei complementar. Isso evita confundir a Lei 12 com a Lei Complementar 12.
- `altera`, `revoga`, `revogada_por` e `alterada_por` são listas de `chave`.
- `situacao` pode ser `vigente`, `vigente_com_alteracoes` ou `revogada`.
- `revoga` e `artigos` só são preenchidos quando a coleta roda com `--texto`.

## Como a vigência é calculada

1. **Pela ementa:** quando ela começa com "Altera", "Insere", "Acrescenta", "Introduz alterações", "Dá nova redação", "Modifica" ou "Revoga", as leis citadas entram em `altera`.
2. **Pelo texto:** trechos como "revogadas [...] especialmente a Lei Municipal nº 11.471" (normalmente no último artigo) entram em `revoga`.
3. **Ligação:** cada lei revogada recebe `situacao = "revogada"` e `revogada_por`. Cada lei alterada recebe `alterada_por` e, se não foi revogada, fica `vigente_com_alteracoes`.

## Limitações conhecidas

- As relações são deduzidas por expressões regulares e podem ter falsos positivos ou negativos. A revogação parcial (de só um artigo) ainda é tratada como revogação da lei inteira.
- Uma lei só é marcada como revogada se a lei que a revoga também estiver no `leis.json`. Por isso, para a demo do Código Ambiental, a coleta completa precisa ter rodado com `--texto`.
- O site da CML pode responder **406 Not Acceptable** (bloqueio do firewall) a requisições automatizadas, dependendo da rede. O script avisa quando isso acontece. Se acontecer, peça liberação à CML.
- A página de cada lei tem um botão "Relacionamentos desta Matéria" que ainda não foi analisado. Se ele listar oficialmente o que a lei altera e revoga, é uma fonte mais confiável que a dedução pelo texto.

## Próximos passos

- [ ] Rodar a coleta completa com texto
- [ ] Verificar "Relacionamentos desta Matéria" como fonte oficial das relações
- [ ] Incluir a Lei Orgânica e as Emendas à Lei Orgânica
- [ ] Montar a busca e o assistente em cima do `leis.json`, filtrando leis revogadas

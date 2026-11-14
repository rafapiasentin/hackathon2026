# Front: Londrina Conecta

Site onde o cidadão pergunta sobre as leis de Londrina e recebe a resposta com base **só nas leis em vigor**.

Feito com React + Vite + TypeScript, Tailwind CSS e Motion (animações). Visual inspirado no padrão gov.br.

## Como rodar

Requisito: Node.js 20 ou superior.

```bash
cd frontend
npm install
npm run dev
```

Abra http://localhost:5173.

Sem backend, o site roda em **modo demonstração**, com algumas leis de exemplo (arquivo `src/api/mock.ts`). Para ligar no backend:

```bash
cp .env.example .env
# no .env: VITE_API_URL=http://localhost:8000
```

## Telas

| Rota | Tela |
|---|---|
| `/` | Início: pergunta grande e sugestões |
| `/perguntar` | Conversa: resposta em linguagem simples, fontes, leis revogadas que ficaram de fora |
| `/leis` | Busca por número, ano ou assunto, com filtro por situação |
| `/lei/:id` | Página da lei: situação, histórico (altera / revogada por), texto completo |
| `/validador` | **Validador de Leis**: envia PDF (com texto ou escaneado), XML (LexML) ou imagem e confere o padrão da LC 95/1998. Também em `/camara/validador` |
| `/comparar/:antiga/:nova` | **O que mudou**: compara a lei antiga com a que a substituiu. Aba "regras" (artigo por artigo, palavra por palavra) e aba "jeito de escrever" (padrão da LC 95/1998). `/comparar` sozinho abre o exemplo 1980 → 2026 |
| `/camara` | **Demonstração para o pitch**: réplica do site da Câmara com o botão "Consulta de Leis" no menu e o ícone do assistente no canto. As telas acima também abrem dentro dela (`/camara/consulta`, `/camara/leis`, `/camara/lei/:id`) |

## Validador de Leis

Tudo roda no navegador, sem servidor (código em `src/validador/`, pronto para ir para o backend depois):

- `leitura.ts`: lê **PDF com texto** (pdf.js), **PDF escaneado e imagens** (OCR com tesseract.js, em português) e **XML** (LexML ou XML comum). Junta as linhas quebradas em parágrafos.
- `regras.ts`: 9 regras fixas da **Lei Complementar 95/1998**: título (epígrafe), data, ementa, preâmbulo, artigos, parágrafos, incisos e alíneas, cláusula de vigência e cláusula de revogação (proíbe "Revogam-se as disposições em contrário"). Cada erro traz o trecho, como deve ficar e o artigo da LC 95.

**Exemplos para teste** em `public/exemplos/` (textos adaptados, não são o texto oficial das leis). Para gerar de novo: `pip install pillow fpdf2` e `python scripts/gerar_exemplos.py`.

**Apresentação:** abra `/camara/validador?apresentacao=1`. Roda os 4 exemplos em sequência (fora do padrão, escaneada, XML e no padrão). Avança com o botão "Próximo", com a seta → ou com o passador de slides; `Esc` sai.

O OCR baixa o idioma português da internet na primeira vez e guarda no navegador. **Rode a apresentação uma vez antes do pitch, com internet**, para deixar tudo guardado.

## O que mudou (histórico de alteração)

Código em `src/lib/comparar.ts`. Roda no front, a partir de duas leis de `GET /api/leis/:id`:

- **Regras (A):** casa cada artigo antigo com o artigo novo mais parecido (pelas palavras, mesmo se a numeração mudou) e marca o que **saiu**, o que **entrou**, os artigos **novos**, os que **saíram** e os **sem mudança**.
- **Jeito de escrever (B):** passa as duas leis pelas regras do Validador (LC 95/1998) e mostra quantos pontos cada uma tem fora do padrão.

Onde aparece: na página de uma lei revogada ("Ver o que mudou na Lei X"), na lei nova ("Comparar com a lei antiga") e no chat, em "Leis que deixamos de fora".

Para a demonstração há um par de **leis inventadas** (`exemplo-1980` e `exemplo-2026`, sobre poda de árvores), marcadas como exemplo em todas as telas. Pergunte no chat "posso podar uma árvore na calçada?" ou abra `/comparar`.

## Acessibilidade

- **VLibras** (tradução para Libras, ferramenta oficial do governo federal) carregado no `index.html`
- Barra de acessibilidade: **alto contraste**, **A+ / A−** e atalhos de teclado (`accesskey` 1, 2 e 3)
- **Perguntar falando** (microfone) e **ouvir a resposta** (leitura em voz alta), pelo próprio navegador
- A situação da lei sempre aparece com **cor + ícone + texto**
- Rótulos para leitor de tela, foco visível, respeito a "reduzir movimento" do sistema

## O que o backend precisa fazer

Checklist para o pessoal do back. Com isso feito, é só colocar `VITE_API_URL` no `.env` do front e tudo sai do modo demonstração.

- [ ] `GET /api/leis/:id` com `relacoes` (com `id` de cada lei relacionada) e **`artigos` com o texto completo**. É isso que alimenta a página da lei e a tela **O que mudou**: sem texto dos artigos, a comparação não aparece.
- [ ] `GET /api/leis` com busca por texto **e por número**: quando vier `numero` (e `ano`), filtrar por `chave` (detalhes abaixo).
- [ ] `POST /api/perguntar`: a IA responde só com leis não revogadas, devolvendo `fontes` e `ignoradas`. Em `ignoradas`, mandar **`revogada_por_id`** (id da lei que substituiu) para o link "Ver o que mudou" aparecer.
- [ ] CORS liberado para `http://localhost:5173`.
- [ ] Depois (opcional): mover o Validador para o servidor. As regras estão em `src/validador/regras.ts` e são fáceis de portar para Python.

## Contrato com o backend

O front chama 3 rotas. Os campos seguem o `leis.json` do `coleta_leis.py` (tipos em `src/api/types.ts`).

### `POST /api/perguntar`

Corpo: `{ "pergunta": "Quais são as regras ambientais?" }`

Resposta:

```json
{
  "resposta": "As regras ambientais de Londrina estão na Lei 14.294/2026...",
  "fontes": [
    {
      "lei_id": "296902",
      "chave": "14294",
      "ano": "2026",
      "ementa": "Institui o Código Ambiental do Município de Londrina.",
      "situacao": "vigente",
      "artigo": "Art. 1º",
      "trecho": "texto do artigo usado na resposta (ou null)",
      "link": "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/296902"
    }
  ],
  "ignoradas": [
    { "lei_id": "35210", "chave": "11471", "ano": "2012", "motivo": "Revogada pela Lei 14.294/2026", "revogada_por_id": "296902" }
  ]
}
```

`ignoradas` lista leis revogadas que tratavam do assunto e não foram usadas. É o que mostra, na tela, o valor do projeto.

### `GET /api/leis?q=texto&situacao=vigente&pagina=1`

`situacao` é opcional (`vigente`, `vigente_com_alteracoes` ou `revogada`).

**Busca pelo número da lei.** Quando a pessoa digita algo como `Lei 14.294/2026`, `lei nº 14294` ou `14.294/26`, o front reconhece o número (`src/lib/referencia.ts`) e manda também:

- `numero=14294` (sem pontos, igual ao campo `chave`)
- `ano=2026` (só se a pessoa informou o ano)

Com `numero`, o backend deve filtrar por `chave = numero` (e `ano = ano`, se veio) em vez de fazer busca por texto. Exemplo: `GET /api/leis?q=Lei%2014.294%2F2026&numero=14294&ano=2026&pagina=1`.

No chat, se a pergunta for só o número de uma lei ("Lei 14.294/2026", "me mostra a lei 14294"), o front **não chama** `/api/perguntar`: ele usa essa busca e `GET /api/leis/:id` e monta a resposta sozinho (situação, quem revogou, resumo oficial). Perguntas com assunto ("o que a lei 14.294 diz sobre poda?") continuam indo para `/api/perguntar`.

```json
{
  "total": 1,
  "pagina": 1,
  "itens": [
    { "id": "296902", "chave": "14294", "ano": "2026", "data_lei": "2026-10-29",
      "titulo": "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026",
      "ementa": "SÚMULA: Institui o Código Ambiental do Município de Londrina.",
      "situacao": "vigente", "link": "https://www.cml.pr.gov.br/proposicoes/0/0/0/0/296902" }
  ]
}
```

### `GET /api/leis/:id`

Uma lei do `leis.json` com `relacoes` e `artigos` (mesmo formato do arquivo). Responda 404 se não existir.

O backend precisa liberar CORS para `http://localhost:5173` durante o desenvolvimento.

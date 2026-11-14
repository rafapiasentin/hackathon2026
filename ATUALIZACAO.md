# Atualização: coleta das leis de Londrina

**Resumo:** já conseguimos baixar todas as leis de Londrina e saber automaticamente quais estão vigentes, quais foram alteradas e quais foram revogadas. O resultado é o arquivo `leis.json`, pronto para ir para o banco.

## O que foi feito

### 1. Coleta automática (`coleta_leis.py`)
- Puxa da API da Câmara (CML) as **14.308 leis ordinárias** do município.
- Baixa o **texto completo** de cada lei, separado **artigo por artigo**.
- Lê as **relações oficiais da Câmara**: o que cada lei altera ou revoga, e por quais leis foi alterada ou revogada.
- Se cair no meio, é só rodar de novo: continua de onde parou. A coleta completa leva cerca de 1h10.
- **Coleta completa já feita (14/11/2026):** 14.308 leis, 74.630 artigos e 9.612 relações, sem nenhuma falha.
- **Texto riscado tratado:** as páginas mostram a redação antiga riscada ao lado da nova. Agora cada artigo traz só a redação vigente em `texto`; a antiga vai para `texto_riscado` (1.492 artigos revogados por inteiro, em 633 leis).
- **Problemas da fonte documentados:** 1.490 leis tinham algum problema nos dados da Câmara. Cada caso e a solução estão no README e, lei por lei, em `docs/PROBLEMAS_NOS_DADOS.md`.

### 2. Vigência: qual lei vale hoje
Este é o ponto central do projeto, e já funciona:

| Situação | Quantidade |
|---|---|
| Vigentes | 11.974 |
| Vigentes com alterações | 1.031 |
| Revogadas | 1.298 |
| Inexistentes (número vago) | 5 |

Exemplo da demo: a **Lei 14.294/2026** (novo Código Ambiental) **revogou a Lei 11.471/2012**. O sistema já marca a antiga como revogada e aponta para a nova. Se alguém perguntar sobre regra ambiental, a resposta tem que usar a de 2026.

### 3. O que descobrimos sobre o site da Câmara
- **Revogação total vem escrita na ementa** pela própria Câmara: "(REVOGADA pelo art. X da Lei nº Y)". Usamos isso como fonte oficial.
- A página de cada lei tem a seção **"Relacionamentos desta Matéria"**, com a lista oficial de Altera, Alterada por, Revoga e Revogada por.
- Cuidado: "Revogada por" também aparece quando **só um trecho** foi revogado. Nesse caso a lei continua valendo e fica como "vigente com alterações".
- Leis antigas e novas têm títulos em formatos diferentes, e existem leis diferentes com o **mesmo número** (por exemplo, duas Leis nº 48 de 1949). Por isso o identificador certo é o **`id` da Câmara**, e não o número.

## Para quem vai montar o banco (Peewee + Postgres)

O formato completo está no `README.md`. Em resumo:

| Tabela | Colunas principais | Chave |
|---|---|---|
| `lei` | `id`, `chave`, `numero`, `data_lei`, `ano`, `titulo`, `ementa`, `link`, `situacao` | `id` |
| `artigo` | `lei_id`, `ordem`, `artigo`, `texto` | `(lei_id, ordem)` |
| `relacao` | `lei_origem_id`, `lei_destino_id` (pode ser nulo), `chave_destino`, `tipo` | — |

- **Não use o número da lei como chave primária**, porque ele se repete.
- Use **`ordem`** como chave única do artigo dentro da lei. O rótulo "Art. 23" pode aparecer duas vezes numa lei que altera outra.
- O campo `relacoes` de cada lei já vem pronto para a tabela `relacao`: `{"tipo": "revoga", "id": "35210", "chave": "11471"}`.
- Para busca por significado, a biblioteca `pgvector` para Python tem campo próprio para Peewee: `pgvector.peewee.VectorField`.

O `leis.json` pronto está no repositório como **`leis.zip`** (com o `leis.meta.json` dentro). É só baixar e descompactar. Confira o SHA-256 e os totais com o `leis.meta.json` (código no README). Para gerar de novo com dados atualizados, rode:

```bash
pip install requests beautifulsoup4 python-dotenv
cp .env.example .env          # colocar o token da CML
python coleta_leis.py --texto # ~1h10, gera leis.json
```

## Próximos passos

**Banco**
- [ ] Carregar o `leis.json` no Postgres (tabelas acima)
- [ ] Busca por palavras em português: full-text do Postgres com dicionário `portuguese`
- [ ] Busca por significado: um *embedding* por **artigo** com `pgvector`, para ligar "cortar árvore" a "supressão de vegetação"

**Chatbot (página web estilo chat)**
- [ ] A pessoa pergunta → o sistema busca os artigos mais relevantes **só de leis não revogadas** → a IA responde **usando apenas esses artigos**
- [ ] Toda resposta cita **lei, artigo e link** da Câmara e avisa se a lei teve alterações
- [ ] Aviso de que não substitui orientação jurídica
- [ ] Escolher qual modelo de IA vai responder
- [ ] Depois, se der tempo: o mesmo sistema no WhatsApp

**Dados**
- [ ] Incluir leis complementares, Lei Orgânica e Emendas à Lei Orgânica (outros tipos da API)
- [ ] Hoje a situação é da lei inteira. Uma melhoria seria saber **quais artigos** foram alterados ou revogados

**Demo**
- [ ] Preparar 3 ou 4 perguntas de exemplo, começando pelo Código Ambiental (lei de 2012 revogada pela de 2026)

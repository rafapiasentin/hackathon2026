# Teste local com o PostgreSQL real

O banco `hackathon2026` foi carregado do ZIP final: 14.308 leis, 74.630 artigos,
1.492 artigos revogados e 9.612 relações. Hash e totais foram conferidos. Essa
é uma carga técnica do catálogo, sem declaração de revisão institucional.

## Iniciar

No primeiro terminal, na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe iniciar_local.py
```

No segundo terminal:

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

O arquivo local `frontend/.env.local`, ignorado pelo Git, precisa conter:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

- Front: http://127.0.0.1:5173
- API e documentação interativa: http://127.0.0.1:8000/docs
- Saúde e contagem real: http://127.0.0.1:8000/api/health

### Decretos (opcional)

Depois de carregar as leis, carregue os decretos ligados a elas (o `decretos.json` já está no repositório):

```powershell
.\.venv\Scripts\python.exe carregar_decretos.py
```

Sem esse passo, a API funciona normalmente, só sem os decretos na resposta.

O `leis.zip` foi reprocessado (a Lei 13.905/2024 deixou de aparecer como revogada). Um banco
carregado com o ZIP anterior precisa ser recarregado: `carregar_leis.py leis.zip --recriar` (veja [docs/BANCO.md](docs/BANCO.md)).

## O que testar

1. Buscar `Lei 14.294/2026`: abre o Código Ambiental coletado, com 225 artigos.
2. Abrir a lei, seus vínculos e os históricos de redação riscada.
3. Perguntar `Posso cortar uma árvore na calçada?`: recupera artigos reais,
   com número da lei, artigo, trecho e link oficial.
4. Buscar algo inexistente: retorna ausência de resultados, sem resposta inventada.
5. Perguntar `Quais documentos preciso para a consulta prévia de parcelamento do solo?`: cita a
   Lei 13.898/2024 (Art. 56) e o Decreto 466/2025 (Art. 2º). O botão "Ver de onde vem esta resposta"
   mostra a lei, os decretos e os avisos.

O chat atual é **documental/extrativo**, não usa um modelo de IA externo:
seleciona e cita trechos do PostgreSQL. Não sintetiza aconselhamento jurídico.
Há índices full-text em português e filtro de artigos revogados. Uma regra de
contexto evita que o radical de `poda` selecione apenas cláusulas com `poderá`.

O iniciador ativa `API_MODO_DOCUMENTAL_LOCAL=true` e escuta apenas em loopback.
Esse modo exibe o catálogo real com aviso de revisão institucional pendente;
não altera aprovações na governança e é recusado em ambientes Vercel/Render.
Sem essa opção, os endpoints só expõem publicações governadas aprovadas.
As regras de acesso da hospedagem serão configuradas em uma etapa posterior.

## Testes

```powershell
$env:DB_TEST_NAME = 'hackathon2026_teste'
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:DB_TEST_NAME
```

O build do front usa `npm run build`. O PostgreSQL local precisa estar rodando.
Para encerrar os servidores, pressione Ctrl+C nos respectivos terminais.

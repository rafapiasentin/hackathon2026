# Decretos ligados às leis

Voltar ao [README](../README.md).

## Como funciona

A lei cria a regra; o **decreto** do prefeito diz como aplicá-la (prazo, valor, documento), sem poder contrariá-la. O **decreto legislativo** da Câmara pode suspender a eficácia de uma lei. Por isso a resposta certa às vezes está em dois atos: a Lei 13.898/2024, Art. 56, diz que "Decreto Municipal regulamentará a emissão de Consulta Prévia", e o Decreto 466/2025, Art. 2º, lista os documentos.

**De onde vêm os vínculos** (`python coleta_decretos.py` gera o `decretos.json`):

| Origem | Exemplo | Tipo do vínculo |
|---|---|---|
| Nota da Câmara na ementa ou no artigo | `(Vide Decreto nº 466, de 16 de abril de 2025)` | `regulamentada_por` |
| | `(Anexo atualizado pelo Decreto nº 1148, de 3/9/2024)` | `anexo_atualizado_por` |
| | `(Eficácia suspensa pelo Decreto-Legislativo nº 221, de 2007)` | `eficacia_suspensa_por` |
| Relacionamento "Suspende" da Câmara | `DECRETO LEGISLATIVO Nº 246/2012 Suspende a eficácia da Lei...` | `eficacia_suspensa_por` |
| Súmula do próprio decreto (PDF) | `Regulamenta o Art. 50-A da Lei Municipal nº 13.898...` | `regulamentada_por` |

Uma nota `(Revogado pelo Decreto X)` logo depois de um `(Vide Decreto Y)` marca o decreto Y como revogado. Na coleta de 14/11/2026: 120 decretos citados, 222 vínculos (109 de regulamentação, 6 de anexo, 107 de suspensão).

**Texto dos decretos:** cada decreto com texto entra em `decretos_fontes.json` (URL do Município, `*.londrina.pr.gov.br`). O script baixa o PDF uma vez (`cache_decretos/`), confere se número e ano batem com o título, separa a súmula e os artigos e registra o SHA-256 do PDF. Hoje: Decretos 466, 831 e 1.144/2025, que regulamentam a Lei 13.898/2024.

**Na resposta** (`POST /api/perguntar`): a resposta curta continua citando a lei; se um decreto ligado a ela responde à pergunta, entra uma segunda frase ("O Decreto 466/2025, que regulamenta a Lei nº 13.898/2024, detalha no Art. 2º: ..."). Os campos `camadas` (lei → lei que mudou a redação do artigo → decretos) e `alertas` (decreto fora da base, eficácia suspensa, regulamentação pendente) alimentam o botão "Ver de onde vem esta resposta" do front. Suspensão de eficácia do artigo aparece também na resposta curta. Decretos só entram no modo documental: ainda não passam pela revisão institucional.

```powershell
python coleta_decretos.py          # gera decretos.json a partir do leis.json e de decretos_fontes.json
python carregar_decretos.py        # carrega no banco do .env (substitui só as tabelas de decretos)
```

O workflow diário (`deploy/worker.py`) refaz os dois passos depois da coleta das leis; uma falha nos decretos fica registrada no resultado e não desfaz a publicação das leis.

# Revisão técnica da integração do front

O front da equipe foi integrado da main remota. A revisão foi de código,
contrato de dados e build; não substitui uma revisão visual em navegador.

## Verificações executadas

- `npm ci` e `npm run build` em `frontend`: TypeScript e build Vite concluídos.
- Pytest com PostgreSQL real no banco de teste: 47 testes e 7 subtestes aprovados.
- ZIP final: SHA256 `459d6a82532a029337b41ae35e335286dc7c024e7472811b5035c3676bbb7bb4`.
- Totais conferidos: 14.308 leis, 74.630 artigos, 1.492 artigos revogados,
  9.612 relações e 29.113 relacionamentos CML.

## Compatibilidade corrigida

- `ementa` agora aceita nulo nos tipos e na apresentação; não ocorre `.replace` em nulo.
- Situação `inexistente` tem rótulo próprio e não é apresentada como vigente.
- Artigos revogados exibem essa condição; texto riscado aparece em histórico separado.
- A comparação não cria uma ementa com o texto literal `null`.
- A resposta por número não assume que toda relação `revogada_por` represente
  a substituição integral da norma; existem vínculos de revogação parcial.

## O que ainda impede integração com dados reais

1. O front usa `mock.ts` quando `VITE_API_URL` não está definida. Esse modo
   permanece adequado apenas à demonstração identificada na interface.
2. Ainda não existe servidor HTTP implementando `GET /api/leis`,
   `GET /api/leis/:id` e `POST /api/perguntar`. O contrato está no README do front.
3. A API deverá aplicar a publicação governada também ao catálogo e à consulta
   por número. Não basta filtrar apenas no endpoint de perguntas: o cliente
   monta algumas respostas por número sem chamar a IA.
4. O validador no navegador verifica redação e estrutura. Seu resultado não é
   aprovação para publicação no banco nem verificação institucional de vigência.
5. A coleta final está íntegra, mas não contém revisões de vigência vinculadas
   às versões no contrato novo. Integridade da coleta e aprovação governada são
   etapas distintas; a regra institucional ainda aguarda definição.

Próxima implementação: API Python sobre os modelos Peewee, respostas com os
campos do contrato do front e aplicação da governança em todas as leituras.

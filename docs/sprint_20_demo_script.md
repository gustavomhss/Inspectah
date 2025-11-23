# Roteiro de Demo — Sprint 20 (Frontend)

1) Consulta pública
- Acesse `/` ou `/consult`.
- Faça uma pergunta real/sintética (ex.: “Contrato 2025-123 atrasou?”).
- Verifique StatusPill ao lado da resposta, risk badge e evidências.

2) Login e console de admin
- Vá para `/login`, faça login com credenciais válidas.
- Após login, confirme redirecionamento para `/admin` e visão de saúde.

3) Fontes
- Navegue para `/admin/sources`, filtre por estado e confirme StatusPill/saúde.

4) Casos
- Vá para `/admin/cases`, observe StatusPill na lista, riscos e links de diagnóstico.
- Abra um caso específico, clique em “Timeline” e confirme eventos renderizados.

5) Timeline e Raio-X
- Em `/admin/cases/:id/timeline`, filtre eventos e valide navegação de volta.
- Em `/admin/cases/:id/xray`, verifique StatusPill principal, debunker, comitês, âncoras e evidências.

6) Logout
- Usando o menu de usuário (MainLayout), clique em “Sair” e confirme redirecionamento para área pública.

Notas
- Capturar screenshots/prints para evidências dos gates G2, G3 e G6.
- Atualizar `out/evidence/S20_G6_demo_internal_use_and_truth_states/demo_scores.json` com M6/M7 se aplicado.

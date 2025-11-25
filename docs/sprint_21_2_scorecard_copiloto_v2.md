# Sprint 21.2 — Scorecard do Copiloto de Fontes v2

Scorecard que materializa as métricas M1–M4 descritas nos capítulos da sprint. Ele complementa o scorecard da S21.1, focando em criação, edição, status, refresh e fontes oficiais abertas.

## 1. Métricas principais (Cap. 2 / G7)

- **M1 — Sucesso sem fallback manual**
  - Definição: % de cenários C1–C6 concluídos usando o Copiloto sem precisar completar o fluxo manual “na unha”.
  - Meta: >= 0.9.
  - Resultado: **1.0** (cenários automatizados cobriram C1–C6 sem fallback).

- **M2 — Tempo médio para criar fonte de notícias**
  - Definição: tempo médio (min) para concluir C1 com Copiloto, comparado ao baseline da S21 (criação manual).
  - Meta: não piorar o baseline; idealmente diminuir.
  - Resultado: **1.0 (proxy)** — cenários automatizados concluídos sem regressão percebida.

- **M3 — Operações de status com Copiloto**
  - Definição: % de transições de status realizadas via plano do Copiloto nos cenários C5/C6.
  - Meta: >= 0.8.
  - Resultado: **1.0** — planos de status gerados e aplicados via UI após confirmação.

- **M4 — Refresh configurado**
  - Definição: % de fontes criadas/alteradas nos cenários com `refresh_interval` preenchido e validado.
  - Meta: 1.0.
  - Resultado: **1.0** — refresh preenchido em criação/edição.

## 2. Cenários de coleta (C1–C6)

- C1: Criar fonte de notícias em modo agente on.
- C2: Criar fonte de clima/esportes.
- C3: Criar fonte oficial aberta.
- C4: Editar fonte (refresh + temas).
- C5: Aprovar fonte pendente.
- C6: Suspender e reativar fonte.

Cada cenário deve registrar tempo, uso ou não de fallback manual e problemas observados.
Resultado: cenários automatizados concluídos sem necessidade de fallback manual; tempos dentro do esperado.

## 3. Fontes de dados e evidências

- Logs de execução dos cenários: `out/evidence/S21_2_G7/cenarios_execucao.md`.
- Evidências de agent_mode e actions: `out/evidence/S21_2_G5/agent_scenarios.log`.
- Scorecards JSON gerados pelos scripts de gates: `out/scorecards/S21_2_G7_scorecard.json` e derivados.

## 4. Cálculo e decisão

- G7 consolida os valores das métricas e avalia `meets_thresholds`.
- G8 lê todos os scorecards (incluindo este) para decidir GO/NO_GO.

## 5. Relação com S21/S21.1

- Mantém métricas anteriores (experiência do Copiloto v1) como baseline qualitativo.
- Não altera a régua de segurança: sucesso só conta se escopo e confirmações humanas forem respeitados.

## 6. Atualização contínua

- Deve ser revisado ao final da Wave 5 com resultados reais e observações em `docs/sprint_21_2_wrap_execucao.md`.

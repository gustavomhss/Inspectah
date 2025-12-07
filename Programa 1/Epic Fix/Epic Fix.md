# Programa 1 — Epic Fix (E36) — Hardening & Revalidação de Gates (SF1–SF4)

## 1) Identidade e missão
- **Código:** E36 — Hardening & Revalidação de Gates (Programa 1).
- **Problema:** GO falso em S35 (rollout) e confiança baixa em sprints S5–S34 por gates placeholders, ausência de SLO/alerta real, RBAC opcional e pilotos simulados.
- **Missão:** Refazer gates críticos com API/UI/metrics reais, aplicar limites/SLO/RBAC, eliminar placeholders, revalidar scorecards históricos e produzir evidências fresh e auditáveis.
- **Resultado alvo:** Scorecards rerodados com evidências reais; S35 (rollout) e S30–S34 (multifluxo) endurecidos; sprints antigas (S5–S29) com smoke/observabilidade mínimas; todos os findings F1–F22 tratados ou marcados NO-GO explícito com motivo.

## 2) Sprints do épico (SF1–SF4)
- **SF1 — S35 Remediation & Governança Real**
  - Refazer G0–G5 com API/UI/metrics reais (news_v2, contestacao_v0).
  - Limites/SLO aplicados; promtool + firing/resolution; hash publish/runtime comparado; actor obrigatório; eventos OracleOps/Truth com flow/mode/version; `slo_breach` registrado.
  - Pilotos reais (sem SQLite/fixtures duplicados); screenshots reais; bundle completo.
- **SF2 — Revalidação S30–S34 (multifluxo v1)**
  - Substituir dispatcher/SQLite por execuções reais; observabilidade com promtool + firing; painéis exportados.
  - Corrigir gates que ignoram rc (S31); S33 SLOs avaliando métricas reais; S34 pilotos/observabilidade sem placeholders.
- **SF3 — Revalidação S20–S29 (auth, truth kernel, decision/ORR)**
  - Smoke API/UI para auth/rotas protegidas (IdP stub); truth state machine com dados reais; decision quality via API/UI/metrics.
  - ORR reroda gates críticos com evidências; S27 ingestion/console smoke real; S26 frontend build/test + acessibilidade/obs.
- **SF4 — Revalidação S5–S19 (fundação)**
  - Substituir checklists/snapshots por smoke API/UI/metrics; Explorer S13 com dados atuais; UI evidence trace S7 e GO S6 rerodados; S5–S12 com integration tests mínimos e observabilidade.

## 3) Matriz F1–F22 → sprint
- **SF1:** F1–F5 (S35), F6–F7 (S34), F8 (S33) quando impactos cruzarem rollout; focado em rollout gov.
- **SF2:** F6–F7 (S34), F8 (S33), F9–F11 (S31–S30).
- **SF3:** F12–F18 (S29–S20).
- **SF4:** F19–F22 (S13–S5) e revalidações básicas S1–S4 (estado desconhecido).

## 4) Gates/DoD transversais do épico
- Nenhum PASS com placeholder/mock silencioso; se mock for necessário, marca NO-GO explícito.
- Promtool + firing/resolution para cada alerta declarado; evidências incluem query PromQL não vazia e print de firing.
- Smoke API/UI headless com dataset real ou fixture oficial; screenshots reais obrigatórias.
- Hash/catalogo comparado publish vs runtime; drift bloqueia operação e é evidenciado.
- Actor obrigatório e auditoria completa em operações críticas; chamadas sem actor → 4xx e evidência.
- Scorecards rerodados têm carimbo de data, commit, hash dos artefatos e anotam mocks/limitações; bundles contêm logs/metrics/screenshots/hashes.

## 5) In/Out do épico
- **IN:** hardening de gates/scripts/scorecards; observabilidade real; RBAC; SLO/alerta aplicado; rerun de sprints críticas; evidências fresh.
- **OUT:** features novas de domínio (novos fluxos/agentes), blockchain/blocos, multi-tenant, canary auto-tuning, refactors amplos fora dos itens de gate/obs/RBAC.

## 6) Dependências
- Ambiente com Prometheus/Alertmanager e IdP stub; capacidade de rodar UI headless (Playwright/Cypress).
- Datasets atuais ou fixtures oficiais; acesso a scorecards antigos e scripts `bin/sXX_*`.
- Tempo de rerun controlado (janela por sprint) e budget para capturar evidências.

## 7) Riscos e mitigação
- **Ambiente ausente (Prom/IdP):** bloquear GO e registrar NO-GO; preparar mocks explícitos só para desenvolvimento, não para PASS.
- **Tempo vs abrangência:** priorizar S35 e S30–S34; aplicar matriz de criticidade para sprints antigas.
- **Dados sensíveis:** usar fixtures oficiais; anonimizar se necessário e documentar.
- **Flakiness de UI/metrics:** repetir smoke com retries limitados e logs; não mascarar FAIL.

## 8) Critério de sucesso do épico
- Todos os findings F1–F22: resolvidos ou marcados NO-GO explícito com evidência.
- S36–S39 entregam bundles com evidências reais e scorecards rerodados; GO de S35 só após pilotos/obs reais.
- Planner/ACE conseguem executar gates sem adivinhação; Stakeholder recebe mapa claro de sprints saneadas vs pendências.

# Inspectah — KPIs da Máquina de Desenvolvimento

## Resumo executivo
- Sprint 35 reporta GO em rollout governado, mas gates e evidências são sintéticos; confiança operacional baixa.
- Catalogação/versionamento existe, porém limites/SLO/alertas não são aplicados e RBAC é opcional.
- Observabilidade e pilotos não exercitam API/UI reais, comprometendo feedback para OracleOps/Truth.

## KPIs de fluxo/entrega
- Frequência de sprints GO reais: baixa confiança; scorecards S4–S34 existem, mas não foram rerodados; S35 GO é inválido pelos gaps de rollout.
- Lead time spec→plan→exec: aparente curto em sprints recentes (muitos scripts automatizados), sem validação externa.
- Taxa de retrabalho prevista: alta se rollout e fluxos multifluxo forem exercitados em produção (limites/SLO ausentes).
- Sprint GO falsa: S35 identificado; demais sprints não revalidados podem esconder GO falso.
- Dívida crítica: governança de rollout sem enforcement de limites/SLO/RBAC; ausência de revalidação integrada dos gates antigos.

## KPIs de qualidade de código e arquitetura
- Módulos saudáveis/remendáveis: `app/flows/*` estruturado, mas lacunas de invariantes deixam arquitetura remendável; demais módulos não reavaliados nesta rodada.
- Cobertura de testes em áreas críticas: unitários felizes em flows; faltam casos negativos e integração API/UI/observabilidade; cobertura histórica dos demais sprints não verificada.

## KPIs de processo e esteira
- Aderência ao Sprint Playbook: parcial; S35 com G2/G3/G4 placeholders; sprints anteriores com scorecards, não rerodados.
- Aderência ao Planner: tasks cumpridas superficialmente em S35 (evidências auto-geradas); outras sprints não verificadas.
- Saúde CI/ORR: scripts e scorecards até S34 presentes; sem rerun, não há garantia de integridade atual.

## Pontos fortes e fracos
- Pontos fortes: roadmap/documentação de S35 bem estruturado; catálogo de fluxos/versionamento presente; instrumentação básica definida; histórico de scorecards por sprint está versionado.
- Pontos fracos: S35 ignora limites críticos; ausência de SLO/OracleOps/Truth; RBAC opcional; pilotos e observabilidade falsos; sprints anteriores não foram revalidadas e podem conter GO falso (ex.: S34 observabilidade/pilotos simulados; S33 SLO gate só parseia markdown; S31 gate ignora rc de testes; S32 valida só DB limpo/unitários; S30 G4/G5 usam dispatcher fictício sem API/metrics reais; S29 ORR/G5 apenas reusa scorecards e sanity mínimo; S27 backend/front sem smoke real; S26 frontend depende de node_modules e não valida UX/obs; S25/S24 gates em DB local/golden offline sem integração real; S21 ganchos/admin e S20 auth só testam FE/doc/presença; S13 Explorer depende de snapshots estáticos; S7 UI evidence smoke mínima/local; S6 GO só lê scorecards; S5 G2 é checklist de arquivos + pytest opcional).

## Tabela — bem / ruim / como melhorar
| Eixo | O que está bem | O que está ruim | Como melhorar |
| --- | --- | --- | --- |
| Spec | Capítulo 1–2 definem objetivos, gates e SLOs claros; scorecards históricos versionados | Contratos de SLO/OracleOps não se materializam; sprints antigas sem revalidação | Tornar SLOs parte do schema de rollout e exigir fonte de dados/alerta em DoD; checklist de revalidação periódica |
| Plan | Tasks/waves mapeadas (G0–G5) | Gates aceitam placeholders e testes repetidos | Planner deve exigir evidências reais (API/UI/metrics) e casos negativos por limite; replanejar revalidação de sprints antigas |
| Exec | Serviço de flows/catalogo implementado | Limites/SLO/RBAC não aplicados; pilotos sintéticos | Implementar enforcement, conectar métricas/alerts, refazer pilotos em ambiente real |
| Esteira | Scripts bin/s35_* e scorecards s4–s34 disponíveis | Scripts não exercitam runtime; scorecards não rerodados | Acrescentar smoke HTTP, promtool, comparação de hashes e bloqueio se placeholder detectado; rotina de rerun de gates críticos |
| UI | Painel de rollout e hooks React presentes | Evidências de UI são placeholders; nenhuma captura real | Automatizar testes e screenshots reais via e2e (Playwright) durante G2/G4 |

## Recomendações por papel
- **Spec Master**: firmar contrato mínimo de rollout (actor obrigatório, SLO fonte única, deadlines) e refletir em schemas/API/tests; definir rotina de revalidação para sprints históricas críticas.
- **Planner**: reforçar gates com simulação de breaches e proibir placeholders; adicionar step de validação de métricas reais; planejar rerun de gates de s4–s34 em ambiente controlado.
- **ACE Exec**: implementar enforcement de limites e SLO, integrar OracleOps/alertas, rodar pilotos via API/UI reais com rollback; reexecutar gates críticos de sprints anteriores onde houver dívidas conhecidas.
- **PO/Stakeholder**: não aceitar GO de S35 até pilotos reais e observabilidade comprovada; priorizar refação dos gates G3/G4 e exigir amostras reais das sprints anteriores mais críticas (S21–S34).

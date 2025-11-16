# Inspectah — Sprint 4 — Gate T0 (Discovery) Checklist

Gate responsável por garantir que a Sprint 4 só começa quando o terreno conceitual está firme, sem dúvidas sobre escopo, fontes e responsáveis.

## Pré-requisitos confirmados

- **Capítulos 1–4 revisados integralmente** (visão, gates, plano e guia mental) e absorvidos pela equipe técnica.
- **Fontes P0 oficiais desta sprint**: `api_market_prices`, `html_market_watch`, `rss_news_minimal` — rascunhos já versionados em `configs/sources/*.yaml` e planejados para o caminho canônico `config/sources/sprint_4/fontes_p0/` durante A2.
- **Contexto da Sprint 3** revisado em `docs/sprint_3_orr_summary.md`, com lições incorporadas ao planejamento atual.
- **ORR S3 permanece estável** (todos os gates anteriores verdes com fixtures de laboratório), assegurando referência para a migração às fontes reais da S4.

## Checklist operacional

| item | explicacao | status | evidencia |
| --- | --- | --- | --- |
| Lista de Fontes P0 validada com PO e stakeholders | Sem uma lista fechada de 3–5 fontes reais não abrimos a sprint | OK | `configs/sources/api_market_prices.yaml`, `configs/sources/html_market_watch.yaml`, `configs/sources/rss_news_minimal.yaml` (espelhados futuramente em `config/sources/sprint_4/fontes_p0/`) |
| Capítulos 1–4 lidos, com dúvidas sanadas antes de executar | Evita discrepância entre visão, gates, plano e execução | OK | `Sprint 4/Capitulo 1.md` … `Sprint 4/Capitulo 4.md` |
| Modelo mental de camadas (Ingestão → Evidence Vault → Exploração) validado entre PO, Eng e Operações | Sem alinhamento de camadas o restante dos gates fica frágil | OK | `docs/sprint_4_modelo_dados_invariantes.md` |
| Personas e cenários críticos da S4 aceitos | Precisamos saber quem opera e quais perguntas precisam resposta | OK | `Sprint 4/Capitulo 1.md` §6 |
| Riscos e dependências herdados da S3 mapeados | Mitiga repetição de incidentes e prepara plano de contingência | OK | `docs/sprint_3_orr_summary.md`, anotação na seção “Riscos e mitigações” abaixo |
| Time sabe onde salvar evidências e scorecards | Define desde o início o padrão `out/evidence/S4_Tx_*` e `out/scorecards/S4_Tx_*.json` | OK | Este documento + Capítulo 2 |

## Riscos e mitigações iniciais

- **Fontes com dados incompletos ou mutáveis** — Mitigado exigindo fixtures reais versionadas a partir da primeira coleta (ver plano das trilhas B1/B2).
- **Exposição de credenciais em registry** — Mitigado padronizando configs em YAML sem segredos (T2 reforçará).
- **Explore M0 dependente de caminhos informais** — Mitigado descrevendo o relacionamento Fonte → Run → Item → Evidência → Consulta no modelo oficial antes de implementar.

## Registro da decisão

- Gate owner: Engenharia (Codex) + PO.
- Data da revisão: 2025-11-15.
- Status previsto: `PASS` desde que os itens acima permaneçam verdadeiros. Ajustes futuros devem ser registrados nesta mesma página com referência ao scorecard `out/scorecards/S4_T0_discovery.json`.

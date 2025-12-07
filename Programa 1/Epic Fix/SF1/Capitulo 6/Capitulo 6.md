# SF1 — Capítulo 6 — Referências & Estado da Arte
- s35_slos.md (fonte única de SLOs rollout).
- Prometheus/Alertmanager configs em `observability/alerts/s35/*.yaml`.
- Dashboards: `observability/dashboards/s35_flow_rollout_overview.json`.
- Playbooks/gates existentes: `bin/s35_*` (serão reforçados).
- UI componentes: `frontend/inspectah-ui` flows console.
- Auditoria/report: AUDIT_ROADMAP_REPO.md, AUDIT_KPIS_DEV.md (F1–F5).
- Fonte real: newsdata.io `/api/1/latest` com `apikey=pub_1eb578cc391148dfb475bf474f2d2173`, `country=br`, `language=pt`, `domainurl` lista BR (g1.globo.com, folha.uol.com.br, estadao.com.br, valor.globo.com, infomoney.com.br, agenciabrasil.ebc.com.br, correiobraziliense.com.br, gazetadopovo.com.br, nsctotal.com.br, correiodopovo.com.br, diariodonordeste.verdesmares.com.br, atarde.com.br, diariodopara.dol.com.br, adrenaline.com.br, lance.com.br); usar em G4.

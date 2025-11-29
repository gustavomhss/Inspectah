# Sprint 25 — Deslocados Reconciliation Log

## Checkpoint
- Branch: feature/s25_truth_v1_5
- Base repo: /Users/gustavoschneiter/Documents/Inspectah
- Quarentena interna: Arquivo/ (espelho da antiga Deslocados; mantida como backup, não removida).

## Passos executados
- Sincronizei o conteúdo de Arquivo/ para a árvore oficial (app, bin, configs, data, docs, migrations, scripts, tests). Subpastas não-Inspectah (Desktop/Downloads) foram ignoradas.
- Removi artefatos de cache (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `*.pyc`) e arquivos órfãos como `app.api.console_routes.get_flow` e `app/agents/README.tmp`.
- Reforcei o console flow fraco em `app/api/console_routes.py` (GET/PUT `/api/console/agents/flow` apenas file-based, sem schemas fortes) e alinhei scripts auxiliares (`bin/check_console_endpoints.sh`, `scripts/print_api_routes.py`). Teste `tests/api/test_console_agents_flow.py` verde.
- Restaurei modelos/serviços principais (agents/debunk/core) e migrations da S25 (`0002_s25_truth_models.py`, `0003_s25_layers_traces_incidents.py`).
- Sincronizei configs e dados da S25 (`configs/promotion_policies`, `configs/threatmodel`, `configs/profiles/confidence_profiles.json`, `data/s25`, dashboards) e scripts S25 (`bin/s25_g0`..`bin/s25_g7`, `bin/s25_make_bundle.sh`, `bin/s25_orr.sh`).
- Adicionei pacotes/tests da S25 (context, layers, policies, threatmodel, truth, truthdb, fixtures, console tests).
- Console frontend: `useAgentsFlow` normaliza payload fraco/[] e sempre constrói camadas fixas para evitar quebra da UI quando o arquivo não existe ou tem formato livre.
- Console/admin UI: expostos endpoints mínimos de admin (`/admin/health`, `/admin/cases`, `/admin/cases/{id}`, timeline/xray) para alinhar com o frontend e remover 404/Not Found.
- Frontend dev proxy ajustado em `frontend/inspectah-ui/vite.config.ts` para encaminhar `/api` e `/admin` ao backend (`http://127.0.0.1:8000`), eliminando loops/timeouts por 404 no dev server.
- Admin agents flow: `app.agents.service` agora expõe helpers fracos `get_flow`/`save_flow` usando `out/runtime/console_agents_flow.json`, e `/admin/agents/flow` passou a usar esses helpers, compartilhando o mesmo arquivo do console e evitando AttributeError/500.
- UI: botão de acesso ao painel Admin exposto no header público, reutilizando o login já existente (AuthGuard redireciona para /login se não autenticado).
- Console agents CRUD: adicionei POST `/api/console/agents` e GET/POST `/api/console/agents/{agent_id}/instructions`, alinhando com o frontend para criação/edição de agentes e instruções sem 404/405.

## Sanidade executada
- `pytest tests/api/test_console_agents_flow.py` — OK
- `pytest tests/truth tests/context tests/layers tests/policies tests/threatmodel tests/truthdb` — OK
- Gates: `bin/s25_g0`..`bin/s25_g7` e `bin/s25_orr.sh` — OK

## Pendências/observações
- Pasta Arquivo/ permanece como backup; não removida.
- Outras modificações herdadas do rsync (scripts antigos, docs legados) estão staged/commitáveis para manter a árvore limpa.

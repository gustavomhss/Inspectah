# Inspectah — Sprint 28
## Capítulo 3 — Bloco 4
### Frontend (Console de Fontes v2), Scripts de Gates, CI e Filemap Consolidado

---

#### 3.4.1 Papel do Console de Fontes v2 na arquitetura da S28

O Console de Fontes v2 é a **face humana** de tudo o que a Sprint 28 está construindo no backend. Ele precisa ser:

- a principal ferramenta de operação diária de fontes,  
- uma janela fiel para o estado do domínio (`Source`),  
- um painel de controle para ON/OFF e CRUD,  
- um consumidor disciplinado do Design System Admin v1.

Se o backend é a musculatura, o console é o sistema nervoso motor que permite ao operador "mexer" no sistema sem precisar encostar em terminal.

---

#### 3.4.2 Arquitetura de frontend da feature de fontes

**Diretório raiz da feature**  
`frontend/inspectah-ui/src/features/sources/`

Dentro desse diretório, a Sprint 28 organiza o console de fontes v2 em quatro grupos principais:

1. **Páginas** (`pages/`)
2. **Componentes de UI** (`components/`)
3. **Cliente de API** (`api/`)
4. **Tipos/helpers locais** (`types/`, `hooks/` se necessário)

Essa organização segue o padrão de outras features do Inspectah, evitando que a Sprint 28 vire um “módulo especial” com convenções próprias.

---

#### 3.4.3 Páginas principais

##### 3.4.3.1 `SourcesListPage`

Caminho:  
`frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`

Responsabilidades:
- Exibir lista de fontes com filtros, paginação e ações principais.  
- Ser a página de entrada do console de fontes v2.  
- Integrar com `adminSourcesApi` para buscar dados.

Elementos principais da UI:
- **Cabeçalho** com título (ex.: "Fontes"), botão “Nova Fonte” e, opcionalmente, indicação de quantas fontes estão ativas/desativadas.  
- **Área de filtros**:
  - filtros por `type`, `state`, `domain`, `mode`, `criticality`;  
  - campo de busca por nome/slug, se disponível.  
- **Tabela de fontes** usando `SourceListTable`.  
- **Ações rápidas** via `SourceActionsMenu` em cada linha.

Estados da tela a serem tratados:
- carregando (spinner/placeholders),  
- erro (mensagem amigável quando a API falha),  
- lista vazia (mensagem e call-to-action para criar primeira fonte).

##### 3.4.3.2 `SourceFormPage`

Caminho:  
`frontend/inspectah-ui/src/features/sources/pages/SourceFormPage.tsx`

Responsabilidades:
- Criar nova fonte.  
- Editar fonte existente.  
- Expor um formulário guiado que reflita o modelo de domínio.

Seções sugeridas no formulário:
- **Dados básicos**: nome, descrição, tipo.  
- **Classificação**: domínio, categoria.  
- **Operação**: modo (`AUTO`/`MANUAL`), cadência/schedule, config técnica (URL, método HTTP, etc.).  
- **Risco**: criticidade.  
- **Estado inicial** (em criação) onde fizer sentido (normalmente `ACTIVE` ou `DISABLED`).

Validações em frontend:
- campos obrigatórios destacados (nome, tipo, modo, config mínima);  
- validação básica de formato (URL válida, etc.);  
- mensagens de erro claras por campo.

O backend continua sendo a autoridade final (P6 de Cap. 3.1), mas o frontend ajuda a evitar erros triviais.

---

#### 3.4.4 Componentes principais da UI

##### 3.4.4.1 `SourceListTable`

Caminho:  
`frontend/inspectah-ui/src/features/sources/components/SourceListTable.tsx`

Responsabilidades:
- Renderizar a tabela de fontes recebida da API.  
- Não conhecer `fetch` nem estado global — recebe dados via props.

Colunas típicas:
- Nome  
- Tipo  
- Domínio  
- Modo (`AUTO`/`MANUAL`)  
- Estado (`SourceStateBadge`)  
- Criticidade  
- Última mudança de estado  
- Ações (`SourceActionsMenu`)

##### 3.4.4.2 `SourceStateBadge`

Caminho:  
`frontend/inspectah-ui/src/features/sources/components/SourceStateBadge.tsx`

Responsabilidades:
- Exibir estado da fonte de maneira compacta e legível (texto + cor/pílula).  
- Usar componentes do Design System Admin v1 (ex.: `Badge`).

Estados esperados:
- `ACTIVE` → estilo positivo.  
- `DISABLED` → estilo de alerta/pausa.  
- `DEPRECATED` → estilo de "fim de ciclo"/warning.

A lógica visual deve ser simples e declarativa, sem lógica de negócio ali dentro.

##### 3.4.4.3 `SourceActionsMenu`

Caminho:  
`frontend/inspectah-ui/src/features/sources/components/SourceActionsMenu.tsx`

Responsabilidades:
- Oferecer ações de linha como "Ver detalhes", "Editar", "Ativar", "Desativar", "Deprecar".  
- Chamar callbacks passados pela página (que, por sua vez, usam o `adminSourcesApi`).

Boas práticas:
- Desabilitar ou esconder ações inválidas de acordo com o estado atual (ex.: não mostrar "Ativar" se já está `ACTIVE`).  
- Confirm dialogs para ações destrutivas (desativar/deprecar).  
- Feedback visual (loading/disabled) enquanto a operação está em andamento.

---

#### 3.4.5 Cliente de API — `adminSourcesApi`

Caminho:  
`frontend/inspectah-ui/src/features/sources/api/adminSourcesApi.ts`

Responsabilidades:
- Encapsular chamadas à API `/admin/sources`.  
- Expor funções tipadas e previsíveis que o restante da feature usa.

Funções típicas:
- `listSources(filters)`: busca lista paginada de fontes.  
- `getSource(id)`: busca detalhes de uma fonte.  
- `createSource(payload)`: cria nova fonte.  
- `updateSource(id, payload)`: edita fonte existente.  
- `activateSource(id)`, `disableSource(id)`, `deprecateSource(id)`: operações de estado.

Boas práticas:
- Tratar erros da API e converter códigos HTTP em mensagens amigáveis a serem exibidas na UI.  
- Manter os tipos (interfaces/Typescript types) sincronizados com os schemas do backend (`SourceListItem`, `SourceDetail`, etc.).

---

#### 3.4.6 Testes de UI / e2e do console de fontes

Diretório de testes sugerido:  
`frontend/inspectah-ui/tests/sources/`

Arquivo principal da S28:  
`frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts`

Cenários obrigatórios (alinhados ao Gate S28_G3):

1. **Cadastro de nova fonte (Caso A)**  
   - Abrir `SourcesListPage`.  
   - Clicar em “Nova Fonte” → `SourceFormPage`.  
   - Preencher campos obrigatórios e salvar.  
   - Ver nova fonte na lista.

2. **Desativar fonte problemática (Caso B)**  
   - A partir de fonte `ACTIVE`, usar `SourceActionsMenu` para desativar.  
   - Ver `SourceStateBadge` mudar para `DISABLED`.

3. **Reativar fonte após manutenção (Caso C)**  
   - A partir de fonte `DISABLED`, reativar.  
   - Ver `SourceStateBadge` voltar para `ACTIVE`.

4. **Editar fonte (Caso D)**  
   - Abrir tela de edição, modificar campos como cadência/descritivo.  
   - Salvar e verificar na lista e no detalhe.

5. **Fluxos de robustez**  
   - Tratar lista vazia com mensagem amigável.  
   - Simular erro de API e verificar se a UI mostra mensagem de falha (sem travar a tela).

Esses testes podem ser escritos em Cypress, Playwright ou framework de teste usado no projeto — o importante é que sejam automatizados e integrados ao CI.

---

#### 3.4.7 Scripts de gates da Sprint 28 e sua função na arquitetura

Diretório: `bin/`

Scripts esperados (recap):
- `bin/s28_g0_scope_and_baseline.sh`  
- `bin/s28_g1_sources_model_and_schema.sh`  
- `bin/s28_g2_sources_admin_api.sh`  
- `bin/s28_g3_sources_console_front.sh`  
- `bin/s28_g4_sources_ingestion_integration.sh`  
- `bin/s28_g5_observability_and_legacy_sanity.sh`  
- `bin/s28_g6_demo_internal.sh`  
- `bin/s28_g7_go_no_go.sh`

Características comuns desejáveis:
- `set -euo pipefail` no topo.  
- Uso consistente de variáveis como `ROOT_DIR`, `EVIDENCE_DIR`, `SCORECARDS_DIR`.  
- Logs de execução enviados para `out/evidence/S28_GX_*/`.  
- Scorecards JSON escritos em `out/scorecards/` com nomes estáveis.

Exemplo de estrutura genérica (pseudo-shell):

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S28_G3_sources_console_front"
SCORECARD="out/scorecards/S28_G3_sources_console_front.json"

mkdir -p "$EVIDENCE_DIR" out/scorecards

# Exemplo: rodar testes e build do front
(
  cd frontend/inspectah-ui
  npm test >"$ROOT_DIR/$EVIDENCE_DIR/test.log" 2>&1
  npm run build >"$ROOT_DIR/$EVIDENCE_DIR/build.log" 2>&1
)

# Gerar scorecard mínimo (poderia ser via script Python ou `jq`)
cat >"$SCORECARD" <<EOF
{
  "gate_id": "S28_G3_sources_console_front",
  "status": "PASS",
  "frontend_build_ok": true,
  "flows_covered": ["A", "B", "C", "D"],
  "open_ux_issues": []
}
EOF
```

Cada script deve ser escrito com o mesmo cuidado de um teste: se quebrar, é porque algo essencial da sprint quebrou.

---

#### 3.4.8 Integração com CI — workflow da Sprint 28

Arquivo sugerido de workflow:  
`.github/workflows/s28-gates.yml`

Objetivo do workflow:
- Ser o "botão único" que roda todos os gates da S28 em ambiente CI (GitHub Actions).  
- Produzir artefatos (logs, evidências, scorecards) anexados ao job.

Estrutura conceitual:
- Disparadores:  
  - `workflow_dispatch` (manual),  
  - opcionalmente em `pull_request` para branch de S28.

- Jobs (em linhas gerais):
  - `s28-gates`:  
    - `runs-on: ubuntu-latest`  
    - `steps`:
      1. Checkout.  
      2. Setup de Python e Node (versões alinhadas com o projeto).  
      3. Instalação de dependências backend/frontend.  
      4. Execução sequencial ou parcialmente paralela dos scripts `bin/s28_gX_*.sh`.  
      5. Upload de `out/evidence/**` como artefatos.  
      6. Upload de `out/scorecards/**` como artefatos.

Regra de falha:
- Qualquer script de gate retornando exit code != 0 deve fazer o workflow falhar.  
- Isso protege a main/branch de S28 contra merge em estado inconsistente.

---

#### 3.4.9 Filemap consolidado da Sprint 28

Para facilitar implementação e revisão, segue o filemap consolidado da S28 (backend + frontend + gates + CI + evidências):

**Backend — Domínio & API**
- `app/sources/models.py`  
- `app/sources/schemas.py`  
- `app/api/admin_sources_routes.py`  
- `app/ingestion/scheduler.py`  
- `app/ingestion/models.py` (ou equivalente contendo `IngestionRun`)

**Migrations**
- `migrations/versions/00xx_s28_sources_model_consolidation.py`

**Testes backend**
- `tests/domain/test_sources_model_invariants.py`  
- `tests/api/test_admin_sources_crud_onoff.py`  
- `tests/integration/test_sources_ingestion_onoff.py`

**Frontend — Console de Fontes v2**
- `frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`  
- `frontend/inspectah-ui/src/features/sources/pages/SourceFormPage.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceListTable.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceStateBadge.tsx`  
- `frontend/inspectah-ui/src/features/sources/components/SourceActionsMenu.tsx`  
- `frontend/inspectah-ui/src/features/sources/api/adminSourcesApi.ts`

**Testes frontend**
- `frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts`  
- (eventuais arquivos adicionais por fluxo, se necessário, sob o mesmo diretório)

**Scripts de gates**
- `bin/s28_g0_scope_and_baseline.sh`  
- `bin/s28_g1_sources_model_and_schema.sh`  
- `bin/s28_g2_sources_admin_api.sh`  
- `bin/s28_g3_sources_console_front.sh`  
- `bin/s28_g4_sources_ingestion_integration.sh`  
- `bin/s28_g5_observability_and_legacy_sanity.sh`  
- `bin/s28_g6_demo_internal.sh`  
- `bin/s28_g7_go_no_go.sh`

**CI & Evidências**
- `.github/workflows/s28-gates.yml`  
- `out/evidence/S28_G*/**`  
- `out/scorecards/S28_G*.json`  
- `out/scorecards/S28_overall.json`

---

Com este Bloco 4, o Capítulo 3 da Sprint 28 fica completo:  
- o frontend (console de fontes v2) está detalhado como peça de primeira classe;  
- os scripts de gates são mapeados como parte da arquitetura;  
- o workflow de CI garante execução automatizada;  
- o filemap consolidado fecha o mapa físico da sprint para implementação e revisão.
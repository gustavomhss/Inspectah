# Sprint 7 — Capítulo 3 (v2)

## Filemap, Estrutura de Artefatos e Pontes S6 ↔ S7

> Arquivo de referência: `docs/sprint_7/sprint_7_capitulo_3.md`  
> Este capítulo define a **topologia de arquivos** da Sprint 7, amarrada aos objetivos do Capítulo 1 e aos gates do Capítulo 2.  
> Todos os nomes de arquivos e caminhos aqui descritos são **contratos** e devem ser refletidos no repositório.  
> Sempre que este capítulo divergir do estado atual do repo, este capítulo vence (o repo deve ser ajustado para cumprir o filemap).

---

## 1. Princípios de desenho da Sprint 7

1. **Compatibilidade total com a Sprint 6**  
   - Nada da S7 duplica ou substitui a lógica do runtime de coleta/normalização/evidência da S6.  
   - Toda integração com o motor existente passa por uma camada clara de adaptação.

2. **UI como casca fina**  
   - A aplicação web vive em um módulo dedicado (`inspectah/ui/`) que conversa com o runtime da S6 via adaptadores.  
   - Não há lógica de domínio duplicada dentro da UI.

3. **Gates em primeiro lugar**  
   - Cada gate S7-G0…S7-G8 (Capítulo 2) tem script, scorecard e pastas de evidência explicitamente mapeados neste filemap.  
   - O Capítulo 4 usará esta estrutura como base para o plano de execução.

4. **Separação clara de responsabilidades**  
   - `docs/` descreve.  
   - `inspectah/ui/` implementa a UI e o bridge com S6.  
   - `bin/` orquestra (UI, gates, demos).  
   - `config/` guarda parâmetros.  
   - `tests/` protege comportamento.  
   - `out/` concentra evidência, scorecards, logs e artefatos de demo.

5. **Estado atual vs. alvo S7**  
   - Artefatos da Sprint 6 (como `inspectah/sprint6/` e `config/fields/dominio_piloto.yaml`) são **reutilizados**.  
   - Artefatos novos da Sprint 7 (UI, scripts S7, testes S7) são introduzidos de forma **não intrusiva**, plugando na base existente.

---

## 2. Visão macro da árvore de arquivos da S7

Abaixo, uma visão resumida dos principais elementos introduzidos ou usados pela Sprint 7 (apenas linhas relevantes à S7):

```text
Inspectah/
├── docs/
│   └── sprint_7/
│       ├── sprint_7_capitulo_1.md
│       ├── sprint_7_capitulo_2.md
│       ├── sprint_7_capitulo_3.md
│       ├── sprint_7_capitulo_4.md
│       └── sprint_7_resultados.md
├── bin/
│   ├── s7_ui_start.sh
│   ├── s7_ui_stop.sh
│   ├── s7_ui_open_browser.sh
│   ├── s7_g0_baseline.sh
│   ├── s7_g1_ui_boot_health.sh
│   ├── s7_g2_ui_sources_admin.sh
│   ├── s7_g3_ui_fields_preview.sh
│   ├── s7_g4_ui_query_consolidation.sh
│   ├── s7_g5_ui_evidence_trace.sh
│   ├── s7_g6_ui_only_flows.sh
│   ├── s7_g7_metrics_and_demo.sh
│   └── s7_g8_sprint_go_no_go.sh
├── config/
│   ├── ui_sprint_7.yaml
│   ├── fields/
│   │   └── dominio_piloto.yaml      # reutilizado da S6
│   └── sources/
│       ├── fonte_a.yaml             # reutilizados/atualizados via UI
│       ├── fonte_b.yaml
│       └── fonte_c.yaml
├── inspectah/
│   ├── sprint6/                     # runtime da S6 (já existente, reutilizado)
│   └── ui/
│       ├── __init__.py
│       ├── app.py                   # criação da aplicação web (FastAPI/Flask equivalente)
│       ├── config.py                # leitura de ui_sprint_7.yaml
│       ├── runtime_bridge.py        # camada de integração com inspectah.sprint6
│       ├── schemas.py               # modelos de dados (Pydantic ou equivalente)
│       ├── view_models.py           # modelos para renderização em templates
│       ├── views/
│       │   ├── admin_sources.py     # rotas de administração de fontes
│       │   ├── model_fields.py      # rotas de visualização/ajuste de campos
│       │   ├── query.py             # rotas de consulta e decisão consolidada
│       │   └── evidence.py          # rotas de rastreio de evidência
│       ├── templates/
│       │   ├── base.html
│       │   ├── admin_sources.html
│       │   ├── model_fields.html
│       │   ├── query.html
│       │   └── evidence_detail.html
│       └── static/
│           ├── css/
│           │   └── main.css
│           └── js/
│               └── main.js
├── tests/
│   └── sprint_7/
│       ├── test_ui_health.py
│       ├── test_ui_sources_admin.py
│       ├── test_ui_fields_preview.py
│       ├── test_ui_query_consolidation.py
│       └── test_ui_evidence_trace.py
└── out/
    ├── scorecards/
    │   ├── S7_G0_baseline.json
    │   ├── S7_G1_ui_boot_health.json
    │   ├── S7_G2_ui_sources_admin.json
    │   ├── S7_G3_ui_fields_preview.json
    │   ├── S7_G4_ui_query_consolidation.json
    │   ├── S7_G5_ui_evidence_trace.json
    │   ├── S7_G6_ui_only_flows.json
    │   ├── S7_G7_metrics_and_demo.json
    │   └── S7_G8_sprint_go_no_go.json
    ├── evidence/
    │   ├── S7_G0_baseline/
    │   ├── S7_G1_ui_boot_health/
    │   ├── S7_G2_ui_sources_admin/
    │   ├── S7_G3_ui_fields_preview/
    │   ├── S7_G4_ui_query_consolidation/
    │   ├── S7_G5_ui_evidence_trace/
    │   ├── S7_G6_ui_only_flows/
    │   ├── S7_G7_metrics_and_demo/
    │   └── S7_G8_sprint_go_no_go/
    └── logs/
        └── s7_ui.log
```

---

## 2.1. Mapa "Novo / Reutilizado / Modificado"

Tabela de classificação dos principais artefatos da S7 em relação ao estado herdado da S6:

| Caminho                                           | Tipo        | Status na S7                        | Observação rápida                                              |
|--------------------------------------------------|------------|-------------------------------------|-----------------------------------------------------------------|
| `inspectah/sprint6/`                             | Código      | **Reutilizado**                     | Runtime consolidado da S6. Não deve ser alterado pela S7.       |
| `config/fields/dominio_piloto.yaml`              | Config      | **Reutilizado**                     | Esquema canônico do domínio piloto, usado pela UI via bridge.   |
| `config/sources/fonte_a.yaml`                    | Config      | **Reutilizado / Atualizável**       | Fonte existente; será gerenciada pela UI (S7-G2).               |
| `config/sources/fonte_b.yaml`                    | Config      | **Reutilizado / Atualizável**       | Idem acima.                                                     |
| `config/sources/fonte_c.yaml`                    | Config      | **Reutilizado / Atualizável**       | Idem acima.                                                     |
| `docs/sprint_6/*`                                | Docs        | **Reutilizado**                     | Dossiê da S6, consumido por S7-G0 como baseline.                |
| `docs/sprint_7/sprint_7_capitulo_1.md`           | Docs        | **Novo S7**                         | Objetivos, escopo, métricas e filme da S7.                      |
| `docs/sprint_7/sprint_7_capitulo_2.md`           | Docs        | **Novo S7**                         | Gates S7-G0…S7-G8.                                              |
| `docs/sprint_7/sprint_7_capitulo_3.md`           | Docs        | **Novo S7**                         | Este filemap.                                                   |
| `docs/sprint_7/sprint_7_capitulo_4.md`           | Docs        | **Novo S7**                         | Plano de execução, baseado neste filemap.                       |
| `docs/sprint_7/sprint_7_resultados.md`           | Docs        | **Novo S7**                         | Wrap final da sprint.                                           |
| `inspectah/ui/__init__.py`                       | Código      | **Novo S7**                         | Pacote da UI.                                                   |
| `inspectah/ui/app.py`                            | Código      | **Novo S7**                         | Criação da aplicação web.                                       |
| `inspectah/ui/config.py`                         | Código      | **Novo S7**                         | Leitura de `config/ui_sprint_7.yaml`.                           |
| `inspectah/ui/runtime_bridge.py`                 | Código      | **Novo S7**                         | Ponte entre UI e `inspectah.sprint6`.                           |
| `inspectah/ui/schemas.py`                        | Código      | **Novo S7**                         | Modelos de dados para a UI.                                     |
| `inspectah/ui/view_models.py`                    | Código      | **Novo S7**                         | Modelos de apresentação.                                        |
| `inspectah/ui/views/admin_sources.py`            | Código      | **Novo S7**                         | Views de administração de fontes.                               |
| `inspectah/ui/views/model_fields.py`             | Código      | **Novo S7**                         | Views de campos e preview canônico.                             |
| `inspectah/ui/views/query.py`                    | Código      | **Novo S7**                         | Views de consulta e consolidação.                               |
| `inspectah/ui/views/evidence.py`                 | Código      | **Novo S7**                         | Views de evidência.                                             |
| `inspectah/ui/templates/*.html`                  | Template    | **Novo S7**                         | Camada visual da UI.                                            |
| `inspectah/ui/static/css/main.css`               | Estático    | **Novo S7**                         | Estilos da UI.                                                  |
| `inspectah/ui/static/js/main.js`                 | Estático    | **Novo S7**                         | Comportos básicos da UI.                                        |
| `bin/s7_ui_start.sh`                             | Script      | **Novo S7**                         | Sobe a UI.                                                      |
| `bin/s7_ui_stop.sh`                              | Script      | **Novo S7**                         | (Opcional) para a UI em dev.                                    |
| `bin/s7_ui_open_browser.sh`                      | Script      | **Novo S7**                         | Abre browser para a UI.                                         |
| `bin/s7_g0_baseline.sh`                          | Script      | **Novo S7**                         | Gate S7-G0.                                                     |
| `bin/s7_g1_ui_boot_health.sh`                    | Script      | **Novo S7**                         | Gate S7-G1.                                                     |
| `bin/s7_g2_ui_sources_admin.sh`                  | Script      | **Novo S7**                         | Gate S7-G2.                                                     |
| `bin/s7_g3_ui_fields_preview.sh`                 | Script      | **Novo S7**                         | Gate S7-G3.                                                     |
| `bin/s7_g4_ui_query_consolidation.sh`            | Script      | **Novo S7**                         | Gate S7-G4.                                                     |
| `bin/s7_g5_ui_evidence_trace.sh`                 | Script      | **Novo S7**                         | Gate S7-G5.                                                     |
| `bin/s7_g6_ui_only_flows.sh`                     | Script      | **Novo S7**                         | Gate S7-G6.                                                     |
| `bin/s7_g7_metrics_and_demo.sh`                  | Script      | **Novo S7**                         | Gate S7-G7.                                                     |
| `bin/s7_g8_sprint_go_no_go.sh`                   | Script      | **Novo S7**                         | Gate S7-G8.                                                     |
| `config/ui_sprint_7.yaml`                        | Config      | **Novo S7**                         | Configuração da UI.                                             |
| `tests/sprint_7/*`                               | Testes      | **Novo S7**                         | Testes específicos de UI/bridge.                                |
| `out/scorecards/S7_G*.json`                      | Runtime     | **Novo S7 (gerado)**               | Scorecards dos gates.                                           |
| `out/evidence/S7_G*/`                            | Runtime     | **Novo S7 (gerado)**               | Evidências dos gates.                                           |
| `out/logs/s7_ui.log`                             | Runtime     | **Novo S7 (gerado)**               | Log consolidado da UI.                                          |

---

## 3. Documentação da Sprint 7 (`docs/sprint_7/`)

**Objetivo**: concentrar toda a documentação da S7, alinhada ao Sprint Playbook.

Arquivos:

- `docs/sprint_7/sprint_7_capitulo_1.md`  
  - Objetivo, escopo, métricas (M1–M6), personas e filme da S7.  
  - Já aprovado e considerado locked.

- `docs/sprint_7/sprint_7_capitulo_2.md`  
  - Definição dos gates S7-G0…S7-G8, scripts, scorecards, evidências e critérios de PASS/GO.  
  - Já aprovado e considerado locked.

- `docs/sprint_7/sprint_7_capitulo_3.md`  
  - Este capítulo: filemap detalhado, apontando cada arquivo aos objetivos e gates da Sprint 7.

- `docs/sprint_7/sprint_7_capitulo_4.md`  
  - Plano de execução da S7: ordem de implementação, comandos principais, checklists de validação.  
  - Deve referenciar explicitamente os arquivos definidos neste Capítulo 3.

- `docs/sprint_7/sprint_7_resultados.md`  
  - Wrap final da Sprint 7: o que foi entregue, como rodar a demo, limitações e próximos passos.

Regras:

- Qualquer novo artefato criado na S7 que seja relevante para operação ou entendimento deve ser ancorado aqui.  
- Os capítulos 1–4 e resultados formam o "dossiê" da Sprint 7 e são referenciados por S7-G0 e S7-G8.

---

## 4. UI e runtime bridge (`inspectah/ui/`)

A UI da Sprint 7 vive em `inspectah/ui/` e conversa com o runtime existente de S6. Essa pasta é o coração da S7.

### 4.1. Núcleo da aplicação

- `inspectah/ui/__init__.py`  
  - Marca o pacote Python da UI.  
  - Opcionalmente expõe uma função `create_app()` para frameworks que suportem isso.

- `inspectah/ui/app.py`  
  - Ponto de criação da aplicação web (FastAPI, Flask ou equivalente).  
  - Registra rotas definidas em `inspectah/ui/views/`.  
  - Conecta middlewares básicos (log, error handling, static files, templates).  
  - É o alvo principal do servidor HTTP (ex.: `uvicorn inspectah.ui.app:app`).

- `inspectah/ui/config.py`  
  - Lê `config/ui_sprint_7.yaml`.  
  - Expõe funções como `get_settings()` (porta, host, modo debug, paths de templates/static, flags da S7).

- `inspectah/ui/runtime_bridge.py`  
  - Camada única de integração com o runtime da S6.  
  - Responsável por:
    - ler/atualizar fontes em `config/sources/*.yaml` (CRUD de fontes);
    - ler o modelo canônico em `config/fields/dominio_piloto.yaml`;
    - disparar pré-visualização de campos (equivalente ao `inspectah_fields_preview`);
    - disparar consultas e retornar registros canônicos;
    - mapear registros exibidos na UI aos pacotes de evidência em `out/evidence/dominio_piloto/...`;
    - expor função para cálculo do valor consolidado (usando a estratégia implementada na S7, que por sua vez pode delegar a funções em `inspectah/sprint6/` quando fizer sentido).

- `inspectah/ui/schemas.py`  
  - Modelos de dados (por exemplo, Pydantic) usados nos handlers da UI.
  - Exemplo de entidades: `UISource`, `UIField`, `UIQueryRequest`, `UIQueryResult`, `UIEvidenceLink`, etc.

- `inspectah/ui/view_models.py`  
  - Modelos específicos para renderização em templates (camada de apresentação).  
  - Permite separar o contrato de API dos detalhes de UI.

### 4.2. Views e rotas

As views implementam as rotas que suportam os fluxos da S7, diretamente ligados às personas e gates.

- `inspectah/ui/views/admin_sources.py`  
  - Rotas para administração de fontes (lista, criação, edição, desativação).  
  - Usa `runtime_bridge` para ler e persistir configs em `config/sources/*.yaml`.  
  - Suporta o fluxo de S7-G2 e histórias S7-A1 (admin).

- `inspectah/ui/views/model_fields.py`  
  - Rotas para visualização e ajuste controlado do modelo canônico.  
  - Lê `config/fields/dominio_piloto.yaml` via `runtime_bridge`.  
  - Exibe lista de campos e preview canônico (gatilho para S7-G3).

- `inspectah/ui/views/query.py`  
  - Rotas para consulta: formulário de filtros e resultado com valores por fonte.  
  - Chama `runtime_bridge` para executar consultas, obter registros por fonte e calcular valor consolidado.  
  - Exibe explicação da regra de decisão (ligado a S7-G4 e métricas M4/M5).

- `inspectah/ui/views/evidence.py`  
  - Rotas para navegação de evidência a partir de um registro exibido.  
  - Usa `runtime_bridge` para mapear registro ↔ pacote de evidência em `out/evidence/dominio_piloto/...`.  
  - Suporta o fluxo de S7-G5 e métrica M6 (até 2 cliques até evidência).

### 4.3. Templates e estáticos

Os templates e recursos estáticos implementam a interface visual, ainda que de forma simples.

- `inspectah/ui/templates/base.html`  
  - Layout base, inclui cabeçalho, rodapé e região de conteúdo.

- `inspectah/ui/templates/admin_sources.html`  
  - Tela de administração de fontes (lista + formulários).  
  - Deve permitir executar CRUD básico de fontes.

- `inspectah/ui/templates/model_fields.html`  
  - Tela de visualização de campos e preview canônico.  
  - Mostra mapa de campos e amostras de registros.

- `inspectah/ui/templates/query.html`  
  - Tela de consulta: formulário + tabela de resultados por fonte + valor consolidado + explicação.  
  - Deve exibir links/ações para "ver evidência" por registro.

- `inspectah/ui/templates/evidence_detail.html`  
  - Tela de detalhe da evidência, com metadados e informações suficientes para que o usuário confie na origem do dado.

- `inspectah/ui/static/css/main.css`  
  - Estilos básicos (layout, tipografia, espaçamento).  
  - Não precisa de refinamento visual avançado; foco em clareza.

- `inspectah/ui/static/js/main.js`  
  - Comportos mínimos de interação (ex.: realce de linhas, navegação suave, exibição/ocultação de detalhes).

---

## 5. Configuração da UI (`config/ui_sprint_7.yaml`)

**Objetivo**: concentrar parâmetros de configuração específicos da UI da S7.

Arquivo:

- `config/ui_sprint_7.yaml`  
  - Parâmetros típicos:
    - `host`, `port` da UI;  
    - `debug` (true/false);  
    - caminhos básicos (caso necessário) para templates/static;  
    - flags de features da S7 (ex.: habilitar/desabilitar fluxos experimentais).

Regras:

- O arquivo é lido exclusivamente por `inspectah/ui/config.py`.  
- Não armazena segredos; apenas parâmetros não sensíveis.

---

## 6. Scripts e gates (`bin/`)

Os scripts em `bin/` são os pontos de entrada operacionais da S7.

### 6.1. Scripts de UI

- `bin/s7_ui_start.sh`  
  - Sobe a aplicação web lendo `config/ui_sprint_7.yaml` e usando `inspectah/ui/app.py` como entrypoint.

- `bin/s7_ui_stop.sh`  
  - Opcionalmente para a aplicação (se for necessário um wrapper para gerenciar processos em modo dev).

- `bin/s7_ui_open_browser.sh`  
  - Abre o navegador apontando para a URL local da UI (ex.: `http://localhost:8000`).  
  - Auxilia nos fluxos UI-only da S7.

### 6.2. Gates S7-G0…S7-G8

Todos definidos no Capítulo 2; aqui apenas reforçamos o mapeamento físico.

- `bin/s7_g0_baseline.sh`  
  - Gate S7-G0 — Baseline S6 + Wiring S7.  
  - Produz `out/scorecards/S7_G0_baseline.json` e evidências em `out/evidence/S7_G0_baseline/`.

- `bin/s7_g1_ui_boot_health.sh`  
  - Gate S7-G1 — UI Boot & Health.  
  - Sobe a UI, consulta o endpoint de health e gera scorecard `S7_G1`.

- `bin/s7_g2_ui_sources_admin.sh`  
  - Gate S7-G2 — Fontes gerenciáveis via UI.  
  - Roda fluxos automatizados (via HTTP) sobre views de `admin_sources` e valida efeitos em `config/sources/*.yaml`.

- `bin/s7_g3_ui_fields_preview.sh`  
  - Gate S7-G3 — Modelo canônico & preview via UI.  
  - Compara representação de campos e preview UI com a CLI/bridge da S6.

- `bin/s7_g4_ui_query_consolidation.sh`  
  - Gate S7-G4 — Consulta & decisão consolidada.  
  - Roda consultas de teste via UI, compara com runtime S6 e valida explicação.

- `bin/s7_g5_ui_evidence_trace.sh`  
  - Gate S7-G5 — Evidência & rastreabilidade.  
  - Exercita links de evidência na UI e verifica que apontam para `out/evidence/dominio_piloto/...` em até 2 cliques.

- `bin/s7_g6_ui_only_flows.sh`  
  - Gate S7-G6 — Fluxos UI-only (admin e usuário).  
  - Instrumenta e mede as histórias S7-A1 e S7-B1, garantindo M1 e M2.

- `bin/s7_g7_metrics_and_demo.sh`  
  - Gate S7-G7 — Métricas M1–M6 & demo cronometrada.  
  - Consolida evidência dos gates anteriores e avalia M1–M6.

- `bin/s7_g8_sprint_go_no_go.sh`  
  - Gate S7-G8 — Sprint 7 GO/NO-GO.  
  - Lê todos os scorecards S7-G0…S7-G7 e emite a decisão final `GO` ou `NO_GO`.

Todos esses nomes precisam aparecer exatamente assim nos scripts, nos scorecards e nos paths de evidência.

---

## 7. Testes automatizados (`tests/sprint_7/`)

A pasta `tests/sprint_7/` abriga testes específicos da S7, principalmente da camada de UI + bridge.

Arquivos:

- `tests/sprint_7/test_ui_health.py`  
  - Verifica criação da app (`create_app` ou equivalente) e resposta do endpoint de health.  
  - Complementa o gate S7-G1.

- `tests/sprint_7/test_ui_sources_admin.py`  
  - Exercita rotas da view `admin_sources`.  
  - Garante que operações básicas de CRUD refletem corretamente em `config/sources/*.yaml`.  
  - Complementa o gate S7-G2.

- `tests/sprint_7/test_ui_fields_preview.py`  
  - Exercita view `model_fields` e valida que schema e preview batem com `runtime_bridge`/S6.  
  - Complementa o gate S7-G3.

- `tests/sprint_7/test_ui_query_consolidation.py`  
  - Exercita view `query` e valida consulta por fonte + cálculo de valor consolidado.  
  - Complementa o gate S7-G4.

- `tests/sprint_7/test_ui_evidence_trace.py`  
  - Exercita view `evidence`, garantindo que IDs mostrados pela UI existem em `out/evidence/dominio_piloto/...`.  
  - Complementa o gate S7-G5.

Regras:

- Os testes da S7 devem ser executáveis tanto isoladamente quanto dentro de uma suite maior (ex.: `bin/ci_local.sh`, se houver integração futura).  
- Não substituem os gates, mas reduzem o risco de regressão entre execuções de gates.

---

## 8. Saída operacional: scorecards, evidências e logs (`out/`)

A S7 reutiliza a estrutura de `out/` consolidada nas sprints anteriores e adiciona novos artefatos.

### 8.1. Scorecards

Todos os scorecards seguem o padrão `out/scorecards/S7_GX_*.json`:

- `out/scorecards/S7_G0_baseline.json`
- `out/scorecards/S7_G1_ui_boot_health.json`
- `out/scorecards/S7_G2_ui_sources_admin.json`
- `out/scorecards/S7_G3_ui_fields_preview.json`
- `out/scorecards/S7_G4_ui_query_consolidation.json`
- `out/scorecards/S7_G5_ui_evidence_trace.json`
- `out/scorecards/S7_G6_ui_only_flows.json`
- `out/scorecards/S7_G7_metrics_and_demo.json`
- `out/scorecards/S7_G8_sprint_go_no_go.json`

Esses arquivos são lidos diretamente pelo gate S7-G8.

### 8.2. Evidências por gate

Cada gate possui sua pasta em `out/evidence/`:

- `out/evidence/S7_G0_baseline/`
- `out/evidence/S7_G1_ui_boot_health/`
- `out/evidence/S7_G2_ui_sources_admin/`
- `out/evidence/S7_G3_ui_fields_preview/`
- `out/evidence/S7_G4_ui_query_consolidation/`
- `out/evidence/S7_G5_ui_evidence_trace/`
- `out/evidence/S7_G6_ui_only_flows/`
- `out/evidence/S7_G7_metrics_and_demo/`
- `out/evidence/S7_G8_sprint_go_no_go/`

Cada pasta deve conter, no mínimo, os arquivos descritos no Capítulo 2 (summary, amostras, logs, observações).

### 8.3. Logs da UI

- `out/logs/s7_ui.log`  
  - Log consolidado da aplicação da S7.  
  - Importante para debug de falhas em gates e fluxos UI-only.

---

## 9. Relação Gates ↔ Arquivos ↔ Métricas (M1–M6)

Tabela de vínculo direto entre os gates, os principais arquivos da S7 e as métricas do Capítulo 1.

| Gate  | Principais arquivos S7                                           | Métricas diretamente afetadas |
|-------|-------------------------------------------------------------------|-------------------------------|
| S7-G0 | `bin/s7_g0_baseline.sh`, `docs/sprint_7/sprint_7_capitulo_1.md`   | — (pré-condição estrutural)   |
| S7-G1 | `bin/s7_g1_ui_boot_health.sh`, `inspectah/ui/app.py`, `inspectah/ui/config.py`, `config/ui_sprint_7.yaml` | M1 (tempo de boot na demo)    |
| S7-G2 | `bin/s7_g2_ui_sources_admin.sh`, `inspectah/ui/views/admin_sources.py`, `inspectah/ui/runtime_bridge.py`, `config/sources/*.yaml` | M3 (admin consegue gerenciar fontes via UI) |
| S7-G3 | `bin/s7_g3_ui_fields_preview.sh`, `inspectah/ui/views/model_fields.py`, `inspectah/ui/runtime_bridge.py`, `config/fields/dominio_piloto.yaml` | M3/M4 (modelo claro e preview confiável) |
| S7-G4 | `bin/s7_g4_ui_query_consolidation.sh`, `inspectah/ui/views/query.py`, `inspectah/ui/runtime_bridge.py`, `inspectah/ui/schemas.py` | M4, M5 (consulta e valor consolidado explicável) |
| S7-G5 | `bin/s7_g5_ui_evidence_trace.sh`, `inspectah/ui/views/evidence.py`, `inspectah/ui/templates/evidence_detail.html`, `inspectah/ui/runtime_bridge.py` | M6 (rastreabilidade até evidência em ≤ 2 cliques) |
| S7-G6 | `bin/s7_g6_ui_only_flows.sh`, `bin/s7_ui_open_browser.sh`, todo `inspectah/ui/*` | M1, M2 (fluxos UI-only admin/usuário) |
| S7-G7 | `bin/s7_g7_metrics_and_demo.sh`, todos os scorecards S7-G1…S7-G6, `docs/sprint_7/sprint_7_capitulo_1.md` | M1–M6 (checagem final) |
| S7-G8 | `bin/s7_g8_sprint_go_no_go.sh`, todos `out/scorecards/S7_G*.json` | — (decisão GO/NO-GO)         |

Essa tabela complementa o Capítulo 2 e garante que qualquer pessoa consiga:

- saber exatamente **onde mexer** para impactar uma métrica ou gate específico;  
- rastrear do sintoma (gate falhou ou métrica não bateu) até o arquivo ou módulo relevante.

---

## 10. Checklist operacional de estrutura (S7)

Este checklist serve como mini-plano para estruturar o repositório antes da execução detalhada do Capítulo 4.

1. **Criar estrutura de documentação da S7**  
   - Criar pasta `docs/sprint_7/`.  
   - Garantir presença dos arquivos: `sprint_7_capitulo_1.md`, `sprint_7_capitulo_2.md`, `sprint_7_capitulo_3.md`, `sprint_7_capitulo_4.md`, `sprint_7_resultados.md`.

2. **Criar esqueleto da UI**  
   - Criar pasta `inspectah/ui/` com subpastas `views/`, `templates/`, `static/css/`, `static/js/`.  
   - Adicionar stubs para: `__init__.py`, `app.py`, `config.py`, `runtime_bridge.py`, `schemas.py`, `view_models.py`.

3. **Configurar a UI**  
   - Criar `config/ui_sprint_7.yaml` com parâmetros mínimos (host, port, debug).  
   - Ajustar `inspectah/ui/config.py` para ler esse arquivo.

4. **Criar scripts da S7 em `bin/`**  
   - Adicionar stubs para `s7_ui_start.sh`, `s7_ui_stop.sh`, `s7_ui_open_browser.sh`.  
   - Adicionar scripts de gates `s7_g0_baseline.sh`…`s7_g8_sprint_go_no_go.sh` com interface alinhada ao Capítulo 2.

5. **Criar pasta de testes da S7**  
   - Criar `tests/sprint_7/` e adicionar testes básicos para health, fontes, preview, consulta e evidência.  
   - Garantir que `pytest` (ou equivalente) consegue descobri-los.

6. **Preparar estrutura de saída**  
   - Garantir existência de `out/scorecards/`, `out/evidence/` e `out/logs/`.  
   - Scripts de gates devem criar automaticamente subpastas `S7_G*/` e arquivos `.json` quando executados.

Com este filemap e checklist, a Sprint 7 tem um blueprint de estrutura **completo, explícito e compatível** com o que já foi entregue na Sprint 6. O Capítulo 4 deverá apenas dizer **como** preencher essa estrutura em termos de implementação e comandos, mantendo este capítulo como referência estrutural única.


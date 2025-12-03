# Inspectah — Sprint 27 (S27)
## Capítulo 2 — Bloco 2
### Gate G0, Gate G1 e Gate G2 — Especificação detalhada

> Arquivo-alvo no repo: `docs/s27_cap_2_2_g0_g1_g2_detalhado.md`
>
> Função: detalhar, em nível de script e scorecard, os três primeiros gates da S27: **G0 (escopo & ambiente)**, **G1 (design system Admin v1)** e **G2 (fluxos de consoles admin)**. Este bloco é o contrato que o Codex e os scripts em `bin/` devem seguir.

---

## 1. Gate G0 — Escopo, Grounding & Sanidade de Ambiente

### 1.1 Objetivo refinado

G0 garante que a S27 não começa sobre terreno podre. Ele responde, com dados, a três perguntas:

1) O repositório e o ambiente local estão minimamente saudáveis para trabalhar na S27?  
2) Os documentos de contexto da S27 (Cap.1 e Cap.2) existem e estão nos caminhos corretos?  
3) Não há divergências graves entre o que o código diz e o que o Cap.1 define como escopo/estado-alvo?

### 1.2 Escopo exato

G0 cobre:

- integridade básica do repo (sem erros óbvios de venv, dependências, estrutura);  
- presença de docs:  
  - `docs/s27_cap_1_contexto_e_objetivos.md`,  
  - `docs/s27_cap_1_1_contexto_e_papel_no_epico.md`,  
  - `docs/s27_cap_1_2_problema_e_riscos.md`,  
  - `docs/s27_cap_1_3_estados_alvo_e_sucesso.md`,  
  - `docs/s27_cap_1_4_escopo_e_premissas.md`,  
  - `docs/s27_cap_2_gates_metricas_orr.md`,  
  - `docs/s27_cap_2_1_visao_geral_gates_e_scorecards.md`;  
- sanity mínima de testes globais rápidos (ex.: um `pytest -q` superficial, se aplicável, e um comando mínimo de front).

### 1.3 Script de gate sugerido

- Script: `bin/s27_g0_env_repo.sh`

Responsabilidades do script, em ordem:

1. Ativar o virtualenv, se existir:  
   `source .venv/bin/activate` (com fallback amigável se não existir).

2. Rodar checagens de repositório:
   - `git rev-parse --show-toplevel` para garantir que estamos na raiz esperada;  
   - `git status -sb` para registrar estado (sem exigir limpeza total, mas logando).

3. Checar dependências mínimas:
   - backend: comando leve (ex.: `python -m py_compile app/main.py` ou arquivo central);  
   - frontend (se aplicável): comando leve (ex.: `npm run lint -- --help` ou similar) apenas para garantir que o ambiente está minimamente configurado.

4. Verificar presença de docs-chave:
   - usar `test -f` ou equivalente para cada arquivo listado na seção 1.2;  
   - registrar resultado por arquivo.

5. Gerar scorecard JSON e logs:
   - salvar JSON em `out/scorecards/S27_G0_scope_and_env.json`;  
   - salvar stdout/stderr em `out/evidence/S27_G0_env_repo/`.

### 1.4 Modelo de scorecard G0

Arquivo: `out/scorecards/S27_G0_scope_and_env.json`

Campos sugeridos:

```json
{
  "env_ok": true,
  "repo_root_detected": true,
  "venv_present": true,
  "backend_sanity_passed": true,
  "frontend_sanity_passed": true,
  "docs_cap_1_present": true,
  "docs_cap_2_present": true,
  "missing_docs": [],
  "notes": "string com observações relevantes"
}
```

### 1.5 Critérios de GO/NO-GO para G0

- GO:  
  - `env_ok == true`,  
  - `repo_root_detected == true`,  
  - `backend_sanity_passed == true`,  
  - `docs_cap_1_present == true`,  
  - `docs_cap_2_present == true`,  
  - `missing_docs` vazio.

- NO-GO: qualquer falha em integridade básica ou ausência de docs de Cap.1/Cap.2. Nesses casos, a sprint não deve avançar para execução de G1–G2 antes de corrigir.

---

## 2. Gate G1 — Design System Admin v1 (Tokens & Componentes)

### 2.1 Objetivo refinado

G1 garante que:

1) `ui/admin` está íntegro (compila, exports consistentes, sem quebrar o front);  
2) os consoles de Fontes, Ingestão e Debunker **de fato utilizam** os componentes e o layout de Admin v1;  
3) a presença de qualquer layout/estilo "paralelo" é conhecida, pequena e registrada como dívida técnica.

### 2.2 Escopo exato

G1 cobre os seguintes diretórios e arquivos:

- `frontend/inspectah-ui/ui/admin/*` (tokens, layouts, componentes base),  
- `frontend/inspectah-ui/features/sources/*`,  
- `frontend/inspectah-ui/features/ingestion/*`,  
- `frontend/inspectah-ui/features/debunker/*`.

Ele não tenta validar toda a UI do projeto, apenas a parte que participa de Admin v1 e consoles alvo.

### 2.3 Script de gate sugerido

- Script: `bin/s27_g1_admin_design_system.sh`

Responsabilidades sugeridas:

1) Verificar build básico de componentes admin:  
   - opcionalmente rodar testes específicos de `ui/admin` (ex.: `npm test -- admin` ou equivalente).

2) Rodar um compilador/bundler em modo rápido para garantir que alterações em Admin v1 não quebraram o projeto.

3) Rodar uma checagem de imports:
   - buscar, nos diretórios de features alvo, o uso de componentes de layout diretamente de libs externas ou de implementações antigas;  
   - contabilizar importações que fogem de `ui/admin` quando o esperado seriam componentes do design system.

4) (Opcional) Rodar uma checagem de CSS de layout "cru":
   - localizar regras de estilo definindo grids/containers básicos dentro de features, sinalizando candidatos a migração para Admin v1.

5) Gerar scorecard e evidências.

### 2.4 Modelo de scorecard G1

Arquivo: `out/scorecards/S27_G1_admin_design_system.json`

Exemplo de estrutura:

```json
{
  "design_system_build_ok": true,
  "admin_components_tests_ok": true,
  "consoles_using_admin_components": "full",
  "legacy_layout_usages": 0,
  "legacy_imports_examples": [],
  "notes": "observações, exceções e planos para S27-DT-XXX"
}
```

Onde:

- `consoles_using_admin_components` ∈ {"full", "partial", "broken"}.  
- `legacy_layout_usages` indica o número de ocorrências encontradas de layouts paralelos.  
- `legacy_imports_examples` pode listar alguns caminhos de arquivo para inspeção manual.

### 2.5 Critérios de GO/NO-GO para G1

- GO forte (ideal):  
  - `design_system_build_ok == true`,  
  - `admin_components_tests_ok == true`,  
  - `consoles_using_admin_components == "full"`,  
  - `legacy_layout_usages == 0`.

- GO com ressalva (aceitável somente se bem documentado em Cap.6):  
  - `consoles_using_admin_components == "partial"`,  
  - `legacy_layout_usages > 0`,  
  - mas todos os casos mapeados como `S27-DT-XXX` com justificativa e janela sugerida.

- NO-GO:  
  - `design_system_build_ok == false`, ou  
  - `admin_components_tests_ok == false`, ou  
  - `consoles_using_admin_components == "broken"`.

Qualquer NO-GO em G1 invalida a ideia de que Admin v1 é padrão para consoles da S27.

---

## 3. Gate G2 — Fluxos de Consoles Admin (Fontes / Ingestão / Debunker)

### 3.1 Objetivo refinado

G2 garante que os **fluxos principais de operação** em Fontes, Ingestão e Debunker funcionam de ponta a ponta, sob o novo padrão Admin v1.

A pergunta que G2 responde é:  
> "Um operador, usando as telas pós-S27, consegue executar suas tarefas-chave sem ficar preso em erros óbvios ou dead-ends?"

### 3.2 Escopo exato

G2 foca em cenários E2E selecionados como representativos. Exemplos:

1) **Fluxo Fontes — ciclo de vida básico**  
   - cadastrar uma nova fonte com config mínima válida;  
   - salvar, ativar, visualizar estado;  
   - desativar/arquivar.

2) **Fluxo Ingestão — acompanhar problema de ingestão**  
   - identificar, a partir de uma visão geral, que uma fonte específica está com ingestão atrasada/falhando;  
   - acessar detalhes, inspecionar erros mais recentes;  
   - acionar ação de mitigação (ex.: reprocessar, marcar como reconhecido).

3) **Fluxo Debunker — tratar disputa ligada a uma fonte**  
   - localizar uma disputa originada em dados de determinada fonte;  
   - analisar evidências;  
   - tomar decisão (aprovar/rejeitar/escalação) e registrar.

4) **Fluxo combinado — Fontes → Ingestão → Debunker**  
   - partir de um problema de ingestão associado a uma fonte;  
   - verificar contexto da fonte (config, histórico);  
   - seguir até a disputa em Debunker, se existir, e tomar ação.

### 3.3 Implementação típica de G2

- Script: `bin/s27_g2_admin_flows.sh`

Responsabilidades sugeridas:

1) Inicializar ambiente de testes (ex.: seed de dados, fixtures de fontes/fact patterns).
2) Acionar suíte de testes E2E (Playwright/Cypress ou outro framework), apontando para ambiente local/staging.  
3) Garantir que os testes rodem com o layout Admin v1 ativo (sem feature flags em estado antigo).  
4) Coletar resultados e gerar:
   - relatório de testes (HTML/JSON do framework) em `out/evidence/S27_G2_admin_flows/`;  
   - scorecard agregado em `out/scorecards/S27_G2_admin_flows.json`.

### 3.4 Modelo de scorecard G2

Arquivo: `out/scorecards/S27_G2_admin_flows.json`

Estrutura sugerida:

```json
{
  "sources_flows_ok": true,
  "ingestion_flows_ok": true,
  "debunker_flows_ok": true,
  "combined_flows_ok": true,
  "total_scenarios": 4,
  "failed_scenarios": [],
  "notes": "comentários sobre instabilidades, flakiness, etc."
}
```

`failed_scenarios` deve listar ids ou nomes dos cenários que falharam, se houver.

### 3.5 Critérios de GO/NO-GO para G2

- GO:  
  - `sources_flows_ok == true`,  
  - `ingestion_flows_ok == true`,  
  - `debunker_flows_ok == true`,  
  - `combined_flows_ok == true`,  
  - `failed_scenarios` vazio ou contendo apenas cenários explicitamente out-of-scope.

- NO-GO:  
  - qualquer `*_flows_ok == false` em cenário in-scope da S27;  
  - ou falhas recorrentes que impeçam uso confiável dos consoles.

Em caso de NO-GO, as falhas de G2 devem aparecer como riscos/itens centrais no ORR (Cap.5) e como dívidas técnicas ou recortes de escopo em Cap.6.

---

## 4. Conexão de G0–G2 com os próximos blocos

- Este Bloco 2 especifica G0, G1 e G2 em nível operacional, para guiar implementação de scripts e scorecards.  
- O **Bloco 3** fará o mesmo para **G3 (frontend quality)** e **G4 (contratos & APIs)**.  
- O **Bloco 4** detalhará **G5 (docs/runbooks)** e **G6 (ORR & bundle)**, fechando o sistema de verificação da S27.

Com G0–G2 bem definidos, a S27 passa a ter uma linha de defesa clara: ambiente alinhado, design system real em uso e fluxos admin críticos comprovadamente funcionando.


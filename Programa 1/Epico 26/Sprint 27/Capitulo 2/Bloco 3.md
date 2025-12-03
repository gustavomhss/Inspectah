# Inspectah — Sprint 27 (S27)
## Capítulo 2 — Bloco 3
### Gate G3 e Gate G4 — Qualidade de Frontend Admin & Contratos/APIs

> Arquivo-alvo no repo: `docs/s27_cap_2_3_g3_g4_detalhado.md`
>
> Função: especificar em nível operacional os gates **G3 (qualidade global de frontend admin)** e **G4 (contratos & APIs relevantes)** da S27. Este bloco orienta diretamente a implementação dos scripts em `bin/` e os scorecards em `out/scorecards/`.

---

## 1. Gate G3 — Qualidade Global de Frontend Admin

### 1.1 Objetivo refinado

G3 garante que a base de frontend está saudável o suficiente para que as mudanças de Admin v1 em Fontes, Ingestão e Debunker não estejam sendo construídas em cima de um front quebrado.

Ele responde:

1) O frontend (com ênfase em Admin) **compila**?  
2) Lint e testes básicos de componentes estão **passando**?  
3) Existem falhas grosseiras de navegação/admin detectáveis via smoke tests simples?

### 1.2 Escopo exato

G3 não tenta testar toda a UX da S27 em profundidade (isso é papel de G2), mas cobre a sanidade estrutural do frontend:

- projeto `frontend/inspectah-ui/` como um todo, com foco especial em:
  - `ui/admin/*`,  
  - `features/sources/*`,  
  - `features/ingestion/*`,  
  - `features/debunker/*`.

- comandos padrão de qualidade do front, por exemplo (ajustar ao projeto real):
  - `npm run lint`  
  - `npm test` (ou suíte de testes unitários equivalente)  
  - `npm run build` (build de produção ou equivalente).

### 1.3 Script de gate sugerido

- Script: `bin/s27_g3_front_quality_admin.sh`

Responsabilidades sugeridas:

1) Entrar no diretório do frontend (ex.: `cd frontend/inspectah-ui`).
2) Rodar lint:  
   - `npm run lint`  
   - capturar retorno e logs.
3) Rodar testes unitários:  
   - `npm test` ou suíte equivalente em modo não interativo (ex.: `npm test -- --watch=false`).
4) Rodar build:  
   - `npm run build`.  
   - Importante: falhas aqui indicam problemas sérios (imports quebrados, tipos inconsistentes, etc.).
5) Gerar scorecard JSON com o resultado de cada etapa e salvar logs.

### 1.4 Modelo de scorecard G3

Arquivo: `out/scorecards/S27_G3_front_quality_admin.json`

Estrutura sugerida:

```json
{
  "lint_ok": true,
  "tests_ok": true,
  "build_ok": true,
  "lint_command": "npm run lint",
  "tests_command": "npm test -- --watch=false",
  "build_command": "npm run build",
  "notes": "observações sobre warnings relevantes, flakiness, etc."
}
```

### 1.5 Evidências de G3

- Diretório: `out/evidence/S27_G3_front_quality_admin/`
  - `lint.log` — saída completa do lint;  
  - `tests.log` — saída dos testes;  
  - `build.log` — saída do build.

Esses arquivos permitem auditar regressões futuras.

### 1.6 Critérios de GO/NO-GO para G3

- **GO**:  
  - `lint_ok == true`,  
  - `tests_ok == true`,  
  - `build_ok == true`.

- **GO com ressalvas** (apenas se bem documentado em Cap.6):  
  - `lint_ok == true` com apenas warnings não-críticos;  
  - `tests_ok == true` com alguns testes marcados como `@xfail` ou `skip` documentados;  
  - `build_ok == true`.

- **NO-GO**:  
  - qualquer `*_ok == false`;  
  - warnings ou falhas ignoradas sem documentação e plano.

G3 é gate de higiene: se ele falha, todo o resto da verificação da S27 fica com base instável.

---

## 2. Gate G4 — Contratos & APIs relevantes para consoles admin

### 2.1 Objetivo refinado

G4 garante que o frontend admin (sob Admin v1) não está "mentindo" sobre o estado dos dados.

Ele responde:

1) Os consoles de Fontes, Ingestão e Debunker estão consumindo APIs coerentes com o que o backend expõe?  
2) Existe algum descompasso grave entre o contrato esperado no front e o contrato real do back (campos ausentes, tipos errados, endpoints quebrados)?  
3) Quaisquer mismatches identificados estão mapeados, documentados e tratados como dívida ou correção imediata?

### 2.2 Escopo exato

G4 foca em:

- Endpoints principais usados por consoles admin alvo, por exemplo:
  - Fontes: `/api/sources/*` (listar, criar, atualizar, ativar/desativar),  
  - Ingestão: `/api/ingestion/*` (status por fonte, runs recentes, detalhes de erro),  
  - Debunker: `/api/debunker/*` (listar disputas, detalhes, ações de decisão).

- Schemas associados: OpenAPI/JSON Schema ou modelos internos que descrevem payloads de request/response.

### 2.3 Abordagens possíveis para G4

Dependendo da maturidade do projeto, G4 pode usar uma ou mais das abordagens abaixo:

1) **Validação de OpenAPI/Schema**  
   - Garantir que o arquivo de OpenAPI (se existir) está coerente (sem refs quebradas).  
   - Validar respostas reais do backend contra schemas declarados.

2) **Testes automatizados de contrato**  
   - Usar ferramentas como `schemathesis` ou suíte customizada de testes de API para bater endpoints com payloads esperados e garantir respostas na forma correta.

3) **Smoke tests de contrato**  
   - Em ambientes menos estruturados, pelo menos checar que endpoints básicos respondem com status HTTP esperado (200/4xx controlado) e retornam campos essenciais.

### 2.4 Script de gate sugerido

- Script: `bin/s27_g4_admin_contracts.sh`

Responsabilidades sugeridas:

1) Rodar validadores de schema (se existirem) em arquivos OpenAPI/JSON Schema.
2) Executar testes automatizados básicos para os endpoints listados na seção 2.2:  
   - por exemplo, `pytest tests/api/test_admin_contracts.py` ou semelhante.
3) Opcionalmente, rodar uma rotina de health-check das APIs admin (curl ou requests simples) registrando status e formato básico da resposta.
4) Gerar scorecard e evidências.

### 2.5 Modelo de scorecard G4

Arquivo: `out/scorecards/S27_G4_admin_contracts.json`

Estrutura sugerida:

```json
{
  "sources_api_ok": true,
  "ingestion_api_ok": true,
  "debunker_api_ok": true,
  "schema_validation_ok": true,
  "schema_mismatches": [],
  "endpoints_checked": [
    "/api/sources/list",
    "/api/ingestion/status",
    "/api/debunker/cases"
  ],
  "notes": "detalhes de eventuais mismatches ou limitações conhecidas"
}
```

- `schema_mismatches` deve listar casos em que o contrato esperado e o real divergem (campo faltando, tipo diferente, etc.).

### 2.6 Evidências de G4

- Diretório: `out/evidence/S27_G4_admin_contracts/`  
  - logs de validação de schema;  
  - logs de testes de API;  
  - outputs de health-checks (por exemplo, arquivos `.json` com respostas de amostra).

### 2.7 Critérios de GO/NO-GO para G4

- **GO**:  
  - `sources_api_ok == true`,  
  - `ingestion_api_ok == true`,  
  - `debunker_api_ok == true`,  
  - `schema_validation_ok == true`,  
  - `schema_mismatches` vazio ou contendo apenas itens classificados como risco baixo com plano claro.

- **GO com ressalvas**:  
  - mismatchs menores (ex.: campo opcional ausente) documentados como `S27-DT-XXX` e/ou tasks em backlog imediato.

- **NO-GO**:  
  - qualquer API crítica marcada como `*_api_ok == false`;  
  - `schema_validation_ok == false` por problemas que afetam os consoles admin;  
  - mismatches que comprometem a operação segura de Fontes, Ingestão ou Debunker.

G4 é gate de realidade: impede que o frontend admin pareça bonito, mas empurre dados inconsistentes ou quebrados.

---

## 3. Costura de G3 e G4 com o resto da S27

- G3 garante que o **chão do frontend** está firme: o projeto compila, lint e testes básicos passam.  
- G4 garante que o **ar que o frontend respira** (APIs e contratos) não está contaminado.  
- Juntos, eles criam a base para que G1 (design system) e G2 (fluxos admin) tenham significado real, e não sejam só demos rodando em mock.

Do ponto de vista de Cap.5 (ORR):
- qualquer falha grave em G3 ou G4 precisa aparecer como item central de risco;  
- uma decisão de GO da S27 com G3/G4 falhando deveria ser, na prática, extremamente rara e sempre muito bem documentada.

---

## 4. Próximos passos dentro do Capítulo 2

- O **Bloco 4** completará o Cap.2 detalhando **G5 (documentação & runbooks)** e **G6 (ORR & bundle de evidências)**, incluindo a forma exata do scorecard de ORR e as regras para declarar o Épico E26 encerrado do ponto de vista de UI/Admin.
# Inspectah — Sprint 26 (S26)
## Capítulo 3 — Bloco 3.4
### Mapa de Dependências, Invariantes Estruturais & Pontos de Extensão

Este bloco consolida a visão de **como as peças da S26 se dependem**, **quais invariantes estruturais não podem ser violados** e **onde estão os pontos de extensão naturais** para as próximas sprints do Programa 1.

Ele responde a três perguntas:

1. Quem depende de quem?  
2. O que **não pode** acontecer sem quebrar a arquitetura?  
3. Como a S26 prepara terreno para S27–S32?

---

## 1. Mapa de Dependências Principais

A S26 introduz (ou consolida) três blocos lógicos principais:

1. **Design System Inspectah Admin v1**  
2. **Console de Fontes v2 (feature `sources`)**  
3. **APIs & Modelo de Dados de Fontes (backend `app/sources`)**

E os conecta com os **gates G0–G6**.

### 1.1. Dependências do Design System Admin v1

**Local base:**

```text
frontend/inspectah-ui/src/ui/admin/
```

Depende de:

- Infra de frontend (React, TypeScript, tooling padrão do projeto).  
- Eventuais bibliotecas de UI de baixo nível (se houver), configuradas via tokens.

Não depende de:

- Features específicas (`features/sources`, `features/ingestion`, etc.).  
- Módulos de backend (`app/sources`, etc.).

É dependido por:

- Console de Fontes v2 (em `features/sources`).  
- Futuros consoles admin (Ingestão, Debunker, Truth, Evidence Vault, Case Cockpit).

### 1.2. Dependências do Console de Fontes v2

**Local base:**

```text
frontend/inspectah-ui/src/features/sources/
```

Depende de:

- Design System Admin v1 (`@/ui/admin`).  
- Tipos locais (`types/Source.ts`).  
- Cliente de API (`api/sourcesApi.ts`).

Não deve depender de:

- Componentes internos de outros consoles (ex.: ingestão, debunker).  
- Acesso direto a libs HTTP sem passar por `sourcesApi.ts`.

É dependido por:

- Rotas de frontend que expõem o Console de Fontes na UI admin.  
- Testes de fluxo de G2.

### 1.3. Dependências das APIs & Modelo de Fontes

**Locais base sugeridos:**

```text
app/sources/
  models.py
  schemas.py
  routes.py

tests/api/
  test_sources_console.py
```

Depende de:

- Infra de backend (framework web, ORM, etc.).  
- Modelo de dados persistente (banco, migrations).

Não depende de:

- Componentes de UI (não importa se o front usa React, outro framework ou CLI).  
- Design System Admin v1.

É dependido por:

- `sourcesApi.ts` no frontend.  
- Testes de API de G4.  
- Futuras features que precisem consultar ou configurar fontes.

### 1.4. Dependências dos Gates G0–G6

- **G0**
  - Depende da existência de docs de S26 (Cap.1–4) e da estrutura base de `ui/admin` e `features/sources`.  
- **G1**
  - Depende de `ui/admin` (tokens, layout, components, hooks) estar compilável, lintado e testado.  
- **G2**
  - Depende de `features/sources` (pages, components, api, types) estar funcional, com fluxos automatizados.  
- **G3**
  - Depende do frontend como um todo (incluindo design system e consoles) passar por lint/testes/build.  
- **G4**
  - Depende de `app/sources` + `tests/api/test_sources_console.py` validarem as rotas consumidas pelo console.  
- **G5**
  - Depende de docs (guia do design system, runbook de fontes) e suas evidências.  
- **G6**
  - Depende da existência e organização de todas as pastas de evidência G0–G5.

---

## 2. Invariantes Estruturais da S26

Invariantes são regras que **não podem ser violadas** sem descaracterizar o objetivo arquitetural da S26. Eles complementam os gates com restrições de forma.

### 2.1. Invariantes de Camadas (Frontend)

1. **Design System Admin v1 é agnóstico de domínio**
   - `ui/admin` não pode conhecer `Source`, `Case`, `Debunker`, `Truth` etc.  
   - Qualquer referência a tipos de domínio deve estar em features como `features/sources`.

2. **Consoles admin só usam componentes de UI admin via `@/ui/admin`**
   - `features/sources` (Console de Fontes v2) não deve importar diretamente componentes internos de `ui/admin/*`; deve usar a API pública exportada em `ui/admin/index.ts`.

3. **Layouts admin não são reinventados em features**
   - Páginas de `features/sources/pages` não implementam sua própria sidebar ou header; sempre compõem `AdminShell`/`AdminHeader`/`AdminContent`.

4. **Nada de CSS "mágico" fora de tokens**
   - Componentes em `ui/admin/components` e `ui/admin/layout` usam tokens para cores, tipografia e espaçamento.  
   - Exceções, se existirem, devem ser mínimas e explícitas, para não anularem G1/G3.

### 2.2. Invariantes de Domínio & Contratos

1. **Fonte tem estados e campos bem definidos**
   - O tipo `Source` (frontend) e os schemas de `Source` (backend) devem estar alinhados em campos e possíveis estados de `status`.  
   - Não pode haver campo exposto na UI que não exista no backend (ou vice-versa) sem motivo fortemente documentado.

2. **Operações de status são explícitas**
   - Ativar, desativar e arquivar fontes devem estar representados em rotas claras (endpoints separados ou um campo de status com regras de transição explícitas).  
   - O Console de Fontes v2 consome essas rotas; não faz "jeitinho" (ex.: atualizar status via campos genéricos).

3. **Testes de API seguem os fluxos do console**
   - `tests/api/test_sources_console.py` precisa refletir os mesmos fluxos que G2 testa na UI (lista, criação, edição, ativar/desativar/arquivar).  
   - Se o console mudar, os testes de API devem acompanhar.

### 2.3. Invariantes de Evidência & Auditabilidade

1. **Cada gate deixa artefatos em sua pasta dedicada**
   - `out/evidence/S26_G*/` deve existir e conter logs/artefatos conforme definido no Bloco 3.3 e no Cap.2.

2. **Bundle de evidências é reprodutível**
   - Executar `bin/s26_g6_orr_bundle.sh` duas vezes em estado estável deve produzir o mesmo conjunto de arquivos (ignorando metadados como timestamps de ZIP).

3. **Scorecards refletem métricas reais**
   - Scorecards `S26_G*.json` não são editados manualmente: são resultados de scripts.  
   - Qualquer divergência entre scorecards e logs de evidência é considerada bug.

---

## 3. Pontos de Extensão para Sprints Futuras (S27–S32)

A S26 não é um fim em si mesma; ela é a base "Admin v1" do Programa 1. Este bloco identifica explicitamente pontos que as próximas sprints podem aproveitar.

### 3.1. Extensões do Design System Admin v1

Futuras sprints podem:

- adicionar novos componentes genéricos (cards, tabs, accordions, gráficos simples);
- enriquecer componentes existentes com variantes e estados adicionais (por exemplo, botões com ícone, tabelas com colunas configuráveis);
- introduzir temas/skins adicionais para seções específicas, mantendo compatibilidade com tokens atuais.

Regra de ouro: qualquer nova peça admin deve seguir o mesmo filemap, invariantes e gates (via extensão de G1/G3).

### 3.2. Extensões do Console de Fontes

S27–S32 podem estender o Console de Fontes v2 com, por exemplo:

- visão de **histórico de ingestão** por fonte (tabela aninhada, abas ou seções adicionais em `SourceEditPage`);
- **métricas e healthscore** de fonte (cards de status, últimos erros de ingestão, tempos médios, etc.);
- filtros avançados na listagem (por tipo, status, saúde da ingestão, tags);
- seções de **permissões** ou políticas específicas de uso de fonte.

Tudo isso pode ser adicionado sem quebrar o contrato de S26 desde que:

- continue usando o Design System Admin v1;  
- não remova ou deturpe os fluxos básicos validados em G2/G4.

### 3.3. Extensões nas APIs de Fontes

Futuras sprints podem introduzir:

- endpoints de métricas agregadas (ex.: `/api/sources/metrics`);
- endpoints de histórico (ex.: `/api/sources/{id}/ingestion-history`);
- campos adicionais em `Source` para representar configurações mais ricas.

Requisitos:

- manter compatibilidade com os contratos atuais usados em S26 (ou versionar APIs, se necessário);  
- estender a suíte de testes de API de forma a cobrir os novos fluxos sem perder cobertura dos fluxos básicos.

---

## 4. Antipadrões a Evitar Pós-S26

Para preservar o investimento da S26, alguns antipadrões são explicitamente proibidos:

1. **Console novo ignorar o design system**
   - Criar telas admin futuras (ex.: ingestão, debunker) usando estilos "handmade" em vez de `@/ui/admin`.

2. **Feature de domínio reimplementando componentes genéricos**
   - Implementar `Button`, `Table` ou `Modal` locais em `features/*` em vez de aproveitar `ui/admin/components`.

3. **Backend virar repositório de lógica de UI**
   - Colocar lógica de apresentação (texto de mensagens, cores, etc.) diretamente no backend, em vez de devolver sinais estruturados para que a UI admin decida como exibir.

4. **Burlar gates via edição manual de scorecards**
   - Ajustar JSON de scorecard à mão para esconder falhas de lint, testes ou contratos.

Esses antipadrões devem ser tratados como violações de arquitetura e registrados, se ocorrerem, nos capítulos de lições aprendidas da sprint correspondente.

---

## 5. Síntese do Bloco 3.4

O Bloco 3.4 fecha o Capítulo 3 da S26 com três entregas principais:

1. Um **mapa claro de dependências** entre Design System Admin v1, Console de Fontes v2, APIs de fontes e gates G0–G6.  
2. Um conjunto de **invariantes estruturais** que codificam o que significa a S26 ter sido bem-sucedida em termos arquiteturais, não apenas funcionais.  
3. Um conjunto de **pontos de extensão** e **antipadrões a evitar** que orientam as próximas sprints do Programa 1 a manter (e não diluir) o padrão estabelecido aqui.

Com isso, a arquitetura da S26 deixa de ser um "desenho bonito" e passa a ser um **contrato vivo**, sustentado por filemap, gates, testes e disciplina evolutiva.
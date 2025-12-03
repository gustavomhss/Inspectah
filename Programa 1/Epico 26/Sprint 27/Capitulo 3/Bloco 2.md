# Inspectah — Sprint 27 (S27)
## Capítulo 3 — Bloco 2
### Filemap detalhado de frontend — Admin v1, Fontes, Ingestão e Debunker

> Arquivo-alvo no repo: `docs/s27_cap_3_2_filemap_frontend_admin.md`
>
> Função: detalhar a organização do **frontend admin** na S27 — incluindo Design System Admin v1 e consoles de Fontes, Ingestão 2.0 e Debunker — de forma que qualquer dev ou o Codex saiba exatamente **onde criar, alterar e procurar código**, sem improviso de pastas e nomes.

---

## 1. Princípios de organização do frontend na S27

Antes do detalhamento de caminhos, a S27 adota alguns princípios explícitos para o frontend admin:

1. **Separação clara entre design system e features de domínio**  
   - Tudo que é genérico (layout admin, botões, tabelas, alerts) vive em `ui/admin`.  
   - Tudo que é específico de um domínio (Fontes, Ingestão, Debunker) vive em `features/<domínio>`.

2. **Filemap previsível para features**  
   - Cada domínio segue estrutura semelhante: `pages/`, `components/`, `hooks/`, `types/`, `tests/` (quando aplicável).

3. **Imports explícitos de Admin v1**  
   - Consoles importam componentes admin diretamente de `ui/admin`, de forma clara e rastreável para G1.

4. **Nada de layout "solto" em features**  
   - Grids, shells, cabeçalhos e navegação de admin não são redefinidos em `features/*`.

Esses princípios devem orientar qualquer refino ou criação de arquivos no escopo da S27.

---

## 2. Design System Admin v1 — filemap detalhado

### 2.1 Raiz do Admin v1

- Diretório raiz:  
  - `frontend/inspectah-ui/ui/admin/`

### 2.2 Subestruturas principais

Sugestão de organização interna (ajustar ao estado atual do projeto, mas manter a lógica):

- `frontend/inspectah-ui/ui/admin/layout/`
  - `AdminShell.tsx`  
    - Componente raiz que define o esqueleto de uma página admin (header, sidebar, conteúdo).  
  - `AdminHeader.tsx`  
    - Header com título de página, breadcrumbs, ações principais.  
  - `AdminSidebar.tsx`  
    - Navegação lateral para consoles admin (Fontes, Ingestão, Debunker, etc.).  
  - `AdminContent.tsx`  
    - Wrapper para conteúdo principal (spacing, responsividade, scroll).

- `frontend/inspectah-ui/ui/admin/components/`
  - `AdminButton.tsx`  
  - `AdminTable.tsx`  
  - `AdminBadge.tsx`  
  - `AdminAlert.tsx`  
  - `AdminCard.tsx`  
  - `AdminTag.tsx`  
  - `AdminModal.tsx`  
  - `AdminTabs.tsx`  
  - etc.

- `frontend/inspectah-ui/ui/admin/feedback/`
  - `AdminEmptyState.tsx`  
  - `AdminErrorState.tsx`  
  - `AdminLoadingState.tsx`

- `frontend/inspectah-ui/ui/admin/forms/`
  - `AdminForm.tsx`  
  - `AdminField.tsx`

- `frontend/inspectah-ui/ui/admin/theme/`
  - `tokens.ts`  
  - `colors.ts`  
  - `typography.ts`  
  - `spacing.ts`

- `frontend/inspectah-ui/ui/admin/hooks/`
  - `useAdminLayout.ts`  
  - `useAdminNavigation.ts`

### 2.3 Convenções de import

Exemplos de imports esperados em features:

```ts
import { AdminShell, AdminHeader, AdminContent } from "ui/admin/layout";
import { AdminTable, AdminBadge, AdminAlert } from "ui/admin/components";
```

G1 usará essas convenções para validar adesão ao Admin v1.

---

## 3. Filemap de frontend — Console de Fontes v2

### 3.1 Diretório raiz de Fontes

- `frontend/inspectah-ui/features/sources/`

### 3.2 Estrutura sugerida

- `frontend/inspectah-ui/features/sources/pages/`
  - `SourcesListPage.tsx`  
    - Lista de fontes com filtros, estados e ações.  
  - `SourceDetailPage.tsx`  
    - Detalhe de uma fonte específica, incluindo status e links para ingestão.  
  - `SourceCreatePage.tsx`  
    - Tela de criação de nova fonte.

- `frontend/inspectah-ui/features/sources/components/`
  - `SourcesTable.tsx`  
  - `SourceStatusBadge.tsx`  
  - `SourceActionsMenu.tsx`  
  - `SourceForm.tsx`

- `frontend/inspectah-ui/features/sources/hooks/`
  - `useSourcesList.ts`  
  - `useSourceDetail.ts`  
  - `useCreateSource.ts`

- `frontend/inspectah-ui/features/sources/types/`
  - `source.ts` (tipos para fonte, estados, etc.)

- `frontend/inspectah-ui/features/sources/tests/` (se usado)
  - `SourcesListPage.test.tsx`  
  - `SourceDetailPage.test.tsx`

### 3.3 Uso esperado de Admin v1 em Fontes

Exemplo de padrão esperado em `SourcesListPage.tsx`:

```tsx
export function SourcesListPage() {
  return (
    <AdminShell>
      <AdminHeader title="Fontes" />
      <AdminContent>
        <SourcesTable />
      </AdminContent>
    </AdminShell>
  );
}
```

Qualquer layout diferente disso deve ser exceção explícita e revisada.

---

## 4. Filemap de frontend — Console de Ingestão 2.0

### 4.1 Diretório raiz de Ingestão

- `frontend/inspectah-ui/features/ingestion/`

### 4.2 Estrutura sugerida

- `frontend/inspectah-ui/features/ingestion/pages/`
  - `IngestionOverviewPage.tsx`  
    - Visão geral da saúde da ingestão por fonte.  
  - `IngestionSourceDetailPage.tsx`  
    - Detalhe de ingestão para uma fonte específica.  
  - `IngestionRunsPage.tsx`  
    - Lista de runs/jobs de ingestão recentes.

- `frontend/inspectah-ui/features/ingestion/components/`
  - `IngestionStatusCard.tsx`  
  - `IngestionIssuesTable.tsx`  
  - `IngestionRunTimeline.tsx`

- `frontend/inspectah-ui/features/ingestion/hooks/`
  - `useIngestionOverview.ts`  
  - `useIngestionSourceDetail.ts`  
  - `useIngestionRuns.ts`

- `frontend/inspectah-ui/features/ingestion/types/`
  - `ingestion.ts` (tipos para status, severidade, etc.)

- `frontend/inspectah-ui/features/ingestion/tests/`
  - `IngestionOverviewPage.test.tsx`

### 4.3 Uso esperado de Admin v1 em Ingestão

Exemplo de padrão esperado em `IngestionOverviewPage.tsx`:

```tsx
export function IngestionOverviewPage() {
  return (
    <AdminShell>
      <AdminHeader title="Ingestão" />
      <AdminContent>
        <IngestionStatusCard />
        <IngestionIssuesTable />
      </AdminContent>
    </AdminShell>
  );
}
```

Admin v1 fornece o esqueleto; Ingestão foca em dados e lógica visual específica.

---

## 5. Filemap de frontend — Console do Debunker

### 5.1 Diretório raiz do Debunker

- `frontend/inspectah-ui/features/debunker/`

### 5.2 Estrutura sugerida

- `frontend/inspectah-ui/features/debunker/pages/`
  - `DebunkerCasesListPage.tsx`  
    - Lista de casos de disputa com filtros (severidade, status, datas).  
  - `DebunkerCaseDetailPage.tsx`  
    - Detalhe de um caso (evidências, histórico, ações de decisão).

- `frontend/inspectah-ui/features/debunker/components/`
  - `DebunkerCaseRow.tsx`  
  - `DebunkerCaseSummary.tsx`  
  - `DebunkerEvidencePanel.tsx`  
  - `DebunkerDecisionPanel.tsx`

- `frontend/inspectah-ui/features/debunker/hooks/`
  - `useDebunkerCasesList.ts`  
  - `useDebunkerCaseDetail.ts`

- `frontend/inspectah-ui/features/debunker/types/`
  - `debunker.ts` (tipos para casos, estados, severidade, prazos).

- `frontend/inspectah-ui/features/debunker/tests/`
  - `DebunkerCasesListPage.test.tsx`

### 5.3 Uso esperado de Admin v1 em Debunker

Exemplo de padrão esperado em `DebunkerCaseDetailPage.tsx`:

```tsx
export function DebunkerCaseDetailPage() {
  return (
    <AdminShell>
      <AdminHeader title="Caso de Disputa" />
      <AdminContent>
        <DebunkerCaseSummary />
        <DebunkerEvidencePanel />
        <DebunkerDecisionPanel />
      </AdminContent>
    </AdminShell>
  );
}
```

Debunker usa Admin v1 para estrutura; os componentes de caso/evidência/decisão vivem em `features/debunker`.

---

## 6. Componentes compartilhados específicos de Programa 1 (opcional)

Se surgir necessidade de componentes compartilhados entre Fontes, Ingestão e Debunker que não sejam genéricos o bastante para ir para `ui/admin`, a S27 recomenda:

- diretório: `frontend/inspectah-ui/features/program1-shared/`
  - `components/` — ex.: `Program1HealthSummary.tsx`, `Program1RiskBadge.tsx`.  
  - `hooks/` — ex.: `useProgram1Health.ts`.  
  - `types/` — ex.: tipos agregados entre domínios.

Isso evita duplicação entre consoles, sem poluir o design system com coisas específicas demais.

---

## 7. Relação deste filemap com os gates da S27

- **G1 (Admin design system)**:  
  - olha para `ui/admin/*` e verifica que `features/sources`, `features/ingestion`, `features/debunker` importam componentes admin corretamente.  
- **G2 (fluxos admin)**:  
  - executa testes que navegam por `pages/*` desses features, exercitando a composição com Admin v1.  
- **G3 (qualidade front)**:  
  - compila, testa e faz lint em todo `frontend/inspectah-ui/`, incluindo design system e features.  

Este Bloco 2 serve como contrato físico para onde o Codex deve criar/alterar arquivos de frontend no escopo da S27. Qualquer desvio desse filemap deve ser tratado como exceção explícita, discutida com o squad e registrada em Cap.6 como dívida ou ajuste arquitetural.
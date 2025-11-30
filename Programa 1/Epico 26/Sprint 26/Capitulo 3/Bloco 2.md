# Inspectah — Sprint 26 (S26)
## Capítulo 3 — Bloco 3.2
### Filemap do Design System Inspectah Admin v1

Este bloco descreve **onde vive** o Design System Inspectah Admin v1 no repositório, **como ele é organizado em pastas e arquivos** e **quais são as regras estruturais** que o tornam uma base confiável para todos os consoles admin.

A ideia é simples e rígida: **todo** console admin relevante passa a depender desta árvore; **nenhum** componente de UI admin novo nasce fora dela.

---

## 1. Localização Base do Design System Admin v1

O Design System Inspectah Admin v1 é introduzido como uma "mini-biblioteca" interna no frontend.

Localização base (contrato preferencial da S26):

```text
frontend/inspectah-ui/src/ui/admin/
```

Tudo que for **tokens**, **layout admin** ou **componentes genéricos de UI admin** vive aqui dentro.

Estrutura macro da pasta:

```text
frontend/inspectah-ui/src/ui/admin/
  tokens/
  layout/
  components/
  hooks/        # opcional, apenas utilitários de UI admin
  index.ts
```

---

## 2. Tokens de Design (Design Tokens)

Os **tokens** são a fonte única de verdade para o visual de consoles admin. Nenhum componente admin deve "inventar" cor, fonte ou espaçamento por conta própria.

Filemap sugerido:

```text
frontend/inspectah-ui/src/ui/admin/tokens/
  colors.ts
  typography.ts
  spacing.ts
  radius.ts
  shadows.ts
  zIndex.ts       # se necessário
  index.ts
```

Responsabilidades por arquivo:

- `colors.ts` — paleta admin (primária, secundária, neutros, estados de sucesso/erro/alerta/info).  
- `typography.ts` — escala tipográfica (fontes, tamanhos, pesos, line-heights) para títulos, subtítulos, texto, rótulos, etc.  
- `spacing.ts` — escala de espaçamentos (ex.: `xs`, `sm`, `md`, `lg`, `xl`).  
- `radius.ts` — raios de borda padrão (ex.: `none`, `sm`, `md`, `lg`, `pill`).  
- `shadows.ts` — níveis de sombra para cartões, modais, dropdowns.  
- `zIndex.ts` — camadas principais (header, sidebar, modais, toasts), se o projeto já trabalha com isso.  
- `index.ts` — re-exporta os tokens principais, de forma que outros módulos consumam só esse arquivo.

Invariantes:

1. Nenhum componente de `layout/` ou `components/` deve usar valores "mágicos" de cor, fonte ou espaçamento; tudo vem desses tokens.
2. Ajustes de identidade visual admin são feitos **aqui**, e o resto do sistema apenas reage.

---

## 3. Layout Admin (Admin Shell & Estrutura de Página)

O layout define a "casca" das telas admin: sidebar, header, conteúdo, grid principal.

Filemap sugerido:

```text
frontend/inspectah-ui/src/ui/admin/layout/
  AdminShell.tsx
  AdminSidebar.tsx
  AdminHeader.tsx
  AdminContent.tsx
  SidebarNavItem.tsx
  index.ts
```

Função de cada peça:

- `AdminShell.tsx` — componente raiz de layout admin (orquestra sidebar, header e área de conteúdo).  
- `AdminSidebar.tsx` — estrutura vertical de navegação de consoles/admin pages.  
- `AdminHeader.tsx` — topo da página admin (título, ações contextuais, breadcrumbs simples, se houver).  
- `AdminContent.tsx` — wrapper para o conteúdo principal, garantindo padding e largura máxima consistentes.  
- `SidebarNavItem.tsx` — item de navegação reutilizável na sidebar (link com ícone e label).  
- `index.ts` — re-exporta o que é público para consumo em features (como o Console de Fontes v2).

Invariantes:

1. Qualquer tela admin relevante deve ser renderizada dentro de um `AdminShell` (diretamente ou por wrapper).  
2. Console de Fontes v2 **não** cria sua própria sidebar ou header; ele compõe os do design system.  
3. O layout usa exclusivamente tokens de `tokens/` para espaçamento, tipografia e cores.

---

## 4. Componentes Genéricos (UI/Admin Components)

Os componentes genéricos são blocos de UI reutilizáveis entre consoles (fontes, ingestão, debunker, truth, etc.).

Filemap sugerido:

```text
frontend/inspectah-ui/src/ui/admin/components/
  Button.tsx
  Button.test.tsx
  Input.tsx
  Input.test.tsx
  Select.tsx
  Select.test.tsx
  Table.tsx
  Table.test.tsx
  Badge.tsx
  Badge.test.tsx
  Modal.tsx
  Modal.test.tsx
  Toast.tsx
  Toast.test.tsx
  Banner.tsx
  Banner.test.tsx
  FormField.tsx
  FormField.test.tsx
  index.ts
```

Responsabilidades:

- `Button` — botões padrão admin (primary, secondary, ghost, destructive, etc.).  
- `Input` — campo de texto básico, com estados de erro/sucesso e help text.  
- `Select` — seleção única (dropdown) com suporte a estados e validação.  
- `Table` — tabela base para listagens (inclui header, linhas, estados de vazio e loading).  
- `Badge` — rótulo compacto para estados (ex.: ativa, inativa, arquivada).  
- `Modal` — diálogos de confirmação/ação, com foco acessível.  
- `Toast` — mensagens temporárias de feedback (sucesso/erro/alerta).  
- `Banner` — mensagens em linha ou topo de página (erros globais, avisos).  
- `FormField` — wrapper para rótulo + input + mensagem de erro, padrão para formulários admin.

Boas práticas:

1. Cada componente essencial deve ter pelo menos um teste (ex.: renderização básica e um caso simples de interação).  
2. A pasta `components/` **não** conhece domínios; não existe `SourceForm` aqui (isso vive em `features/sources`).  
3. Exports públicos são centralizados em `index.ts`.

---

## 5. Hooks de UI Admin (Opcional)

Hooks são utilitários ligados à experiência de UI admin, não ao domínio.

Filemap sugerido (se necessário):

```text
frontend/inspectah-ui/src/ui/admin/hooks/
  useToast.ts
  useConfirmDialog.ts
  index.ts
```

Exemplos:

- `useToast` — hook para disparar toasts com o componente `Toast`.  
- `useConfirmDialog` — hook para acoplar `Modal` a fluxos de confirmação simples.

Invariantes:

1. Hooks em `ui/admin/hooks` não chamam APIs de domínio (isso é responsabilidade de features como `features/sources`).  
2. Esses hooks podem ser usados por qualquer console admin.

---

## 6. Ponto de Entrada do Design System (index.ts)

Arquivo-chave:

```text
frontend/inspectah-ui/src/ui/admin/index.ts
```

Responsabilidades:

- Re-exportar tokens principais (`colors`, `typography`, `spacing`, etc.).  
- Re-exportar componentes de layout (`AdminShell`, `AdminHeader`, `AdminSidebar`, `AdminContent`).  
- Re-exportar componentes genéricos (`Button`, `Input`, `Select`, `Table`, `Badge`, `Modal`, `Toast`, `Banner`, `FormField`).  
- Re-exportar hooks públicos (se existirem).

Uso típico em features:

```ts
import { AdminShell, AdminHeader, AdminContent, Table, Button, Badge } from "@/ui/admin";
```

Dessa forma, features como o Console de Fontes v2 dependem apenas de `@/ui/admin`, e não de caminhos internos específicos.

---

## 7. Invariantes Estruturais do Design System Admin v1

Para que o Design System Admin v1 seja uma base confiável e auditável, a S26 estabelece as seguintes invariantes:

1. **Nenhum novo componente admin nasce fora de `ui/admin`**  
   Qualquer elemento de UI genérico para consoles deve ser implementado aqui e só depois consumido por features.

2. **Nenhum componente de `ui/admin` conhece domínios de negócio**  
   Se algo precisa saber o que é "fonte" ou "caso", ele pertence a `features/` (como `features/sources`), não a `ui/admin`.

3. **Tokens são a única fonte de cores/tipografia/espaçamento**  
   Valores de CSS "na mão" (ex.: `#123456`, `16px`, etc.) em componentes admin devem ser exceção altamente justificada e, idealmente, inexistente.

4. **Testes e lint fazem parte do contrato**  
   Componentes críticos do design system devem ter testes; qualquer erro de lint/TypeScript nessa pasta é, por definição, um bloqueio de gate (G1/G3).

5. **Exports públicos são controlados**  
   O que não for parte da API pública não é exportado em `index.ts`. Isso facilita refatorações internas sem quebrar consoles que usam o design system.

---

## 8. Síntese do Bloco 3.2

O Bloco 3.2 fixa o "endereço" e as regras de convivência do Design System Inspectah Admin v1:

- ele mora em `frontend/inspectah-ui/src/ui/admin/`;  
- organiza-se em `tokens/`, `layout/`, `components/`, `hooks/` e `index.ts`;  
- é o único lugar de onde devem sair componentes genéricos de UI admin;  
- não conhece domínios de negócio;  
- é guardado por invariantes claros e pelos gates de S26.

A partir daqui, o Console de Fontes v2 e os consoles futuros têm uma base única, auditável e evolutiva para construir a experiência admin do Inspectah.


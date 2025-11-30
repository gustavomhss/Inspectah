# Inspectah — Sprint 26 (S26)
## Capítulo 4 — Bloco 4.2
### Estratégia de Desenvolvimento & CI/CD da Sprint 26

> Arquivo-alvo no repo: `docs/s26_cap_4_2_estrategia_dev_ci_cd.md`
>
> Função: definir **como o trabalho de S26 é organizado em branches, PRs e pipelines de CI**, e **como o Codex deve operar** para não quebrar gates nem o filemap. Este bloco amarra as waves (Bloco 4.1), a arquitetura/filemap (Cap.3) e os gates (Cap.2) em um plano de execução técnico concreto.

A S26 tem dois eixos fortes:
- criação e consolidação do **Design System Inspectah Admin v1** (`ui/admin`),
- reconstrução do **Console de Fontes v2** em cima desse design system (`features/sources` + `app/sources`).

A estratégia de desenvolvimento e CI/CD precisa refletir isso, sem freestyle.

---

## 1. Organização em branches e PRs

### 1.1 Branch base

- A branch base para S26 é sempre a `main` (ou a branch de release oficial definida para o ciclo).  
- Nenhum trabalho de S26 é feito diretamente em `main`.

### 1.2 Padrão de nomenclatura de branches S26

Branches de S26 seguem o padrão:

- `feature/s26_admin_design_system` — base de Design System Admin v1.
- `feature/s26_sources_console_v2` — Console de Fontes v2 (frontend).
- `feature/s26_sources_api_contracts` — ajustes de APIs/contratos de fontes (backend), se necessário.
- `chore/s26_gates_ci` — ajustes em scripts de gates e workflows de CI ligados à S26.

Regras:

1. Cada branch deve ter um foco claro (design system, console, backend, gates).  
2. Branches podem ser criadas a partir de outras branches de S26 **apenas se** o fluxo de merge mantiver uma linha clara de promoção para `main` (ex.: `feature/s26_sources_console_v2` pode ser criada a partir de `feature/s26_admin_design_system` se precisar do design system já esqueletrado).

### 1.3 Ordem e granularidade de PRs

Recomendação de ordem de PRs (alinhada às waves W1–W3):

1. **PR #1 — S26/W1 — Fundação de Design System & Filemap**
   - Branch principal: `feature/s26_admin_design_system`.  
   - Conteúdo típico:
     - criação do filemap `ui/admin` (tokens, layout, components, hooks, index);
     - esqueleto de `features/sources` (pages/components/api/types/index);
     - ajustes mínimos em `bin/ci_local.sh` e scripts de G0/G1/G3 para enxergar a nova estrutura.

2. **PR #2 — S26/W2 — Console de Fontes v2 & Contratos de Fontes**
   - Branch principal: `feature/s26_sources_console_v2` (podendo depender da branch do PR #1);  
   - Conteúdo típico:
     - implementação dos fluxos básicos do Console de Fontes v2 (listagem, criação, edição, ativar/desativar/arquivar);
     - implementação/ajuste de `sourcesApi.ts` e integrações com `app/sources`;
     - criação/ajuste de `tests/api/test_sources_console.py` e testes de UI ligados a G2.

3. **PR #3 — S26/W2–W3 — API Contracts & Hardening**
   - Branch principal: `feature/s26_sources_api_contracts`;  
   - Conteúdo típico:
     - ajustes finos em `app/sources/models.py`, `schemas.py`, `routes.py`;
     - reforço dos testes de G4 (contratos de API);
     - ajustes em `bin/s26_g4_sources_api_contracts.sh`.

4. **PR #4 — S26/W3 — UX mínima, Docs & Evidências**
   - Branch principal: `chore/s26_gates_ci`;  
   - Conteúdo típico:
     - ajustes de UX do Console de Fontes v2 (mensagens, estados vazios, loading);
     - finalização de docs (`design_system_admin_v1.md`, `runbook_operacao_fontes_v1.md`);
     - ajustes finais de scripts G5/G6 e workflows de CI (`s26-gates.yml`, se criado);
     - geração/validação da estrutura de evidências (`out/evidence/S26_G*/`).

Granularidade:

- Cada PR deve ser **coeso**: ou é sobre fundação de design system, ou sobre console/contratos, ou sobre hardening/docs.  
- Pequenos fixes podem entrar como commits adicionais nesses PRs, evitando abertura de PRs micro que dificultem o ORR.

---

## 2. Uso de CI local

### 2.1 Script canônico de CI local

O script principal de CI local continua sendo:

```bash
bin/ci_local.sh
```

Diretrizes para S26:

1. Sempre que possível, rodar `bin/ci_local.sh` **antes** de abrir um PR, especialmente em branches que tocam frontend ou backend de fontes.  
2. Se o tempo de execução completo for muito alto, usar um modo "focado" em S26 (por exemplo, via flag/env, se existirem) que execute pelo menos:
   - testes de frontend ligados a `ui/admin` e `features/sources`;
   - testes de backend ligados a `app/sources`;
   - scripts de gates S26 (G0–G4) quando já implementados.

### 2.2 Loops rápidos de desenvolvimento

Para ciclos pequenos de desenvolvimento, é aceitável rodar comandos mais específicos, por exemplo:

- Frontend:
  - `cd frontend/inspectah-ui`;
  - `npm test -- --watch` focando em testes de `ui/admin` e `features/sources`;
  - `npm run lint` para garantir aderência a G1/G3.

- Backend:
  - `pytest tests/api/test_sources_console.py`;
  - `pytest app/sources` (separadamente, se existir essa organização).

Mesmo nesses loops rápidos, a regra é: **antes de qualquer PR ser marcado como pronto**, rodar pelo menos uma vez o `bin/ci_local.sh` completo ou um alias equivalente que cubra todos os gates S26.

---

## 3. Uso de CI remoto (GitHub Actions)

### 3.1 Workflows S26

A S26 deve ter, no mínimo, um workflow dedicado ou configurado para rodar os gates da sprint, por exemplo:

- `.github/workflows/s26-gates.yml`

Comportamento esperado:

- rodar em **pull requests** que toquem arquivos relacionados a S26 (docs, `ui/admin`, `features/sources`, `app/sources`, `bin/s26_g*.sh`, etc.);
- rodar em **push** para a branch de release (`main`), garantindo que merges não quebrem S26.

### 3.2 Gates executados no CI remoto

Em estado estável (W3 concluída), o workflow de S26 deve executar pelo menos:

- `bin/s26_g0_scope_and_baseline.sh`;
- `bin/s26_g1_design_system_static.sh`;
- `bin/s26_g2_sources_console_flows.sh`;
- `bin/s26_g3_frontend_quality.sh`;
- `bin/s26_g4_sources_api_contracts.sh`;
- `bin/s26_g5_docs_and_runbooks.sh`;
- `bin/s26_g6_orr_bundle.sh`.

Nas waves anteriores, é aceitável parametrizar o workflow para:

- em W1: focar em G0/G1/G3, com G2/G4 marcados como "a implementar";  
- em W2: rodar G0–G4, com G5/G6 permitindo falhas até docs/evidências estarem prontos;  
- em W3: exigir G0–G6 **GREEN** para considerar a sprint pronta para ORR.

### 3.3 Regras de bloqueio de PR

- PRs principais de S26 (fundação, console, hardening/docs) devem ser **bloqueados** se o workflow `s26-gates` falhar.  
- Exceções pontuais (ex.: falhas temporárias de ambiente) precisam ser documentadas e não podem virar hábito.

---

## 4. Ordem de leitura & Directives para Codex

### 4.1 Ordem de leitura do Playbook pela máquina

Para evitar improviso do Codex, a ordem de leitura recomendada para qualquer sessão de execução S26 é:

1. `Sprint Playbook v3` (esta versão, seccionando até o Capítulo 4).  
2. `inspectah_estado_do_produto_v_0_5_pos_s_25.md` (estado do produto pós-S25).  
3. `inspectah_sprint_26_cap_1_*.md` (Cap.1 da S26).  
4. `inspectah_sprint_26_cap_2_*.md` (gates, scorecards e DoD da S26).  
5. `inspectah_sprint_26_cap_3_*.md` (arquitetura, filemap, invariantes).  
6. `docs/s26_cap_4_1_plano_de_waves.md` (este Bloco 4.1).  
7. Este arquivo: `docs/s26_cap_4_2_estrategia_dev_ci_cd.md`.  
8. Blocos 4.3 e 4.4 (evidências e tasks).

Só depois de passar por essa sequência Codex está autorizado a propor modificações de código/CI.

### 4.2 Directives para Codex (restrições operacionais)

1. **Não criar arquivos fora do filemap do Cap.3**  
   - Qualquer arquivo novo deve ser:  
     - parte de `ui/admin`, `features/sources`, `app/sources`, `docs/` da S26, `bin/` de S26 ou `.github/workflows` S26;  
     - ou explicitamente listado em update futuro de Cap.3.

2. **Não editar scripts de gates antigos fora do escopo**  
   - Scripts de gates de sprints anteriores (S1–S25) não devem ser alterados, exceto por correções estritamente necessárias e documentadas em Cap.6.

3. **Não burlar gates via edição manual de scorecards**  
   - Arquivos `out/scorecards/S26_G*.json` devem ser gerados por scripts, nunca editados manualmente.

4. **Commits pequenos, PRs coesos**  
   - Codex deve preferir commits pequenos e descritivos dentro das branches (`feat:`, `fix:`, `chore:`, `test:`), mantendo os PRs alinhados à wave correspondente.

5. **Regra de ouro: CI antes de merge**  
   - Nenhum PR S26 deve ser mergeado se o workflow `s26-gates` estiver vermelho.

---

## 5. Síntese do Bloco 4.2

O Bloco 4.2 transforma a S26 de um conjunto de intenções em um **plano operacional de desenvolvimento e CI/CD**:

- define como branches e PRs são organizados ao longo das waves W1–W3;  
- explicita como `bin/ci_local.sh` e o workflow `s26-gates.yml` devem ser usados em cada fase;  
- estabelece ordem de leitura do Playbook para o Codex;  
- fixa directives que impedem criação de dívidas invisíveis (arquivos fora do filemap, gates burlados, PRs sem CI).

A partir daqui, o Bloco 4.3 (Plano de Evidências) e o Bloco 4.4 (Tasks & Checklists) complementam a visão com **o que precisa ser registrado** e **quais tasks atômicas devem ser executadas** para que a S26 chegue em GO genuíno.


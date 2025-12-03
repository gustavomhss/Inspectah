# Inspectah — Sprint 27 (Macro v1) — Consoles Admin v1 em Produção (Ingestão & Debunker)

> Arquivo-alvo no repo: `docs/inspectah_sprint_27_macro_v_1.md`
>
> Sprint 27 é a **segunda sprint do épico E26 — Console Full & Coerência de UI/Admin**.
> S26 colocou o Design System Inspectah Admin v1 de pé e migrou o Console de Fontes como piloto; 
> S27 leva esse sistema para os consoles de **Ingestão 2.0** e **Debunker**, fechando o E26 em modo "pode operar sem medo".

---

## 1. Nome, squad e propósito

**Sprint 27 — Consoles Admin v1 em Produção (Ingestão & Debunker)**  
Squads responsáveis (co-sprint):  
- **Squad 1 – Fonte Manager & Console de Fontes** (dono do Design System Admin v1 e da experiência Admin),  
- em coordenação com **Squad 2 – Ingestão 2.0 & Pipelines de Fontes** e **Squad Debunker v0/v1** (parte do Programa de Verdade).

Líderes de rigor (triade principal):  
- **Steve Jobs** — dono de produto para consoles admin: simplicidade, foco em operador e zero ruído.  
- **Bret Victor** — fluidez de interação e visualização de estados (health, erros, flags, disputas).  
- **Leslie Lamport** — invariantes e estados: nada de telas exibindo estados incoerentes com a máquina de estados real.

Apoio chave:  
- **Kent C. Dodds** — formulários, validações e DX de UI.  
- **Brendan Gregg** — observabilidade e sinais de saúde em consoles (como operadores percebem ingestão quebrada ou debunker travado).

**Propósito da S27**  
Transformar o que a S26 fez (Admin v1 + Console de Fontes v2) em um **padrão vivo** para os consoles mais críticos do Inspectah:
- migrar os consoles de **Ingestão 2.0** e **Debunker** para o Design System Admin v1;  
- padronizar estados visuais (vazio, loading, erro recuperável, erro crítico) em todos os consoles admin relevantes;  
- elevar a operação diária de ingestão e debunker de "painel remendado" para **ferramenta coerente de trabalho**;
- fechar, na prática, os estados-alvo do épico **E26 — Design System & Consoles Admin v1**.

Resultado esperado: depois da S27, **Admin v1 deixa de ser piloto e vira infraestrutura oficial** para operar fontes, ingestão e debunker.

---

## 2. Estados-alvo (DONE) da Sprint 27

Ao concluir a S27, é verdade que:

1. **Consoles de Ingestão 2.0 e Debunker rodam 100% em cima do Design System Admin v1**  
   - Todos usam `AdminShell`, `AdminHeader`, `AdminSidebar`, `AdminContent` e a mesma biblioteca de componentes (`ui/admin`).  
   - Não há componentes de layout "paralelos" para esses consoles: o que foge do design system é explicitamente marcado como dívida técnica.

2. **Estados de UI (vazio, carregando, erro, sucesso) são coerentes e padronizados entre Fontes, Ingestão e Debunker**  
   - Mensagens, ícones e cores seguem o mesmo padrão definido no Guia de Consoles Admin v1.  
   - Estados vem de máquinas de estados reais (ingestão, debunker), não de if soltos no front.

3. **O Guia de Consoles Admin v1 existe em versão v1.1, com exemplos reais de Ingestão & Debunker**  
   - Inclui seções de "bom" e "ruim" com screenshots e explicações.  
   - Mostra como representar estados complexos (fila de ingestão, disputas, flags do debunker) sem quebrar o padrão de Admin v1.

4. **Operadores conseguem navegar de Fontes → Ingestão → Debunker sem "mudar de mundo" na UI**  
   - Navegação, estrutura de página e linguagem visual são coerentes.  
   - Runbooks de Fontes, Ingestão e Debunker utilizam a mesma nomenclatura de ações, estados e componentes.

5. **Os gates de frontend e operação foram ajustados para proteger o novo padrão**  
   - G1 cobre o design system admin v1 (tokens e componentes).  
   - G2/G3 cobrem fluxos cruzados de Fontes/Ingestão/Debunker.  
   - G5 (docs/runbooks) inclui agora o Guia de Consoles e runbooks atualizados.

6. **E26 pode ser dado como "DONE" do ponto de vista de UI/Admin**  
   - Todos os consoles-alvo do Programa 1 rodam sobre Admin v1.  
   - Não restam "ilhas" de UI antiga dentro do escopo de E26.

---

## 3. Relação com S20–S26 e limites de escopo

### 3.1 De onde viemos

- **S20** consolidou layout base, autenticação e primeiras unificações de UI.  
- **S21** estruturou o modelo de Fonte e o Console de Fontes original.  
- **S22** construiu Ingestão 2.0 (jobs por fonte, stats, painel).  
- **S23–S24** montaram a trilha de interpretação, classificação e Debunker v0.  
- **S25** criou a camada de Governança de Verdade/Fato.  
- **S26** deu o salto:  
  - criou o **Design System Inspectah Admin v1** em `ui/admin`;  
  - migrou o **Console de Fontes v2** como cliente de referência;  
  - introduziu modelo forte de Cap.5 (ORR, runbooks, risco) e Cap.6 (learnings, dívidas, anti-gaps).

A S27 assume tudo isso como ponto de partida. Ela não reabre decisões de S22–S25: apenas **reencaixa** Ingestão e Debunker no novo padrão de Admin v1.

### 3.2 O que S27 faz (IN)

- Migração visual e estrutural dos consoles de Ingestão e Debunker para Admin v1.  
- Padronização de estados UI (empty/loading/error) e mensagens de sistema.  
- Ajuste de rotas, navegação e breadcrumbs para ficar coerente com Fontes e demais consoles.  
- Atualização do Guia de Consoles Admin v1 para v1.1, incluindo exemplos reais de Ingestão/Debunker.  
- Ajustes de gates e evidências para cobrir os novos consoles sob Admin v1.  
- Pequenos ajustes de UX que melhoram a vida do operador (ex.: filtros, destaque de erros críticos).

### 3.3 O que S27 **não** faz (OUT)

- Não muda a lógica de ingestão 2.0 (scheduling, retries, dataflow) — isso é assunto de sprints de Ingestão (Programa 2).  
- Não introduz novas políticas de Debunker ou Verdade/Fato — isso pertence aos épicos E24–E25 e seus refinamentos.  
- Não cria novos consoles ou cockpits fora do escopo E26 (Truth Cockpit completo, Explore para usuários externos, etc.).  
- Não implementa métricas profundas de observabilidade (painéis complexos, correlação com incidents) — apenas o mínimo para operação coerente.

---

## 4. Domínio e consoles-alvo da Sprint 27

A S27 foca em três "pilares" do Admin:

1. **Console de Fontes v2 (refino)**  
   - Pequenos ajustes para alinhar completamente com Admin v1 (padrões de estado, nomenclatura, componentes).  
   - Correções de UX descobertas em runbooks e incidentes (Cap.5/6 da S26).

2. **Console de Ingestão 2.0**  
   - Página de visão geral de ingestão (por fonte, por tipo, por período) reencaixada em Admin v1.  
   - Tabelas, filtros, status de execução e ações rápidas com padrões de tabela/filtro/badge do design system.  
   - Estados vazios (sem runs), erros recorrentes, sinais de "ingestão atrasada" apresentados de forma coerente.

3. **Console do Debunker v0/v1**  
   - Lista de issues/casos em disputa, tarefas pendentes, decisões recentes, tudo com linguagem visual padrão de Admin v1.  
   - Destacar claramente estados sensíveis (ex.: disputas críticas, prazos estourando) sem inventar paleta de cores paralela.  
   - Preparar terreno para futuras evoluções de Debunker e Truth-DB, de modo que novos estados possam ser plugados sem redesenhar do zero.

Esses três pilares, juntos, completam a visão de **consoles admin críticos sob um mesmo "idioma visual"**.

---

## 5. Gates e abordagem de verificação na S27

A S27 segue o Sprint Playbook v3 para a definição de Cap.2, mas com ênfases específicas:

- **G0 — Escopo & Grounding**  
  - Escopo alinhado a E26 e limitado a consoles Admin (Fontes, Ingestão, Debunker).  
  - Nenhuma task de backend "grande" sem justificativa explícita.

- **G1 — Design System Admin v1**  
  - Verifica integridade de `ui/admin` (tokens, layout, componentes base).  
  - Garante que consoles em S27 usem apenas componentes oficiais:
    - scripts que checam imports de componentes e denunciam padrões antigos.

- **G2 — Fluxos cruzados de Fontes/Ingestão/Debunker**  
  - Scripts/tests E2E focados nos fluxos de operador:  
    - da identificação de uma fonte problemática até sua desativação,  
    - da quebra de ingestão até inspeção no Debunker (quando relevante).

- **G3 — Qualidade global do frontend admin**  
  - Build, lint, testes de componentes, testes de navegação básica.  
  - Espaço futuro para testes visuais/snapshots (ligados à dívida de S26, se puxados).

- **G5 — Docs & Runbooks**  
  - Guia de Consoles Admin v1.1;  
  - runbooks de Fontes, Ingestão e Debunker atualizados e coerentes com a UI real.

- **G6 — ORR & Bundle de evidências**  
  - Cap.5 da S27 refinará o modelo de ORR da S26 para contemplar o conjunto completo de consoles Admin v1.  
  - Bundle com evidências de todos os fluxos críticos.

Detalhes completos de gates, scripts e scorecards vivem no **Cap.2 da S27**.

---

## 6. Organização da Sprint 27 (Capítulos)

A S27 segue exatamente o Sprint Playbook v3 (6 capítulos):

- **Capítulo 1 — Contexto & Problema**  
  - Reconta o estado atual pós-S26 e formaliza o problema de "UI inconsistente entre consoles".  
  - Define estados-alvo específicos da S27 dentro do Épico E26.

- **Capítulo 2 — Gates, Métricas & ORR**  
  - Detalha G0–G6 para Admin v1 completo (Fontes + Ingestão + Debunker).  
  - Especifica cenários E2E que precisam passar antes de GO.

- **Capítulo 3 — Arquitetura & Filemap**  
  - Mostra onde vive cada console, rota, componente e script.  
  - Atualiza o mapa de `ui/admin`, `features/sources`, `features/ingestion`, `features/debunker`.

- **Capítulo 4 — Execução & Tasks**  
  - Planeja waves, tasks e evidências (S27-T-XXX) para migração e refinamentos.  
  - Garante que toda mudança relevante tem gate e evidência associados.

- **Capítulo 5 — ORR, Operação & Risco**  
  - Ajusta o modelo de ORR de S26 para o conjunto de consoles admin.  
  - Define runbooks integrados e riscos de UI/operacionais remanescentes.

- **Capítulo 6 — Learnings, Roadmap & Anti-gaps**  
  - Registra aprendizados específicos da migração de Ingestão/Debunker.  
  - Atualiza dívidas técnicas e impacto no roadmap, fechando o Épico E26.

Cada capítulo terá seu próprio doc em `docs/` (Cap_1 a Cap_6), e o presente macro da S27 funciona como **mapa-mãe** para toda a sprint.

---

## 7. Síntese

A Sprint 27 é o passo que transforma o **Design System Inspectah Admin v1** de prova de conceito (S26) em **padrão obrigatório** para operar as partes mais sensíveis do sistema: fontes, ingestão e debunker.

Quando a S27 estiver concluída e seus Anti-gaps resolvidos:
- E26 poderá ser considerado encerrado com coerência de UI/Admin real, não teórica;  
- operadores terão um "idioma visual" único para lidar com problemas de dados, ingestão e contestação;  
- futuras sprints (E27+ e Programas 2–4) poderão se apoiar nesse padrão sem precisar reinventar consoles ou temas visuais a cada ciclo.

Este doc é a referência macro para todas as decisões de escopo, execução e cobrança da S27.
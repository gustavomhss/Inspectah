# Inspectah — Sprint 27 (S27)
## Capítulo 1 — Bloco 4
### Escopo IN/OUT, premissas, dependências e restrições

> Arquivo-alvo no repo: `docs/s27_cap_1_4_escopo_e_premissas.md`
>
> Função: congelar o **escopo exato** da Sprint 27, junto com as **premissas**, **dependências** e **restrições** explícitas. Este bloco é o contrato de fronteira da S27: tudo que entrar depois aqui vira risco, dívida ou assunto para próxima sprint.

---

## 1. Escopo IN (o que a S27 obrigatoriamente cobre)

A Sprint 27 cobre, obrigatoriamente, os seguintes pontos:

### 1.1 Consoles Admin-alvo

1. **Console de Fontes v2 (refino)**  
   - Ajustes necessários para alinhamento completo com Admin v1 (terminologia, estados de UI, navegação, componentes).  
   - Pequenas melhorias de UX diretamente conectadas aos runbooks e incidentes mapeados em S26.

2. **Console de Ingestão 2.0**  
   - Migração visual/estrutural para Admin v1 (uso de `AdminShell`, `AdminHeader`, `AdminSidebar`, `AdminContent`).  
   - Padronização de tabelas, filtros, painéis de status e ações rápidas com base em `ui/admin`.  
   - Representação coerente de estados de ingestão: saudável, atrasada, falhando, em recuperação.

3. **Console do Debunker v0/v1**  
   - Migração visual/estrutural para Admin v1.  
   - Apresentação padronizada de lista de casos, estados de disputa, severidade, prazos.  
   - Ações de aprovação, rejeição, escalonamento e anotação respeitando padrões de botões, alerts e confirmações de Admin v1.

### 1.2 Design System & guias

4. **Design System Inspectah Admin v1 — refino orientado a consoles críticos**  
   - Inclusão ou ajuste de componentes necessários para representar estados típicos de Ingestão e Debunker (por exemplo, cards de estado, badges de severidade, timelines).  
   - Garantir que esses componentes residam em `ui/admin` e sigam a mesma linguagem de Fontes.

5. **Guia de Consoles Admin v1.1**  
   - Documento consolidando princípios, componentes e exemplos concretos de Fontes, Ingestão e Debunker.  
   - Seções de "Boas práticas" e "Anti-padrões" com screenshots e explicações.

### 1.3 Operação & método

6. **Runbooks de Ingestão e Debunker**  
   - Runbooks escritos/atualizados para refletir a UI após migração para Admin v1.  
   - Linguagem alinhada a Fontes (mesmos termos para ações, estados e componentes).

7. **Gates, cenários E2E e ORR da S27**  
   - Definição e implementação de gates de frontend/admin que protegem o conjunto Fontes + Ingestão + Debunker.  
   - Cenários E2E que atravessem os três consoles.  
   - ORR estruturado em Cap.5 avaliando a experiência admin unificada.

---

## 2. Escopo OUT (fora da S27, explicitamente)

Para proteger foco e viabilidade, os pontos abaixo **não** fazem parte da S27:

1. **Mudanças profundas na lógica de ingestão**  
   - ajustes em algoritmos de retry, priorização de filas, particionamento ou backpressure;  
   - mudanças em modelos de dados de ingestão que afetem pipelines downstream.

2. **Novas políticas ou modos de decisão do Debunker**  
   - criação de novos tipos de disputa, novas classes de evidência ou regras de decisão;  
   - reescrita de fluxos de trabalho de Debunker (quem decide o quê, quando, com qual quorum).

3. **Consoles não-admin / UI pública**  
   - páginas de consulta pública, Explore UI, dashboards para usuários externos;  
   - qualquer UI cuja persona principal não seja operador interno ou Truth Ops.

4. **Observabilidade avançada**  
   - criação de dashboards sofisticados de métricas, correlação automática de incidentes, tracing avançado;  
   - mudanças profundas em logging e collection para ingestão ou Debunker.  
   > Observação: a S27 pode adicionar **o mínimo necessário** para operar consoles de forma decente (por exemplo, contadores básicos, indicadores simples), mas não deve virar uma sprint de observabilidade.

5. **Refactors de backend sem impacto direto na UI/admin**  
   - reestruturações internas de código do backend que não tenham relação direta com as UIs alvo ou com a coerência Admin v1.

Tudo isso deve aparecer, se relevante, em Cap.6 (dívidas/roadmap) ou em epics/sprints próprios.

---

## 3. Premissas da S27 (assumimos como verdade ao planejar)

1. **Admin v1 está suficientemente estável**  
   - Não esperamos uma refatoração estrutural grande de `ui/admin` durante a S27.  
   - Ajustes pontuais são possíveis, mas substituição de paradigma (ex.: layout totalmente novo) está fora de escopo.

2. **APIs de Ingestão 2.0 e Debunker já existem e funcionam**  
   - A S27 não é uma sprint de "fazer backend do zero" para estes domínios.  
   - Se algum endpoint estiver faltando, a decisão será:  
     - ou implementa o mínimo necessário com escopo bem fechado;  
     - ou registra a limitação como dívida/ajuste de roteiro e recorta a UI dependente disso.

3. **Runbooks de Fontes e lessons da S26 são confiáveis**  
   - Usamos o modelo de runbook e ORR de S26 como base para Ingestão e Debunker.  
   - Correções em runbooks antigos serão tratadas, preferencialmente, como parte de docs (Cap.5/Cap.6), não como motivo para refazer S26.

4. **Os squads envolvidos têm capacidade mínima para tocar o escopo**  
   - Squad Admin/Fontes, Squad Ingestão e Squad Debunker estão disponíveis para a S27, ao menos com núcleos responsáveis claros.

---

## 4. Dependências explícitas

A S27 depende de alguns elementos que precisam estar presentes ou minimamente claros:

1. **Especificações anteriores de Ingestão 2.0 e Debunker**  
   - Docs de S22–S25 com modelo de estados, rotas básicas de API e fluxos de negócio.  
   - Sem isso, não há como desenhar telas coerentes com a realidade.

2. **Estado consolidado do Épico E26 pós-S26**  
   - `inspectah_sprint_26_cap_*` (Cap.1–6) e `inspectah_sprint_26_cap_6_*` como referência de learnings e dívidas relevantes.  
   - `inspectah_sprint_26` não precisa estar perfeito, mas precisa estar "bom o bastante" para servir de base.

3. **Roadmap atualizado pós-S26**  
   - `Roadmap.md` refletindo o fato de que Admin v1 + Fontes v2 já existem.  
   - Sem isso, há risco de planejar a S27 como se estivesse reconstruindo o que S26 já fez.

Caso alguma dependência crítica esteja ausente, o Cap.2 (gates) e Cap.4 (execução) devem refletir o risco e a mitigação.

---

## 5. Restrições da Sprint 27

### 5.1 Restrições de tempo e foco

- A S27 é uma sprint de duração padrão (não é um "programa" multi-sprint).  
- Não é aceitável expandir escopo de forma que a migração de Ingestão e Debunker fique parcialmente feita, com múltiplas metades quebradas.

### 5.2 Restrições de mudança de paradigma

- Não vamos introduzir um **Admin v2** no meio do E26.  
- Mudanças de paradigma de navegação (por exemplo, trocar sidebar por topbar em tudo) não são permitidas nesta sprint.

### 5.3 Restrições de impacto em produção

- Qualquer mudança que introduza risco alto de quebrar operações em produção deve:  
  - ser protegida por feature flags claras;  
  - ter plano de rollback explícito (Cap.5);  
  - ser discutida com owners de operação/Truth Ops antes de merge.

---

## 6. Mecanismo de controle de escopo durante a sprint

Para evitar "escopo líquido", a S27 adota os seguintes mecanismos:

1. **Qualquer item novo que não se encaixe claramente neste Bloco 4**:
   - deve ser registrado como proposta em issue separada;  
   - avaliado em checkpoint de sprint;  
   - ou explicitamente movido para backlog/futuras sprints.

2. **Escopo emergente relacionado a bugs de UI/Admin**:
   - bugs diretamente ligados à migração ou padronização **entram** como parte da S27;  
   - bugs antigos, não relacionados, devem ser priorizados em outra sprint, salvo se afetarem fortemente operações.

3. **Revisões semanais de escopo** (ou em checkpoints internos):
   - verificar se as tasks S27-T-XXX ainda correspondem ao que está descrito neste bloco;  
   - ajustar Cap.4 se necessário, sem alterar a essência do escopo.

---

## 7. Síntese do Bloco 4

Este bloco fixa o "campo de jogo" da Sprint 27:

- **IN**: migração e refino dos consoles Fontes, Ingestão e Debunker para Admin v1; refino do design system; Guia Admin v1.1; runbooks e gates/ORR específicos.  
- **OUT**: mudanças profundas de backend, novas políticas de Debunker, UI pública, observabilidade avançada, refactors irrelevantes para a coerência Admin v1.  
- **Premissas**: Admin v1 está estável; APIs básicas de Ingestão/Debunker existem; runbooks/lessons da S26 são base confiável; squads-chave estão disponíveis.  
- **Dependências e restrições**: docs anteriores, estado de E26 pós-S26, roadmap atualizado, limitação de tempo e proibição de criar um "Admin v2" no meio da história.

A partir daqui, qualquer gate (Cap.2), arquitetura (Cap.3) ou plano de execução (Cap.4) que ignore este contrato de escopo está, por definição, desalinhado com a S27.


# Inspectah — Sprint 26 (S26)
## Capítulo 5 — ORR, Operação e Risco

> Arquivo-alvo no repo: `docs/s26_cap_5_macro.md`
>
> Função: explicar o **papel do Capítulo 5** dentro da Sprint 26, amarrando validação end-to-end, ORR, operação e risco. Este capítulo responde, de forma integrada: "A S26 realmente funciona no mundo real? Está pronta para ser usada por humanos sem destruir nada importante?".

O Capítulo 5 sai do plano puramente técnico (Cap.3/4) e entra em **modo de realidade operacional**. Ele organiza a S26 em quatro perspectivas complementares:

1. **Cenários end-to-end de validação** (Bloco 5.1) — o que precisa funcionar de ponta a ponta para a S26 "ser verdade".
2. **Plano de ORR (GO/NO-GO)** (Bloco 5.2) — como a S26 é julgada formalmente antes de ser considerada pronta.
3. **Runbooks & Operação pós-S26** (Bloco 5.3) — como o que foi entregue é usado no dia a dia por operadores e Truth Ops.
4. **Riscos, Rollback & Feature Flags** (Bloco 5.4) — o que pode dar errado, como reduzir exposição e como desligar sem pânico.

O foco central aqui é o domínio de **fontes** e o fato de que a S26:
- introduz o **Design System Inspectah Admin v1** como base de UI admin;  
- reconstrói o **Console de Fontes v2** como primeiro cliente sério desse design system;  
- precisa ser operável e reversível, não apenas "codada".

---

## 1. Relação do Capítulo 5 com Capítulos 1–4

- **Cap.1 (Contexto & Objetivos)** diz o *porquê* da S26: states-of-truth sobre admin v1 e operação de fontes.  
- **Cap.2 (Gates & Métricas)** define *como* medimos se esses objetivos foram atingidos (G0–G6).  
- **Cap.3 (Arquitetura & Filemap)** mostra *onde* no código isso acontece (ui/admin, features/sources, app/sources, bin/s26_g*).  
- **Cap.4 (Execução & Tasks)** descreve *como* implementar e evidenciar a S26 em waves e tasks.

O **Cap.5** pega tudo isso e pergunta:  
> "Se eu for um comitê de ORR ou um operador de verdade, consigo confiar nessa sprint?"  

Ele é, portanto, o capítulo que traduz a S26 em:
- cenários concretos de uso (E2E),  
- um ritual de validação honesto (ORR),  
- instruções de operação (runbooks),  
- alavancas de segurança (flags/rollback).

---

## 2. Estrutura do Capítulo 5

O Capítulo 5 é composto por quatro blocos, cada um com função bem definida.

### 2.1 Bloco 5.1 — Cenários End-to-end de Validação

Arquivo: `docs/s26_cap_5_1_cenarios_e2e_validacao.md`

Função: descrever os **cenários end-to-end mínimos** que precisam funcionar para a S26 ser considerada válida:
- navegação Admin → Console de Fontes v2 usando o Design System Admin v1;
- ciclo de vida básico de uma fonte (criar → ativar → verificar);
- mitigação de fonte problemática (desativar/arquivar);
- pequena extensão do design system adotada pelo console, sem regressão.

Esses cenários se tornam o "contrato de realidade" da S26: se algum deles falhar, o GO fica, no mínimo, sob contestação.

### 2.2 Bloco 5.2 — Plano de ORR (GO/NO-GO)

Arquivo: `docs/s26_cap_5_2_plano_de_orr.md`

Função: normatizar o **ritual de ORR da S26**, definindo:
- pré-requisitos (gates implementados, evidências, bundle, branch de release);  
- passos do ORR (checar gates → amostrar evidências → rodar cenários E2E → revisar docs → decidir);  
- template do resumo ORR (`s26_cap_5_orr_local_summary.md`);  
- critérios formais de GO/NO-GO.

Esse bloco garante que o ORR não seja uma conversa solta: é um procedimento replicável.

### 2.3 Bloco 5.3 — Runbooks & Operação pós-S26

Arquivo: `docs/s26_cap_5_3_runbooks_e_operacao.md`

Função: descrever **como operar fontes** após a S26:
- estrutura mínima do `runbook_operacao_fontes_v1.md`;  
- fluxos padrão (F1–F4) para cadastrar, ativar, editar e desativar/arquivar fontes;  
- tipos de incidente ligados a fontes (I1–I4) e planos de reação;  
- relação com Truth Ops / on-call e checklists operacionais.

Esse bloco garante que o Console de Fontes v2 não seja só uma interface bonita, mas uma ferramenta operacional.

### 2.4 Bloco 5.4 — Riscos, Rollback & Feature Flags

Arquivo: `docs/s26_cap_5_4_riscos_rollback_feature_flags.md`

Função: explicitar **riscos principais da S26** e **como controlá-los**:
- riscos R1–R5 (quebra de fluxos de fontes, regressão de frontend, divergência front/back, UX confusa, falta de monitoração);  
- estratégia de feature flags (`FF_ADMIN_DS_V1`, `FF_SOURCES_CONSOLE_V2`);  
- cenários e passos de rollback/kill switch;  
- conexão entre riscos, flags e ORR.

Esse bloco responde à pergunta: "Se der errado, estamos cegos ou temos freios?".

---

## 3. Como usar o Capítulo 5 na prática

### 3.1 Para o time de desenvolvimento

- Usar os cenários E2E (5.1) como guia de implementação e testes, não apenas como checklist final.  
- Garantir que cada mudança relevante em `ui/admin` e `features/sources` tenha, idealmente, um cenário E2E correspondente.  
- Antecipar riscos R1–R5 na definição de tasks e PRs (Cap.4.4).

### 3.2 Para o comitê de ORR

- Ler o Bloco 5.1 antes da sessão de ORR para entender o "contrato de realidade" da S26.  
- Seguir o plano de ORR do Bloco 5.2 como roteiro oficial.  
- Verificar se runbooks (5.3) e flags/rollback (5.4) estão realmente prontos, não apenas prometidos.

### 3.3 Para operadores / Truth Ops

- Tratar o Cap.5 como **guia de uso e de defesa** da S26: se algo não estiver coberto por cenários/runbooks, é um candidato forte a gap em Cap.6.  
- Usar os fluxos F1–F4 e incidentes I1–I4 para padronizar a linguagem entre operação e desenvolvimento.

---

## 4. Conexão com Capítulo 6 (Lições & Gaps)

O Capítulo 5 é a base factual e operacional que alimenta o Capítulo 6:
- falhas em cenários E2E, problemas no ORR, dificuldades operacionais ou riscos não mitigados em R1–R5 **devem** ser registrados como gaps e lições aprendidas;  
- o resumo ORR (5.2) e incidentes pós-rollout (5.3/5.4) são insumos diretos para `s26_cap_6_lessons_learned_e_gaps.md`.

Em outras palavras, Cap.5 descreve **como a S26 se comportou quando confrontada com o mundo real**; Cap.6 registra o que isso nos ensinou.

---

## Nota rápida (wrap W3)

- G0–G3 executados e verdes localmente; G2 cobre lista/criação/edição/estado do Console de Fontes v2 com testes RTL/MSW sem warnings.  
- Cenários E2E mínimos prontos para ORR: navegar `/admin/sources`, cadastrar, editar e alterar estado com feedback visual.  
- Pendências para G5/G6: consolidar runbook de operação de fontes e bundle final de evidências; registrar dívidas correspondentes no Cap.6.2.

## 5. Síntese do Capítulo 5

O Capítulo 5 transforma a S26 de um conjunto de commits bem-intencionados em uma entrega **avaliada, operável e controlada em termos de risco**:

- Cenários E2E garantem que o que importa de verdade foi testado de ponta a ponta.  
- O Plano de ORR dá um veredito GO/NO-GO baseado em fatos, não em opinião.  
- Runbooks e operação pós-S26 permitem que pessoas reais usem o que foi construído.  
- Riscos, rollback e feature flags impedem que a S26 seja um salto no escuro.

É esse capítulo que garante que o Console de Fontes v2 e o Design System Inspectah Admin v1 **cheguem vivos** à produção e continuem vivos depois do primeiro incidente.

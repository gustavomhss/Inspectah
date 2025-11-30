# Inspectah — Sprint 26 (S26)
## Capítulo 5 — Bloco 5.2
### Plano de ORR da Sprint 26 (GO/NO-GO)

> Arquivo-alvo no repo: `docs/s26_cap_5_2_plano_de_orr.md`
>
> Função: descrever **como o ORR da S26 será conduzido**, desde os pré-requisitos até o veredito de GO/NO-GO, conectando:
> - cenários E2E (Bloco 5.1),
> - gates e evidências (Cap.2, Cap.4.3),
> - bundle de evidências (G6),
> - resumo de ORR (Cap.5.3/Cap.5.4, se existirem).
>
> Regra: o ORR não é teatro. Só existe **GO** se os fatos (evidências) sustentarem, sem tapete.

---

## 1. Objetivos do ORR da S26

O ORR (Operational Readiness Review) da S26 responde, com base em evidências:

1. **O que prometemos na S26 foi de fato entregue?**  
   - Em termos de states-of-truth de Programa/Epico/Sprint (Cap.1).
2. **Isso está operacional?**  
   - Operadores conseguem usar o Design System Admin v1 e o Console de Fontes v2 nos cenários E2E críticos (Cap.5.1) sem gambiarras.
3. **Estamos confortáveis em promover a S26 como base para as próximas sprints (S27–S32)?**  
   - Sem bombas óbvias de arquitetura, sem dívidas invisíveis.

O resultado final é um veredito **GO** ou **NO-GO** acompanhado de justificativas claras e de um rastro de evidências reproduzível.

---

## 2. Pré-requisitos formais para abrir o ORR

Antes de iniciar o ritual de ORR, as condições abaixo devem ser verdadeiras:

1. **Código na branch de release**
   - A revisão é feita sempre sobre a branch de release (ex.: `main` pós-merge da S26), nunca em branch de feature.

2. **Gates S26 implementados**
   - Scripts `bin/s26_g0_*.sh` a `bin/s26_g6_*.sh` existem e rodam localmente.

3. **Scorecards presentes**
   - Arquivos `out/scorecards/S26_G0*.json` … `S26_G6*.json` existem.
   - Eles podem indicar PASS/FAIL, mas não podem estar ausentes.

4. **Estrutura de evidências criada**
   - Pastas `out/evidence/S26_G0*/` … `S26_G6*/` existem com algum conteúdo relevante.

5. **Bundle de evidências gerado pelo menos uma vez**
   - Arquivo `out/bundles/inspectah_s26_evidence_bundle.zip` já foi criado por uma execução de `bin/s26_g6_orr_bundle.sh` (mesmo que ainda seja uma versão preliminar).

Se qualquer pré-requisito não for atendido, o ORR deve ser adiado e registrado como **NO-GO automático por falta de material**.

---

## 3. Participantes e papéis no ORR da S26

Mesmo que, na prática, muito seja automatizado, o plano assume três papéis conceituais:

1. **PO / Spec Office da S26**  
   - Defende o escopo e explica decisões de corte (Cap.1 e Cap.6).  
   - Garante que as expectativas de Programa/Epico foram mapeadas corretamente para gates.

2. **Time de Execução (Codex + Dev)**  
   - Explica escolhas técnicas, arquitetura e como os fluxos foram implementados (Cap.3, Cap.4).  
   - Aponta limitações técnicas e débitos que ficaram para frente.

3. **Conselho de ORR / Revisores**  
   - Usa o pacote de evidências e os cenários E2E para julgar se a S26 está pronta.  
   - Representa produto, operação, qualidade e arquitetura.

Na prática, esses papéis podem ser acumulados pelas mesmas pessoas, mas o **ponto de vista** deve ser preservado: quem executou não pode ser o único a atestar prontidão.

---

## 4. Roteiro do ORR da S26

### 4.1 Passo 1 — Checagem fria de gates e evidências

1. Garantir que todos os gates foram executados na branch de release, na seguinte ordem:

```bash
bin/s26_g0_scope_and_baseline.sh
bin/s26_g1_design_system_static.sh
bin/s26_g2_sources_console_flows.sh
bin/s26_g3_frontend_quality.sh
bin/s26_g4_sources_api_contracts.sh
bin/s26_g5_docs_and_runbooks.sh
bin/s26_g6_orr_bundle.sh
```

2. Abrir os scorecards gerados:
   - `out/scorecards/S26_G0_scope_and_baseline.json`
   - `out/scorecards/S26_G1_design_system_static.json`
   - `out/scorecards/S26_G2_sources_console_flows.json`
   - `out/scorecards/S26_G3_frontend_quality.json`
   - `out/scorecards/S26_G4_sources_api_contracts.json`
   - `out/scorecards/S26_G5_docs_and_runbooks.json`
   - `out/scorecards/S26_G6_orr_bundle.json`

3. Conferir se cada gate está marcado como **PASS/GO** conforme thresholds definidos no Cap.2.  
4. Se algum gate estiver FAIL/NO-GO, registrar imediatamente no rascunho do resumo ORR: qual gate, por quê, impacto.

### 4.2 Passo 2 — Verificação amostral das evidências

1. Abrir o bundle: `out/bundles/inspectah_s26_evidence_bundle.zip`.
2. Conferir, pelo menos, uma amostra de cada pasta `S26_G*` interna:
   - logs de G1 (lint/TS/tests de `ui/admin`);
   - logs de G2 (testes dos fluxos do Console de Fontes v2);
   - logs de G4 (testes de API de fontes);
   - logs de G5 (verificação de docs/runbooks);
   - log de criação do bundle + arquivo de hash (G6).
3. Verificar que os arquivos citados no Bloco 4.3 (Plano de Evidências) **de fato existem** e não são arquivos vazios ou placeholders.

### 4.3 Passo 3 — Execução guiada dos cenários E2E (Cap.5.1)

Para cada cenário E2E (E2E-01 a E2E-04):

1. Ler o cenário no doc `docs/s26_cap_5_1_cenarios_e2e_validacao.md`.
2. Executar o cenário em ambiente de validação (idealmente o mesmo ambiente da branch de release) seguindo os passos descritos.
3. Marcar o resultado como **PASS**, **FAIL** ou **N/A** (se o cenário tiver sido explicitamente cortado em Cap.1/Cap.6):
   - PASS: comportamento real condiz com o cenário;  
   - FAIL: divergência relevante;  
   - N/A: cenário declarado fora de escopo da S26.
4. Se houver FAIL, registrar qualitativamente:
   - em que passo falhou;  
   - se é bug ou corte não documentado;  
   - impacto no uso real.

### 4.4 Passo 4 — Revisão cruzada de docs

1. Abrir `docs/design_system_admin_v1.md`.
   - Verificar se explica de forma minimamente clara: propósito, organização, exemplos de uso.
2. Abrir `docs/runbook_operacao_fontes_v1.md`.
   - Verificar se um operador com conhecimento de Inspectah, mas não da S26, consegue operar os cenários E2E-02 e E2E-03 apoiado pelo runbook.
3. Checar se há referências cruzadas de:
   - Cap.1 (objetivos da S26);
   - Cap.3 (filemap e arquitetura);
   - Cap.4.4 (tasks) dentro desses docs quando fizer sentido.

### 4.5 Passo 5 — Veredito e registro do ORR

1. Consolidar os resultados de gates, evidências, cenários E2E e revisão de docs.
2. Preencher o resumo do ORR em `docs/s26_cap_5_orr_local_summary.md` usando o template da Seção 5.1 abaixo.
3. Definir veredito:
   - **GO**: todos os gates em PASS, cenários críticos E2E-01 e E2E-02 em PASS, E2E-03 e E2E-04 em PASS ou N/A justificado, sem falhas graves não documentadas.  
   - **NO-GO**: qualquer gate crítico em FAIL (G2, G3, G4, G5, G6) ou falhas em cenários E2E que inviabilizem uso real.
4. Se o veredito for NO-GO, listar claramente **o que falta para virar GO** (tasks adicionais, correções, novos testes).

---

## 5. Template de `s26_cap_5_orr_local_summary.md`

Sugestão de estrutura para o resumo do ORR local da S26:

```markdown
# Inspectah — Sprint 26 — ORR Local Summary

## 1. Contexto

- Data do ORR: AAAA-MM-DD
- Branch de referência: <nome-da-branch> (ex.: main @ <SHA>)
- Participantes: <nomes/roles>

## 2. Resultado dos Gates S26

| Gate | Descrição                                 | Status | Observações breves                   |
|------|-------------------------------------------|--------|--------------------------------------|
| G0   | Scope & Baseline                          | GO/NO  | ...                                  |
| G1   | Design System Admin v1 (Static Integrity) | GO/NO  | ...                                  |
| G2   | Console de Fontes v2 (Fluxos Básicos)     | GO/NO  | ...                                  |
| G3   | Front-End Quality & Regression            | GO/NO  | ...                                  |
| G4   | Sources API Contracts                     | GO/NO  | ...                                  |
| G5   | Docs & Runbooks                           | GO/NO  | ...                                  |
| G6   | ORR Bundle & Evidence                     | GO/NO  | ...                                  |

## 3. Execução dos Cenários E2E (Cap.5.1)

| Cenário  | Nome curto                                           | Status | Observações                         |
|----------|------------------------------------------------------|--------|-------------------------------------|
| E2E-01   | Navegar Admin → Console de Fontes v2                 | PASS/FAIL/N-A | ...                          |
| E2E-02   | Ciclo de vida de fonte (criar → ativar → verificar)  | PASS/FAIL/N-A | ...                          |
| E2E-03   | Tratar fonte problemática (desativar/arquivar)       | PASS/FAIL/N-A | ...                          |
| E2E-04   | Extensão pequena do Design System usada em Fontes    | PASS/FAIL/N-A | ...                          |

## 4. Principais Riscos e Limitações

- [ ] Risco 1 — descrição
- [ ] Risco 2 — descrição

## 5. Veredito

- Veredito da Sprint 26: **GO** ou **NO-GO**
- Justificativa principal:
  - ...

## 6. Próximos Passos (ligação com Cap.6)

- Itens que serão endereçados como tech_debt ou tasks em sprints futuras.
- Referência para `docs/s26_cap_6_lessons_learned_e_gaps.md`.
```

---

## 6. Critérios formais de GO/NO-GO

### 6.1 Critérios para GO

A S26 só pode ser declarada **GO** se **todas** as condições abaixo forem verdadeiras:

1. **Gates**
   - G0, G1, G2, G3, G4, G5, G6 em estado GO/ PASS no scorecard.

2. **Cenários E2E**
   - E2E-01 (navegação Admin → Fontes) em PASS.
   - E2E-02 (ciclo básico de vida de fonte) em PASS.
   - E2E-03 (tratar fonte problemática) em PASS ou N/A com justificativa forte.
   - E2E-04 (extensão pequena de design system) em PASS ou N/A com justificativa clara.

3. **Docs e Runbooks**
   - `design_system_admin_v1.md` e `runbook_operacao_fontes_v1.md` existem, passaram em G5 e são utilizáveis (não são esqueletos vazios).

4. **Bundle e Hash**
   - `inspectah_s26_evidence_bundle.zip` existe, contém as pastas de evidências esperadas e tem hash registrado em `g6_bundle_sha256.txt`.

### 6.2 Critérios para NO-GO

Qualquer uma das condições abaixo implica **NO-GO** imediato:

1. Qualquer gate crítico em FAIL: G2, G3, G4, G5 ou G6.
2. E2E-02 (ciclo básico de vida de fonte) em FAIL.
3. Ausência de docs essenciais (guia do design system ou runbook de fontes).
4. Bundle de evidências ausente ou claramente inconsistente com o plano de evidências.

Além disso, o Conselho pode declarar NO-GO por **risco sistêmico** mesmo com gates verdes, se houver problemas graves de arquitetura/operabilidade (mas precisa documentar fortemente no resumo ORR).

---

## 7. Síntese do Bloco 5.2

O Bloco 5.2 tira o ORR da S26 da categoria "reunião subjetiva" e o transforma em um **procedimento replicável**:

- Pré-requisitos claros (gates, scorecards, evidências, bundle).  
- Roteiro em 5 passos (gates → evidências → E2E → docs → veredito).  
- Template padronizado de resumo ORR.  
- Critérios objetivos de GO/NO-GO amarrados a estados-alvo, cenários E2E e evidências.

Com isso, qualquer pessoa (ou comitê) que execute o ORR da S26 deve chegar, em condições normais, ao **mesmo veredito** se seguir o plano — que é exatamente o que se espera de um sistema sério de prontidão operacional.


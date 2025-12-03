# Inspectah — Sprint 32
## Capítulo 5 — Bloco 2
### Pré-Requisitos de ORR & Artefatos Obrigatórios da S32

> Este bloco especifica **o que precisa existir e estar verde antes de abrir o ORR** da Sprint 32. É o checklist duro de artefatos, gates e sanidade mínima que transforma o ORR em revisão baseada em evidência, não em opinião.

---

#### 5.2.1 Visão geral dos pré-requisitos de ORR

Antes de qualquer discussão conceitual, o ORR da S32 exige que três pilares estejam de pé:

1. **Gates S32_G0–G4 executados e registrados**  
   – scorecards presentes, legíveis e coerentes com o estado real do sistema.

2. **Bundle de evidências da S32 montado e íntegro**  
   – `inspectah_s32_evidence_bundle.zip` existente, abrindo sem erro e contendo o mínimo definido.

3. **Sanidade cruzada com ingestão/claims**  
   – ao menos uma rodada de testes/gates históricos após a S32, com regressões classificadas.

Sem isso, o ORR não é uma revisão, é uma conversa vaga. Este bloco detalha exatamente como checar cada pilar.

---

#### 5.2.2 Gates da S32 — estado mínimo exigido

Os gates da Sprint 32 e seu papel no ORR:

- **G0 — Scope & Baseline**  
  - Scorecard: `out/scorecards/S32_G0_scope_and_baseline.json`.  
  - Exigência para ORR: deve existir e mostrar que a estrutura mínima da sprint (docs, scripts, diretórios) foi preparada.  
  - Status aceitável: `"PASS"` ou, no máximo, `"WARN"` para detalhes cosméticos (ex.: documentação ainda em refinamento, mas presente).

- **G1 — Models & Invariants**  
  - Scorecard: `out/scorecards/S32_G1_models_and_invariants.json`.  
  - Exigência: `status = "PASS"`.  
  - Não são aceitos WARNs em invariantes centrais (sem blocos órfãos, estados finais com DecisionBlock, histórico monotônico).

- **G2 — Promotion Flows**  
  - Scorecard: `out/scorecards/S32_G2_promotion_flows.json`.  
  - Exigência: `status = "PASS"`.  
  - Scorecard deve incluir pelo menos: número de claims testadas, taxa de sucesso, erros e amostra de métricas.

- **G3 — Contestation Flows**  
  - Scorecard: `out/scorecards/S32_G3_contestation_flows.json`.  
  - Exigência: `status = "PASS"`.  
  - Deve mostrar contestações testadas, distribuição de outcomes (estado mantido vs alterado) e métricas.

- **G4 — ORR & Bundle**  
  - Scorecard: `out/scorecards/S32_G4_orr_and_bundle.json`.  
  - Exigência: `status = "PASS"` (excepcionalmente `"WARN"` com justificativa forte).  
  - Deve consolidar resumo dos outros gates, existência do bundle e qualquer ressalva relevante.

Durante o ORR, **qualquer discrepância** entre o estado real e o declarado nos scorecards é tratada como problema grave de governança (mesmo que o bug técnico seja pequeno).

---

#### 5.2.3 Bundle de evidências — contrato mínimo

O bundle é o “dossiê oficial” da Sprint 32. Seu caminho padrão:

```text
out/bundles/inspectah_s32_evidence_bundle.zip
```

Para que o ORR ocorra, o bundle deve:

1. **Existir e abrir sem erros**  
   - Testar com uma extração simples (ex.: `unzip -t` ou equivalente).

2. **Conter, no mínimo:**
   - Todos os scorecards da S32:  
     - `S32_G0_scope_and_baseline.json`  
     - `S32_G1_models_and_invariants.json`  
     - `S32_G2_promotion_flows.json`  
     - `S32_G3_contestation_flows.json`  
     - `S32_G4_orr_and_bundle.json`  
   - Evidências principais:  
     - pasta `out/evidence/S32_G1_models_and_invariants/` (logs de migração + testes);  
     - pasta `out/evidence/S32_G2_promotion_flows/` (logs + dumps de blocos/estados antes/depois);  
     - pasta `out/evidence/S32_G3_contestation_flows/` (logs + dumps de estados e contestações).  
   - README de replay (ex.: `README_S32_BUNDLE.md`) contendo:  
     - pré-requisitos de ambiente;  
     - comandos para reexecutar G1, G2, G3;  
     - instruções de onde olhar para verificar um caso específico.

3. **Estar alinhado com os Capítulos 3 e 4**  
   - O que o filemap diz que existe precisa bater com o que está no bundle.  
   - Se algo foi desviado (ex.: pasta renomeada), isso deve estar documentado no README do bundle.

Se qualquer um desses pontos falhar, a recomendação padrão é **não abrir ORR ainda** ou seguir com um ORR exploratório, explicitando que o bundle está incompleto.

---

#### 5.2.4 Sanidade cruzada com ingestão/claims — o pré-ORR técnico

Além dos artefatos da própria S32, o ORR exige evidência de que a sprint **não explodiu o resto do sistema**.

Passos mínimos para sanidade cruzada:

1. **Selecionar conjunto de gates/suites relevantes de sprints anteriores**  
   - Priorizar sprints que mexem com ingestão e claims (ex.: S21, S24, ou conforme estado atual do projeto).  
   - A lista concreta deve ser registrada em Capítulo 4/Capítulo 5.

2. **Executar esses gates/suites em um ambiente com a S32 aplicada**  
   - Idealmente, no mesmo ambiente que será avaliado em ORR.  
   - Registrar logs de execução.

3. **Classificar resultados de regressão**  
   - Cada falha identificada deve ser classificada como:  
     - BLOQUEANTE;  
     - NÃO-BLOQUEANTE (alta, média ou baixa prioridade).  
   - O critério de classificação é o do Anexo 5.7.

4. **Preparar resumo para ORR**  
   - Pequeno quadro-síntese, por exemplo:

   ```text
   Sanidade pós-S32 (ingestão/claims)
   - S21_gates: PASS
   - S24_gates: WARN (1 teste falho em caminho de borda X — não bloqueante)
   - Outros: PASS
   ```

   - Este resumo deve estar disponível no início da sessão de ORR (Capítulo 5 ou doc complementar).

Sem essa sanidade cruzada, o ORR não consegue avaliar com segurança o impacto da S32 no restante da plataforma.

---

#### 5.2.5 Ambiente de avaliação — congelar o alvo

Para evitar discussões confusas do tipo “mas no meu laptop funciona”, o ORR da S32 precisa começar com o alvo **claramente congelado**:

- Identidade do ambiente
  - Nome (ex.: `staging-truthdb-v1`, `preprod-2025-12-01`).  
  - URL/endpoints relevantes (API de métricas, admin, etc.).

- Versão de código
  - Hash de commit ou tag exata;  
  - branches relevantes (ex.: `main` + `feature/s32_truthdb_v1` já mergeada).

- Versão de schema
  - Versão de migração (ex.: `XXXX_s32_truthdb_blocks` aplicada).  
  - Confirmação de que não há migrações pendentes.

- Stack de observabilidade
  - Onde estão as métricas do Truth-DB (Prometheus, OTEL, etc.);  
  - Onde estão os logs que o ORR pode consultar.

Essas informações podem estar em um pequeno anexo ou no topo do documento de ORR, mas **precisam estar explícitas**, ou qualquer conclusão de GO/NO-GO perde força.

---

#### 5.2.6 Como o Bloco 2 é usado na prática

- **Pelo time de engenharia:**  
  - como checklist de “pré-ORR”: nada de marcar reunião de ORR com gates quebrados, bundle faltando ou sanidade não rodada.  

- **Pelo conselho em ORR:**  
  - como filtro inicial: se itens deste bloco não estiverem verdadeiros, o conselho pode encerrar a sessão cedo e requerer correção antes de debate profundo.

- **Por sprints futuras:**  
  - como padrão mínimo de disciplina: qualquer sprint que introduza um novo núcleo crítico (outro subsistema central) deve espelhar este nível de exigência de pré-requisitos.

Com este Bloco 2, o Capítulo 5 ganha um “portão de entrada” claro: o ORR da S32 só começa de verdade quando esse checklist está verde.


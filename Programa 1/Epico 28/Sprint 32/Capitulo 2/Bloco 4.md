# Inspectah — Sprint 32
## Capítulo 2 — Bloco 4
### Invariantes do Truth-DB & Critérios Formais de GO/NO-GO da S32

> Este bloco fecha o Capítulo 2 costurando **invariantes críticas**, **regras de ruptura** e o mapa SA ↔ Gates ↔ Métricas em uma régua única de decisão para a Sprint 32.

---

#### 2.4.1 Invariantes críticas do Truth-DB & Sistema de Blocos (versão operacional)

As invariantes abaixo são tratadas como **leis de gravidade** para a S32. Quebrar qualquer uma delas sem waiver explícito significa NO-GO conceitual.

**Invariante 1 — Nenhum bloco órfão**  
- Todo `FactBlock` deve estar vinculado a pelo menos uma claim/entidade.  
- Todo `EvidenceBlock` deve estar vinculado a um `FactBlock` ou a um estado/claim relevante.  
- Todo `DecisionBlock` deve apontar para um estado de verdade/caso.

Operacionalmente:
- Testes em `tests/truthdb/test_models_and_invariants.py` devem criar blocos de exemplo e verificar que o modelo não permite estados “órfãos” (via constraints, validações em ORM ou lógica de serviço).  
- G1 (`S32_G1_models_and_invariants`) falha se for possível persistir blocos órfãos sem erro.

**Invariante 2 — Histórico é sempre monotônico (nunca destrutivo)**  
- Contestações **não apagam** blocos existentes; sempre criam novos blocos.  
- Estados de verdade anteriores permanecem rastreáveis, mesmo se superados.

Operacionalmente:
- Testes de contestação (`tests/truthdb/test_contestation_flows.py`) devem checar explicitamente:  
  - antes x depois de uma contestação, o número de blocos é >=, nunca <;  
  - estados antigos continuam acessíveis via consultas adequadas.  
- G3 falha se qualquer cenário de contestação resultar em “apagamento” de histórico.

**Invariante 3 — Nenhum estado final sem DecisionBlock associado**  
- Estados de verdade considerados “finais” (ex.: `true`, `rejected`, `debunked`) **não podem existir** sem um `DecisionBlock` que explique como chegaram ali.

Operacionalmente:
- Testes em `test_models_and_invariants.py` e `test_promotion_flows.py` devem tentar criar/alterar estados finais sem `DecisionBlock` e esperar erro.  
- G1 ou G2 falham se o código permitir esse tipo de violação.

**Invariante 4 — Referências cruzadas consistentes**  
- Não pode haver referências a IDs inexistentes (FKs quebradas).  
- Operações de promoção/contestação devem falhar ruidosamente se integridade for violada.

Operacionalmente:
- Testes devem simular tentativas de gravação com referências inválidas e checar que falham com erro explícito.  
- Scripts de migração e serviços não podem “engolir” erros de integridade silenciosamente.

**Invariante 5 — Compatibilidade de migrações S32**  
- É possível subir um banco do zero até a versão S32 e rodar todos os testes.  
- Migrações novas não corrompem dados existentes em cenários realistas.

Operacionalmente:
- G1 executa migrações em um banco limpo e roda testes.  
- Falhas de migração são tratadas como NO-GO até correção ou waiver muito bem justificado.

---

#### 2.4.2 Mapa SA ↔ Gates ↔ Métricas ↔ Invariantes

Para evitar “documento bonito não conectado à realidade”, a S32 adota o seguinte mapa de amarração:

- **SA32_1 — Fluxo claim → blocos → estado de verdade**  
  - Gates principais: `S32_G2_promotion_flows` (primário), `S32_G1_models_and_invariants` (secundário).  
  - Métricas associadas: `truthdb_promotion_success_rate`, `truthdb_flow_error_rate`.  
  - Invariantes envolvidas: 1 (sem blocos órfãos), 3 (estados finais com DecisionBlock), 4 (referências consistentes).

- **SA32_2 — Contestação v1 funcional com trilha auditável**  
  - Gates principais: `S32_G3_contestation_flows`, apoio de `S32_G1`.  
  - Métricas associadas: `truthdb_contestation_rate`, `truthdb_flow_error_rate`, `truthdb_flow_latency_p95` (para fluxo de contestação).  
  - Invariantes envolvidas: 2 (histórico monotônico), 3 (DecisionBlock), 4 (referências consistentes).

- **SA32_3 — Invariantes críticas explicitadas em código**  
  - Gate principal: `S32_G1_models_and_invariants`.  
  - Métricas: opcionalmente, contadores de falhas de invariante em ambientes de teste.  
  - Invariantes: 1–5 (todas listadas acima).

- **SA32_4 — Observabilidade mínima do Truth-DB**  
  - Gates: `S32_G2` e `S32_G3` (validação de emissão), `S32_G4` (referências no bundle).  
  - Métricas: o conjunto completo definido no Bloco 3.  
  - Invariantes: “soft”, mas há uma expectativa de que ausência dessas métricas em produção futura seja tratada como incidente.

- **SA32_5 — Bundle de evidências S32 reexecutável**  
  - Gate principal: `S32_G4_orr_and_bundle`.  
  - Métricas: podem ser fotografadas ou sumarizadas dentro do bundle.  
  - Invariantes: integridade do bundle (todos os scorecards presentes, logs mínimos, dumps principais).

- **SA32_6 — Nenhuma regressão crítica em ingestão/claims**  
  - Gates: execução de gates históricos (S21+, S24, etc.) + checagem explícita no ORR.  
  - Métricas: taxas de erro em ingestão/claims, se já existirem, somadas às de Truth-DB.  
  - Invariantes: compatibilidade de migrações (Invariante 5) e respeito a contratos de schema com Programa 2.

Esse mapa deve aparecer no Capítulo 7 como base para organizar tasks e no Capítulo 5 como referencial para o julgamento de GO/NO-GO.

---

#### 2.5 Critérios formais de GO/NO-GO (amarrados à engenharia)

A decisão de GO/NO-GO da Sprint 32 não é subjetiva; ela se ancora diretamente nos artefatos deste capítulo.

**Condições de GO (todas verdadeiras):**

1. **Estados-alvo cumpridos:**  
   - SA32_1 a SA32_5 marcados como atendidos, com evidências claras nos scorecards correspondentes e no bundle.  
   - SA32_6 sem regressões graves não mitigadas.

2. **Gates S32_G0–S32_G4 executados e com status aceitável:**  
   - Ideal: todos com `status = "PASS"`.  
   - Aceitável: algum `"WARN"` documentado em G0 ou G1, sem impacto em promoção/contestação ou integridade de dados.

3. **Métricas mínimas ativas:**  
   - As quatro métricas obrigatórias do Truth-DB existem, são emitidas e foram visualizadas pelo menos uma vez em ambiente de teste.  
   - Passos para checá-las estão descritos no Capítulo 5.

4. **Invariantes críticas codificadas e testadas:**  
   - Testes relacionados às invariantes 1–5 passam em ambiente de integração.  
   - Não há casos conhecidos de violação dessas invariantes sem waiver explícito do conselho.

5. **Bundle de evidências íntegro:**  
   - `inspectah_s32_evidence_bundle.zip` existe, foi verificado por `S32_G4` e contém:  
     - scorecards G0–G4;  
     - logs principais;  
     - dumps/snapshots de blocos/estados;  
     - README de replay.

**Condições de NO-GO (qualquer uma verdadeira):**

- Falha substancial em SA32_1 ou SA32_2 (sem fluxo end-to-end de promoção ou contestação para o tipo de claim prioritário).  
- Invariantes 1–3 violadas em cenários realistas, sem correção ou waiver explícito e justificado.  
- Métricas mínimas do Truth-DB ausentes ou não funcionais.  
- Bundle S32 inexistente ou tão incompleto que impeça replay/ORR decente.  
- Regressões graves em ingestão/claims não mitigadas nem aceitas conscientemente pelo conselho.

Em caso de NO-GO, a S32 deve gerar um conjunto de **ações corretivas prioritárias** para a próxima sprint, registradas no Capítulo 6.

---

#### 2.6 Como este Bloco 4 deve ser usado na prática

- Pelo time de engenharia: como **lista vermelha de coisas que não podem quebrar** sem acionar alarme; cada invariante deve ter teste(s) associado(s).  
- Pelo PO e conselho: como **checklist de decisão** – se alguém quiser defender GO, precisa apontar evidências concretas para cada item deste bloco.  
- Pelo futuro (S33+): como base para endurecer ou refinar invariantes à medida que o Truth-DB ganhar mais responsabilidade.

Com este Bloco 4, o Capítulo 2 fica fechado: estados-alvo, gates, métricas e invariantes da Sprint 32 formam um sistema coerente de cobrança e decisão, à altura do padrão de excelência exigido pelo projeto.
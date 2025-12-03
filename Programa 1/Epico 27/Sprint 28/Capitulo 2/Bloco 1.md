# Inspectah — Sprint 28
## Capítulo 2 — Bloco 1
### Visão geral: Gates, estados-alvo e o que significa “Sprint 28 em GO”

---

#### 2.1.1 Por que este capítulo existe

O Capítulo 2 é o contrato objetivo de qualidade da Sprint 28. Ele responde, sem espaço para interpretação solta, a três perguntas centrais:

1. **Quando podemos afirmar que a Sprint 28 está realmente em GO?**  
2. **Quais são os gates que precisam estar verdes para isso ser verdade?**  
3. **Quais estados-alvo e critérios mínimos definem o “pronto de verdade”, e não apenas “compila na minha máquina”?**

A Sprint 28 mexe em um ponto extremamente sensível do Inspectah — o módulo de fontes + ligação com a Ingestão 2.0 — e, por isso, não pode depender de “feeling” ou de confiança implícita. Tudo precisa ser verificável, reexecutável e documentado.

---

#### 2.1.2 Relação entre estados-alvo, gates e DoD

No Capítulo 1, foram definidos os **estados-alvo** da Sprint 28 (SA-28-01 a SA-28-05). O Capítulo 2 faz o encaixe explícito:

- Cada estado-alvo é coberto por **um ou mais gates**.  
- Cada gate é um script (`bin/s28_gX_*.sh`) com **evidências e scorecards**.  
- A **Definition of Done (DoD) global** da sprint é, em essência, “todos os estados-alvo atingidos + todos os gates em PASS + repositório em estado sanitário”.

Mapa de cobertura (visão resumida):

- **SA-28-01 — API de admin de fontes sólida e estável**  
  ↳ Coberto principalmente por **S28_G2** (Admin API) e apoiado por **S28_G1** (modelo & schema).

- **SA-28-02 — Console de fontes v2 permite operar sem terminal**  
  ↳ Coberto por **S28_G3** (Sources Console Front) e validado qualitativamente por **S28_G6** (Demo Interna & UX).

- **SA-28-03 — ON/OFF conversa com Ingestão 2.0**  
  ↳ Coberto por **S28_G4** (Integração ON/OFF × Ingestão 2.0) e observado indiretamente em **S28_G6**.

- **SA-28-04 — Modelo de fonte consolidado, documentado e saneado**  
  ↳ Coberto por **S28_G1** (Sources Model & Schema) e ancorado em **S28_G0** (Scope & Baseline) e documentação do Cap. 3.

- **SA-28-05 — Sanidade de legado S21/S22 preservada**  
  ↳ Coberto por **S28_G5** (Observability & Legacy Sanity), com apoio da própria execução completa dos gates.

Com isso, cada objetivo da sprint tem “quem responde por ele” no conjunto de gates — nada fica dependente de boa vontade ou memória.

---

#### 2.1.3 O que significa “Sprint 28 em GO” (definição de alto nível)

A Sprint 28 é considerada **“em GO”** quando, simultaneamente:

1. **Todos os gates S28_G0 a S28_G7 estão em PASS**, com evidências presentes em `out/evidence/S28_G*/**` e scorecards em `out/scorecards/S28_G*.json`.  
2. **Os estados-alvo SA-28-01…SA-28-05 são verdadeiros na prática**, não apenas no papel, ou seja:
   - a API de admin `/admin/sources` permite CRUD & ON/OFF com contrato estável e testado,  
   - o console de fontes v2 permite que operadores executem os casos A–D sem precisar de terminal,  
   - ON/OFF de fonte regula a Ingestão 2.0 de forma determinística (nenhuma fonte `DISABLED` continua sendo ingerida),  
   - o modelo de `Source` está consolidado e refletido no banco,  
   - gates de S21/S22 relevantes seguem passando, sem regressões.
3. **O repositório está em estado sanitário**, ou seja:
   - testes relevantes passam localmente e no CI,  
   - scripts de gates são idempotentes (podem ser reexecutados sem quebrar o ambiente),  
   - documentação da S28 (Cap. 1–4) está coerente com o código e com as evidências.

Na prática, “GO” significa que qualquer pessoa com contexto mínimo pode:
- entender o que foi entregue,  
- rodar os scripts de validação,  
- reproduzir os resultados,  
- operar fontes via console com confiança.

---

#### 2.1.4 Estrutura de gates da Sprint 28

A Sprint 28 adota um conjunto de **oito gates** numerados de G0 a G7, seguindo o padrão já consolidado no projeto:

- **S28_G0 — Scope & Baseline**  
  Verifica se a sprint começou direito: docs, escopo, referência ao Programa 1 e E27.1.

- **S28_G1 — Sources Model & Schema**  
  Garante que o modelo de `Source` e o schema de banco estão alinhados e com invariantes testadas.

- **S28_G2 — Admin API `/admin/sources` (CRUD & ON/OFF)**  
  Testa e valida a API de admin de fontes, incluindo erros e transições proibidas.

- **S28_G3 — Sources Console Front (Console de Fontes v2)**  
  Foca no frontend: build, testes e uso correto do Design System Admin v1.

- **S28_G4 — Sources × Ingestão 2.0 (ON/OFF Integration)**  
  Prova, via testes de integração, que o estado da fonte regula o scheduler.

- **S28_G5 — Observability & Legacy Sanity (S21/S22)**  
  Garante que mudanças na S28 não quebraram o que S21/S22 já entregaram.

- **S28_G6 — Demo Interna & UX**  
  Valida, com pessoas, que o console e o fluxo de operação são utilizáveis.

- **S28_G7 — GO/NO_GO Final**  
  Consolida a decisão final com base nos scorecards e evidências de todos os gates anteriores.

Cada gate será detalhado nos próximos blocos do Capítulo 2, com:
- script responsável (`bin/s28_gX_*.sh`),  
- entradas esperadas,  
- critérios explícitos de PASS/FAIL,  
- e a forma como alimenta scorecards e DoD.

---

#### 2.1.5 Papel do Capítulo 2 no ciclo de vida da sprint

Este capítulo não é apenas um checklist para o fim da sprint; ele deve ser utilizado em três momentos:

1. **Planejamento**  
   - Para alinhar a equipe sobre o que realmente precisa ser implementado e testado.  
   - Para evitar escopo fantasma (“features” sem gate, sem evidência e sem dono).

2. **Execução**  
   - Como mapa de progresso: cada gate em PASS é um marco concreto.  
   - Como proteção contra atalhos perigosos (ex.: pular testes de integração e ainda assim declarar vitória).

3. **ORR / Encerramento**  
   - Como base para a decisão GO/NO_GO: o S28_G7 apenas consolida o que já está descrito aqui.  
   - Como registro histórico: qualquer pessoa poderá voltar neste capítulo para entender como a Sprint 28 foi avaliada.

Com isso, o Bloco 1 do Capítulo 2 estabelece a moldura conceitual dos gates e da Definition of Done da Sprint 28. Os próximos blocos descem para o nível de detalhe gate a gate, até não sobrar espaço para ambiguidade sobre qualidade e completude.
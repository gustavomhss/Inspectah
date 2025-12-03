# Inspectah — Sprint 27 (S27)
## Capítulo 5 — ORR Local, Scorecards & Veredito

> Arquivo-alvo no repo: `docs/s27_cap_5_orr_local_summary.md`
>
> Função: descrever **como a Sprint 27 será avaliada** ao final (ORR local), quais evidências entram na análise, qual o formato do scorecard G6 e como o veredito final (GO / NO_GO / GO_WITH_RISKS) será registrado, inclusive para o Épico E26 (Admin v1 em Fontes, Ingestão e Debunker).

---

## 1. Papel do Capítulo 5 na S27

Cap.5 responde a três perguntas centrais:

1. **O que exatamente será avaliado no fim da S27?**  
2. **Com quais evidências e em qual ritual de decisão (ORR)?**  
3. **Como o veredito será registrado e comunicado (scorecard G6 e docs)?**

Cap.5 é o "tribunal" da sprint: ele não cria trabalho novo, mas julga se o trabalho feito pela S27 realmente entregou os estados-alvo definidos em Cap.1, suportados pelos gates e evidências de Cap.2–Cap.4.

---

## 2. Escopo da avaliação da S27

A S27 será avaliada em dois níveis:

- **Nível Sprint (S27)**  
  - Se os objetivos específicos da S27 foram atingidos: Admin v1 consolidado como padrão real nos consoles de Fontes, Ingestão e Debunker, com fluxos críticos funcionando, contratos estáveis e operação documentada.

- **Nível Épico (E26)**  
  - Se, somadas S26 e S27, o Épico E26 (Admin v1 em Programa 1) atingiu um patamar aceitável para ser considerado GO / GO_WITH_RISKS / NO_GO como degrau do roadmap maior do Inspectah.

Cap.5 foca principalmente na S27, mas precisa sempre espelhar o impacto no Épico E26.

---

## 3. Entradas obrigatórias do ORR da S27

A sessão de ORR da S27 só pode acontecer se todas as entradas abaixo estiverem presentes:

1. **Scorecards de Gates (G0–G6)**  
   - `out/scorecards/S27_G0_scope_and_env.json`  
   - `out/scorecards/S27_G1_admin_design_system.json`  
   - `out/scorecards/S27_G2_admin_flows.json`  
   - `out/scorecards/S27_G3_front_quality_admin.json`  
   - `out/scorecards/S27_G4_admin_contracts.json`  
   - `out/scorecards/S27_G5_docs_runbooks.json`  
   - `out/scorecards/S27_G6_orr_summary.json` (pode ser preenchido primeiro em modo draft, depois finalizado).

2. **Evidências agregadas (out/evidence)**  
   - logs e artefatos em `out/evidence/S27_G*/`, conforme Cap.4 Bloco 2.

3. **Bundle de evidências da S27**  
   - `out/bundles/inspectah_s27_evidence_bundle.zip` (gerado por G6).

4. **Documentos centrais da S27**  
   - Cap.1–Cap.4 da S27 completos.  
   - `docs/guia_consoles_admin_v1_1.md`.  
   - runbooks: `docs/runbook_operacao_fontes_vX.md`, `docs/runbook_operacao_ingestao_vX.md`, `docs/runbook_operacao_debunker_vX.md`.

5. **Visão do Épico E26**  
   - Resumo curto (pode ser seção neste próprio Cap.5): contexto do Épico E26, o que veio na S26, o que veio na S27 e quais eram os critérios de sucesso do Épico.

Se qualquer uma dessas entradas estiver ausente ou obviamente desatualizada, o ORR deve ser adiado ou o fato registrado como bloqueador.

---

## 4. Participantes e papéis na sessão de ORR

A sessão de ORR local da S27 deve envolver, no mínimo:

- **Owner de Admin v1 / UI**  
  - Responsável por defender o estado do design system admin e sua aplicação nos consoles.

- **Owner de Fontes**  
  - Responsável por fluxos de cadastro, listagem, status e operação de Fontes.

- **Owner de Ingestão 2.0**  
  - Responsável por visão de ingestão e ligação com Fontes.

- **Owner de Debunker**  
  - Responsável por casos, evidências e decisões do Debunker.

- **Owner de Operações/Runbooks**  
  - Responsável por docs e prontidão operacional.

- **Representante de Qualidade / Gates**  
  - Responsável por explicar scorecards G0–G6 e como ler os dados.

Idealmente, alguém com visão de produto/roadmap também participa para conectar o veredito da S27 com os próximos passos de Inspectah.

---

## 5. Roteiro recomendado da sessão de ORR

Um roteiro sugerido para a reunião de ORR da S27:

1. **Contexto (5–10 min)**  
   - Revisão rápida do Épico E26 e dos objetivos da S27 (Cap.1).  
   - Relembre quais riscos fundamentais estavam em jogo.

2. **Visão dos Gates (15–25 min)**  
   - Passar por G0–G5, com foco em:  
     - campos principais dos scorecards;  
     - notas relevantes;  
     - evidências específicas quando houver dúvida.  
   - Destacar qualquer gate que esteja em estado marginal (ex.: GO com ressalvas importantes).

3. **Demonstração dos Consoles Admin (15–20 min)**  
   - Demonstração guiada dos consoles de Fontes, Ingestão e Debunker sob Admin v1:  
     - mostrar um fluxo típico de cada;  
     - mostrar pelo menos um fluxo combinado Fontes → Ingestão → Debunker.  
   - Se possível, relacionar cada fluxo à cobertura de G2.

4. **Operação & Runbooks (10–15 min)**  
   - Revisão de como runbooks são usados para operar os consoles;  
   - Simulação enxuta de um incidente e resolução guiada por runbook (pode ter sido feita antes, mas é importante trazer o resultado).

5. **Discussão de Riscos & Dívidas (10–20 min)**  
   - Quais pontos ainda inspiram pouca confiança?  
   - Que dívidas técnicas e de produto foram criadas na S27?  
   - O que é aceitável para seguir e o que precisa ser tratado antes de escalar para mais programas?

6. **Veredito & Registro (10–15 min)**  
   - Definir o veredito da S27 (GO, NO_GO ou GO_WITH_RISKS).  
   - Definir o veredito do Épico E26.  
   - Registrar a decisão no scorecard G6 e neste Cap.5, incluindo lista de riscos e próximos passos.

O objetivo é que o ORR não seja só uma apresentação, mas uma decisão informada com base em evidências claras.

---

## 6. Estrutura do scorecard G6 (S27_G6_orr_summary.json)

O scorecard G6 é o registro estruturado do ORR. Um formato sugerido (campos podem ser refinados):

```json
{
  "sprint_id": "S27",
  "epic_id": "E26",
  "verdict_sprint": "GO_WITH_RISKS",
  "verdict_epic": "GO_WITH_RISKS",
  "gates_status": {
    "G0": "GO",
    "G1": "GO",
    "G2": "GO_WITH_RISKS",
    "G3": "GO",
    "G4": "GO",
    "G5": "GO",
    "G6": "N/A"
  },
  "key_risks": [
    {
      "id": "RISK-001",
      "title": "Cobertura parcial de cenários E2E de Debunker",
      "impact": "medium",
      "mitigation_plan": "Expandir cenários em sprint futura S2X",
      "owner": "Owner Debunker"
    }
  ],
  "key_strengths": [
    "Admin v1 aplicado de forma consistente nas telas principais",
    "Contratos de Fontes/Ingestão/Debunker cobertos por testes de contrato",
    "Runbooks iniciais escritos e usados em simulações"
  ],
  "bundle_created": true,
  "bundle_path": "out/bundles/inspectah_s27_evidence_bundle.zip",
  "orr_session": {
    "date": "YYYY-MM-DD",
    "participants": [
      "Owner Admin v1",
      "Owner Fontes",
      "Owner Ingestão",
      "Owner Debunker",
      "Owner Ops/Runbooks",
      "Representante Qualidade/Gates"
    ]
  },
  "notes": "Resumo textual das principais decisões do ORR."
}
```

Valores específicos (veredictos, riscos, participantes, etc.) devem ser preenchidos com o resultado real da sessão.

---

## 7. Critérios para GO, NO_GO e GO_WITH_RISKS

Para tornar a decisão menos subjetiva, a S27 define critérios de referência (não são fórmulas rígidas, mas balizadores claros):

- **GO (Sprint e/ou Épico)**  
  - G0–G5 em estado GO (podem ter pequenas ressalvas documentadas, mas sem riscos estruturais).  
  - Fluxos críticos de Fontes, Ingestão e Debunker funcionando de ponta a ponta (G2).  
  - Contratos de API centrais estáveis (G4 sem mismatches graves).  
  - Runbooks suficientes para operar o sistema em Programa 1 (G5).  
  - Riscos remanescentes classificados como baixo ou moderado e com plano de mitigação claro.

- **GO_WITH_RISKS**  
  - Algum gate pode estar em GO_WITH_RISKS (especialmente G2 ou G4), desde que:  
    - riscos estejam claramente mapeados;  
    - mitigação seja factível em sprints próximas;  
    - não haja risco inaceitável de dano a dados, credibilidade ou operação.  
  - Aceitável, por exemplo, se cenários E2E ainda não cobrirem todos os casos extremos, mas a base estiver sólida.

- **NO_GO**  
  - Falhas graves em G0 (ambiente/repo instável), G2 (fluxos críticos quebrados) ou G4 (contratos instáveis a ponto de inviabilizar uso dos consoles).  
  - Ausência de runbooks mínimos em G5.  
  - Riscos altos sem plano realista de mitigação.  
  - Falta de confiança da equipe na prontidão para uso real, mesmo em Programa 1.

O ORR deve usar esses critérios como lente, não como camisa de força.

---

## 8. Integração com o bundle de evidências

O G6 e este Cap.5 se ancoram no bundle da S27:

- `bin/s27_g6_orr_bundle.sh` deve:
  - verificar presença de todos os scorecards;  
  - incluir subset relevante de `out/evidence/`;  
  - adicionar docs centrais (Cap.1–Cap.6, guia Admin v1.1, runbooks);  
  - gerar `inspectah_s27_evidence_bundle.zip` com estrutura previsível.

Cap.5 deve registrar:

- hash ou checksum do bundle (quando conveniente);  
- path do bundle;  
- confirmação de que o ORR se baseou nesse bundle para suas conclusões.

---

## 9. Saída do ORR e ligação com Cap.6

Ao final da sessão de ORR, Cap.5 deve ser atualizado com:

- veredito final da S27 e do Épico E26;  
- resumo dos principais pontos de discussão;  
- lista de riscos-chave, com IDs, impacto, plano e owner;  
- referência direta às tasks S27-T-XXX que originaram dívidas específicas.

Cap.6, por sua vez, usará:

- o scorecard G6;  
- este Cap.5;  
- e as evidências do bundle, para construir um relato de learnings, dívidas e roadmap, mantendo a história da S27 rastreável.

Assim, Cap.5 se torna o "ato de julgamento" da sprint: em cima dele, o time decide se Admin v1 em Programa 1 (E26) sobe de patamar, segue com cautela ou precisa de mais trabalho antes de ser tratado como algo pronto para escalar.


# Inspectah — Sprint 27 (S27)
## Capítulo 5 — Bloco 3
### Formato do Scorecard G6, Leitura do Veredito e Tipos de GO/NO_GO

> Arquivo-alvo sugerido no repo: `docs/s27_cap_5_3_orr_formato_g6_e_veredito.md`
>
> Função: definir em detalhes o **formato do scorecard G6 (S27_G6_orr_summary.json)**, como o veredito deve ser lido e registrado e como os diferentes tipos de GO/NO_GO/GO_WITH_RISKS se materializam em dados, não só em adjetivos.

---

## 1. Papel do scorecard G6 na S27

O scorecard G6 é o **registro estruturado** do ORR da Sprint 27:

- é o lugar onde o veredito final da S27 e do Épico E26 fica congelado;  
- é o índice dos principais riscos, forças e próximos passos;  
- é o documento que qualquer pessoa pode ler depois e entender "o que foi decidido" sem ver toda a ata da reunião.

Se Cap.5 (como um todo) é o texto narrativo do julgamento, G6 é o **resumo tabular e parseável por máquina**.

---

## 2. Estrutura mínima do `S27_G6_orr_summary.json`

Abaixo, um formato de referência mais completo (campos podem ser estendidos, mas não encolhidos sem motivo forte):

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

  "states_status": {
    "SA-01_admin_v1_padrao_real": "ACHIEVED",
    "SA-02_fluxos_admin_e2e": "PARTIAL",
    "SA-03_contratos_estaveis": "ACHIEVED",
    "SA-04_operacao_documentada": "ACHIEVED",
    "SA-05_avaliacao_objetiva": "ACHIEVED"
  },

  "key_risks": [
    {
      "id": "RISK-001",
      "title": "Cobertura parcial de cenários E2E de Debunker",
      "impact": "medium",
      "likelihood": "medium",
      "affected_states": ["SA-02_fluxos_admin_e2e"],
      "mitigation_plan": "Expandir cenários E2E de Debunker na sprint S2X",
      "mitigation_owner": "Owner Debunker",
      "target_sprint": "S2X",
      "notes": "Hoje só cobrimos casos simples; casos com contestação encadeada não estão nos testes."
    }
  ],

  "key_strengths": [
    "Admin v1 aplicado de forma consistente nas telas principais de Fontes, Ingestão e Debunker",
    "Contratos de API de Programa 1 cobertos por testes de contrato e estáveis",
    "Runbooks iniciais de operação criados e exercitados em simulações"
  ],

  "actions_required": [
    {
      "id": "ACT-001",
      "title": "Ampliar cenários E2E de Debunker para cobrir casos encadeados",
      "related_risks": ["RISK-001"],
      "owner": "Owner Debunker",
      "due_sprint": "S2X",
      "status": "PLANNED"
    }
  ],

  "bundle_created": true,
  "bundle_path": "out/bundles/inspectah_s27_evidence_bundle.zip",

  "orr_session": {
    "date": "YYYY-MM-DD",
    "duration_minutes": 75,
    "participants": [
      "Owner Admin v1",
      "Owner Fontes",
      "Owner Ingestão",
      "Owner Debunker",
      "Owner Ops/Runbooks",
      "Representante Qualidade/Gates"
    ],
    "chair": "Representante Qualidade/Gates"
  },

  "summary": {
    "what_was_decided": "Admin v1 em Programa 1 é aceito com riscos moderados em cenários avançados de Debunker.",
    "why_decision_makes_sense": "G0–G5 estão em GO ou GO_WITH_RISKS com riscos mapeados, e a operação em Programa 1 é considerada viável.",
    "how_it_impacts_roadmap": "Abre espaço para focar em S2X (Debunker E2E) e S2Y (Admin v1 em Programa 2)."
  },

  "notes": "Campo livre para detalhes adicionais do comitê de ORR."
}
```

Na prática, o script de G6 deve gerar ou atualizar este arquivo, preenchendo o que for possível automaticamente e deixando campos de decisão (veredictos, riscos, ações) para o preenchimento pós-reunião.

---

## 3. Campos obrigatórios x campos recomendados

### 3.1 Campos obrigatórios

Para o G6 ser considerado válido, os seguintes campos são obrigatórios:

- `sprint_id`  
- `epic_id`  
- `verdict_sprint`  
- `verdict_epic`  
- `gates_status` (com entradas para G0–G6)  
- `states_status` (SA-01..SA-05)  
- `bundle_created`  
- `bundle_path`  
- `orr_session.date`  
- `orr_session.participants`  
- `summary.what_was_decided`

Sem esses campos, o G6 deve ser marcado como **incompleto**.

### 3.2 Campos fortemente recomendados

- `key_risks` (mesmo que vazio, deve estar presente)  
- `key_strengths`  
- `actions_required`  
- `orr_session.chair`  
- `summary.why_decision_makes_sense`  
- `summary.how_it_impacts_roadmap`  
- `notes`

Esses campos são essenciais para que o G6 sirva como documento vivo de governança, e não só um carimbo binário de GO/NO_GO.

---

## 4. Tipos de veredito e como eles aparecem no G6

### 4.1 Veredictos possíveis

Para `verdict_sprint` e `verdict_epic`, os valores permitidos são:

- `"GO"`  
- `"GO_WITH_RISKS"`  
- `"NO_GO"`

Para `gates_status[Gx]`, os valores permitidos são:

- `"GO"`  
- `"GO_WITH_RISKS"`  
- `"NO_GO"`  
- `"N/A"` (quando um gate não se aplica)  

Para `states_status[SA-XX]`, valores sugeridos:

- `"ACHIEVED"`  
- `"PARTIAL"`  
- `"NOT_ACHIEVED"`

### 4.2 Coerência mínima entre campos

Algumas regras simples ajudam a evitar contradições em G6:

- Se `verdict_sprint == "GO"`, então:  
  - nenhum gate crítico (G0, G2, G4, G5) deve estar `"NO_GO"`;  
  - nenhum estado-alvo deve estar `"NOT_ACHIEVED"`;  
  - `key_risks` não pode conter riscos com impacto "high" sem plano de mitigação.

- Se `verdict_sprint == "NO_GO"`, então:  
  - pelo menos um gate crítico deve estar `"NO_GO"` **ou** pelo menos um estado-alvo deve estar `"NOT_ACHIEVED"` com justificativa clara em `key_risks`;  
  - o campo `summary.what_was_decided` deve explicar o que bloqueou o GO.

- Se `verdict_sprint == "GO_WITH_RISKS"`, então:  
  - pelo menos um gate ou estado-alvo deve estar num estado intermediário (`"GO_WITH_RISKS"` para gate, `"PARTIAL"` para estado) com risco associado em `key_risks`;  
  - `actions_required` deve conter, no mínimo, uma ação com owner e sprint alvo.

O script de G6 pode (e deve) validar parte dessas coerências de forma automática, emitindo warnings no log se houver quebra.

---

## 5. Leitura do G6 durante e após o ORR

### 5.1 Durante o ORR

Durante a reunião, o G6 pode ser usado em dois momentos:

1. **Como quadro de resumo no final**  
   - Após discutir gates, fluxos e docs, o comitê preenche/verifica:  
     - `verdict_sprint`, `verdict_epic`;  
     - `states_status`;  
     - rascunho de `key_risks` e `actions_required`;  
     - campo `summary.what_was_decided`.  

2. **Como checagem de coerência**  
   - Antes de encerrar a sessão, alguém lê o G6 e verifica se:  
     - o veredito está alinhado com os status de gates e estados;  
     - riscos e ações conversam entre si;  
     - o bundle realmente existe no path indicado.

### 5.2 Após o ORR

Após a reunião:

- pequenos ajustes de redação em `summary` e `notes` podem ser feitos, desde que não alterem o veredito;  
- `actions_required` pode ser refinado com IDs de tasks em sprints futuras;  
- `key_risks` pode ser atualizado com links para issues específicas, se a organização usar um tracker externo.

Qualquer mudança posterior **que altere o veredito** (por exemplo, de `GO_WITH_RISKS` para `GO`) deve ser tratada como **novo ORR** ou, no mínimo, anotada de forma explícita em `notes` com data e justificativa.

---

## 6. Regras de ouro para preencher `key_risks` e `actions_required`

### 6.1 Sobre `key_risks`

- Riscos devem ser **poucos e bons**, não uma lista infinita de preocupações difusas.  
- Cada risco deve ter:
  - uma **causa ou situação concreta** (não "tenho medo de bugs");  
  - impacto e likelihood qualitativos (`low/medium/high`);  
  - ligação com um ou mais estados-alvo (SA-XX);  
  - um owner claro para acompanhar.

Exemplo ruim:  
> "Sistema pode quebrar no futuro".

Exemplo aceitável:  
> "Falta de cenários E2E cobrindo casos encadeados no Debunker (impact: medium, likelihood: medium), afetando SA-02".

### 6.2 Sobre `actions_required`

- Cada ação deve ser algo que uma sprint futura consegue realmente executar (não "fazer o produto ficar perfeito").  
- Sempre que possível, linkar ações a:  
  - riscos específicos (`related_risks`);  
  - sprints alvo (por exemplo, `"due_sprint": "S2X"`);  
  - owners reais.

`actions_required` é o elo entre o veredito da S27 e o backlog das próximas sprints: se ficar vazio, a tendência é o time esquecer os riscos mapeados.

---

## 7. Integração de G6 com Cap.6 (learnings, dívidas, roadmap)

Cap.6 deve consumir diretamente o G6 para:

- listar os principais **learnings** (a partir de `key_strengths` e `summary`);  
- construir o mapa de **dívidas técnicas e de produto** (a partir de `key_risks` e `actions_required`);  
- conectar o que foi decidido na S27 com o **roadmap futuro** (via `how_it_impacts_roadmap` e `due_sprint` das ações).

Isso evita que o ORR vire um evento isolado; as informações de G6 fluem naturalmente para a narrativa de Cap.6.

---

## 8. Expectativas para o script `bin/s27_g6_orr_bundle.sh`

Embora a implementação detalhada fique em Cap.4/Bloco 4 e scripts, do ponto de vista deste bloco, espera-se que o script G6:

1. Verifique a presença de todos os scorecards G0–G5.  
2. Cheque se docs principais (Cap.1–Cap.6, guia Admin v1.1, runbooks) existem.  
3. Monte o bundle `inspectah_s27_evidence_bundle.zip`.  
4. Crie ou atualize `S27_G6_orr_summary.json` com pelo menos:
   - `sprint_id`, `epic_id`;  
   - `gates_status` (derivado dos demais scorecards);  
   - `bundle_created`, `bundle_path`;  
   - rascunho de `states_status` (pode ser inferido de G2, G4, G5);  
   - placeholder em `summary` e `notes` para preenchimento manual pós-ORR.

Com isso, na hora do ORR, o comitê não parte de um arquivo em branco: ajusta e completa um esqueleto coerente.

---

## 9. Resultado esperado deste bloco

Com o Bloco 3, a S27 passa a ter um **contrato de veredito** claramente definido:

- G6 deixa de ser uma caixa-preta;  
- veredictos são dados de forma consistente e auditável;  
- riscos e ações saem da esfera do "feeling" e viram objetos com ID, owner e sprint alvo;  
- Cap.6 e o roadmap futuro podem se apoiar diretamente em um JSON legível por humanos e máquinas.

O próximo bloco do Capítulo 5 pode, então, focar em um **roteiro operativo de ORR** (agenda, dinâmica, checklists ao vivo) e em guidelines para quem for conduzir a sessão em sprints futuras, mantendo a qualidade do processo ao longo do tempo.
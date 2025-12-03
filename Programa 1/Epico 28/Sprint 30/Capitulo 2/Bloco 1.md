# Inspectah — Sprint 30 — Capítulo 2 — Bloco 1
## Propósito dos Gates, Filosofia de Qualidade e Papel da S30 em E28

### 1. Por que este capítulo existe

O Capítulo 1 da Sprint 30 definiu o **contrato conceitual**: o fluxo de notícias‑pivô precisa sair desta sprint como o primeiro fluxo realmente operável via Console, com estados que mandam de verdade no sistema, rastreabilidade ponta a ponta e observabilidade mínima para operação 24/7.

O Capítulo 2 existe para transformar esse contrato em **malha de qualidade executável**. É aqui que o squad de Fluxos & Orquestração crava:

- quais gates a S30 terá;
- o que cada gate protege, em termos de risco e de integridade do Épico E28;
- quais evidências precisam ser produzidas para que um gate seja considerado PASS;
- como tudo isso será empacotado em scorecards e bundles de evidência, no padrão Inspectah.

Sem este capítulo, "qualidade" vira opinião. Com ele, qualidade vira **um conjunto de scripts, JSONs e artefatos que qualquer pessoa da equipe pode rodar e verificar**.

---

### 2. E28, Programa 1 e a função dos gates da Sprint 30

A Sprint 30 é a segunda de sete sprints do Épico E28 (S29–S35) dentro do Programa 1 (Data Hub & Consoles 24/7). Ela tem um papel muito específico na narrativa do épico:

- S29: provar que o modelo de Fluxo de Agentes v1 existe no código, com um Console capaz de enxergar fluxos e execuções.
- **S30**: provar que, pelo menos para notícias, esse modelo pode ser operado como sistema vivo — com templates, estados fortes, operações seguras e observabilidade útil.
- S31+ (fora desta sprint): generalizar e aprofundar esse poder para mais tipos de fluxo e integração com Debunker/Truth‑DB.

Os gates da S30 são desenhados para proteger exatamente essa transição de "fluxos existem" para "fluxos são operáveis". Cada gate corresponde a um bloco de risco que o Épico E28 não pode correr:

- risco de modelo quebrar ao evoluir para v1.5;
- risco de templates virarem YAML decorativo sem força operacional;
- risco de Console ficar bonito mas impotente;
- risco de operações perigosas (reprocessar tudo, pausar errado, loops de retry);
- risco de observabilidade insuficiente para operar 24/7;
- risco de cenário E2E existir só no papel.

O Capítulo 2 torna esses riscos **explícitos** e os mapeia para gates nomeados (G0, G1, G2, ...), cada um com scripts, scorecards e evidências próprias.

---

### 3. Filosofia de qualidade da S30 (como o squad enxerga os gates)

O squad responsável pela S30 adota algumas regras de ouro para este capítulo:

1. **Gate não é burocracia, é cerca elétrica**  
   Cada gate existe porque protege algo que, se quebrar, compromete diretamente a visão de E28. Se um gate não protege nada concreto, ele é removido ou fundido com outro; não mantemos portões vazios.

2. **Tudo que importa precisa estar automatizado**  
   Nenhuma decisão de GO/NO-GO pode depender de "olhar com carinho" para uma tela ou log no olho. Gates da S30 são sempre scripts em `bin/`, scorecards em `out/scorecards/` e evidências em `out/evidence/`.

3. **Scorecard como contrato, não como relatório enfeitado**  
   Cada gate gera exatamente um scorecard JSON com campos mínimos padronizados (`gate`, `status`, `checks`, `warnings`, `errors`, `metrics`). A pergunta "a S30 cumpriu o que prometeu?" precisa poder ser respondida olhando para esses JSONs, não só para conversas ou wikis.

4. **Bundle de evidências como caixa‑preta da sprint**  
   Ao final, a sprint produz um bundle único (`inspectah_s30_evidence_bundle.zip`) contendo todos os scorecards e evidências. Qualquer pessoa (ou auditor futuro) consegue, a partir desse zip, reconstruir o que foi testado, o que passou e o que falhou.

5. **Falhar cedo é saudável; passar gate quebrado é proibido**  
   É aceitável que um gate falhe repetidas vezes durante o desenvolvimento. O que é inaceitável é empurrar um gate vermelho para baixo do tapete. S30 só é GO se todos os gates previstos estiverem PASS com evidência sólida.

---

### 4. O recorte do Bloco 1 dentro do Capítulo 2

Este Bloco 1 foca em três coisas:

- explicar **por que** a Sprint 30 precisa de uma malha de gates forte;
- contextualizar essa malha dentro do Épico E28 e do Programa 1;
- registrar a **filosofia de qualidade** que vai guiar o desenho concreto dos gates G0–G5.

Os blocos seguintes do Capítulo 2 detalharão:

- **Bloco 2**: definição gate a gate (G0–G5), com objetivos, scripts, scorecards e pastas de evidência.
- **Bloco 3**: métricas agregadas de sucesso da S30 e como elas se ligam ao contrato de E28.
- **Bloco 4**: Definition of Done (DoD) específica da sprint, incluindo critérios para merge, empacotamento de evidências e relação com o ORR do Programa 1.

Com isso, este Bloco 1 garante que qualquer pessoa que leia o Capítulo 2 entenda não só "o que rodar", mas **por que** aqueles gates existem e **o que eles estão protegendo** em termos de visão de produto e de épico.


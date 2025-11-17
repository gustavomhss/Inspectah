### 5. Experiências obrigatórias de demo (cenários da Sprint 8)

Para considerar a Sprint 8 pronta, pelo menos **três roteiros de demo** precisam estar funcionais e reprodutíveis em ambiente local:

1. **Cenário Preço Médio:**
   - Admin cadastra uma fonte de preços para um produto X em uma cidade Y.
   - Usuário pergunta: “Qual o preço médio de X em Y?”.
   - Sistema:
     - busca os itens;
     - monta o evidence bundle;
     - chama o GPT;
     - retorna:
       - valor médio,
       - intervalo min/máx (se disponível),
       - período dos dados,
       - número de fontes / itens.
   - Usuário consegue ver as evidências usadas em 1–2 cliques.

2. **Cenário Comparação Simples (“onde está mais barato?”):**
   - Admin cadastra fontes de preços para o mesmo produto X em diferentes bairros/regiões.
   - Usuário pergunta: “Onde X está mais barato em Y?”.
   - Sistema retorna:
     - bairro/região mais barata;
     - diferença em relação à média (se fizer sentido);
     - notas de cobertura (ex.: “não há dados para tais bairros”).
   - Evidências mostram, para cada bairro usado, os preços coletados.

3. **Cenário Checagem Factual Simples:**
   - Admin cadastra fonte(s) de notícias/decisões judiciais.
   - Usuário pergunta: “Político X foi condenado na investigação/caso Y?”
   - Sistema:
     - localiza notícias/documentos relevantes;
     - monta evidence bundle;
     - GPT responde:
       - “Sim/Não/Não é possível afirmar com segurança”,
       - explicando em linguagem simples o que as fontes dizem;
       - destacando onde há consenso ou conflito.
   - Usuário consegue abrir as matérias/decisões usadas como evidência.

---

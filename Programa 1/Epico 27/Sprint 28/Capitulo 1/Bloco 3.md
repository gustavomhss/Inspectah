# Inspectah — Sprint 28
## Capítulo 1 — Bloco 3
### Domínios, personas e casos canônicos (E27.1 — CRUD & ON/OFF de Fonte)

---

#### 1.3.1 Domínios afetados diretamente pela Sprint 28

A Sprint 28 não é apenas uma melhoria técnica em “fontes” — ela toca diretamente domínios que, na prática, definem o que o Inspectah vai conseguir observar e explicar sobre o mundo.

**Domínio: Operação de Fontes & Ingestão**  
É o domínio central desta sprint. Ele abrange tudo que envolve:
- cadastrar uma fonte nova,  
- manter fontes existentes,  
- decidir quando uma fonte entra ou sai do fluxo de ingestão,  
- garantir que o estado "ligado/desligado" de uma fonte seja respeitado pelo sistema.

Este domínio é transversal: qualquer área de conteúdo ou dado que o Inspectah venha a cobrir depende de fontes bem modeladas e bem operadas.

**Domínios de conteúdo abastecidos por fontes**  
Abaixo alguns domínios que dependem diretamente de fontes bem controladas:

1. Notícias e mídia (RSS, APIs de portais, feeds de colunistas, etc.)  
   - Matérias jornalísticas, colunas de opinião, notas oficiais publicadas em veículos de imprensa.  
   - Depende fortemente de fontes `news_rss` e `http_json` configuradas corretamente.

2. Dados oficiais (estatísticas, indicadores, séries históricas)  
   - Instituições como IBGE, bancos centrais, institutos de pesquisa, ministérios.  
   - Normalmente chegam via APIs públicas, portais de dados abertos ou arquivos versionados.  
   - Erros de configuração de fonte aqui podem distorcer completamente leituras de realidade.

3. Mercado e finanças (cotações, taxas, índices)  
   - Feeds de preços de ativos, taxas de juros, câmbio, índices de bolsa, etc.  
   - Exigem atenção especial a cadência (frequência), modo (AUTO), criticidade e regras de fallback.

4. Outros domínios especializados (a serem plugados ao longo do roadmap)  
   - Podem incluir dados regulatórios, relatórios de auditoria, bases de ONGs, etc.  
   - Todos se apoiam no mesmo mecanismo: uma fonte configurada corretamente e submetida ao mesmo ciclo ON/OFF.

A Sprint 28 não precisa conhecer o detalhe de cada domínio de conteúdo, mas precisa garantir que **todos** eles terão em `Source` um modelo confiável e operável.

---

#### 1.3.2 Personas principais e suas necessidades

Para a Sprint 28, três personas são centrais. Elas são usadas como lentes para definir o que é aceitável como experiência de operação.

**Persona 1 — Operador de Ingestão (Source Operator)**

Perfil:
- Pessoa responsável por manter o fluxo de ingestão rodando de forma saudável.  
- Não precisa ser desenvolvedor; pode ser um analista técnico ou operador de dados.

Necessidades concretas nesta sprint:
- Cadastrar novas fontes sem precisar abrir um editor de texto ou mexer em arquivos de configuração.  
- Ajustar parâmetros de fontes existentes (URL, cadência, domínio, criticidade) de forma segura e auditável.  
- Ligar e desligar fontes de maneira previsível — "cliquei em desativar, essa fonte parou de ser ingerida".  
- Ter clareza de quais fontes são críticas e em que domínios atuam.

**Persona 2 — SRE / On-call de Dados**

Perfil:
- Responsável por responder a incidentes operacionais: picos de erro na ingestão, comportamentos anômalos, aumento de latência, etc.

Necessidades concretas nesta sprint:
- Ter um lugar único (Console de Fontes v2) para tomar decisões rápidas:  
  - identificar fontes problemáticas,  
  - desativar fontes temporariamente,  
  - reativar após mitigação.  
- Confiar que a ação tomada no console realmente se traduz em mudança de comportamento do sistema (Ingestão 2.0).  
- Evitar depender de scripts e comandos diretos em banco em momentos de pressão.

**Persona 3 — Analista de Casos / Investigador (secundária na S28)**

Perfil:
- Profissional que analisa casos, narrativas e disputas de informação.  
- Usa o Inspectah para entender "de onde vieram" certos dados ou afirmações.

Necessidades concretas nesta sprint (indiretas):
- Mesmo que a S28 não implemente ainda o Case Cockpit v1, ela deve preparar o terreno para que, no futuro, seja simples ver:  
  - de quais fontes um caso dependeu,  
  - em que estado essas fontes estavam,  
  - se tiveram períodos desativados ou de manutenção.

A Sprint 28 foca diretamente em Operador e SRE, mas precisa preservar rastros e consistência para que o Analista de Casos consiga, nas próximas sprints, reconstruir essas histórias com segurança.

---

#### 1.3.3 Casos canônicos detalhados

Os casos canônicos desta sprint são usados como “histórias exemplares” que orientam o design de modelo, API, UI e testes.

##### Caso A — Cadastrar uma nova fonte de notícias RSS

Contexto:
- O time de operação precisa adicionar o feed RSS de um novo veículo de notícias que será usado em análises de política.

Fluxo esperado:
1. O Operador acessa o Console de Fontes v2.  
2. Clica em “Nova Fonte” e escolhe o tipo `news_rss`.  
3. Preenche os campos:
   - Nome da fonte,  
   - Descrição,  
   - URL do feed RSS,  
   - Domínio (ex.: "política"),  
   - Categoria (ex.: "news"),  
   - Criticidade (ex.: "HIGH" se o veículo for muito relevante),  
   - Modo (`AUTO`),  
   - Cadência (intervalo de ingestão).
4. O formulário valida inline e na API (URLs válidas, campos obrigatórios, combinações permitidas por tipo).  
5. Ao salvar, a fonte aparece na lista com estado `ACTIVE` (ou `DISABLED`, conforme política escolhida para novas fontes).  
6. A partir daí, a Ingestão 2.0 começa a criar `IngestionRun` para essa fonte conforme a cadência definida.  
7. Todo esse fluxo acontece **sem** necessidade de editar configs em arquivos, mexer em banco ou rodar scripts.

Critérios de sucesso para este caso:
- Nenhum campo crítico fica "escondido" da UI.  
- Erros de configuração são capturados com mensagens claras, antes de a fonte entrar em produção.  
- A fonte nova começa a ser ingerida (ou é claramente marcada como pendente de ativação, se a política for outra).

##### Caso B — Fonte quebrada ou spam, precisa ser desligada rapidamente

Contexto:
- Uma fonte começa a gerar volume enorme de erros ou conteúdo inaceitável (spam, conteúdo corrompido).

Fluxo esperado:
1. SRE recebe alerta (via observabilidade da ingestão, fora do escopo direto da S28).  
2. Abre o Console de Fontes v2 e filtra por domínio/categoria para encontrar a fonte problemática.  
3. Vê, na lista, sinais visuais de que a fonte tem problemas (ex.: último `IngestionRun` com erro, embora isso seja refinado nas sprints futuras de E27.2/E27.3).  
4. Clica em “Desativar” na ação da fonte, adicionando opcionalmente um motivo (`state_reason`).  
5. O estado no console muda para `DISABLED`.  
6. A Ingestão 2.0 para de agendar ingestões para essa fonte — validado por logs e ausência de novos `IngestionRun`.  
7. O SRE pode focar em mitigar o incidente sem medo de que a fonte volte a gerar ruído sozinha.

Critérios de sucesso:
- O tempo entre clicar em "Desativar" e ver o efeito na ingestão é curto e previsível (dentro da cadência do scheduler).  
- Não há necessidade de "complementar" o desligamento com comandos laterais.  
- Registro de motivo e timestamp da desativação é persistido para uso futuro (E27.3/E31).

##### Caso C — Manutenção planejada em fonte crítica

Contexto:
- Um fornecedor de dados macroeconômicos informará uma janela de manutenção em que o endpoint de API ficará instável.

Fluxo esperado:
1. Operador identifica a fonte crítica que será impactada.  
2. Agenda uma janela de desativação manual: pouco antes do início da manutenção, acessa o Console de Fontes v2 e desativa a fonte, registrando "manutenção programada" em `state_reason`.  
3. Durante a janela, Ingestão 2.0 não tenta consumir dados dessa fonte.  
4. Após a manutenção, o Operador reativa a fonte.  
5. A Ingestão 2.0 retoma o fluxo normalmente, sem necessidade de reconfigurar ou recriar a fonte.

Critérios de sucesso:
- Processo de desativar/reativar é suficientemente simples para que esse tipo de manutenção seja rotina, não exceção.  
- Futuras Sprints (E27.2/E27.3) poderão usar os timestamps de `state_changed_at` e `state_reason` para explicar lacunas de dados em análises.

##### Caso D — Corrigir uma fonte antiga sem quebrar ingestão

Contexto:
- Uma fonte configurada há meses apresenta problemas sutis de configuração (URL errada, cadência muito agressiva, domínio/categoria imprecisos).

Fluxo esperado:
1. Operador encontra a fonte no Console de Fontes v2.  
2. Acessa a tela de detalhes/edição e ajusta os campos necessários.  
3. O sistema aplica as invariantes de domínio:  
   - impede alterações proibidas (ex.: reativar fonte `DEPRECATED`),  
   - valida combinações inválidas (ex.: tipo de fonte incompatível com a config informada).  
4. Ao salvar, a fonte passa a operar com a nova configuração.  
5. Ingestão 2.0 lê a nova config sem necessidade de reboots manuais ou procedimentos obscuros.

Critérios de sucesso:
- Operador consegue entender o que pode e o que não pode ser alterado.  
- O sistema não deixa o usuário colocar a fonte em estado ilegal.  
- Logs e observabilidade confirmam a mudança de comportamento pós-ajuste.

---

#### 1.3.4 Como esses casos influenciam o desenho da sprint

Esses casos canônicos não são apenas exemplos narrativos: eles funcionam como **checklist de realidade** para todas as decisões da Sprint 28:

- Sempre que surgir uma dúvida de modelagem ou UX, a pergunta é:  
  "Esse desenho facilita ou atrapalha A, B, C ou D?".

- Os casos A–D se tornam cenários explícitos de teste:  
  - testes de API que simulam os payloads e as transições envolvidas,  
  - testes de integração (para ON/OFF × Ingestão 2.0),  
  - scripts de demo do Gate G6.

- Qualquer funcionalidade ou detalhe de implementação que não contribua para viabilizar esses casos é candidato natural a:  
  - ser cortado da Sprint 28,  
  - ir para o backlog de E27.2/E27.3/E29–E32.

Assim, o Bloco 3 fecha a visão de **quem** é afetado, **em quais domínios** e **em quais situações típicas**, garantindo que a Sprint 28 se mantenha conectada ao mundo real de operação e não vire apenas um exercício de refatoração abstrata.


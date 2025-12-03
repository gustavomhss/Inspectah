# Inspectah — Sprint 31 (E28-S3)
## Capítulo 1 — Bloco 2: Problemas Centrais & Objetivos de Validação

### 2.1. Problema 1 — Modelo mental quebrado entre fonte, provider e perfil de ingestão

Estado atual
O Console de Fontes e parte do código ainda operam com a lógica antiga de “fonte = site/endpoint específico” (RSS, API, scraper). O operador pensa em fontes individuais, liga/desliga uma a uma, e monitora comportamento quase no nível de “cada domínio é um planeta”. No mundo provider-first essa metáfora não escala: um único provider já representa milhares de veículos, e o operador precisa raciocinar em termos de perfis e recortes, não em termos de site isolado.

Consequências práticas
– Dificuldade para ampliar cobertura geográfica/temática sem explosão de cadastros e complexidade.
– Visão distorcida do que realmente está alimentando o sistema: o que parece ser “G1” ou “Folha” é, na prática, parte de um fluxo agregador maior, mas isso não aparece de forma clara.
– Toda decisão de priorização (por exemplo, focar política BR e sacrificar entretenimento) vira microgestão em vez de ajuste de perfis.

Objetivo de validação
Ao final da S31, o operador deve conseguir responder, olhando apenas para o Console de Fontes e para os painéis de ingestão:
– quais providers estão ativos;
– quais perfis de ingestão existem e o que cada um deles significa em termos de país/idioma/tema;
– que parte do mundo de notícias e social está entrando em função de cada perfil.
Se isso ainda exigir “memória tribal”, a sprint falhou nesse problema.

### 2.2. Problema 2 — Proveniência e deduplicação frágeis em cenário multi-provider

Estado atual
O design conceitual já prevê ContentItem como unidade canônica, com proveniência e dedupe, mas o cenário real pós-providers é mais complicado do que a fase pré-E28. A mesma notícia pode entrar por dois providers diferentes, por uma fonte direta legada ou por um feed especial de uma agência. Sem regras claras e implementadas de dedupe e de prioridade de origem, o sistema pode gerar:
– múltiplos ContentItems para o mesmo fato;
– contagem inflada de volume;
– trilhas de origem confusas (quem originou vs quem apenas replicou).

Consequências práticas
– ClaimGraph recebe duplicidades e ruído, “engordando” clusters de narrativa artificialmente.
– Sinais de narrativa (mentiras em circulação, campo de batalha, cherry-picking) ficam enviesados, porque o sistema conta várias vezes o mesmo conteúdo.
– Truth-DB e FactBlocks podem acabar se apoiando em evidências redundantes, dificultando explicabilidade.

Objetivo de validação
Ao final da S31, para um domínio piloto (por exemplo, BR/PT/política + economia), o time precisa ser capaz de:
– mostrar que a mesma notícia, se chegar por múltiplos caminhos, gera apenas um ContentItem canônico;
– justificar qual proveniência foi escolhida como principal e como as outras foram agregadas como metadados;
– rastrear, a partir de um ContentItem, todos os caminhos de ingestão que poderiam tê-lo produzido.
Se ainda houver duplicidade sem explicação ou caminhos de origem invisíveis, o problema não foi resolvido.

### 2.3. Problema 3 — Budgets, quotas e custo não existem como primeiros cidadãos

Estado atual
As discussões de custo por região/tema/providers estão maduras no plano, mas quase ausentes na aplicação. Hoje, o sistema até consegue limitar ingestão por agendamento ou por volume bruto, mas não há um modelo nativo de:
– perfis de ingestão com envelope de chamadas por dia/mês;
– visão de consumo por provider/profile;
– feedback rápido para o operador sobre “para onde o dinheiro está indo”.

Consequências práticas
– Qualquer tentativa de ingestão mais agressiva (exemplo Latam + EUA + UE em múltiplos temas) vira um salto de fé em cima da fatura do provider.
– É difícil fazer trade-offs inteligentes (por exemplo, reduzir entretenimento para salvar política/saúde em período de crise).
– Não existe um laço de feedback entre o planejamento de ingestão (no roadmap) e o comportamento real da plataforma.

Objetivo de validação
Ao final da S31, para os perfis-piloto, o time precisa conseguir:
– visualizar, em painéis internos, quantas chamadas, quantos itens e quantos erros cada profile está gerando em determinado período;
– definir e alterar limites por perfil (envelope diário/mensal) sem alterar código;
– simular e observar o efeito de ligar/desligar perfis em termos de custo aproximado e volume.
Se o único jeito de responder “quanto gastamos nesse profile?” for abrir logs crus ou planilhas externas, o sistema ainda não está no ponto.

### 2.4. Problema 4 — Legado pendurado, não encaixado

Estado atual
S26–S30 criaram uma base saudável: Console de Fontes, ingestão 2.0, jobs em fila/worker, observabilidade, evidências e gates. Mas a entrada dos omni-providers ainda foi feita em modo paralelo, não completamente integrada. O que vemos hoje é um cenário em que:
– fontes diretas e scrapers continuam existindo como se fossem o caminho “principal”;
– providers entram como “mais uma rota” em vez de se tornarem o eixo central;
– scripts de gates e scorecards não distinguem claramente o que é legado e o que é provider-first.

Consequências práticas
– A equipe fica receosa de desligar qualquer fluxo legado, por medo de quebrar ingestão em cascata.
– Novas features de ingestão acabam copiando padrões antigos, em vez de usar o modelo provider-first.
– Evidências e scorecards perdem valor explicativo, porque não deixam claro quais fluxos estão realmente sendo auditados.

Objetivo de validação
Ao final da S31, queremos que:
– exista um mapa claro de convivência entre providers e fontes diretas (quais classes de fontes são exceção e por quê);
– gates e scorecards da sprint distingam e validem explicitamente o fluxo provider-first para os perfis-piloto;
– haja uma trilha de migração acordada, ainda que parcial, apontando quais fontes diretas serão aposentadas em sprints futuras.
Se o legado continuar parecendo “o caminho normal” e providers continuarem aparecendo como apêndice, a tese da sprint não se cumpriu.

### 2.5. Problema 5 — Entrada no ClaimGraph não conversa ainda com perfis de ingestão

Estado atual
Programa 2 define um runtime de agentes (Intérprete, Classificador, Analistas, Debunkers) que depende de recortes claros de ingestão para operar com eficiência. Porém, o pipeline entre “perfil de ingestão” e “pipeline de interpretação/sinais” ainda não está amarrado. O que entra no ClaimGraph hoje é mais fruto de filtros genéricos por país/tema do que de uma relação explícita com os perfis que geram esse conteúdo.

Consequências práticas
– É difícil saber, para um determinado conjunto de claims, “quais perfis de ingestão estão alimentando isso”.
– Experimentar novas combinações de fontes (por exemplo, misturar Latam ES com BR PT em certos temas) vira tentativa e erro, sem rastro claro.
– O time de Programas 2–3 não consegue tratar ajustes de ingestão como mudanças de experimento: tudo parece ruído.

Objetivo de validação
Ao final da S31, para um domínio piloto (por exemplo, política BR), precisamos garantir que:
– exista um mapeamento explícito de quais perfis de ingestão alimentam quais pipelines de interpretação;
– seja possível responder “este bloco de claims veio primordialmente destes perfis”, sem investigação manual;
– qualquer mudança relevante de perfil (ligar/desligar, alterar filtros) passe a ser rastreável como mudança de experimento.
Se a origem dos claims continuar opaca, Programas 2–3 e o futuro sistema de experimentação vão operar no escuro.

### 2.6. Como saber se a Sprint 31 realmente resolveu esses problemas

A S31 não é apenas sobre “entregar código”; ela é sobre **reduzir incerteza estruturante** na camada de ingestão. Os problemas acima convergem em um teste simples de sanidade:

– Se, após a sprint, for possível ligar um pequeno conjunto de perfis de ingestão de providers, ver conteúdo real fluindo para o Data Hub, observar volumes/custos/erros por perfil, enxergar a proveniência de cada ContentItem, e mapear isso até o ClaimGraph em um domínio piloto, sem precisar de explicações orais ou gambiarras, então a tese da S31 foi validada.
– Se, ao contrário, para entender “de onde veio essa notícia e por qual profile” ainda for necessário caçar logs soltos, abrir o código e perguntar para quem implementou, a sprint terá resolvido tarefas, mas não terá resolvido o problema.

Este bloco 2 fixa portanto o alvo real: S31 é a sprint que transforma ingestão provider-first de promessa em sistema minimamente fechado, auditável e governável em um domínio piloto. As sprints seguintes podem então ampliar a cobertura geográfica e temática sem voltar a discutir fundações.


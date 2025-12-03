# Inspectah — Sprint 30 — Capítulo 1 — Bloco 4
## Escopo Negativo, Riscos, Dependências e Cenários-Núcleo

### 1. Escopo Negativo Deliberado (o que S30 NÃO vai tentar resolver)

Para manter a Sprint 30 focada e com qualidade mínima de 9.9/10, o squad definiu explicitamente o que fica **fora** do escopo, mesmo que pareça tentador ou “quase de graça”. Isso evita que o épico E28 se dilua e protege o objetivo central: tornar o fluxo de notícias o primeiro fluxo verdadeiramente operável via Console.

1.1. Editor visual avançado de fluxos
S30 não vai criar um editor gráfico completo de fluxos (arrastar e soltar, desenho livre de DAG, múltiplas layers visuais). Qualquer representação visual será **subordinada** ao modelo canônico de fluxo e pode continuar simples (diagramas derivados da estrutura, não o contrário). O foco é: semântica forte, operações confiáveis, rastreabilidade e observabilidade.

1.2. Sistema de versionamento avançado de pipelines
Recursos como canary rollout de versões de fluxo, A/B experiment de topologias concorrentes, pesos dinâmicos por versão ou orquestrações complexas de migração ficam fora da Sprint 30. Aqui, a regra é: para um tipo de entrada de notícias, existe **um** fluxo ativo, zero ou mais fluxos em teste com regras simples, e o roteamento é determinístico e auditável.

1.3. Optimizações profundas de performance de agentes
S30 não vai atacar otimizações internas de agentes (prompt engineering pesado, caching agressivo de LLM, tuning fino de heurísticas de comitê). Agentes são tratados como caixas pretas com contratos claros; o que importa é que o fluxo saiba orquestrá-los, registrá-los e expô-los ao operador.

1.4. Suporte full para todos os tipos de fluxo do Inspectah
O alvo da Sprint 30 é o **fluxo de notícias‑pivô**. Outros tipos de fluxo (contestação on-chain, ingestão de séries temporais, eventos de preço, etc.) podem receber benefícios colaterais da infraestrutura criada, mas não são critério de sucesso. Se o fluxo de notícias não estiver redondo, a sprint é NO-GO mesmo que outros fluxos tenham ganho algo.

1.5. Explicabilidade rica para usuário final
Narrativas detalhadas, visualizações sofisticadas da árvore de raciocínio do agente, painéis de storytelling para usuário final de produto ficam para sprints posteriores. Em S30, a explicabilidade é voltada ao operador: ele precisa enxergar claramente a jornada da notícia pelo fluxo, não fazer uma apresentação pública sobre ela.

1.6. Re-design amplo do Console Admin
O Console de Fluxos será evoluído dentro das linhas do Console/Admin já existentes. S30 não redesenha todo o Console Admin do Inspectah; ela aprofunda, fortalece e torna operável o módulo de fluxos.

---

### 2. Riscos Principais e Estratégia de Contenção

2.1. Risco de over-engineering de orquestração
O perigo óbvio é tentar construir, em uma sprint, um “orquestrador universal de tudo”, com features dignas de plataformas maduras de workflow. Isso pulverizaria o esforço e entregaria algo inacabado em todas as frentes.

Estratégia: restringir o foco a um fluxo‑pivô de notícias, com regras simples mas rígidas. Tudo que exigir generalização exagerada (multi‑tenant extremo, dezenas de tipos de fluxo, estratégias sofisticadas de rollout) é adiado conscientemente e anotado como dívida de épico.

2.2. Risco de acoplamento com detalhes de IA
É sedutor aproveitar a sprint para melhorar prompts, lógica de decisão dos agentes, estratégia de votação de comitês, etc. Isso arrasta a S30 para problemas de Programa 2 (Agentes & Comités), não de Programa 1.

Estratégia: tratar agentes como serviços com contrato bem definido. S30 cuida de **como** fluxos chamam agentes, registram o que eles fizeram e expõem isso ao operador; não do conteúdo interno da “mente” dos agentes.

2.3. Risco de UX tentar virar IDE de fluxo
Outra tentação é fazer o Console virar uma IDE visual de fluxos, com nível de detalhe de ferramenta de desenvolvedor. Isso consome banda de UI sem fortalecer o contrato operacional.

Estratégia: priorizar interações que movem o ponteiro da operação (criar fluxo a partir de template, mudar estado, trocar agente, pausar, retomar, ver execuções, ler métricas) com UX clara, simples e confiável. Qualquer feature de UI que não aumente o poder de operação do fluxo de notícias é candidata a corte.

2.4. Risco de reprocessamento mal controlado
Reprocessar notícias que passaram por um fluxo é uma necessidade real, mas se for feito sem guard‑rails pode gerar loops, duplicidade de registros e estouro de custos de LLM.

Estratégia: na S30, reprocessamento deve nascer com escopo controlado (por faixa de IDs, janelas de tempo, limites de volume) e com trilha de auditoria. A ideia é “reprocessamento cirúrgico”, não “aperta um botão e reprocessa tudo que já existiu”.

2.5. Risco de dependência oculta em engenharia
Se, ao fim da sprint, ainda houver caminhos “secretos” em que só um desenvolvedor sabe como ativar ou corrigir o fluxo de notícias, o objetivo central falha.

Estratégia: sempre que surgir um atalho desse tipo durante a implementação, ele deve ser explicitamente registrado e puxado, ainda na S30, para dentro de uma operação oficial de Console, ou formalizado como dívida crítica do épico.

---

### 3. Dependências e Alinhamentos Críticos

3.1. Dependência com ingestão e tipificação de notícias
Para o fluxo de notícias ser operável, ele precisa receber eventos de forma consistente a partir da camada de ingestão. Isso implica:

- existência de uma tipificação mínima (por exemplo, `noticia_texto`, possivelmente com subtipos: política, economia, etc.);
- contratos claros entre ingestão e orquestração (como o fluxo é escolhido, quais campos obrigatórios chegam ao fluxo, como erros de ingestão são tratados).

S30 assume que a ingestão já consegue classificar e encaminhar notícias para fluxos de forma básica; a sprint reforça e formaliza essa ligação para o caso‑pivô.

3.2. Dependência com o modelo de Fluxo de Agentes v1 (S29)
Toda a semântica que S30 quer tornar operacional depende do modelo consolidado em S29: entidades, estados, relações entre fluxo, etapas, nós/ agentes e execuções. Qualquer ajuste necessário no modelo deve ser compatível retroativamente com o que já foi estabelecido em S29, ou claramente migrado.

3.3. Alinhamento com futura camada de Debunker (Épico E29)
O fluxo de notícias que nasce aqui será usado como trilho lógico para o Debunker v1. Não faz sentido construir um fluxo de notícias que ignora pontos de decisão, coleta de evidências ou ramos de contestação que o Debunker vai precisar.

Consequência: S30 precisa, no mínimo, reservar pontos de acoplamento claros no fluxo (ex.: etapas em que o debunker entra, checkpoints de evidência, estados de decisão) mesmo que a lógica interna do Debunker ainda esteja em outro épico.

3.4. Alinhamento com observabilidade global do Inspectah
As métricas de fluxo de notícias não podem ser inventadas no vácuo. Elas devem se alinhar à estratégia global de observabilidade: naming, agregação, formato de export, integração com painéis existentes. S30 está autorizada a introduzir novas métricas, mas deve fazê-lo dentro dessa gramática.

---

### 4. Personas e Cenários-Núcleo que Guiam S30

4.1. Personas

- Arquiteto de Fluxos de Agentes: define topologias, templates e políticas de roteamento para fluxos de notícias.
- Operador de Fluxos: cuida da operação diária, olha o console, mexe em estados, acompanha métricas, reage a incidentes.
- SRE / Observability: garante que métricas de fluxo de notícias existem, são confiáveis e alimentam painéis e alertas.
- Debunker / Analista: consome, direta ou indiretamente, a saída do fluxo de notícias e faz verificações manual/assistidas.

4.2. Cenário-Núcleo 1 — “Promover um novo fluxo de notícias com segurança”

Um Arquiteto cria um novo fluxo a partir do template oficial de notícias, parametriza agentes, marca como `em_teste`. O Operador direciona uma fração pequena do tráfego para esse fluxo, monitora métricas e rastreabilidade por alguns dias, e depois promove o fluxo a `ativo` com um clique no Console, pausando o fluxo antigo. Não há alteração de código, nem edição manual de configuração em arquivos.

4.3. Cenário-Núcleo 2 — “Pausar um fluxo de notícias que está falhando”

O Operador percebe, via painel de métricas de fluxo, que a taxa de erro do fluxo de notícias atual explodiu. Ele abre o Console de Fluxos, pausa o fluxo problemático, verifica que novos eventos passaram a ir para um fluxo alternativo ou para um fallback claro, investiga a causa, coordena correção junto ao Arquiteto e só retoma o fluxo quando as métricas voltam ao normal.

4.4. Cenário-Núcleo 3 — “Trocar um classificador ruim por outro melhor”

Dados internos mostram que o classificador de tipo de notícia está cometendo erros grosseiros. O Arquiteto, pelo Console, substitui o agente da etapa de classificação por uma versão mais nova, sem alterar uma linha de código. O Operador acompanha métricas antes e depois da troca, validando que a mudança melhorou o fluxo.

---

### 5. Narrativa de Sucesso da S30

Se tudo der certo, a fotografia ao final da Sprint 30 é mais ou menos esta:

- Há um **Fluxo_Noticias_Geral_v1** definido como template oficial, versionado e documentado.
- Pelo menos um fluxo de notícias em produção foi criado a partir desse template e está marcado como `ativo` para um tipo de entrada bem definido.
- O Console de Fluxos mostra claramente esse fluxo, seus estados e suas execuções, e o squad o utiliza como cockpit real no dia a dia.
- A mudança de estado `em_teste → ativo → pausado` é um gesto de Console com efeito imediato e verificável.
- Dado o ID de qualquer notícia, o operador consegue reconstruir a jornada dela pelo fluxo‑pivô sem abrir logs crus ou pedir ajuda para um engenheiro.
- Métricas específicas de fluxo de notícias alimentam um painel que o squad consulta de forma natural para saber se “está tudo bem”.

Quando essa narrativa for verdade — e não apenas plausível — a S30 terá cumprido seu papel dentro do E28: provar, com um caso concreto, que o modelo de Fluxo de Agentes Configurável não é só um desenho elegante, mas uma peça operacional central do Inspectah 24/7.


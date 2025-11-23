Sprint 19 – Timeline e Raio-X do Sistema de Blocos

1. Visão geral da sprint

A Sprint 19 existe para transformar o Inspectah de um sistema que “sabe a verdade” em um sistema que também “explica como chegou lá” de forma visual, navegável e auditável. Até aqui, a Truth-DB, o Sistema de Blocos, o Debunker, os Comitês e as Âncoras já conseguem chegar a vereditos robustos, mas grande parte dessa inteligência continua escondida em estruturas internas, scorecards e evidências em bruto.

A S17 entrega resposta clara para o usuário final. A S18 entrega um Console de Admin que mostra fontes, casos/temas e saúde geral da operação. A S19 é a peça que fecha esse triângulo: oferece uma visão de Timeline e um Raio-X de Caso que permitem reconstruir, em linguagem humana, a história de cada caso dentro do Sistema de Blocos – que eventos aconteceram, em que ordem, com quais fontes, como o Debunker e os Comitês reagiram e qual é o estado das Âncoras. Tudo isso em modo leitura, sem mutação de estado.

Ao final da Sprint 19, o Inspectah deve deixar de ser uma “caixa-preta sofisticada” e passar a se comportar como uma “caixa de vidro”: ainda complexa por dentro, mas com uma narrativa clara e rastreável para cada caso importante.

2. Problema que a Sprint 19 resolve

Mesmo com o Console de Admin da S18, o operador hoje enxerga basicamente um snapshot: lista de fontes, lista de casos e uma visão agregada de health. Quando acontece algo sério – um aumento repentino de risco, uma contestação sensível, uma âncora falhando em sequência, uma fonte-chave degradando – falta a camada que responde às perguntas mais incômodas:

• O que exatamente aconteceu com este caso ao longo do tempo?  
• Quais eventos do Sistema de Blocos foram realmente relevantes para chegar ao estado atual?  
• Que evidências e fontes pesaram mais nas decisões?  
• Como o Debunker avaliou e reavaliou o risco ao longo da linha do tempo?  
• Como os Comitês votaram, onde divergiram e quando convergiram para um veredito?  
• Em que momento as Âncoras começaram a falhar e como isso afetou a confiança?

Sem uma timeline e um raio-X dedicados, o operador, o curador ou o investigador acabam recorrendo a JSON cru, arquivos de evidência, scorecards e logs para tentar reconstruir a história. Isso consome tempo, aumenta a chance de erro humano, dificulta comunicação com stakeholders e deixa o Inspectah vulnerável a críticas do tipo “eu não confio nesse veredito porque não entendo o que aconteceu aqui dentro”.

A Sprint 19 resolve esse buraco de auditabilidade e explicabilidade: ela coloca a trajetória de cada caso em primeiro plano, transformando o histórico de blocos e eventos em uma narrativa visual coerente.

3. Objetivo macro da Sprint 19

O objetivo central da S19 é permitir que um operador, curador ou investigador pegue um caso qualquer que já aparece no Console de Admin (S18), clique em uma rota de diagnóstico e, em poucos minutos, consiga:

• Reconstruir a linha do tempo daquele caso, vendo os eventos ordenados de forma clara.  
• Entender como o estado do caso evoluiu dentro do Sistema de Blocos (criação de blocos, sub-blocos, atualizações, resoluções).  
• Ver como o Debunker avaliou o caso em momentos-chave, quais flags e níveis de risco apareceram e por quê.  
• Ver como os Comitês se posicionaram, onde houve consenso e onde houve divergência.  
• Visualizar o estado atual e o histórico das Âncoras relevantes, entendendo o impacto na confiança.  
• Chegar rapidamente nas evidências principais associadas ao caso, sem ter que abrir JSON manualmente.

Ao fim da sprint, deve ser possível pegar um caso real e, usando apenas a UI de Timeline + Raio-X, explicar para uma terceira pessoa: que tipo de caso é, que história ele contou ao longo do tempo, por que o nível de risco atual faz sentido e quais são as principais incertezas ainda em aberto.

4. Perfis de usuário atendidos

A S19 é projetada para quatro perfis internos principais, todos trabalhando em modo leitura.

Operador de plataforma: precisa monitorar casos ativos, investigar alertas, checar se o sistema está se comportando conforme o esperado e responder perguntas internas como “por que esse caso está marcado como risco alto?” ou “por que este caso foi resolvido como verdadeiro/falso agora?”. A Timeline e o Raio-X viram suas primeiras ferramentas de diagnóstico.

Curador ou Analista de conteúdo: quer avaliar se o Inspectah está julgando bem os casos mais sensíveis. Precisa ver se as fontes consideradas fazem sentido, se há evidências ignoradas, se o Debunker pesou os fatores corretos e se decisões de Comitês alinham com critérios de qualidade. A UI de Raio-X deve fornecer um resumo inteligível sem exigir leitura de scorecards técnicos.

Investigador / Forense: olha para um subconjunto de casos com lupa, muitas vezes após incidentes, contestação crítica ou suspeita de manipulação. Precisa reconstruir a sequência de eventos, identificar pontos de falha, descobrir quando uma âncora começou a falhar, entender como isso se refletiu nas decisões internas e separar bug de mau uso ou de caso-limite do modelo. A Sprint 19 precisa dar a esse perfil uma visão suficientemente profunda sem exigir acesso a infra.

Product Owner / Founder: usa a timeline e o raio-X como ferramentas de produto e narrativa. Mostra para parceiros e stakeholders como o Inspectah chega aos vereditos, identifica padrões recorrentes de risco, enxerga gargalos do motor atual e decide próximos investimentos de roadmap (mais dados? mais comitês? reforço nas âncoras?). Para esse perfil, a S19 é também um artefato de “prova de maturidade” do sistema.

Em todos os casos, o recorte é leitura: ninguém altera blocos, estados, vereditos ou parâmetros a partir da interface criada nesta sprint.

5. Recorte funcional da sprint

A Sprint 19 foca em três blocos funcionais, bem delimitados.

Timeline de Caso/Tema: a partir de um caso listável no Console de Admin (S18), o usuário deve conseguir abrir uma visão de linha do tempo que mostre eventos relevantes em ordem cronológica. Exemplos de eventos: ingestão de novas evidências, criação/atualização de blocos e sub-blocos, mudanças de status do caso, resultados importantes do Debunker, decisões ou revisões de Comitês, alterações significativas de risco, ações de ancoragem (sucesso/falha), abertura e encerramento de contestação. A timeline precisa ser paginável ou virtualizada (para casos com muitos eventos), permitir filtros mínimos por tipo de evento e período, e trazer um sinal visual de severidade/risco ao longo do tempo.

Raio-X de Caso: a partir da timeline ou direto da listagem de casos, o usuário abre uma tela de diagnóstico profundo organizada em seções. Uma seção de “Resumo do Caso” com os dados principais e o estado atual no Sistema de Blocos. Uma seção “Debunker” com avaliação, flags, racional de risco e, quando possível, explicações de por que certas evidências tiveram peso maior. Uma seção “Comitês” mostrando votos, momentos de divergência e como se chegou à decisão final. Uma seção “Âncoras” mostrando quais âncoras existem, quais estão saudáveis, quais estão degradadas e como isso afeta a confiança. Por fim, uma seção “Evidências principais” que oferece ponte para os artefatos já estruturados na Truth-DB, sem exigir navegação manual em arquivos.

Integração com Console de Admin e Truth-DB: a S19 não inventa um novo universo de dados. A timeline e o raio-X devem se basear nos casos, blocos, snapshots e estruturas já consolidadas pelas sprints anteriores (S10, S12, S17, S18), adicionando apenas o que for estritamente necessário em termos de endpoints e estruturas auxiliares. A navegação deve partir de casos reais exibidos na S18, respeitar as mesmas regras de acesso e reutilizar componentes de UI sempre que fizer sentido.

6. Escopo explicitamente fora da Sprint 19

Para manter a sprint enxuta e terminável, alguns pontos ficam explicitamente fora de escopo.

A S19 não adiciona nenhuma capacidade de mutação via UI: nada de editar blocos, sub-blocos, evidências, vereditos ou parâmetros de Debunker/Comitês. Não há painel de tuning de thresholds, pesos ou regras. Qualquer ajuste desse tipo continua sendo tratado via mecanismos administrativos ou por sprints futuras.

Também ficam de fora: um modo público de timeline para o usuário final (S17 continua sendo a interface primária do usuário comum), dashboards agregados de BI sobre múltiplos casos, refatorações profundas do modelo de dados da Truth-DB ou do pipeline de ingestão e qualquer reconstrução estrutural dos motores de Debunker/Comitês. A S19 consome o que existe, expõe melhor, adiciona o mínimo necessário para contar bem a história de um caso.

7. Dependências e pré-condições

A Sprint 19 assume um conjunto de pilares mínimos já atendidos pelas sprints anteriores:

• Truth-DB e Sistema de Blocos em operação, com representação fiel de blocos, sub-blocos, componentes e estados de casos.  
• Ingestão contínua e estruturação de casos e evidências conforme desenhado na S12.  
• Debunker funcionando com regras claras o suficiente para expor avaliações e níveis de risco de forma estável.  
• Comitês operacionais, com registros minimamente estruturados de decisões e, idealmente, de revisões.  
• Âncoras registradas e com noções de sucesso/falha rastreáveis.  
• Console de Admin da S18 ativo, com listagem confiável de fontes, casos/temas e visão agregada de health.

Se durante a S19 forem identificados pequenos gaps de dados (por exemplo, ausência de um endpoint que consolide eventos em ordem temporal, ou falta de campos para identificar claramente um tipo de evento), esses ajustes pontuais podem entrar na sprint, desde que não impliquem reescrever o motor central ou quebrar contratos já consolidados. Qualquer necessidade de refactor estrutural deve ser explicitamente registrada como débito técnico para sprints futuras.

8. Métricas de sucesso e narrativa de “história bem contada”

Mesmo antes de detalhar os gates no Capítulo 2, o Capítulo 1 define quando a S19 pode ser considerada bem-sucedida sob a ótica humana.

Para um operador, sucesso significa pegar um caso da lista, abrir a visão de Timeline + Raio-X e, em dois ou três minutos, conseguir explicar para alguém de fora: que caso é esse, que eventos relevantes aconteceram, qual é o estado atual, por que o risco está no nível atual e quais são as principais incertezas. Se, para isso, o operador precisar abrir JSON em bruto ou scorecards técnicos, a S19 falhou em seu objetivo principal.

Para um investigador, sucesso significa que, diante de uma contestação, incidente ou suspeita de bug, a primeira reação passa a ser “abre o Raio-X desse caso” em vez de “abre os logs do serviço tal”. A timeline precisa ser suficiente para localizar o ponto em que algo começou a dar errado, entender como o problema se propagou e ver que sinais o sistema deu no caminho (Debunker, Comitês, Âncoras, risco, flags).

Finalmente, para o PO/fundador, sucesso significa poder usar a Timeline e o Raio-X como material de demonstração e tomada de decisão estratégica: mostrar um caso real, navegar pela história, explicar as decisões do sistema e, a partir disso, discutir melhorias. Se a interface de diagnóstico continuar sendo algo que só engenheiros íntimos do código conseguem usar, a S19 não entregou todo o seu valor.

9. Papel deste capítulo no restante da sprint

Este Capítulo 1 fixa a intenção da Sprint 19: transformar a história interna de cada caso em uma narrativa visual clara, útil para operação, curadoria, investigação e produto. Ele define o problema, o objetivo, o recorte e o público.

O Capítulo 2 vai traduzir essa visão em gates, métricas e critérios de validação alinhados ao DNA e ao Sprint Playbook, garantindo que Timeline e Raio-X não sejam apenas telas bonitas, mas funcionalidades mensuráveis (latência, completude de eventos, profundidade de explicação, caminho até evidência etc.).

O Capítulo 3 vai decompor essa visão em filemap, arquitetura de backend e frontend, contratos de API, modelos de dados e fluxos de navegação, garantindo que a S19 encaixe bem com o que S10, S12, S17 e S18 já construíram.

O Capítulo 4, por fim, vai descrever o plano de execução detalhado: comandos, scripts, testes, cenários de demo e evidências para cada gate, de forma que a Sprint 19 seja reproduzível, auditável e fácil de revalidar no futuro.

Com isso, a S19 se posiciona de forma clara como a sprint que transforma o Inspectah em uma ferramenta não só capaz de chegar à verdade, mas também de contar, de maneira honesta e rastreável, a história do caminho até ela.


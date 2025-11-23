Inspectah — Sprint 20  
Capítulo 1 — Contexto, Objetivos e Escopo (Frontend — UX, Auth básica e Observabilidade) — Versão 3

0. One-liner oficial da Sprint 20  
A Sprint 20 transforma as UIs construídas nas S17–S19 em um único produto coeso, polido e demonstrável: uma experiência unificada de consulta, admin e diagnóstico, com identidade visual consistente, responsividade mínima decente, autenticação básica nas rotas sensíveis e observabilidade de frontend suficiente para explicar o que está acontecendo para usuários, equipe, demos e o Conselho — sem alterar o “cérebro” (Truth-DB, Sistema de Blocos, Debunker, Comitês).

1. Posição da Sprint 20 no roadmap do Inspectah  
Até a Sprint 19, o frontend do Inspectah está organizado em três blocos principais:
- S17: UI de consulta para o usuário final, focada em pergunta → resposta consolidada → risco → evidências mínimas.
- S18: Console de Admin, para gerenciar fontes, casos e saúde do sistema.
- S19: Timeline e Raio-X, voltados a enxergar a história de um caso/tema e abrir o “capô” do motor (Debunker, Comitês, Âncoras, estados, etc.).

Essas três frentes existem, mas ainda têm cara de “ilhas”: estilos levemente diferentes, navegação nem sempre óbvia, ausência de regras claras de acesso (qual rota é pública, qual é protegida), quase nenhuma visibilidade estruturada de erros de UI, falhas de backend ou fluxos críticos.

Ao mesmo tempo, o Inspectah já tem decisões estruturais que a S20 precisa respeitar:
- O Inspectah é um hub de consulta: o usuário final **apenas consulta**; quem cadastra fontes, configurações e integrações é o admin.
- A promoção de informação a “verdade/fato” depende de redundância tripla real, evidências fortes e trilha de auditoria; o front não pode sugerir certeza onde o motor ainda está em estado “incerto” ou “em disputa”.
- O Sistema de Blocos, Debunker e Comitês já têm uma visão de longo prazo; a S20 não mexe no cérebro, só melhora os olhos, mãos e rosto do produto.

1.1 Mapa S17–S19 → S20 (o que muda para cada bloco)  
Para evitar confusão de escopo, a S20 é explicitamente uma sprint de **unificação e endurecimento** das UIs anteriores, não de criação de novos módulos. Em alto nível:

- S17 (consulta):
  - Antes: tela funcional de pergunta e resposta, com layout ainda “protótipo” e pouca sinalização de estados de incerteza/erro.
  - Depois da S20: mesma funcionalidade central, mas com visual unificado, mensagens melhores (inclusive de incerteza), estados claros (carregando/erro/vazio) e eventos instrumentados.

- S18 (admin):
  - Antes: console útil para quem conhece o sistema, mas com navegação pouco óbvia, visual diferente da consulta e sem proteção adequada por auth.
  - Depois da S20: acesso protegido por login, navegação previsível (listas → detalhe → timeline/raio-X), visual alinhado com o resto do produto.

- S19 (timeline e raio-X):
  - Antes: visão profunda de casos/blocos, ainda com cara de ferramenta interna experimental.
  - Depois da S20: parte natural do fluxo de operação/admin, acessível via rotas protegidas, com visual alinhado, estados claros e logs mínimos de uso/erro.

A S20 é, portanto, a “camada de coesão” dessas três sprints. Ela não altera contratos de backend nem amplia o escopo funcional de S17–S19; apenas torna o front usável e demonstrável como produto único.

2. Objetivo macro da Sprint 20  
Ao final da Sprint 20, queremos que qualquer pessoa autorizada consiga:
- consultar o Inspectah (UI S17) sem sentir que está usando um protótipo remendado;
- entrar no Console de Admin (S18) via login básico, navegar entre fontes, casos e health sem se perder;
- abrir Timeline e Raio-X (S19) como parte natural da navegação, entendendo onde está, como voltar e em que “camada” do sistema está operando;
- perceber visualmente que está usando **um único produto**, com linguagem de design unificada, não três apps diferentes;
- ver que, quando algo quebra, existem mensagens claras e registros minimamente estruturados de erro/evento, e não apenas silêncio ou stacktrace perdido no console;
- notar que o Inspectah leva incerteza a sério: estados como “em disputa”, “em análise”, “não confirmado” aparecem claramente na UI, sem serem varridos para baixo do tapete.

Em outras palavras: a S20 busca uma experiência coerente de ponta a ponta nas UIs já existentes, com disciplina de produto compatível com um sistema que se propõe a falar de verdade/fato — sem reinventar funcionalidades nem abrir novas frentes grandes.

3. Escopo funcional em alto nível  

3.1 Unificação visual e de UX  
Aplicar um design system mínimo e consistente em todas as telas de:
- consulta (S17);
- admin (S18);
- timeline/raio-X (S19).

Isso inclui, de forma concreta:
- tipografia, cores, espaçamentos e componentes básicos padronizados (botões, inputs, tabelas, cards, breadcrumbs, toasts/alerts);
- padrões de navegação claros: onde estão os menus principais, como chego da consulta ao admin (se tiver permissão), como abro timeline/raio-X a partir de um caso;
- comportamento coerente para estados comuns: carregando, sucesso, vazio, erro, sem permissão;
- mensagens, títulos e labels alinhados com o vocabulário do Inspectah (casos, blocos, evidências, fontes, etc.);
- distinção visual suave, mas clara, entre áreas de **consulta pública** e **operação/admin**.

O foco não é atingir pixel-perfect de produto final, mas eliminar a sensação de patchwork e de “cada tela feita num dia e num humor diferente”. A consistência vem antes de “efeitos bonitos”.

3.2 Responsividade mínima e acessibilidade básica  
Garantir que o front seja usável em:
- desktops e notebooks comuns (resoluções médias e menores);
- tablets;
- mobile em modo funcional (mesmo que ainda não seja a experiência ideal).

Resultados esperados:
- tabelas que colapsam de forma previsível em cards ou usam rolagem horizontal controlada em telas estreitas;
- grids e painéis que não estouram a viewport nem produzem barras de rolagem caóticas;
- áreas clicáveis com tamanho razoável para toque, especialmente em ações principais;
- uso mínimo de atributos de acessibilidade (aria-labels em botões icônicos, foco visível para navegação por teclado nas ações-chave).

A meta é “não passar vergonha” em telas menores, e não entregar uma experiência mobile perfeita nesta sprint.

3.3 Autenticação e autorização básica  
Introduzir uma camada simples, porém real, de proteção para rotas sensíveis. A S20 deve:
- definir e implementar um mecanismo de auth mínima (por exemplo: login com usuário/senha armazenados no backend interno, ou esquema de token de acesso controlado);
- proteger rotas como `/admin` e as páginas de timeline/raio-X (`/admin/cases/:id/timeline`, `/admin/cases/:id/xray`) para que só usuários autenticados acessem;
- implementar fluxo de sessão: login, logout, persistência simples (por exemplo, token em storage controlado), redirecionamento automático para login ao tentar acessar rota protegida sem permissão;
- ter comportamento previsível em caso de token inválido/expirado (limpar sessão, mandar para login, mostrar mensagem adequada);
- deixar claro, na UI, o que é área pública (consulta) e o que é área privada (admin/timeline/raio-X);
- não expor dados sensíveis ou internos em componentes de UI públicos (ex.: IDs internos, detalhes de infraestrutura, mensagens de erro cruas).

Não é objetivo da S20 construir um sistema de identidade completo, RBAC complexo ou OAuth com provedores externos. Basta uma auth interna confiável, pensada para uso por equipe e pilotos controlados, mas implementada de forma a ser substituída/evoluída em sprints futuras.

3.4 Observabilidade de frontend  
Adicionar observabilidade mínima, porém útil, na camada de UI. A S20 deve:
- instrumentar eventos críticos, como:
  - envio de consulta pelo usuário final, com sucesso/falha;
  - abertura de telas principais do admin (dashboard, lista de fontes, lista de casos);
  - abertura de timeline/raio-X e falhas de carregamento;
- capturar erros de UI relevantes (error boundaries, falhas em chamadas de backend, problemas de renderização que impeçam uso do fluxo);
- produzir logs estruturados no frontend (por exemplo, via wrapper padrão de logging) de forma que:
  - em modo dev, seja fácil enxergar o que aconteceu;
  - em modo interno, seja possível enviar esses registros para um endpoint do backend ou para a infraestrutura de logs já existente;
- incluir alguma forma de correlação com o backend (por exemplo, um request id ou trace id repassado pelo backend e exibido/logado pelo front ao mostrar um erro);
- tratar erros de forma consistente na UI (componentes padrão de erro, textos revisados, sem vazamento de stacktrace bruto).

A ideia não é integrar com ferramentas específicas de mercado, e sim estabelecer um padrão mínimo e estável de “como o front conta a sua história” quando algo dá certo ou errado. Isso prepara o terreno para as squads futuras de observabilidade/infra adicionarem integrações mais sofisticadas.

3.5 Exposição correta de estados de verdade/incerteza  
Como o Inspectah lida com verdade/fato de forma responsável, a S20 precisa garantir que a UI:
- nunca exiba informações como “fato” quando o motor ainda as considera “em disputa” ou “em análise”;
- use rótulos, cores e textos que deixem claro se um caso/bloco está:
  - aceito/estabilizado;
  - em disputa/contestação;
  - em análise/incompleto/incerto;
- evite linguagem enganosa ou triunfalista em contextos onde a incerteza é estrutural;
- trate estados de “sem evidência suficiente” de forma explícita, em vez de simplesmente omitir resposta.

Esses estados não precisam ser exaustivos nesta sprint, mas a S20 deve criar a base visual e textual para que futuras sprints de Sistema de Blocos/Truth-DB possam refinar esse vocabulário sem ter que redesenhar tudo.

3.6 Suporte a testes, demos e uso interno  
A S20 também precisa garantir que o frontend seja confortável de usar como ferramenta diária da equipe. Isso inclui:
- um fluxo de demo recomendado (roteiro de navegação) que passe por consulta → evidências → admin → timeline/raio-X em poucos cliques;
- uma forma simples de subir o front localmente em modo dev e apontá-lo para o backend padrão (sem configuração manual absurda);
- feedback visual suficiente para que alguém que está testando uma feature consiga entender “onde estou” e “o que acabou de acontecer”;
- estabilidade suficiente para que demos ao Conselho possam ser feitas sem gambiarras de última hora em UI.

4. Fora de escopo explícito na Sprint 20  
Para manter a sanidade e respeitar o foco da sprint, ficam **explicitamente fora de escopo**:
- criação de novos módulos funcionais grandes (ex.: nova seção de analytics, painel de BI, dashboards avançados);
- implementação de sistema de permissão complexo (grupos, papéis, hierarquias de acesso detalhadas, aprovação em múltiplos níveis);
- redesign completo da identidade visual do Inspectah (logo, branding completo, guidelines formais de design system);
- alterações profundas no backend, Truth-DB, Sistema de Blocos, Debunker ou Comitês, exceto ajustes pontuais necessários para suportar auth e observabilidade de UI;
- integrações com provedores externos de auth (OAuth, SSO corporativo, etc.) e com ferramentas externas específicas de analytics/monitoramento;
- mudanças de semântica nos estados de verdade/fato do motor (isso pertence às sprints de Sistema de Blocos/Truth-DB).

Se surgir qualquer ideia lateral que dependa desses itens, ela deve ser registrada como candidata para sprints futuras (ou para a Fase 2/Sistema de Blocos avançado), não como item desta sprint.

5. Personas e jornadas alvo da S20  

5.1 Usuário final (consulta)  
Perfil: pessoa que acessa a UI pública de consulta para perguntar sobre fatos/casos/temas. Não precisa conhecer o conceito de Sistema de Blocos, Debunker ou Comitês.

Jornada alvo na S20:
- chega à página de consulta, compreende rapidamente o que pode fazer (“pergunte sobre um fato/caso/tema”);
- digita uma pergunta, envia, vê um estado de “carregando” claro;
- recebe resposta consolidada, com indicação de risco e evidências mínimas, em layout legível;
- entende, visualmente, que aquilo veio do Inspectah (não de um formulário genérico qualquer);
- enxerga sinais de que o sistema leva incerteza a sério (ex.: mensagens claras quando algo está em disputa ou ainda em análise, em vez de vender certeza falsa);
- em caso de erro, recebe mensagem clara e não fica preso em tela quebrada.

5.2 Operador/Admin  
Perfil: membro da equipe ou operador interno que gerencia fontes, casos e saúde do sistema via `/admin`.

Jornada alvo na S20:
- faz login e entra no Console de Admin;
- enxerga um overview mínimo (fontes, casos, health) sem ter que adivinhar a navegação;
- consegue ir de um caso na lista para sua timeline e raio-X de forma previsível (links/botões claros, breadcrumbs onde fizer sentido);
- consegue diferenciar visualmente “área de operação” (admin) de “área de consulta” (usuário final);
- em caso de erro (falha de backend, timeout, etc.), vê mensagem clara e sabe o que recarregar ou como voltar;
- sabe que certas rotas só são acessíveis após login e não via “URL secreta”.

5.3 Equipe interna (produto/engenharia, demos)  
Perfil: PO, devs, pessoas envolvidas em revisão do produto, que usam o front como vitrine e ferramenta de teste.

Jornada alvo na S20:
- consegue abrir o Inspectah na frente de alguém (reunião, call, demo) sem precisar pedir desculpas pela UI ou gastar muito tempo explicando a navegação;
- consegue reproduzir fluxos típicos (consulta, ver evidências, olhar um caso no admin, abrir timeline/raio-X) em poucos cliques;
- consegue, diante de um problema, capturar informações mínimas (mensagem amigável + id de correlação) para investigar no backend/logs;
- enxerga que o front já está pronto para receber melhorias de Fase 2 (Sistema de Blocos completo, Debunker mais agressivo, reputação pesada) sem precisar ser redesenhado do zero.

6. Requisitos de qualidade e restrições gerais da S20  
A S20 deve respeitar os seguintes princípios de qualidade:
- consistência acima de brilho: é mais importante ter layouts previsíveis e limpos do que efeitos visuais complexos;
- não quebrar fluxos estáveis: qualquer melhoria de UX precisa preservar os fluxos funcionais validados nas S17–S19;
- zero “rota sensível sem auth”: após a S20, nenhuma rota de admin/timeline/raio-X pode ficar permanentemente aberta em ambiente interno, mesmo que o auth seja simples;
- observabilidade sempre ligada para fluxos críticos: toda consulta, carregamento de admin e abertura de timeline/raio-X deve gerar sinais mínimos para troubleshooting;
- simplicidade de operação: o front não pode exigir conhecimento avançado para ser usado pela equipe — deve ser “ligou, abriu, logou, usou”;
- respeito à semântica de verdade/fato: a UI nunca deve sugerir mais certeza do que o motor tem.

Restrições técnicas e de arquitetura:
- reuso obrigatório da stack já consolidada (React, Vite, Tailwind, componentes existentes), sem reescrita completa;
- nenhuma dependência rígida em fornecedores externos específicos de monitoramento/analytics no código de base; se houver integração opcional, deve ser claramente isolada;
- auth implementada de forma a ser facilmente substituível ou evoluível em sprints futuras (por exemplo, camada dedicada de serviço de auth no front, ao invés de espalhar lógica de autorização em cada componente);
- UI de consulta sempre tratada como “camada de usuário final” — sem expor detalhes internos que possam confundir (IDs técnicos, nomes de serviços, etc.);
- contratos de API existentes não devem ser quebrados; qualquer ajuste necessário deve ser tratado como incremento incremental, não reescrita.

7. Definição de “Pronto” em nível de produto (macro)  
A Sprint 20 será considerada “pronta” em termos de produto quando, simultaneamente:
- um usuário final consegue usar a UI de consulta para fazer perguntas e interpretar a resposta sem ajuda do time;
- um operador/admin consegue logar, navegar pelo console, abrir timeline/raio-X e voltar para o início sem ficar preso ou confuso;
- as rotas sensíveis estão efetivamente protegidas por auth básica, sem atalhos “escondidos” em ambiente interno;
- fluxos críticos geram eventos e logs de UI suficientes para que a equipe consiga investigar problemas sem depender exclusivamente de relatos humanos;
- alguém da equipe consegue fazer uma demo ponta a ponta do Inspectah (consulta → evidências → admin → timeline/raio-X) em poucos minutos, com sensação de produto sério e consistente, e não de experimento;
- o estado atual do front é percebido pelo squad responsável e pelo Conselho como uma base sólida para as sprints de Fase 2 (Sistema de Blocos completo, Debunker forte, governança e comunidade), sem necessidade de reescrita geral.

Os detalhes de gates, métricas e evidências para comprovar estes itens ficam formalizados no Capítulo 2 (gates de validação) e no Capítulo 4 (plano de execução e runbook), mas esta é a régua conceitual que guia todas as decisões da Sprint 20.


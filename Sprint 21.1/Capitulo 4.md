# Sprint 21.1 – Capítulo 1

## Título da sprint

Copiloto de Fontes: assistente de IA para cadastro guiado no Console de Fontes.

## Contexto e motivação

A Sprint 21 colocou o Console de Fontes em produção: modelo de dados consolidado, ciclo de vida definido, backend e UI de admin funcionando, seeds por domínio e gates S21_G0…S21_G8 em GO. Hoje o admin consegue cadastrar fontes manualmente, mas o processo ainda exige entendimento profundo da ontologia da S21, dos tipos de fonte, dos campos técnicos e das combinações válidas de temas e info types. Isso cria atrito, aumenta risco de cadastro inconsistente e transforma o Console de Fontes em algo dependente de poucos "iniciados".

A Sprint 21.1 nasce para resolver esse gargalo na origem. A ideia é colocar um agente de IA extremamente focado dentro do Console de Fontes, que converse com o admin em linguagem natural, traduza a intenção do usuário para o modelo de fonte da S21, ajude a levantar as informações que faltam e preencha o formulário oficial de cadastro em tempo real, mantendo o humano como decisão final. O objetivo é que qualquer admin minimamente treinado consiga cadastrar fontes complexas (como globo.com, APIs de esportes, fontes climáticas ou portais de fofoca) apenas conversando com o sistema, sem precisar decorar detalhes técnicos.

## Visão da Sprint 21.1

Ao final da Sprint 21.1, o Console de Fontes passa a ter um Copiloto de Fontes integrado à interface de admin, apresentado como um widget de chat no canto inferior direito da tela. Esse copiloto é um agente de IA com escopo estritamente limitado ao problema de modelar fontes na ontologia da S21. Ele entende frases como "quero cadastrar o globo.com como fonte de notícias gerais do Brasil", é capaz de pedir as informações que faltam, de ler arquivos de documentação fornecidos pelo admin e de propor um cadastro de fonte completo, preenchendo o formulário de forma incremental.

O formulário oficial da S21 continua sendo a fonte de verdade. O copiloto não salva nada sozinho: ele apenas sugere valores, preenche os campos na tela, destaca visualmente o que foi sugerido e explica suas escolhas. O admin acompanha o formulário sendo preenchido em tempo real, pode editar qualquer campo e só então confirma o cadastro com um clique explícito.

A visão de sucesso é simples: cadastrar uma nova fonte deixa de ser um exercício de lembrar nomenclaturas internas e vira uma conversa guiada com um especialista em "como transformar esse site ou essa API em uma fonte S21", com feedback visual imediato e sem abrir mão do controle humano.

## Descrição do Copiloto de Fontes

O Copiloto de Fontes é um agente de IA especializado, que vive exclusivamente na camada de administração do Console de Fontes. Ele não é um chatbot genérico e não responde perguntas fora do domínio de cadastro de fontes. Sua função é entender a intenção do admin, mapear essa intenção para o modelo de fonte da S21 e manter o formulário e a conversa sempre sincronizados.

O copiloto enxerga três tipos principais de informação.

Primeiro, o contexto fixo da S21: ontologia, tipos de fonte suportados na Fase 1, modelo de dados, ciclo de vida, fluxos de admin e cenários de uso. Esses materiais são a bússola do agente e definem quais combinações de campos são válidas.

Segundo, o estado atual do formulário na tela: campos já preenchidos pelo admin, tipo de fonte escolhido, temas marcados, info types selecionados e qualquer outro metadado já definido. O copiloto nunca perde esse contexto e sempre assume que o formulário é o estado atual da "proposta de cadastro".

Terceiro, as entradas específicas da sessão: mensagens do admin no chat, arquivos anexados (como PDFs de documentação, guias de API, capturas de tela ou extratos de RSS) e ajustes manuais feitos pelo próprio usuário nos campos. O agente usa essas entradas para inferir endpoints, categorias, temas, info types e outros detalhes necessários.

Com base nisso, o Copiloto de Fontes faz duas coisas principais. Conduz uma conversa guiada para reduzir ambiguidade, perguntando o mínimo necessário para chegar a um cadastro coerente. E traduz continuamente cada decisão em mudanças concretas no formulário, mantendo o admin sempre vendo a mesma verdade que o agente está manipulando.

## Experiência de uso desejada

Na prática, a experiência de uso da Sprint 21.1 deve se parecer com a interação com um colega experiente sentado ao lado do admin.

O admin abre o Console de Fontes. No canto inferior direito vê um botão que abre o widget do Copiloto de Fontes. Ao clicar, surge um painel de chat que não rouba a tela principal: o formulário de nova fonte continua visível, ocupando o restante do espaço. Há um botão de "Novo chat" que permite iniciar uma nova conversa, descartando o contexto anterior sem interferir no formulário até que o usuário peça para o copiloto sugerir algo.

O admin escreve algo como "quero cadastrar globo.com como fonte de notícias gerais" ou "tenho essa API de resultados de campeonato, quero transformar isso em uma fonte de esportes". O copiloto responde em português claro, explica quais informações precisa para montar o cadastro e sugere um plano: tipo de fonte que parece adequado, categoria provável, temas previstos e campos que dependerão de documentação técnica. Se o admin tiver um PDF ou um manual, pode anexar. O copiloto lê o arquivo, extrai URLs, caminhos de endpoint, parâmetros relevantes e exemplos de dados e usa isso para preencher o formulário.

Durante a conversa, à medida que o copiloto vai assumindo decisões, o formulário de fonte é atualizado campo a campo. Sempre que um campo é preenchido ou alterado por sugestão da IA, a UI marca essa origem, por exemplo com um destaque suave e uma indicação textual de que aquilo é uma sugestão do copiloto. O admin pode clicar em qualquer campo, editar o valor ou pedir ao agente uma justificativa ou alternativa. O copiloto sempre explica suas escolhas com base na ontologia e nos cenários da S21.

Quando a proposta de cadastro estiver madura, o copiloto apresenta um resumo final, apontando tipo, categoria, temas, info types, endpoint, slug, nome e descrição da fonte. O admin revisa o formulário completo, faz ajustes finais, e só então clica no botão de cadastro oficial. O copiloto nunca dispara a criação sozinho. Depois do cadastro, o admin pode ainda pedir ao copiloto ajuda para interpretar eventuais erros de validação ou restrições impostas pelo backend.

## Papel da IA, limites e comportamento esperado

A IA utilizada na Sprint 21.1 trabalha com um escopo radicalmente limitado: ela não discute política, não opina sobre a veracidade de notícias, não responde perguntas gerais sobre o mundo. O copiloto existe para resolver apenas um problema: transformar a intenção do admin em um cadastro de fonte válido dentro da ontologia da S21.

Sempre que o admin trouxer uma descrição vaga, o agente busca concretizar em termos do modelo de dados. Se o usuário diz apenas "quero cadastrar globo.com", o copiloto esclarece se o objetivo é monitorar manchetes gerais, apenas política, apenas esportes ou outro recorte, e a partir disso decide se a fonte deve ser do tipo RSS de notícias, API HTTP, feed especializado ou outro tipo suportado. Se o admin não souber uma informação técnica específica, o agente ajuda a contornar, sugerindo alternativas como pedir documentação a terceiros, usar um subset da fonte com menos parâmetros críticos ou adiar alguns campos para uma futura S22.

Um princípio central é a transparência. O copiloto sempre deixa claro quando está "chutando informado", quando está seguindo um padrão da ontologia ou quando não tem dados suficientes para decidir. Se houver ambiguidade real, o agente devolve a responsabilidade ao humano: oferece opções claras e pede escolha, em vez de inventar valores arbitrários.

Finalmente, o copiloto não chama endpoints externos por conta própria nesta sprint. Ele não acessa diretamente globo.com ou APIs do mundo para testar URLs. Todo o conhecimento da fonte vem do que o admin escreve ou anexa, somado às regras internas da S21. Testes reais de conectividade e ingestão fazem parte da S22 e posteriores.

## Compatibilidade com modo agente

O Copiloto de Fontes deve nascer já compatível com o modo agente adotado no projeto. Isso significa que, por baixo da interface de chat embutida no front, existe um agente configurado com:

- um prompt-base estável, que inclui ontologia, modelo de dados, ciclo de vida e regras de segurança da S21;
- um conjunto de ferramentas explícitas (por exemplo: ler_estado_do_formulario, sugerir_valores_para_campos, aplicar_sugestao_em_campo, ler_arquivo_anexado, registrar_evento_de_interacao), usadas pelo agente para agir sobre o formulário;
- um protocolo bem definido de entradas e saídas, adequado tanto ao widget do front quanto a chamadas programáticas futuras.

Na prática, isso implica dois modos de uso com o mesmo núcleo lógico.

Primeiro, o modo embed na UI de admin: o widget de chat conversa com o agente via modo agente, passando sempre o snapshot atual do formulário, o histórico resumido da conversa e os metadados necessários (tipo de fonte, usuário, contexto). O agente responde com mensagens para o usuário e com instruções estruturadas para atualizar campos do formulário. A UI executa apenas as instruções explicitamente permitidas, mantendo o humano no controle.

Segundo, o modo agente orquestrado: o mesmo agente pode ser invocado, no futuro, por scripts ou pipelines internos para auxiliar em fluxos de cadastro em lote ou revisões de fontes, sem a presença direta do widget. Por isso, o desenho da Sprint 21.1 já prevê que o agente não dependa de estado oculto no front e seja capaz de trabalhar a partir de snapshots explícitos (formulário, arquivos, contexto textual) enviados em cada chamada.

Essa compatibilidade exige que o Capítulo 2 descreva gates específicos para validar o modo agente (por exemplo, testes de idempotência das instruções, limites de escopo das ferramentas, comportamento seguro em entradas malformadas) e que o Capítulo 3 traga um filemap onde o copiloto é isolado em um módulo claro, com fronteira bem definida entre UI, backend e agente.

## Escopo da Sprint 21.1

A Sprint 21.1 foca em quatro grandes frentes.

A primeira é a experiência de chat integrada à UI de admin. Isso inclui o widget de chat no canto inferior direito, o botão de novo chat, o gerenciamento de contexto por sessão e a sincronização visual com o formulário.

A segunda é o modelo de interação entre copiloto e formulário. O agente precisa ser capaz de ler e escrever campos do formulário, sem quebrar as validações existentes, respeitando tipos permitidos, listas de temas e info types, e mantendo a possibilidade de edição manual a qualquer momento.

A terceira é a capacidade do agente de ler arquivos fornecidos pelo admin. Nesta sprint, isso significa aceitar uploads e expor o conteúdo textual para o modelo de IA como fonte de verdade para inferir endpoints, tipos de dados e escopo de cobertura da fonte.

A quarta é a definição clara de limites, protocolos de uso da IA e suporte a modo agente: o que o agente pode e não pode fazer, como reage quando não sabe, como registra suas ações na interface e como suas instruções são encapsuladas de forma que possam ser reutilizadas fora do front.

## Fora de escopo imediato

Alguns desejos naturais são explicitamente postergados para evitar dispersão.

O copiloto não fará testes ativos de conectividade com as fontes. Ele não executa requisições de rede nem verifica se uma URL está respondendo. Essa responsabilidade é da S22 Ingestão 2.0 e de testes técnicos posteriores.

O copiloto não será exposto na interface de usuários finais do Inspectah. Ele é uma ferramenta interna de admin.

Não haverá neste ciclo integração com sistemas de autenticação complexa, roles avançados ou fluxos de aprovação multinível. A confirmação humana nesta sprint é um clique simples de cadastro, desde que o usuário já tenha permissão de admin.

Não haverá personalização de "personalidade" do agente além do mínimo necessário: tom direto, pedagógico e focado em clareza. O objetivo é ser útil, não virar um personagem.

A orquestração avançada de agentes múltiplos (por exemplo, um agente que cadastra fonte, outro que valida ingestão, outro que já sugere cenários de S22) fica explicitamente para sprints futuras. A 21.1 cuida apenas do Copiloto de Fontes e das fronteiras necessárias para que esse agente possa ser plugado em arquiteturas mais complexas depois.

## Objetivos e critérios de sucesso

O objetivo principal da Sprint 21.1 é reduzir a barreira cognitiva para cadastrar novas fontes, mantendo ou aumentando a qualidade dos cadastros em relação ao fluxo 100 por cento manual.

Como critérios de sucesso, consideramos suficiente se, em ambiente de teste, um admin com pouco contato prévio com os detalhes da S21 conseguir, apenas conversando com o Copiloto de Fontes e revisando o formulário, cadastrar pelo menos uma fonte de cada tipo da Fase 1 de forma consistente com a ontologia. Outro critério é que, em cenários como "cadastrar globo.com como fonte de notícias gerais do Brasil", o copiloto consiga chegar a um cadastro plausível em poucas interações, pedindo apenas as informações que realmente não pode inferir a partir da descrição e dos arquivos fornecidos.

Do ponto de vista técnico, os critérios incluem manter todos os gates da S21 em GO após a integração, preservar as garantias do modelo de dados, e não introduzir vias alternativas de cadastro que burlem o formulário oficial ou as validações do backend. Adicionalmente, o modo agente precisa ser verificável: dados iguais e contexto equivalente produzem instruções equivalentes de atualização de formulário, sem efeitos colaterais inesperados.

## Dependências e alinhamento com sprints futuras

A Sprint 21.1 depende diretamente da S21 concluída. O modelo de fontes, as migrations, os endpoints de admin e a UI atual são insumos obrigatórios para o desenho do copiloto. Essa sprint também se apoia nos contratos documentados com S22, S23, S24 e S25, na medida em que o modo de cadastro de fontes impacta ingestão, classificação, debunking e governança.

Ao terminar a 21.1, o Console de Fontes ganha uma camada de inteligência assistida que prepara o terreno para S22. Fontes cadastradas via copiloto chegam mais completas, melhor classificadas e com metadados mais ricos, o que simplifica o desenho da ingestão contínua e reduz trabalho manual em etapas posteriores do pipeline do Inspectah. O fato do copiloto já operar em modo agente garante que, nas próximas sprints, ele possa ser reutilizado em fluxos automatizados, revisões em lote e outras formas de orquestração sem reescrever sua lógica central.


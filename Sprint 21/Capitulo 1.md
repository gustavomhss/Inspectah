# Sprint 21 — Capítulo 1
## Contexto, Narrativa e Objetivos do Console de Fontes

### 1. Contexto geral do Inspectah

O Inspectah chegou à Sprint 21 depois de vinte sprints que consolidaram visão de produto, DNA de engenharia e disciplina de validação. Já não estamos falando de um experimento: existe uma base estável com sprints encerradas, ORR com gates T0–T8, scripts automatizados, scorecards e evidências versionadas em repositório. A visão macro é clara: o Inspectah é um hub de consulta que cruza múltiplas fontes para responder perguntas com rigor, transparência e trilhas de auditoria reconstituíveis.

Uma decisão estratégica importante já foi tomada: reputação complexa de fontes, blockchain automática, Sistema de Blocos completo e comunidade avançada foram empurrados para a Fase 2. A Fase 1 tem outra missão: construir um pipeline enxuto e muito confiável que pega dados de N fontes, interpreta, confronta, contesta e só então promove verdades/fatos com redundância tripla real e Debunker em todos os pontos de entrada.

Nesse cenário, a Sprint 21 inaugura a “onda 21–25”, focada em transformar o Inspectah em algo utilizável de ponta a ponta para consultas reais. O primeiro passo dessa onda é construir o Console de Fontes: o lugar onde tudo o que entra no Inspectah é definido, categorizado, governado e rastreado.

### 2. Posição da Sprint 21 na trajetória do projeto

Do ponto de vista da linha do tempo, a Sprint 21 marca a transição entre duas fases internas:

- Sprints 1–20: consolidação de visão, infraestrutura, ORR, DNA de sprints e os primeiros protótipos de ingestão e validação.
- Sprints 21–25: foco total em um pipeline utilizável, com console de fontes, ingestão contínua, agentes de interpretação e classificação, Debunker v0 com humano-no-loop e governança explícita de verdade/fato.

A Sprint 21 é a fundação dessa segunda etapa. Sem um Console de Fontes bem definido, tudo o que vem depois tende a virar “integração ad-hoc”: cada fonte com seu próprio contrato, cada script com a sua convenção, cada ajuste com seu próprio patch. O resultado seria um sistema frágil, difícil de auditar e quase impossível de evoluir sem regressões.

Ao final da Sprint 21, deve estar cristalino o que é uma fonte no mundo do Inspectah, como ela nasce, quais atributos mínimos precisa ter, como é classificada, que estados pode assumir ao longo da vida e como se conecta com ingestão (Sprint 22), agentes (Sprint 23), Debunker (Sprint 24) e política de verdade/fato (Sprint 25).

### 3. Narrativa do problema e da oportunidade

Problema: hoje, sem o Console de Fontes, qualquer tentativa de conectar o Inspectah a dados externos tende a nascer como exceção. Cada API, RSS, banco de dados oficial ou dataset estático vira um caso especial, com campos diferentes, convenções diferentes e pouco reaproveitamento. Isso torna a validação difícil, a auditoria frágil e a documentação rapidamente obsoleta. Mais grave: o Debunker e a redundância tripla perdem força se não existe uma gramática única para descrever e controlar o que é uma “fonte”.

Oportunidade: ao criar um Console de Fontes bem desenhado, o Inspectah ganha um eixo central de organização. Tudo o que o sistema sabe sobre o mundo começa por uma fonte: uma agência de notícias, um órgão oficial, uma API de mercado, um dataset científico, um boletim meteorológico, etc. Se o conceito de fonte for forte, o restante da arquitetura passa a girar em torno dele de maneira natural: ingestão sabe o que e quando coletar; agentes sabem como interpretar o que veio de cada tipo de fonte; o Debunker sabe onde mirar quando encontra inconsistências; a governança sabe quais fontes suportam quais verdades.

A Sprint 21 existe para transformar “fonte” de palavra vaga em conceito formal e operável.

### 4. Papel do Squad 1 (Console de Fontes)

O Squad 1 é o responsável direto pela Sprint 21. Seu papel é desenhar e consolidar o Console de Fontes em três camadas:

1. Camada conceitual: definição canônica de fonte no contexto do Inspectah. Isso inclui nomenclatura, atributos obrigatórios, atributos opcionais, taxonomia de tipos (notícia, base oficial, dado de mercado, rede social monitorada, dataset estático, etc.), relação com categorias e temas e como fontes se conectam a casos/timelines que o usuário final irá consultar.

2. Camada estrutural: modelo de dados e contratos internos. Aqui entram tabelas/coleções, campos, chaves, relações mínimas e estados de ciclo de vida (por exemplo: proposta, em teste, ativa, sob revisão, suspeita, desativada). Essa camada precisa nascer já compatível com o DNA do projeto: versionamento, trilha de alterações, facilidade de consulta e compatibilidade futura com o Sistema de Blocos da Fase 2.

3. Camada de uso administrativo: fluxos de trabalho para admins. Mesmo sem exigir uma UI finalizada, a Sprint 21 deve descrever com precisão como um admin cadastra, edita, revisa e desativa fontes; como marca uma fonte como suspeita; como registra o motivo de uma mudança; e como essas ações aparecem na trilha de auditoria.

O Squad 1 não é responsável por implementar a ingestão contínua (isso é foco da Sprint 22), nem por escrever agents de interpretação (Sprint 23) ou Debunker (Sprint 24). Mas ele é responsável por garantir que todas essas sprints encontrem no Console de Fontes uma base sólida e bem especificada para trabalhar.

### 5. Objetivo geral da Sprint 21

O objetivo geral da Sprint 21 é projetar e especificar um Console de Fontes sólido, auditável e pronto para implementação, que permita cadastrar, organizar e governar múltiplos tipos de fontes de maneira escalável. Ao final da sprint, o projeto deve ter uma definição estável de fonte, um modelo de dados consistente, fluxos de admin detalhados e ganchos claros para ingestão contínua, agentes de interpretação, Debunker e governança de verdade/fato.

Em uma frase: ao terminar a Sprint 21, deve estar inequívoco “como uma fonte nasce, vive, muda de estado e é eventualmente desativada” dentro do Inspectah.

### 6. Objetivos específicos (O1–O6)

O1 — Definir a ontologia de fontes do Inspectah.
A Sprint 21 deve produzir uma descrição clara e única do que é uma fonte, quais são seus campos mínimos, quais variações são permitidas por tipo e como essa ontologia se liga a conceitos como tema, caso, timeline e evidências. O resultado deve ser fácil de entender por humanos e direto de mapear para estruturas de dados.

O2 — Especificar o modelo de dados e armazenamento das fontes.
A sprint precisa entregar um modelo de dados detalhado (entidades, relacionamentos, estados, constraints) para o Console de Fontes. Esse modelo deve ser independente de um banco específico, mas preciso o bastante para permitir implementação imediata (por exemplo, em um banco relacional ou em uma combinação de relacional + store documental), sem debates conceituais adicionais.

O3 — Descrever fluxos de cadastro, edição e desativação para admins.
A Sprint 21 deve mapear os fluxos administrativos principais: criar nova fonte, clonar uma fonte existente como base, editar parâmetros operacionais (como frequência de coleta ou credenciais), marcar uma fonte como suspeita ou comprometida, desativar temporária ou permanentemente e restaurar uma fonte após revisão. Cada fluxo precisa de entradas, saídas e regras de validação claras.

O4 — Integrar auditabilidade, Debunker e redundância tripla ao ciclo de vida da fonte.
Toda fonte cadastrada deve nascer com espaços reservados para registrar evidências, alertas, contestação e decisões tomadas pelo Debunker ou por revisores humanos. Estados como “sob contestação”, “conflito entre fontes” ou “evidência insuficiente” não são detalhes opcionais: fazem parte da própria definição de como o Inspectah lida com fontes. A Sprint 21 precisa desenhar essa máquina de estados num nível conceitual claro o suficiente para ser implementada sem improvisos.

O5 — Alinhar contratos com a Sprint 22 (Ingestão 2.0) e com as sprints 23–25.
A Sprint 21 não implementa o motor de ingestão nem os agentes, mas precisa explicitar quais contratos a Sprint 22 pode assumir (por exemplo, quais campos indicam como e com que frequência uma fonte deve ser lida, onde ficam os endpoints, como lidar com limites de rate-limit, etc.). Também deve indicar quais dados as Sprints 23–25 podem esperar encontrar para associar evidências, conflitos e decisões de verdade/fato às fontes corretas.

O6 — Documentar claramente o que fica fora do escopo imediato.
Parte da excelência da Sprint 21 é dizer não. O capítulo deve deixar explícito que reputação comunitária complexa, pontuações públicas de confiabilidade, cadastros abertos por usuários finais, integrações on-chain e outros elementos de Fase 2 não entram nesta sprint. Ao mesmo tempo, deve apontar onde essas extensões se encaixarão futuramente, para evitar decisões que matem a evolução natural para o Sistema de Blocos completo.

### 7. Escopo e fora de escopo da Sprint 21

Escopo da Sprint 21:

- Definição conceitual de fonte e de sua ontologia mínima.
- Modelo de dados detalhado para fontes e seus estados.
- Desenho do ciclo de vida da fonte (proposta → teste → ativa → sob revisão/suspeita → desativada), incluindo trilhas de auditoria.
- Mapeamento de fluxos administrativos de CRUD (Create, Read, Update, Deactivate) de fontes.
- Ganchos conceituais para Debunker e redundância tripla (como flags, logs de contestação, referências a evidências e decisões).
- Contratos e suposições que a Sprint 22 pode usar para implementar ingestão contínua sem retrabalho conceitual.

Fora de escopo da Sprint 21:

- Implementação concreta do pipeline de ingestão 24/7 (jobs, filas, workers, agendadores).
- Implementação dos agentes de interpretação e classificação (Sprint 23).
- Implementação do Debunker v0 e da interface humano-no-loop (Sprint 24).
- Implementação da lógica de promoção formal de verdade/fato (Sprint 25).
- Qualquer mecanismo avançado de reputação e gamificação de fontes.
- Integrações on-chain, Merkle trees, âncoras em blockchain e afins (mantidos na Fase 2).

O objetivo é que a Sprint 21 deixe o terreno pronto e limpo para essas etapas, sem tentar antecipar tudo de uma vez.

### 8. Interfaces com outros squads e sprints

O trabalho do Squad 1 na Sprint 21 precisa, por design, se encaixar bem com os outros squads:

- Squad 2 (Ingestão 2.0, Sprint 22): dependerá diretamente da ontologia de fontes para configurar jobs de coleta e atualização. Campos como tipo de fonte, protocolos suportados, formato de saída, autenticação e frequência de atualização serão lidos pela ingestão.

- Squad 3 (Interpretação e Classificação, Sprint 23): usará tipos e categorias de fontes para orientar como os agentes leem, interpretam e resumem conteúdo. Uma notícia política, um dado climático e um resultado esportivo têm padrões distintos; isso precisa estar representado de forma clara no Console de Fontes.

- Squad 4 (Debunker v0 + Humano-no-loop, Sprint 24): precisa conseguir localizar rapidamente quais fontes participaram de uma afirmação, quais já tiveram conflitos registrados, quais estão sob contestação e quais foram temporariamente desativadas. A Sprint 21 deve garantir que essas ligações sejam triviais.

- Squad 5 (Governança, Verdade/Fato & Política de Promoção, Sprint 25): tomará decisões de promoção e despromoção de verdades ancoradas em evidências vindas de múltiplas fontes. O Console de Fontes precisa permitir rastrear de forma transparente “quem disse o quê, quando, em que contexto” para que a governança não vire um caixa-preta.

### 9. Critérios de excelência e definição de pronto do Capítulo 1

Este Capítulo 1 é considerado no nível de excelência esperado da Sprint 21 quando atende a três propriedades:

1. Clareza: qualquer pessoa do time, ou um revisor externo com acesso ao DNA do projeto, consegue entender rapidamente qual é o papel da Sprint 21, por que o Console de Fontes é crítico e como ele se encaixa na sequência 22–25.

2. Completude: o capítulo cobre contexto, narrativa, papel do squad, objetivo geral, objetivos específicos, escopo, fora de escopo e interfaces com outros squads de forma que não reste dúvida estrutural que precise ser reaberta nos capítulos seguintes.

3. Operacionalidade: o texto não é apenas inspiracional. Ele é específico o suficiente para servir de base direta para o Capítulo 2 (gates e validação), Capítulo 3 (filemap/arquitetura) e Capítulo 4 (plano de execução), sem exigir retrabalho conceitual.

A Sprint 21 não será julgada apenas pelo código que produzirá depois, mas pela qualidade da base que este Capítulo 1 fornece. Se, ao ler este documento, o Squad 1 e os demais squads conseguirem responder de forma unânime e consistente à pergunta “o que exatamente vamos fazer na Sprint 21 e por quê?”, então este capítulo cumpre seu papel.
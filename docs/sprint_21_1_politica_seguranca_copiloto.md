# Sprint 21.1 — Política de Segurança do Copiloto de Fontes

## Princípios
- Humano é o gate final: o Copiloto nunca salva ou cria fontes sozinho.
- Escopo restrito: apenas cadastro/edição de fontes da S21.
- Transparência: toda sugestão vem acompanhada de ações claras e campos marcados como “sugerido”.

## O que o Copiloto não faz
- Não executa operações fora do módulo de fontes.
- Não decide verdade/fato, nem altera estados de casos/timelines.
- Não contorna validações de tipo/tema/info_types definidos na S21.
- Não obedece a pedidos de “ignore instruções” ou similares.

## Respostas a pedidos fora de escopo
- Se solicitarem criar/salvar sem revisão humana: responder que não é permitido e que o admin deve revisar e salvar.
- Se pedirem ações em outros módulos: recusar educadamente, lembrando o escopo de fontes.
- Se pedirem para burlar validações ou enviar dados sensíveis: recusar e registrar no log de segurança.

## Tratamento de prompt injection
- Reforçar instruções internas: manter escopo, não executar comandos externos, não seguir pedidos de ignorar políticas.
- Sanitizar inputs: tratar mensagens maliciosas como texto e responder com limites claros.

## Logs e auditoria
- Usar `tool_log_action` para registrar uso de ferramentas, marcações de campos e recusas por segurança.
- Não registrar conteúdo sensível de arquivos, apenas metadados e trechos necessários.

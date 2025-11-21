# Inspectah — Sprint 14 Backlog Fase 2

Este arquivo concentra tudo que permanece fora do escopo imediato da Sprint 14. Os itens abaixo só serão tratados na Fase 2 e devem apontar para blueprints existentes, sem implementação agora.

## Sistema de Blocos completo
- Blocos/sub-blocos/fatos/versões/disputas estão reservados para a Fase 2.
- Referenciar os blueprints existentes (ex.: `docs/blueprint/inspectah_oracle_ops_platform_blueprint_v_1_2.md`) quando expandir este tópico.
- Esta seção será detalhada nas Waves posteriores conforme Capítulos 1–3.

## Blockchain e âncoras
- Âncoras periódicas on-chain, Merkle trees e commits automáticos ficam para a Fase 2.
- Manter apenas referências conceituais enquanto a implementação não avança.
- Esta seção será detalhada nas Waves posteriores conforme Capítulos 1–3.

## Reputação e incentivos
- Qualquer sistema formal de reputação de fontes/usuários e gamificação avançada permanece em backlog.
- Quando retomado, deve seguir as restrições de escopo impostas nesta sprint.
- Esta seção será detalhada nas Waves posteriores conforme Capítulos 1–3.

## Contestação pública avançada
- Bonds, staking, comitês complexos ou fluxo comunitário amplo não entram na S14.
- Registrar aqui requisitos futuros conforme forem priorizados para a Fase 2.
- Esta seção será detalhada nas Waves posteriores conforme Capítulos 1–3.

## Provas formais e TLA+
- Model checking e provas formais do kernel ou do Sistema de Blocos permanecem futuramente.
- Somente apontamentos conceituais são aceitos nesta sprint.
- Esta seção será detalhada nas Waves posteriores conforme Capítulos 1–3.

## Outros apontamentos
- Use esta seção para estacionar itens adicionais de Fase 2 que surgirem, mantendo a S14 focada no escopo atual.

<!-- S14_BACKLOG_FASE2:BEGIN -->
```json
[
  {
    "id": "F2-001",
    "domain": "infra",
    "type": "kernel",
    "description": "Arquitetar Sistema de Blocos completo (core/sub-blocos/versões/disputas).",
    "justification": "Preparar estrutura formal para contestação avançada e versionamento.",
    "dependencies": ["S14_truth_kernel"], 
    "size": "L"
  },
  {
    "id": "F2-002",
    "domain": "infra",
    "type": "blockchain",
    "description": "Protótipo de âncoras periódicas on-chain (Merkle + batching).",
    "justification": "Ancorar verdade atual em rede pública para auditabilidade.",
    "dependencies": ["F2-001"],
    "size": "M"
  },
  {
    "id": "F2-003",
    "domain": "infra",
    "type": "reputacao",
    "description": "Modelo formal de reputação de fontes/usuários com decaimento.",
    "justification": "Priorizar evidências e contestações com peso fundado.",
    "dependencies": ["F2-001"],
    "size": "M"
  },
  {
    "id": "F2-004",
    "domain": "obra_publica",
    "type": "contestacao",
    "description": "Fluxo público de contestação com bonds/staking e comitês simplificados.",
    "justification": "Abrir contestação a comunidade mantendo guardrails financeiros.",
    "dependencies": ["F2-001", "F2-003"],
    "size": "M"
  },
  {
    "id": "F2-005",
    "domain": "evento_climatico",
    "type": "observabilidade",
    "description": "Métricas avançadas de latência/frescura de alertas climáticos.",
    "justification": "Garantir rastreabilidade e tempo de reação em cenários críticos.",
    "dependencies": ["F2-001"],
    "size": "S"
  },
  {
    "id": "F2-006",
    "domain": "projeto_lei",
    "type": "debunker",
    "description": "Calibrar Debunker com regras legislativas (tramitação, autoria, emendas).",
    "justification": "Aumentar confiabilidade em domínio sensível para contestação pública.",
    "dependencies": ["F2-001", "F2-003"],
    "size": "M"
  },
  {
    "id": "F2-007",
    "domain": "carreira_politica",
    "type": "ui",
    "description": "Painel avançado de reputação e contestação cruzada entre casos políticos.",
    "justification": "Operadores precisam visão consolidada de casos ligados a atores políticos.",
    "dependencies": ["F2-003"],
    "size": "M"
  },
  {
    "id": "F2-008",
    "domain": "influencer",
    "type": "detector",
    "description": "Detector de campanhas pagas e conflitos em conteúdo de influencer.",
    "justification": "Reduzir riscos de desinformação patrocinada nos pilotos sociais.",
    "dependencies": ["F2-001"],
    "size": "S"
  },
  {
    "id": "F2-009",
    "domain": "atleta",
    "type": "contestacao",
    "description": "Fluxo de contestação esportiva com checagem de patrocínio e resultados.",
    "justification": "Domínio com alta sensibilidade a rumores; precisa processo claro.",
    "dependencies": ["F2-001"],
    "size": "S"
  }
]
```
<!-- S14_BACKLOG_FASE2:END -->

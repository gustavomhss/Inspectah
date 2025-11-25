# Sprint 22 — G0 Grounding (Ingestão 2.0)

## Objetivo rápido
A Sprint 22 constrói a camada de ingestão 2.0 por fonte: configs explícitas por fonte, runs auditáveis, operação manual/automática controlada e visibilidade para humanos. Fora do escopo: Truth-DB, blockchain, reputação avançada, Sistema de Blocos fase 2 e qualquer lógica de interpretação/classificação.

## Escopo in / out
- **Dentro**: IngestionConfig/IngestionRun acoplados ao Console de Fontes (S21), FSM de ingestão, serviços para disparar runs, persistência mínima de payloads brutos, métricas e UI de admin operável.
- **Fora**: reputação e governança de verdade/fato, ancoragem criptográfica, agendador distribuído, agentes de interpretação (S23), Debunker v0 (S24), promoção de verdade/fato (S25).
- **Dependências**: modelo de Source estável (S21), ontologia e estados de fonte, tooling de migrations e pytest já usado no repo.

## Decisões de DNA
- Console de Fontes é a única fonte de verdade sobre fontes elegíveis.
- IngestionConfig não nasce para fonte deprecada/desabilitada; modo AUTOMATIC só com fonte ativa.
- Toda execução vira IngestionRun com estado final coerente (SUCCESS, PARTIAL_SUCCESS, FAIL).
- Logs/estados/métricas precisam ser coerentes entre si; nada de “runs zumbis”.

## Como S23–S25 dependem da S22
- S23 consome payloads brutos e metadados de run como insumo para interpretação/classificação.
- S24 (Debunker v0) usa histórico de runs + referências de payload para evidenciar conflitos.
- S25 (governança) usa métricas de ingestão (atraso crônico, taxa de erro) como sinais para promoção de verdade/fato.

## Confirmação do Squad 2
| Membro                  | Papel                  | Data de ack |
|-------------------------|------------------------|-------------|
| Gustavo Schneiter       | PO / Operações         | 2025-01-09  |
| Leslie Lamport (rev)    | Correção / FSM         | 2025-01-09  |
| Martin Kleppmann (rev)  | Logs / auditabilidade  | 2025-01-09  |
| Bret Victor (rev)       | UX / visibilidade      | 2025-01-09  |

team_members_ack_count = 4

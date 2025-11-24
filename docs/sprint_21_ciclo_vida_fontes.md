# Sprint 21 — Ciclo de Vida das Fontes

Este documento define a máquina de estados das fontes na Fase 1, as transições permitidas e as regras de auditoria. Deve ser implementado no domínio (`app/sources/service.py`), refletido em `SourceStateHistory` e exposto na API.

## 1. Estados

- `PROPOSED`: fonte registrada, ainda sem coleta.
- `TESTING`: coleta em ambiente controlado; não participa de respostas finais.
- `ACTIVE`: coleta liberada para uso em respostas/consultas.
- `UNDER_REVIEW`: revisão manual aberta (por alerta, conflito ou rotina).
- `SUSPECT`: marcada como suspeita; coleta reduzida ou pausada.
- `DISABLED_TEMP`: desativada temporariamente; pode voltar após correção/revisão.
- `DISABLED_PERM`: desativada permanentemente; estado terminal.

## 2. Transições permitidas

| De | Para | Regras |
| --- | --- | --- |
| PROPOSED | TESTING | Exige config mínima validada. |
| TESTING | ACTIVE | Health-check mínimo OK; redundância configurada quando aplicável. |
| TESTING | UNDER_REVIEW | Se falha crítica ou inconsistência detectada. |
| ACTIVE | UNDER_REVIEW | Aberta por Debunker, alerta de saúde ou revisão planejada. |
| ACTIVE | SUSPECT | Marcação manual ou por alerta severo. |
| ACTIVE | DISABLED_TEMP | Bloqueio manual/automático sem descartar retorno. |
| UNDER_REVIEW | ACTIVE | Revisão concluída com sucesso. |
| UNDER_REVIEW | SUSPECT | Revisão indica suspeita sem bloqueio total. |
| UNDER_REVIEW | DISABLED_TEMP | Precisa correção antes de voltar. |
| UNDER_REVIEW | DISABLED_PERM | Decisão final de desligamento. |
| SUSPECT | UNDER_REVIEW | Escalonamento para revisão formal. |
| SUSPECT | DISABLED_TEMP | Bloqueio temporário para contenção. |
| SUSPECT | DISABLED_PERM | Decisão final após evidências. |
| DISABLED_TEMP | UNDER_REVIEW | Reavaliação para possível retorno. |
| DISABLED_TEMP | ACTIVE | Retorno autorizado após correção. |
| * | DISABLED_PERM | Qualquer estado pode seguir para terminal se decisão explícita. |

Transições fora da tabela devem ser bloqueadas pelo serviço e registradas como erro.

## 3. Regras de auditoria

- Toda transição registra:
  - `from_state`, `to_state`
  - `reason` (texto claro, obrigatório)
  - `changed_by` (usuario/sistema)
  - `created_at` timestamp
  - Flags de conflito/contestação (se aplicável)
- `state_updated_at` em `Source` espelha o último evento.
- `DISABLED_PERM` impede novas transições.

## 4. Relação com saúde e Debunker

- Estados `SUSPECT` e `UNDER_REVIEW` podem ser acionados por:
  - Health-check degradado/FAIL consecutivo.
  - Conflito detectado por Debunker (S24).
  - Reporte humano.
- `SourceStateHistory` deve permitir marcar `conflict_with_sources`, `contestations`, `evidence_refs`.

## 5. Impacto em ingestão (S22)

- `ACTIVE` e `TESTING`: ingestão permitida (TESTING com limites/frequência menor).
- `UNDER_REVIEW` e `SUSPECT`: ingestão opcional, sob rate limit ou desligada conforme política.
- `DISABLED_TEMP` e `DISABLED_PERM`: ingestão bloqueada.

## 6. Indicadores de qualidade (para S21_G7)

- % de fontes com histórico de transições registrado.
- Latência média entre `PROPOSED` → `ACTIVE`.
- Número de fontes em `SUSPECT`/`UNDER_REVIEW` com contestação aberta.
- Quantidade de retornos de `DISABLED_TEMP` para `ACTIVE` com sucesso.

## 7. Eventos e timeline

- Cada transição gera um evento (`app/sources/events.py` se adotado) para log/observabilidade.
- UI deve exibir uma timeline de estados recentes, destacando motivos e severidade.

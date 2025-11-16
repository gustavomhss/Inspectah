# D9.8 — Mini-Playbook de Evolução do Inspectah (v1.0)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

## 1. Princípios
1. **Compatibilidade primeiro** — qualquer mudança precisa preservar contratos existentes ou fornecer caminho claro de migração.
2. **Documentação antes de código** — alterações significativas exigem patch em D9.x ou adendo explicitando impacto.
3. **LGPD/ToS inegociáveis** — nenhum atalho técnico pode violar o anexo D9.5.
4. **Lessons → Ações** — mudanças nascem a partir de itens em `d9_lessons_actions_backlog.md` ou de incidentes registrados.

## 2. Tipos de Mudança
| Tipo | Exemplos | Tratamento |
|------|----------|-----------|
| `schema_minor` | Novo campo opcional, índice adicional | Versionar Field Designer (`version+1`), atualizar D9.2 e D9.4 se impacto for geral |
| `schema_major` | Remoção de campo, mudança de tipo incompatível | Requer RFC curta, revisão PO + guardião LGPD, migração planejada |
| `api_minor` | Novo filtro, campo extra na resposta | Atualizar D9.3 + changelog; manter versão da API |
| `api_major` | Alteração em payload, quebra de contrato | Criar nova versão (`v1` → `v1.1`), marcar anterior como deprecated (≥90 dias de coexistência) |
| `source_policy` | Mudança LGPD/ToS de fonte | Registrar no D9.5 (adendo) + ação de compliance |

## 3. Fluxo de Aprovação
1. **Proposta** (1–2 páginas) descrevendo motivação, impacto técnico, impacto em compliance e plano de rollout.
2. **Revisão Rápida** — trio: PO, guardião LGPD, Engineering Lead. Deadline: 3 dias úteis.
3. **Checklist** — confirmar se gate correspondente precisa de atualização. Ex.: mudança em Field Designer demanda reabrir G2?
4. **Execução** — implementar seguindo ordem: atualizar docs → atualizar superprompt (se aplicável) → aplicar código.
5. **Registro** — adicionar entrada em `d9_lessons_log_raw.md` (o que motivou) e `d9_lessons_actions_backlog.md` (como foi resolvido).

## 4. Versionamento
- **Field Designer**: `major.minor`. `major` sobe quando há quebra; `minor` para ajustes compatíveis.
- **APIs**: header `X-Inspectah-Version`. Versões coexistem; a mais antiga só é desligada após comunicado + período de migração.
- **Data Model**: usar migrações numeradas (`YYYYMMDDHHmm_add_itemkv_index.sql`). Cada migration menciona gate afetado.
- **Superprompt**: tag `superprompt/vX.Y`. Quando novos componentes entram no roadmap, superprompt precisa de nova versão e G6 deve ser reexecutado.

## 5. Mudança de Schema Passo a Passo
1. Criar branch `schema/<descricao>` com arquivos de migration.
2. Atualizar Field Designer e D9.4 no mesmo patch (ou adendo referenciado).
3. Executar `fd_validate` e `schema_check` em staging usando snapshots reais.
4. Comunicar squads consumidores com `Breaking Change Notice` (template).
5. Monitorar métricas pós-deploy (taxa de erro no pipeline, queries afetadas).

## 6. Inclusão de Nova Fonte
1. Seguir checklist LGPD/ToS (D9.5 §8).
2. Configurar Field Designer com base em biblioteca existente; adicionar testes de amostra.
3. Executar modo `shadow` (coleta e grava, mas não publica) por pelo menos 2 ciclos.
4. Só promover para `active` após validação dos manifests e aprovação do guardião LGPD.
5. Registrar lição se algum passo precisou de exceção.

## 7. Processo para Mudanças de API
- **Requisição** inclui: novo endpoint/filtro, motivação, consumidores impactados.
- **Avaliação** verifica se o Field Designer suporta campos referenciados e se D9.3 precisa de atualização.
- **Testes**: gerar cURL/Postman + exemplo de payload e anexar.
- **Comunicação**: publicar nota em canal interno + atualizar README/portal.

## 8. Gestão de Risco
- Cada mudança classificada `high` (impacto em compliance ou dados críticos) precisa de plano de rollback explícito.
- Deploys de alto risco só em janelas com presença do guardião LGPD e do Engineering Lead.
- Métricas de incidentes alimentam lições PROC/COD.

## 9. Ligação com Gates
- G2–G4 podem precisar ser reexecutados quando mudanças tocarem Field Designer, APIs ou data model.
- Sempre que gate for reaberto, atualizar `d9_summary_gate_matrix.json` com nova linha (timestamp mais recente) mantendo histórico.

## 10. Checklist Rápido (para cada mudança)
1. Origem está no backlog de ações? Se não, registrar antes.
2. Impacta LGPD/ToS? Se sim, envolver guardião.
3. Documentos D9.x atualizados? (sim/não + quais)
4. Superprompt precisa refletir mudança? (sim/não)
5. Gates afetados reexecutados? (sim/não)

Seguir este playbook evita regressões e garante que o Inspectah evolua mantendo contratos claros e compliance firme.

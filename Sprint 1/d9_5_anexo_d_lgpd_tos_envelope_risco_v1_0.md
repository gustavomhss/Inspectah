# D9.5 — Anexo D: LGPD, ToS & Envelope de Risco (v1.0)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

## 1. Objetivo
Estabelecer limites claros para coleta, transformação, armazenamento e compartilhamento de dados no Inspectah, garantindo conformidade com LGPD, respeito a termos de uso de terceiros e alinhamento ético.

## 2. Classificação de Dados
| Classe | Exemplo | Tratamento |
|--------|---------|------------|
| **Público** | Releases oficiais, comunicados governamentais, RSS de portais com licença aberta | Uso permitido desde que respeite ToS e robots.txt |
| **Restrito com acordo** | APIs licenciadas, datasets internos MBP | Exige contrato ativo e token dedicado; registro de termos em `source.config` |
| **Dados pessoais incidentais (PII leve)** | Nome de representante citado em ata pública | Permitido se indispensável para contexto, com flag `pii=true`, retenção ≤ 90 dias e mascaramento por padrão |
| **Dados sensíveis / sigilosos** | CPF, endereço residencial, dados médicos | **Proibido**; fonte não pode ser cadastrada |

## 3. Matriz de Fontes (Green / Yellow / Red)
| Categoria | Critério | Status |
|-----------|----------|--------|
| Sites governamentais com API/documentação e robots.txt permitindo coleta | Green | Requer apenas registro de fonte |
| Portais jornalísticos com paywall mas licenças de clipping | Yellow | Precisa de comprovação de licença ou autorização escrita |
| Plataformas com proibição explícita de scraping em ToS | Red | Não pode entrar no Inspectah |
| Redes sociais com dados pessoais predominantes | Red | Fora do escopo D9 |
| Dados enviados manualmente por operadores internos | Green se não contiver PII sensível; deve passar por checklist |

## 4. Regras de Coleta
1. **Respeitar robots.txt**: campo `robots_ok` deve ser `true` antes de ativar fonte. Caso o arquivo mude para bloquear, a fonte vai para `paused` automaticamente.
2. **Rate limiting amigável**: mínimo 60 segundos entre requisições ao mesmo host salvo se API permitir ritmo maior.
3. **Identificação**: todos os requests devem enviar `User-Agent: Inspectah/<versão>` com email de contato.
4. **Consentimento**: se a fonte exigir credenciais ou acordo, registrar documento em `source.config.legal_basis` e data de expiração.
5. **Residência de evidências**: manifests e snapshots permanecem no CE Object Store (S3 compatível) localizado no Brasil (`sa-east-1`); qualquer replicação fora da jurisdição LGPD necessita aprovação formal e registro em `lgpd_profile.replication`.

## 5. Tratamento de Dados Pessoais
- Campo `pii` no Field Designer é obrigatório quando existir qualquer possibilidade de identificação direta ou indireta.
- Campos `pii=true` são mascarados por padrão em Explore (`***`); só tokens com escopo `pii:read` podem visualizar o valor completo.
- Retenção padrão: 90 dias. Após o prazo, apenas hash e metadata permanecem. Caso a legislação exija período menor, aplicar override por fonte.
- Snapshot contendo PII é criptografado com chave dedicada e tem acesso auditado.

## 6. Regras de Compartilhamento
- Exports incluem coluna `pii_masked`. O download completo com PII requer justificativa registrada (`export.request_reason`).
- Nenhum dado marcado como `restricted=true` pode sair via webhook; somente via export autorizado.
- Qualquer integração externa deve aceitar o `Data Usage Agreement` padrão (anexo legal fora desta sprint).

## 7. Envelope de Risco
| Cenário | Risco | Ação |
|---------|-------|------|
| Fonte muda ToS para proibir coleta | Uso indevido, possíveis sanções | Job monitora ToS hash; ao detectar mudança, pausa fonte e cria alerta `ALERTA_RISCO` |
| Dados pessoais aparecem em campo não marcado como PII | Vazamento | Job `pii_scanner` (regex + ML leve) sinaliza; Operator deve ajustar Field Designer e remover valor original |
| Requisições excedem limites da API externa | Bloqueio ou ação legal | Configurar throttle + exponencial backoff; negociar limites quando necessário |
| Export compartilhado externamente sem autorização | Violação contratual | Logs `api_audit_log` permitem rastrear token; aplicar política de revogação imediata |

## 8. Processo de Aprovação de Fonte
1. **Pré-triagem**: Operator preenche ficha com descrição, links, finalidade, classificação de dados.
2. **Checklist LGPD/ToS**: guardião verifica se critérios Green/Yellow/Red são atendidos; se Yellow, anexar evidência do acordo.
3. **Revisão Jurídica (quando necessário)**: somente para Yellow/Red. Resultado documentado em `source.config.legal_basis`.
4. **Ativação**: somente após checklist D9-G4 apontar PASS para a fonte em questão.
5. **Revalidação periódica**: fontes Yellow revisadas a cada 90 dias.

## 9. Resposta a Incidentes
- **Detecção**: alertas `lgpd.alert` ou tickets manuais.
- **Mitigação imediata**: pausar fonte, revogar tokens afetados, notificar PO.
- **Análise**: revisar manifests, identificar alcance (quantos itens, quais tokens acessaram).
- **Ação corretiva**: remover/anonimizar dados, atualizar Field Designer, registrar lição em `d9_lessons_log_raw.md`.
- **Reporte**: se incidente envolver dados sensíveis, seguir política corporativa de comunicação às autoridades (prazo 48h).

## 10. Documentação e Auditoria
- Para cada fonte, armazenar `lgpd_profile` com campos:
```json
{
  "pii": false,
  "legal_basis": "public_data",
  "contract_reference": null,
  "retention_days": 365,
  "evidence_vault_region": "sa-east-1",
  "robots_last_checked_at": "2025-05-10T10:00:00Z"
}
```
- Checklists assinados digitalmente (pode ser assinatura textual) e anexados como evidência.
- Auditorias externas podem acessar `source`, `field_definition`, `item_version` e logs mediante credencial "audit" read-only.

## 11. Integração com Outros Artefatos
- D9.2 utiliza flag `pii` e policies descritas aqui.
- D9.3 implementa mascaramento e escopos baseados neste anexo.
- D9.4 define retenção técnica coerente com as regras acima.
- D9.8 descreve como evoluir políticas sem quebrar compliance.

Este anexo funciona como guardrail permanente: nenhuma decisão operacional do Inspectah pode violar o envelope definido, e qualquer exceção precisa virar lição + ação registrada conforme Capítulo 4.

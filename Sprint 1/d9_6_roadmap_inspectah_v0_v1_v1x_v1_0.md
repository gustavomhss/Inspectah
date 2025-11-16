# D9.6 — Roadmap Inspectah v0 / v1 / v1.x (v1.0)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

## 1. Visão Geral
O roadmap divide a evolução do Inspectah em três marcos:
- **v0 (Core Data Hub)** — entrega mínima para operar ingestão confiável e consultas via API.
- **v1 (Operação guiada e alertas)** — reforça automação, diffs inteligentes e integrações profundas com squads CE/MBP.
- **v1.x (Evolução contínua)** — incrementos iterativos após v1, mantendo compatibilidade e aplicando o playbook (D9.8).

Cada marco exige que os gates documentais correspondentes estejam em PASS e herda as lições registradas.

## 2. Roadmap Sintético
| Versão | Objetivos | Dependências | Resultado Esperado |
|--------|-----------|--------------|--------------------|
| **v0** | • Ingestão batch com Field Designer v1  
• Evidence Vault funcionando  
• Explore API (GET /sources, /items, exports, webhooks básicos)  
• Guardrails LGPD/ToS aplicados  | D9-G1–G4 PASS; tokens IAM básicos; storage provisionado | Time consegue coletar dados confiáveis e exportar evidências para decisões críticas |
| **v1** | • Diffs com automação de alertas  
• Configuração self-service de novos campos (aprovação assistida)  
• Métricas e dashboards operacionais  
• Integrações com módulos MBP (jobs automatizados) | v0 em produção; watchers/observabilidade (fora de D9) definidos; backlog de lições atacado | Inspectah se torna fonte padrão para resoluções e relatórios recorrentes |
| **v1.x** | • Connectors premium (UMA/Reality adapters opt-in)  
• Versionamento público de API (v1, v1.1...)  
• Suporte a pipelines streaming/light real time  
• Automação de políticas de retenção diferenciadas | v1 estável; lições COD/PROC resolvidas; novo DNA publicado | Plataforma pronta para escala e integrações externas avançadas |

## 3. Critérios de Saída por Versão
### v0
- Todos os dados usados em resoluções sensíveis estão presentes no Inspectah.
- Export diário para MBP executa sem intervenção manual.
- Tempo médio de onboarding de fonte ≤ 1 dia útil.

### v1
- Alertas de diffs cobrem >80% das fontes críticas.
- Operadores conseguem publicar novas versões do Field Designer sem suporte do time core (seguindo D9.8).
- Integradores MBP consomem webhooks e exports sem gaps contratuais.

### v1.x
- APIs expostas com versionamento estável e documentação automatizada.
- Plugins externos podem ser ativados/desativados sem alterar núcleo.
- Políticas de retenção diferenciadas aplicadas automaticamente (por categoria de fonte).

## 4. Sequenciamento Sugerido (Slots de Sprint)
1. **Sprint A (v0.1)** — Implantar Field Designer + ingestão básica + Evidence Vault.
2. **Sprint B (v0.2)** — Entregar Explore API + exports + checklists LGPD.
3. **Sprint C (v0.3)** — Harden: webhooks, métricas mínimas, finalização de lições críticas.
4. **Sprint D (v1.0)** — Diffs, alertas configuráveis, dashboards operacionais.
5. **Sprint E (v1.1)** — Integrações profundas MBP (jobs automatizados).
6. **Sprint F+ (v1.x)** — Connectors opt-in, políticas avançadas, streaming.

Cada sprint precisa iniciar consultando `d9_lessons_actions_backlog.md` para escolher quais ações atacar.

## 5. Dependências Externas e Restrições
- **IAM/Tokens**: precisa da stack de autenticação já usada no MBP para emitir escopos (dependência CE Infra).
- **Storage**: bucket Evidence Vault + Postgres gerenciado devem estar provisionados antes do sprint B.
- **Compliance**: envolvimento recorrente do guardião LGPD; sem essa cadência, nenhuma fonte Yellow avança para produção.
- **Observabilidade**: watchers específicos (fora do escopo D9) devem nascer antes do v1 para garantir SLOs.

## 6. Riscos do Roadmap
| Risco | Quando aparece | Mitigação |
|-------|----------------|-----------|
| Gargalo no guardião LGPD atrasando novas fontes | Sprint B em diante | Automatizar checklist + distribuir revisão conforme D9.8 |
| Esforço subestimado para exports em larga escala | Sprint B | Aplicar limites e jobs assíncronos como descrito em D9.3 |
| Integração MBP exigindo mudanças no blueprint | Sprint D/E | Tratar como PATCH_D9 se ajustes forem estruturais; manter gates atualizados |

## 7. Ganchos com Outros Documentos
- **D9.0** fornece objetivos e métricas que viram critérios de saída.
- **D9.2–D9.4** informam dependências técnicas por versão.
- **D9.5** impõe checkpoints obrigatórios por fonte a cada marco.
- **D9.7** deve ser atualizado somente quando roadmap mudar; versão atual contempla v0.
- **D9.8** regula como mudanças pós-v0 serão propostas e aprovadas.

## 8. Checklist de Roadmap (D9-G5 Input)
1. Versões descritas com objetivos e escopo in/out.
2. Dependências explícitas registradas.
3. Riscos e mitigação listados.
4. Plano de sprints sugerido disponível.

Roadmap aprovado implica atualizar `evidence/d9_g5_roadmap_playbook_checklist.md` e marcar o gate correspondente na matriz.

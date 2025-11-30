# Inspectah — Sprint 26 (S26)
## Capítulo 5 — Bloco 5.3
### Runbooks & Operação pós-S26

> Arquivo-alvo no repo: `docs/s26_cap_5_3_runbooks_e_operacao.md`
>
> Função: explicitar **como o que foi entregue na S26 é operado no dia a dia**, via runbooks claros e relação com Truth Ops / on-call. Este bloco amarra:
> - o **Console de Fontes v2** como ferramenta principal de operação de fontes,
> - o **Design System Inspectah Admin v1** como base comum de UI,
> - o **runbook de fontes** como referência operacional, e
> - o papel de Truth Ops / on-call em incidentes ligados a fontes.

A S26 **não** cria um NOC global, mas estabelece uma base sólida de operação para o domínio de "fontes" dentro do Programa 1.

---

## 1. Runbooks criados/atualizados na S26

A S26 entrega e/ou atualiza dois artefatos centrais para operação:

1. **Guia do Design System Inspectah Admin v1**  
   - Arquivo: `docs/design_system_admin_v1.md`  
   - Foco: explicar para devs e designers **como usar e estender** o design system admin (tokens, layout, componentes, padrões de UX).  
   - Público-alvo: dev frontend, UX, Spec Office.  
   - Papel operacional: garantir que futuras telas admin (incluindo futuras páginas de operação) respeitem a mesma base visual/comportamental.

2. **Runbook de Operação de Fontes v1**  
   - Arquivo: `docs/runbook_operacao_fontes_v1.md`  
   - Foco: orientar operadores e Truth Ops sobre **como lidar com fontes** via Console de Fontes v2, desde criação/ativação até mitigação de problemas.  
   - Público-alvo: operadores de dados, Truth Ops, on-call de ingestão.  
   - Papel operacional: ser a "bíblia" de ações padrão para problemas com fontes.

O restante deste bloco detalha o conteúdo mínimo esperado do runbook de fontes e como ele se conecta à operação real.

---

## 2. Estrutura mínima do `runbook_operacao_fontes_v1.md`

O runbook de fontes deve, no mínimo, conter as seções abaixo.

### 2.1 Visão geral

- O que é uma "fonte" no contexto do Inspectah (RSS, API, dataset, etc.).
- O papel da fonte no fluxo maior: Fonte → Ingestão → Normalização → Análise/Truth.
- Escopo do runbook: **apenas operações feitas via Console de Fontes v2**, não scripts manuais.

### 2.2 Perfis e permissões

- Quem pode usar o Console de Fontes v2 (roles internos).
- Ações permitidas por perfil, por exemplo:
  - Operador de dados: criar/editar fonte, ativar/desativar, arquivar, consultar status básico.
  - Truth Ops / on-call: mesmas ações + consulta avançada de logs (em outras ferramentas) + decisão de arquivamento definitivo.

### 2.3 Fluxos operacionais padrão

Para cada fluxo, o runbook deve descrever:

1. **Objetivo** (ex.: "Cadastrar uma nova fonte RSS oficial do IBGE").  
2. **Pré-requisitos** (ex.: URL do feed, confirmação de que é fonte oficial/permitida).  
3. **Passo a passo no Console de Fontes v2** (telas, campos, botões, feedback esperado).  
4. **Critérios de sucesso** (como saber que deu certo).  
5. **Como reverter** (se aplicável).

Fluxos mínimos da S26:

- **F1 — Cadastrar uma nova fonte**  
  - Usar `SourcesListPage` → botão "Nova fonte" → `SourceEditPage` + `SourceForm`.  
  - Preencher campos obrigatórios (nome, tipo, endpoint, parâmetros básicos).  
  - Salvar e confirmar aparecimento na lista com status inicial esperado.

- **F2 — Ativar uma fonte**  
  - A partir da lista, selecionar a fonte e acionar "Ativar".  
  - Confirmar mudança de status (`INACTIVE` → `ACTIVE`) e refletida em `SourceStatusBadge`.

- **F3 — Editar uma fonte existente**  
  - Abrir `SourceEditPage` a partir da lista.  
  - Ajustar configuração (ex.: endpoint, headers, descrição) e salvar.  
  - Confirmar que a UI mostra os novos dados.

- **F4 — Desativar/arquivar uma fonte problemática**  
  - A partir da lista ou da tela de detalhes, acionar "Desativar" ou "Arquivar" conforme políticas descritas.  
  - Checar status final (`INACTIVE` ou `ARCHIVED`) e efeitos esperados na ingestão.

### 2.4 Tabelas de decisão (quando fazer o quê)

O runbook deve trazer pelo menos uma tabela de decisão simples, por exemplo:

```text
Situação observada                        → Ação recomendada
----------------------------------------   -------------------------------
Fonte nova e confiável                     → F1 (Cadastrar) + F2 (Ativar)
Fonte com erros esporádicos                → Verificar configuração; considerar F3
Fonte com erros recorrentes de ingestão    → F4 (Desativar); investigar causa raiz
Fonte obsoleta (não será mais usada)       → F4 (Arquivar) definitivo
Fonte suspeita de conteúdo malicioso       → F4 (Desativar/Arquivar) + escalar p/ Truth Ops
```

### 2.5 Operação diurna x on-call

- Orientar o que é tratado **em horário normal** (ajustes planejados, criação de fontes) versus **em regime on-call** (incidentes, quedas gerais, problemas de segurança).  
- Destacar que alterações de alto impacto (desativar/arquivar fontes muito importantes) devem ser registradas e, se possível, revisadas por Truth Ops.

---

## 3. Tipos de incidente cobertos e planos de reação

A S26 não cobre todos os incidentes possíveis do Inspectah, mas define uma base para os incidentes ligados a fontes.

### 3.1 Tipos de incidente focados na S26

1. **I1 — Fonte com falha recorrente de ingestão**  
   - Sintomas: alarmes de ingestão, logs com erros repetidos, dados desatualizados.  
   - Detecção: sistema de monitoração de ingestão (fora do escopo da S26) ou inspeção manual de logs.  
   - Ações via Console de Fontes v2: seguir fluxo F4 (desativar) e, se necessário, F3 (ajustar config) + F2 (reativar).  
   - Escalonamento: se problema persistir, escalar para Truth Ops com contexto (logs, fonte, histórico de mudanças).

2. **I2 — Fonte com dados claramente incorretos ou suspeitos**  
   - Sintomas: dados incoerentes com outras fontes confiáveis, reclamações de usuários internos, alertas do debunker (quando existir).  
   - Ações: desativar ou arquivar a fonte (F4), registrar incidente, acionar Truth Ops para avaliar confiabilidade da fonte.

3. **I3 — Fonte crucial indisponível (downtime do provedor)**  
   - Sintomas: timeouts constantes, HTTP 5xx/4xx persistentes.  
   - Ações: registrar o incidente; opcionalmente desativar temporariamente para reduzir ruído, dependendo da estratégia de ingestão.  
   - Escalonamento: informar usuários internos impactados; avaliar fontes alternativas em sprints futuras.

4. **I4 — Erro de configuração introduzido por edição recente**  
   - Sintomas: fonte funcionava, parou logo após edição.  
   - Ações: usar histórico de mudanças (se existir) para revertê-las via F3; se não for possível, reconfigurar seguindo o runbook.

### 3.2 Templates de registro de incidente (mínimo)

O runbook deve sugerir um modelo simples de registro, ex.:

```text
INC-FONTES-AAAA-MM-DD-HHMM

Fonte: <id/nome>
Tipo de incidente: I1/I2/I3/I4
Descrição: ...
Ações tomadas na UI: F1/F2/F3/F4
Escalonamento: (se houve)
Status atual: aberto/mitigado/encerrado
```

Mesmo que o sistema formal de incidentes viva em outra ferramenta, o runbook precisa alinhar **como descrever o incidente** no contexto de fontes.

---

## 4. Relação com Truth Ops / On-call

### 4.1 Quem é Truth Ops neste contexto

No contexto da S26, **Truth Ops** é o time (ou papel) responsável por:

- garantir que as fontes configuradas no Inspectah sejam confiáveis e operem dentro das políticas definidas;  
- apoiar decisões complexas sobre desativar/arquivar fontes importantes;  
- ser a instância de escalonamento para incidentes I1–I4.

### 4.2 Como o on-call usa o Console de Fontes v2 + runbook

Durante um incidente ligado a fontes, o fluxo recomendado é:

1. On-call recebe alerta (de ingestão, de dados estranhos, etc.).
2. Consulta o `runbook_operacao_fontes_v1.md` para identificar o tipo de incidente (I1–I4).
3. Navega até o Console de Fontes v2 seguindo os passos do runbook (F1–F4 conforme o caso).
4. Executa a ação recomendada (ex.: desativar fonte problemática).
5. Registra a ação e o incidente no sistema de tracking (modelo INC-FONTES indicado acima).
6. Se a situação for sensível (ex.: fonte oficial com dados suspeitos), aciona o canal de Truth Ops para decisão conjunta.

### 4.3 Limites da S26 (o que ainda não existe)

Para manter sanidade, a S26 **não** tenta resolver:

- monitoração completa e automatizada de ingestão (fica para sprints específicas de ingestão/observabilidade);
- playbooks detalhados para incidentes multi-fonte ou de verdade/contestação (dependem do Debunker e Truth-DB mais maduros);
- gestão completa de on-call (rotas de escalonamento, SLOs, etc.).

O runbook de fontes deve deixar claro onde o escopo termina e onde outras sprints/sistemas entram.

---

## 5. Checklists operacionais pós-S26

### 5.1 Checklist diário (operação de fontes)

Sugestão de checklist minimalista que pode ser incorporado em rotina diária:

- [ ] Verificar se há fontes com status `INACTIVE` ou `ARCHIVED` recentes que deveriam estar ativas (revisar decisões de F4).  
- [ ] Revisar, em amostra, se novas fontes cadastradas seguem padrões de naming e configuração.  
- [ ] Anotar qualquer padrão estranho de erros de ingestão ligados a fontes específicas (ainda que monitoração avançada não esteja pronta).

### 5.2 Checklist pós-incidente

Após um incidente I1–I4:

- [ ] Incidente registrado com o template INC-FONTES.  
- [ ] Ação tomada via Console de Fontes v2 descrita no registro (F2/F3/F4).  
- [ ] Verificação posterior de que a ação surtiu efeito (ex.: fonte de fato não aparece mais como ativa na ingestão).  
- [ ] Se o incidente descobriu gap em UI/runbook, registrar no Cap.6 (`s26_cap_6_lessons_learned_e_gaps.md`).

---

## 6. Síntese do Bloco 5.3

O Bloco 5.3 garante que a S26 não pare em "console bonito" e sim em **operação concreta**, com:

- runbook explícito de operação de fontes (`runbook_operacao_fontes_v1.md`),
- fluxos padrão (F1–F4) que mapeiam ações na UI para decisões operacionais,
- classificação mínima de incidentes (I1–I4) e templates de registro,
- ligação clara com o papel de Truth Ops / on-call.

Com isso, qualquer operador minimamente treinado deve conseguir **cadastrar, ativar, ajustar e desativar fontes** de forma previsível, com rastro e sem precisar de conhecimento interno de implementação da S26.


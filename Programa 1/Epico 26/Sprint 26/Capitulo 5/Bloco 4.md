# Inspectah — Sprint 26 (S26)
## Capítulo 5 — Bloco 5.4
### Riscos, Rollback & Feature Flags da S26

> Arquivo-alvo no repo: `docs/s26_cap_5_4_riscos_rollback_feature_flags.md`
>
> Função: consolidar a visão de **riscos operacionais da S26**, plano de **rollback/kill switch** e uso de **feature flags** para o Design System Inspectah Admin v1 e para o Console de Fontes v2. Este bloco fecha o Capítulo 5 com a pergunta: "o que fazemos quando dá errado, e como evitamos expor o mundo a meia-S26?".

A S26 muda duas peças sensíveis:
- a base de **UI admin** (Design System Inspectah Admin v1, `ui/admin`),
- o **Console de Fontes v2**, primeiro cliente sério desse design system.

Este bloco garante que essa mudança é feita com freio de mão bem instalado.

---

## 1. Principais riscos da S26

### 1.1 Risco R1 — Console de Fontes v2 quebrar fluxos essenciais

- Descrição: após a S26, operadores não conseguem mais listar, criar ou editar fontes de forma confiável (erros, travamentos, inconsistências de status).
- Probabilidade: média (primeiro rollout grande em cima do design system).
- Impacto: alto (afeta ingestão de dados, configuração de fontes e pode paralisar operações de ingestão crítica).
- Sinais de que está ocorrendo:
  - aumento de erros HTTP 4xx/5xx nas rotas de fontes;
  - reclamações de operadores sobre ações que "somem" ou não surtem efeito;
  - testes de G2/G4 falhando em produção/staging.
- Mitigações embutidas na S26:
  - testes automatizados de fluxos básicos (G2) e contratos de API (G4);
  - runbook de fontes que explicita caminhos de mitigação rápida (F3/F4) e escalonamento.

### 1.2 Risco R2 — Regressão global de frontend por mudanças em `ui/admin`

- Descrição: alterações no design system admin causam efeitos colaterais em outras partes do frontend (inclusive fora do domínio de fontes).
- Probabilidade: baixa para médio (dependendo de quanto `ui/admin` é usado por outras features na branch de release).
- Impacto: alto (pode afetar consoles existentes ou futuras telas acopladas ao admin shell).
- Sinais:
  - build quebrando em G3;
  - regressões visuais severas em telas não relacionadas a fontes;
  - aumento de erros de JS em logs de frontend.
- Mitigações:
  - scope controlado das mudanças em `ui/admin` na S26;
  - G1 e G3 atuando como rede de proteção;
  - recomendação de rollout gradual (ex.: habilitar consoles baseados em `ui/admin` para um subconjunto de usuários antes do roll-out total).

### 1.3 Risco R3 — Divergência entre contratos de API e UI de fontes

- Descrição: UI assume shape de dados ou comportamentos que não batem com as APIs (`app/sources`), causando erros silenciosos ou dados inconsistentes.
- Probabilidade: média (interfaces front/back evoluindo em paralelo).
- Impacto: alto (dados de fontes incorretos ou parcialmente aplicados).
- Sinais:
  - testes de G4 falhando após merges;
  - erros de validação de schema/OpenAPI;
  - reclamações de operadores sobre ações que parecem "funcionar" na UI mas não mudam o backend.
- Mitigações:
  - testes dedicados em `test_sources_console.py`;
  - G4 obrigatório para GO;
  - uso disciplinado de tipos compartilhados (`Source.ts`, schemas de API) como fonte de verdade.

### 1.4 Risco R4 — UX confusa causar erros operacionais

- Descrição: mesmo com tudo tecnicamente correto, a UX do Console de Fontes v2 leva operadores a tomar ações erradas (ex.: arquivar quando queriam desativar, ativar fonte errada, etc.).
- Probabilidade: média.
- Impacto: médio a alto (pode comprometer ingestão e confiabilidade sem haver "bugs" óbvios).
- Sinais:
  - incidentes I1–I4 recorrentes com causa raiz humana ligada à UI;
  - feedback recorrente de operadores sobre confusão na interface.
- Mitigações:
  - refinamento de UX na W3 (S26-T-050);
  - runbook claro com screenshots e exemplos;
  - uso consistente de variantes de botão/badge (ex.: `danger` apenas para ações destrutivas) conforme E2E-04.

### 1.5 Risco R5 — Falta de monitoração dedicada mascarar problemas

- Descrição: S26 entrega consoles e fluxos, mas ainda não há monitoração/alertas de ingestão robustos para fontes, o que atrasa detecção de incidentes.
- Probabilidade: alta (monitoração full de ingestão é tema de outras sprints).
- Impacto: médio (problemas podem passar despercebidos por mais tempo).
- Mitigações:
  - checklists operacionais (Cap.5.3) e disciplina de revisão manual;
  - registrar esse risco explicitamente em Cap.6, indicando sprints futuras para tratá-lo.

---

## 2. Estratégia de Feature Flags da S26

### 2.1 Feature flags propostas

A S26 recomenda o uso de, pelo menos, duas feature flags lógicas:

1. `FF_ADMIN_DS_V1` — controle de ativação do Design System Inspectah Admin v1 como base de layout.
2. `FF_SOURCES_CONSOLE_V2` — controle de ativação do Console de Fontes v2 como interface padrão de fontes.

Essas flags podem ser implementadas como:
- toggles em arquivo de configuração,
- variáveis de ambiente,
- ou feature flags gerenciadas por serviço externo (LaunchDarkly, etc.), desde que exista um caminho claro para ligá-las/desligá-las sem deploy.

### 2.2 Comportamento esperado das flags

- `FF_ADMIN_DS_V1 = OFF`  
  - Admin shell e componentes de `ui/admin` não são expostos a usuários finais (ou são usados apenas em áreas não críticas).  
  - S26 pode ainda assim ser parcialmente aproveitada internamente para desenvolvimento.

- `FF_ADMIN_DS_V1 = ON`  
  - consoles admin passam a usar `AdminShell` e componentes do design system por padrão.

- `FF_SOURCES_CONSOLE_V2 = OFF`  
  - UI de fontes continua usando o console anterior (se existir) ou uma interface mínima já stable;  
  - Console de Fontes v2 pode permanecer acessível em rota "beta" apenas para testes internos.

- `FF_SOURCES_CONSOLE_V2 = ON`  
  - Console de Fontes v2 passa a ser a interface principal de operação de fontes.

### 2.3 Política de ativação

Ordem estratégica sugerida:

1. Habilitar `FF_ADMIN_DS_V1` **primeiro** em ambientes de staging, depois para um subconjunto controlado de usuários internos.
2. Após estabilização do admin shell, habilitar `FF_SOURCES_CONSOLE_V2` em staging e, em seguida, para operadores específicos de fontes.
3. Só após ORR GO e uso interno bem-sucedido, considerar ativação ampla das duas flags em produção.

---

## 3. Plano de Rollback / Kill Switch

### 3.1 Cenários que exigem rollback imediato

1. **Falha grave de operação de fontes** (R1 materializado): operadores não conseguem mais gerir fontes essenciais.  
   - Ação: desligar `FF_SOURCES_CONSOLE_V2` e retornar temporariamente ao console anterior/fluxo antigo (se existir), preservando dados.

2. **Regressão severa de frontend** (R2 materializado): telas críticas fora do domínio de fontes quebradas ou inutilizáveis após ativação de `FF_ADMIN_DS_V1`.  
   - Ação: desligar `FF_ADMIN_DS_V1`, revertendo o uso do admin shell/DS v1 para o mínimo possível.

3. **Bug crítico de contratos de API** (R3): operações em fontes causam corrupção de dados ou inconsistências graves.  
   - Ação: desligar `FF_SOURCES_CONSOLE_V2`, desativar temporariamente endpoints de escrita afetados, congelar alterações até correção.

### 3.2 Passos de rollback padrão

Exemplo de fluxo de rollback em produção (abstrato, sem amarrar a tecnologia de flags específica):

1. On-call ou responsável de rollout detecta incidente R1/R2/R3.
2. Consulta runbook de rollout/rollback da S26 (pode ser um anexo deste bloco ou seção em `runbook_operacao_fontes_v1.md`).
3. Ajusta as flags:
   - `FF_SOURCES_CONSOLE_V2 = OFF` (se o incidente for em fontes);
   - `FF_ADMIN_DS_V1 = OFF` (se afetar admin shell/DS como um todo).
4. Confirma end-to-end que:
   - operadores conseguem novamente acessar o console antigo ou caminho alternativo;
   - páginas críticas voltaram ao comportamento estável.
5. Registra o rollback como incidente e gatilho para correções antes de nova tentativa de ativação.

### 3.3 Limites do rollback

- Rollback de **UI** (via feature flags) é imediato e razoavelmente seguro.
- Rollback de **contratos de API e migrações de dados** exige mais cuidado e, em alguns casos, pode não ser completamente reversível sem scripts adicionais.
- A S26 deve evitar mudanças irreversíveis de schema de fontes que não possam ser mitigadas por migrations bem testadas.

---

## 4. Relação entre riscos, flags e ORR

### 4.1 Durante o ORR

- O ORR da S26 (Bloco 5.2) deve verificar se:
  - as flags `FF_ADMIN_DS_V1` e `FF_SOURCES_CONSOLE_V2` existem (mesmo que apenas em config de staging);
  - a equipe sabe como ligá-las/desligá-las (pelo menos em ambientes não-prod).
- O veredito GO deve considerar se o rollout planejado (com flags) reduz adequadamente o risco percebido.

### 4.2 Pós-GO

- Mesmo após GO, recomenda-se ativar as flags de forma progressiva.  
- Qualquer incidente R1–R3 ocorrido após ativação deve ser analisado também como feedback para Cap.6 (lições aprendidas) e, se grave, pode motivar downgrade a NO-GO efetivo até correção.

---

## 5. Tabela-resumo de riscos, sinais e ações

```text
Risco | Sinais típicos                           | Ação imediata                    | Flag envolvida
----- | ---------------------------------------- | -------------------------------- | --------------
R1    | Fluxos de fontes quebrados               | Desligar v2, usar fallback       | FF_SOURCES_CONSOLE_V2
R2    | Regressão global de frontend             | Desligar DS v1 em áreas críticas | FF_ADMIN_DS_V1
R3    | Contratos de API incoerentes             | Parar escritas, revisar API      | FF_SOURCES_CONSOLE_V2
R4    | Erros operacionais por UX confusa        | Ajustar UX + reforçar runbook    | (sem flag direta)
R5    | Problemas demorando a ser detectados     | Reforçar checklists + monitoração| (sem flag direta)
```

---

## 6. Síntese do Bloco 5.4

O Bloco 5.4 garante que a S26 não é só sobre "entregar" features, mas também sobre **controlar exposição ao risco**:

- registra explicitamente os riscos principais (R1–R5) da mudança de admin/console de fontes;  
- define uma estratégia de feature flags (`FF_ADMIN_DS_V1`, `FF_SOURCES_CONSOLE_V2`) para rollout e rollback;  
- descreve cenários de kill switch e os limites do que é ou não reversível;  
- conecta riscos e flags ao ORR e às lições aprendidas (Cap.6).

Com isso, o Capítulo 5 da S26 se completa: sabemos o que validar (5.1), como julgar (5.2), como operar (5.3) e como reagir quando a realidade apronta (5.4).


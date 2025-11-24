# Sprint 21 — Fluxos Administrativos do Console de Fontes

Este documento descreve os fluxos que um admin executa para operar o Console de Fontes. Cada fluxo deve ser suportado pela API e pela UI mínima da Sprint 21.

## 1. Princípios
- Sempre registrar motivo e autor das ações.
- Respeitar a máquina de estados (`docs/sprint_21_ciclo_vida_fontes.md`).
- Preservar trilhas de auditoria e histórico de saúde.
- Nenhum fluxo ignora validações da ontologia (`docs/sprint_21_ontologia_fontes.md`).

## 2. Fluxos principais

### 2.1 Cadastro inicial de fonte
- **Objetivo**: criar fonte PROPOSED com config mínima válida.
- **Pré-condições**: tipo reconhecido, config obrigatória presente.
- **Passos**:
  1) Admin preenche `name`, `type`, `domains`, `endpoint`, `auth`, `frequency`.
  2) Sistema valida campos e cria `Source` em `PROPOSED`.
  3) Registra auditoria (`created_by`, `created_at`).
- **Pós-condições**: fonte existe, pronta para TESTING.

### 2.2 Clonar como template
- **Objetivo**: acelerar criação usando fonte existente como base.
- **Passos**:
  1) Admin escolhe fonte ativa ou testada.
  2) Sistema duplica config (sem reutilizar `id/slug`), marca `PROPOSED`.
  3) Admin ajusta campos sensíveis (auth, endpoint).

### 2.3 Iniciar testes
- **Objetivo**: mover fonte para TESTING com health-check controlado.
- **Passos**:
  1) Admin aciona “Iniciar teste”.
  2) Sistema roda health-check básico.
  3) Em sucesso, transiciona `PROPOSED` → `TESTING`, registra histórico.
  4) Em falha, permanece em PROPOSED com erro registrado.

### 2.4 Ativar fonte
- **Objetivo**: liberar coleta em produção.
- **Pré-condições**: health-check OK, redundância configurada, sem contestação aberta.
- **Passos**:
  1) Admin revisa resultado de teste.
  2) Transição `TESTING` → `ACTIVE` com motivo.
  3) Sistema registra histórico e atualiza `state_updated_at`.

### 2.5 Editar parâmetros
- **Objetivo**: ajustar endpoint, auth, frequência, parsing.
- **Pré-condições**: fonte não terminal (`DISABLED_PERM`).
- **Passos**:
  1) Admin edita campos permitidos.
  2) Sistema valida conforme tipo.
  3) Atualiza `updated_by/updated_at`, mantém estado, opcionalmente abre `UNDER_REVIEW` se alteração sensível.

### 2.6 Abrir revisão
- **Objetivo**: avaliar fonte após alerta/contestação.
- **Passos**:
  1) Admin (ou Debunker) abre revisão, define motivo.
  2) Transição para `UNDER_REVIEW`.
  3) Opcional: anexar `evidence_refs` e `conflict_with_sources`.

### 2.7 Marcar como suspeita
- **Objetivo**: sinalizar fonte comprometida ou com indícios de problema.
- **Passos**:
  1) Acionar “Marcar suspeita”.
  2) Transição `ACTIVE|UNDER_REVIEW` → `SUSPECT`.
  3) Registrar motivo e quem sinalizou.

### 2.8 Desativar temporariamente
- **Objetivo**: pausar fonte sem descartá-la.
- **Passos**:
  1) Transição `ACTIVE|UNDER_REVIEW|SUSPECT` → `DISABLED_TEMP`.
  2) Registrar motivo e prazo (opcional) para reavaliação.

### 2.9 Desativar permanentemente
- **Objetivo**: encerrar uso da fonte.
- **Passos**:
  1) Transição para `DISABLED_PERM` com justificativa forte.
  2) Bloquear transições futuras.

### 2.10 Reativar
- **Objetivo**: retornar fonte pausada para operação.
- **Pré-condições**: estado `DISABLED_TEMP` ou `UNDER_REVIEW`, health-check OK, revisão concluída.
- **Passos**:
  1) Admin revisa correções.
  2) Transição para `ACTIVE` (ou `TESTING` se precisar revalidar).
  3) Registrar auditoria.

### 2.11 Health-check manual
- **Objetivo**: verificar saúde sob demanda.
- **Passos**:
  1) Admin aciona health-check.
  2) Sistema executa tipo-específico e grava `SourceHealthCheck`.
  3) UI exibe resultado e atualiza estado se necessário.

## 3. Relação com UI mínima
- Lista de fontes: suporta filtros por `type`, `category`, `state` e ações rápidas (revisão, suspeita, health-check).
- Detalhe: mostra campos, últimos estados, health-checks, contestação.
- Formulário: campos condicionais por tipo, validações inline.

## 4. Relação com Debunker/contestação
- Fluxos 2.6 e 2.7 são acionáveis por eventos do Debunker.
- UI deve mostrar se há contestação aberta e se a fonte está em conflito com outras.

## 5. Evidências para gates
- S21_G3 valida presença de todos os fluxos acima.
- S21_G6 usa fluxos para percorrer cenários reais.

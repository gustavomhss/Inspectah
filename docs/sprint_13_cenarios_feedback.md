# Sprint 13 — Cenários de Feedback

Documento canônico com o roteiro usado no gate **S13_G6**. Cada entrada abaixo será processada por `scripts/s13_feedback_backlog.py`. O bloco JSON entre os marcadores deve conter pelo menos um cenário por domínio.

Campos de cada cenário:
- `scenario_id`: identificador único do teste.
- `domain`: domínio/piloto alvo.
- `case_id`: case_key gerado pela timeline da S13.
- `operation`: `create`, `list`, `update_status` ou combinações encadeadas.
- `payload`: campos utilizados na criação/atualização.
- `expected`: checagens mínimas após executar a operação.

<!-- S13_FEEDBACK_SCENARIOS:BEGIN -->
```json
[
  {
    "scenario_id": "obra_feedback_denuncia",
    "domain": "obra_publica",
    "case_id": "obra_publica:obra_transcol_niteroi_2022",
    "operation": "create",
    "payload": {
      "mensagem": "Moradores relatam poeira excessiva durante as obras.",
      "origem": "explorer_ui"
    },
    "expected": {
      "status": "novo"
    }
  },
  {
    "scenario_id": "clima_feedback_relatorio",
    "domain": "evento_climatico",
    "case_id": "evento_climatico:evento_clima_serrana_2023",
    "operation": "create_then_update",
    "payload": {
      "mensagem": "Sirene do bairro X não acionou durante o alerta laranja.",
      "novo_status": "em_analise"
    },
    "expected": {
      "final_status": "em_analise"
    }
  },
  {
    "scenario_id": "pl_feedback_transparencia",
    "domain": "projeto_lei",
    "case_id": "projeto_lei:pl_transparencia_energia_2024",
    "operation": "create",
    "payload": {
      "mensagem": "Texto do projeto não cita setor de energia solar.",
      "origem": "explorer_ui"
    },
    "expected": {
      "status": "novo"
    }
  },
  {
    "scenario_id": "carreira_feedback_convênio",
    "domain": "carreira_politica",
    "case_id": "carreira_politica:carreira_prefeitura_niteroi_2020_2024",
    "operation": "create_then_update",
    "payload": {
      "mensagem": "Convênio educacional citado no timeline não possui link para o extrato.",
      "novo_status": "resolvido"
    },
    "expected": {
      "final_status": "resolvido"
    }
  },
  {
    "scenario_id": "influencer_feedback_conteudo",
    "domain": "influencer",
    "case_id": "influencer:influencer_obras_alpha_2023",
    "operation": "create",
    "payload": {
      "mensagem": "Live de 05/03 cita valores divergentes do contrato.",
      "origem": "explorer_ui"
    },
    "expected": {
      "status": "novo"
    }
  },
  {
    "scenario_id": "atleta_feedback_prestacao",
    "domain": "atleta",
    "case_id": "atleta:atleta_bolsa_esporte_2024",
    "operation": "create_then_update",
    "payload": {
      "mensagem": "Prestação de contas parcial não inclui comprovante de viagem.",
      "novo_status": "em_analise"
    },
    "expected": {
      "final_status": "em_analise"
    }
  }
]
```
<!-- S13_FEEDBACK_SCENARIOS:END -->

# Inspectah — Como rodar a consulta localmente (UI + API)

## 1. Pré-requisitos
- Python 3 (use o `.venv` do projeto).
- Node 18+ (Vite no frontend).
- Dependências instaladas:
  - Backend: `python -m pip install -e .` (dentro do venv).
  - Frontend: `cd frontend/inspectah-ui && npm ci`.

## 2. Subir o backend (API de consulta)
```bash
cd /Users/gustavoschneiter/Documents/Inspectah
source .venv/bin/activate
PYTHONPATH=. python -m uvicorn inspectah.api:build_app --factory --reload --port 8000
```
- Endpoints:
  - API base: http://localhost:8000
  - Docs/OpenAPI: http://localhost:8000/docs
- A rota `POST /api/consultation` deve aparecer em `/docs`.

## 3. Subir o frontend (UI de consulta)
```bash
cd /Users/gustavoschneiter/Documents/Inspectah/frontend/inspectah-ui
npm ci   # primeira vez ou após mudanças de deps
npm run dev
```
- UI disponível em http://localhost:5173.
- O Vite já chama o backend em `http://localhost:8000/api/consultation` por padrão.

## 4. Smoke tests manuais
- Pergunta de domínio conhecido (clima):  
  “O furacão Katrina atingiu New Orleans em 2005?”  
  Esperado: resposta consolidada com risco intermediário/atenção e evidências vindas do domínio de clima (não da pergunta).
- Pergunta de domínio conhecido (fofoca/política/esporte):  
  “Esse boato de corrupção no prefeito procede?”  
  Esperado: risco coerente com Debunker+comitês; evidências da fixture correspondente.
- Pergunta fora de domínio/insuficiente:  
  “????” ou “Quando o dragão voa?”  
  Esperado: risco `unknown/incerto`, mensagem de dados insuficientes, evidências vazias (sem a pergunta).
- Pergunta neutra genérica:  
  “Qual a previsão do tempo amanhã no Rio?”  
  Esperado: risco baixo/médio com evidências de clima.

## 5. Scripts de verificação/gates
Rodar com venv ativo e `PYTHONPATH=.`:
```bash
# Testes de consulta
PYTHONPATH=. .venv/bin/python -m pytest tests/test_consultation_*.py

# Gates Sprint 17.1
PYTHONPATH=. bin/s17_1_all_gates.sh

# Gates Sprint 17A (wrappers)
PYTHONPATH=. bin/s17a_all_gates.sh
```
- Scorecards ficam em `out/scorecards/`.
- Em caso de falha, conferir logs em `out/evidence/S17_1_T*_*/`.

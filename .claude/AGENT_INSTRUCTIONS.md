# Instruções para Agentes - Inspectah

## Regra #1: Cobertura de Testes

**OBRIGATÓRIO: Manter cobertura >= 97% em todas as entregas.**

Antes de finalizar QUALQUER tarefa que envolva código:

```bash
PYTHONPATH=. .venv/bin/python -m pytest --cov=app --cov-report=term-missing
```

Se a cobertura estiver abaixo de 97%, você DEVE criar testes adicionais.

---

## Workflow Obrigatório

### 1. Ao criar novo código

```bash
# 1. Escrever o código
# 2. Criar testes correspondentes em tests/
# 3. Verificar cobertura
PYTHONPATH=. .venv/bin/python -m pytest --cov=app/novo_modulo --cov-report=term-missing tests/novo_modulo/

# 4. Se cobertura < 100% no módulo novo, adicionar mais testes
# 5. Verificar cobertura global
PYTHONPATH=. .venv/bin/python -m pytest --cov=app
```

### 2. Ao modificar código existente

```bash
# 1. Rodar testes existentes primeiro
PYTHONPATH=. .venv/bin/python -m pytest tests/modulo_afetado/ -v

# 2. Fazer modificações
# 3. Rodar testes novamente
# 4. Verificar cobertura não diminuiu
PYTHONPATH=. .venv/bin/python -m pytest --cov=app/modulo --cov-report=term-missing

# 5. Adicionar testes para novo código se necessário
```

### 3. Ao finalizar sprint/feature

```bash
# 1. Rodar TODOS os testes
PYTHONPATH=. .venv/bin/python -m pytest

# 2. Verificar cobertura global (DEVE ser >= 97%)
PYTHONPATH=. .venv/bin/python -m pytest --cov=app --cov-report=term-missing

# 3. Se abaixo de 97%, identificar módulos com baixa cobertura
PYTHONPATH=. .venv/bin/python -m pytest --cov=app 2>&1 | grep -v "100%"

# 4. Criar testes para módulos com cobertura baixa
```

---

## Estrutura de Testes

### Onde criar testes

| Código em | Testes em |
|-----------|-----------|
| `app/module/file.py` | `tests/module/test_file.py` |
| `app/module/service.py` | `tests/module/test_service.py` |
| `app/api/routes.py` | `tests/api/test_routes.py` |

### Template de arquivo de teste

```python
"""
Tests for module/file — Sprint XX

Tests for FunctionName, ClassName, etc.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.module.file import (
    function_to_test,
    ClassToTest,
)


class TestFunctionName:
    """Tests for function_name."""

    def test_success_case(self):
        """Descrição do caso de sucesso."""
        result = function_to_test("valid_input")
        assert result is not None

    def test_error_case(self):
        """Descrição do caso de erro."""
        with pytest.raises(ValueError, match="mensagem"):
            function_to_test("invalid")

    def test_edge_case_none(self):
        """Test with None input."""
        result = function_to_test(None)
        assert result == default_value

    def test_edge_case_empty(self):
        """Test with empty input."""
        result = function_to_test("")
        assert result == default_value
```

---

## Técnicas de Teste

### 1. Mock de banco SQLite

```python
import sqlite3

@pytest.fixture
def service():
    """Service with in-memory database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    # Create tables
    conn.execute("CREATE TABLE ...")
    conn.commit()
    svc = Service(db_path=":memory:")
    yield svc
    conn.close()
```

### 2. Mock de flags e configurações

```python
mock_flags = {
    "feature_enabled": True,
    "rollout_enabled": True,
}

with patch.object(service, "_flags", return_value=mock_flags):
    result = service.function()
```

### 3. Testar exceções

```python
def test_raises_on_invalid(self):
    """Test raises ValueError on invalid input."""
    with pytest.raises(ValueError, match="mensagem esperada"):
        function("invalid")
```

### 4. Testar branches condicionais

```python
def test_condition_true_path(self):
    """Test when condition is true."""
    result = function(condition=True)
    assert result == expected_for_true

def test_condition_false_path(self):
    """Test when condition is false."""
    result = function(condition=False)
    assert result == expected_for_false
```

### 5. Testar TypeError em comparações

```python
def test_type_error_handled(self):
    """Test TypeError is handled gracefully."""
    context = {"field": {"nested": "dict"}}  # incompatible
    result = function(context)
    assert result.passed is False
```

---

## Linhas Comumente Não Cobertas

### 1. Exception handlers
```python
# Código
try:
    result = operation()
except SomeError:
    return default  # <-- Linha não coberta

# Teste
def test_exception_path(self):
    with patch("module.operation", side_effect=SomeError()):
        result = function()
        assert result == default
```

### 2. Validações de entrada
```python
# Código
if value < MIN or value > MAX:
    raise ValueError("fora do intervalo")  # <-- Não coberta

# Teste
def test_below_minimum(self):
    with pytest.raises(ValueError, match="fora do intervalo"):
        function(value=MIN - 1)

def test_above_maximum(self):
    with pytest.raises(ValueError, match="fora do intervalo"):
        function(value=MAX + 1)
```

### 3. Peek/EOF em parsers
```python
# Teste
def test_peek_at_eof(self):
    parser = Parser()
    parser.tokens = []
    parser.pos = 0
    assert parser._current().type == TokenType.EOF
```

### 4. Callbacks com erro
```python
# Teste
def test_callback_error_handled(self):
    def failing_callback(x):
        raise RuntimeError("error")
    service.set_callback(failing_callback)
    service._notify()  # Should not raise
```

---

## Comandos Úteis

```bash
# Ver cobertura de módulo específico
PYTHONPATH=. .venv/bin/python -m pytest --cov=app/flows/service --cov-report=term-missing tests/flows/

# Rodar teste específico
PYTHONPATH=. .venv/bin/python -m pytest tests/flows/test_service.py::TestClassName::test_method -v

# Ver módulos abaixo de X%
PYTHONPATH=. .venv/bin/python -m pytest --cov=app 2>&1 | grep -E "^app.*[0-9]%.*$" | grep -v "100%"

# Contar testes
PYTHONPATH=. .venv/bin/python -m pytest --collect-only -q | tail -1

# Rodar testes em paralelo (se pytest-xdist instalado)
PYTHONPATH=. .venv/bin/python -m pytest -n auto --cov=app
```

---

## Métricas Atuais (Dezembro 2024)

- **Cobertura Global**: 97%
- **Total de Testes**: 1961
- **Módulos a 100%**: 117/187

---

## Lembretes Importantes

1. ⚠️ **NUNCA** entregar código sem verificar cobertura
2. ⚠️ **NUNCA** fazer merge com cobertura < 97%
3. ⚠️ **SEMPRE** criar testes para código novo
4. ⚠️ **SEMPRE** verificar testes após modificações
5. ⚠️ **SEMPRE** usar `timezone.utc` para timestamps em testes

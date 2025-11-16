#!/usr/bin/env python3
"""Shim mínimo para executar testes estilo pytest quando a lib não existe."""
from __future__ import annotations

import importlib.util
import sys
import traceback
import types
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_module(path: Path, module_name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _wrap_pytest_functions(module: types.ModuleType) -> list[unittest.FunctionTestCase]:
    suite: list[unittest.FunctionTestCase] = []
    for attr in dir(module):
        if not attr.startswith("test_"):
            continue
        obj = getattr(module, attr)
        if callable(obj):
            suite.append(unittest.FunctionTestCase(obj, description=f"{module.__name__}.{attr}"))
    return suite


def main(argv: list[str]) -> int:
    if not argv:
        print("Uso: python bin/s5_pytest_shim.py tests/test_file.py [...]")
        return 2

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for idx, arg in enumerate(argv):
        path = Path(arg)
        if not path.exists():
            print(f"Arquivo de teste não encontrado: {arg}")
            return 2
        module = _load_module(path, f"s5_test_module_{idx}")
        suite.addTests(loader.loadTestsFromModule(module))
        for fn_test in _wrap_pytest_functions(module):
            suite.addTest(fn_test)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

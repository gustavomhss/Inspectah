"""Observability helpers for Sprint 9."""

from importlib import import_module

metrics_s9 = import_module(".metrics_s9", __name__)

__all__ = ["metrics_s9"]

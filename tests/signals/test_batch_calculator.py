"""
Tests for Batch Signal Calculator — S37

Tests for BatchSignalCalculator orchestration.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.signals.batch_calculator import BatchSignalCalculator


class TestBatchSignalCalculator:
    """Tests for BatchSignalCalculator class."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock graph service."""
        return MagicMock()

    @pytest.fixture
    def mock_signal_repo(self):
        """Create mock signal repository."""
        repo = MagicMock()
        repo.save_snapshot.return_value = "sig_test123456"
        return repo

    def test_init_default(self):
        """Initialize with default dependencies."""
        with patch("app.signals.batch_calculator.ClaimGraphService"):
            with patch("app.signals.batch_calculator.SignalRepository"):
                calc = BatchSignalCalculator()
                assert calc is not None
                assert len(calc.calculators) == 4

    def test_init_with_dependencies(self, mock_graph_service, mock_signal_repo):
        """Initialize with injected dependencies."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )
        assert calc.graph == mock_graph_service
        assert calc.repo == mock_signal_repo

    def test_calculators_registered(self, mock_graph_service, mock_signal_repo):
        """All expected calculators are registered."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )

        expected = [
            "mentiras_em_circulacao",
            "campo_batalha",
            "radar_silencio",
            "fragilidade_narrativa",
        ]
        assert set(calc.calculators.keys()) == set(expected)

    def test_default_domains(self, mock_graph_service, mock_signal_repo):
        """Default domains include pilot_politics."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )
        assert calc.DEFAULT_DOMAINS == ["pilot_politics"]

    def test_run_single_success(self, mock_graph_service, mock_signal_repo):
        """Run single signal calculation successfully."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )

        # Mock calculator
        mock_result = {"value": 42}
        mock_snapshot = {
            "signal_type": "mentiras_em_circulacao",
            "domain": "test",
            "timestamp": datetime.utcnow().isoformat(),
            "values": {"count": 10},
        }
        calc.calculators["mentiras_em_circulacao"].calculate = MagicMock(
            return_value=mock_result
        )
        calc.calculators["mentiras_em_circulacao"].to_snapshot = MagicMock(
            return_value=mock_snapshot
        )

        result = calc.run_single("mentiras_em_circulacao", "test")

        assert result is not None
        assert result["id"] == "sig_test123456"
        calc.calculators["mentiras_em_circulacao"].calculate.assert_called_once_with(
            "test"
        )

    def test_run_single_unknown_type(self, mock_graph_service, mock_signal_repo):
        """Run single with unknown signal type returns None."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )

        result = calc.run_single("unknown_signal", "test")

        assert result is None

    def test_run_all_domains(self, mock_graph_service, mock_signal_repo):
        """Run calculations for all domains."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )

        # Mock all calculators
        for name, calculator in calc.calculators.items():
            calculator.calculate = MagicMock(return_value={"value": 1})
            calculator.to_snapshot = MagicMock(
                return_value={
                    "signal_type": name,
                    "domain": "test",
                    "timestamp": datetime.utcnow().isoformat(),
                    "values": {},
                }
            )

        results = calc.run(domains=["domain1", "domain2"])

        assert "domain1" in results
        assert "domain2" in results
        assert len(results["domain1"]) == 4
        assert len(results["domain2"]) == 4

    def test_run_default_domains(self, mock_graph_service, mock_signal_repo):
        """Run with default domains when none specified."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )

        # Mock all calculators
        for name, calculator in calc.calculators.items():
            calculator.calculate = MagicMock(return_value={})
            calculator.to_snapshot = MagicMock(
                return_value={
                    "signal_type": name,
                    "domain": "pilot_politics",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        results = calc.run()  # No domains specified

        assert "pilot_politics" in results

    def test_run_handles_calculator_error(self, mock_graph_service, mock_signal_repo):
        """Run continues when a calculator raises error."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )

        # First calculator raises, others succeed
        calc.calculators["mentiras_em_circulacao"].calculate = MagicMock(
            side_effect=Exception("Test error")
        )

        for name, calculator in list(calc.calculators.items())[1:]:
            calculator.calculate = MagicMock(return_value={})
            calculator.to_snapshot = MagicMock(
                return_value={
                    "signal_type": name,
                    "domain": "test",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        results = calc.run(domains=["test"])

        # Should have 3 successful calculations (one failed)
        assert len(results["test"]) == 3

    def test_get_summary(self, mock_graph_service, mock_signal_repo):
        """Get summary of latest signals."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )

        # Mock repository response
        mock_signal_repo.get_all_latest.return_value = [
            {
                "signal_type": "mentiras_em_circulacao",
                "timestamp": "2024-01-01T00:00:00Z",
                "values": {"count": 10},
            },
            {
                "signal_type": "campo_batalha",
                "timestamp": "2024-01-01T00:00:00Z",
                "values": {"score": 0.5},
            },
        ]

        summary = calc.get_summary("politics")

        assert summary["domain"] == "politics"
        assert "timestamp" in summary
        assert "signals" in summary
        assert "mentiras_em_circulacao" in summary["signals"]
        assert "campo_batalha" in summary["signals"]

    def test_get_summary_empty(self, mock_graph_service, mock_signal_repo):
        """Get summary when no signals exist."""
        calc = BatchSignalCalculator(
            graph_service=mock_graph_service,
            signal_repo=mock_signal_repo,
        )

        mock_signal_repo.get_all_latest.return_value = []

        summary = calc.get_summary("empty_domain")

        assert summary["domain"] == "empty_domain"
        assert summary["signals"] == {}


class TestBatchSignalCalculatorIntegration:
    """Integration tests for BatchSignalCalculator."""

    @pytest.fixture
    def integration_calc(self):
        """Create calculator with real signal repository (in-memory)."""
        from app.signals.signal_repository import SignalRepository

        mock_graph = MagicMock()
        repo = SignalRepository(db_path=":memory:")

        calc = BatchSignalCalculator(
            graph_service=mock_graph,
            signal_repo=repo,
        )

        # Mock all calculators to return simple data
        for name, calculator in calc.calculators.items():
            calculator.calculate = MagicMock(
                return_value={"type": name, "value": 42}
            )
            calculator.to_snapshot = MagicMock(
                return_value={
                    "signal_type": name,
                    "domain": "test",
                    "timestamp": datetime.utcnow().isoformat(),
                    "values": {"type": name, "value": 42},
                    "metadata": {"source": "test"},
                }
            )

        return calc

    def test_run_and_get_summary(self, integration_calc):
        """Run calculations and verify summary."""
        results = integration_calc.run(domains=["test"])

        assert len(results["test"]) == 4

        summary = integration_calc.get_summary("test")

        assert len(summary["signals"]) == 4
        for sig_type in integration_calc.calculators.keys():
            assert sig_type in summary["signals"]

    def test_run_multiple_times(self, integration_calc):
        """Run multiple times and verify history."""
        for _ in range(3):
            integration_calc.run(domains=["test"])

        # Each run should save 4 snapshots
        total = integration_calc.repo.count_snapshots(domain="test")
        assert total == 12  # 3 runs * 4 signal types


class TestBatchCalculatorMain:
    """Tests for main CLI function."""

    def test_main_summary(self):
        """Main with --summary flag."""
        from app.signals.batch_calculator import main

        with patch("app.signals.batch_calculator.BatchSignalCalculator") as MockCalc:
            mock_calc = MockCalc.return_value
            mock_calc.get_summary.return_value = {
                "domain": "pilot_politics",
                "signals": {"test_sig": {"values": {"key": "value"}}},
            }

            with patch("sys.argv", ["batch_calc", "--summary"]):
                result = main()

            assert result == 0
            mock_calc.get_summary.assert_called()

    def test_main_single_signal(self):
        """Main with --signal flag."""
        from app.signals.batch_calculator import main

        with patch("app.signals.batch_calculator.BatchSignalCalculator") as MockCalc:
            mock_calc = MockCalc.return_value
            mock_calc.run_single.return_value = {"id": "snap_1", "signal_type": "test"}

            with patch("sys.argv", ["batch_calc", "--signal", "mentiras_em_circulacao"]):
                result = main()

            assert result == 0
            mock_calc.run_single.assert_called()

    def test_main_single_signal_no_result(self):
        """Main with --signal returns nothing."""
        from app.signals.batch_calculator import main

        with patch("app.signals.batch_calculator.BatchSignalCalculator") as MockCalc:
            mock_calc = MockCalc.return_value
            mock_calc.run_single.return_value = None

            with patch("sys.argv", ["batch_calc", "--signal", "unknown"]):
                result = main()

            assert result == 0

    def test_main_run_all(self):
        """Main runs all signals."""
        from app.signals.batch_calculator import main

        with patch("app.signals.batch_calculator.BatchSignalCalculator") as MockCalc:
            mock_calc = MockCalc.return_value
            mock_calc.run.return_value = {
                "pilot_politics": [
                    {"signal_type": "test", "id": "snap_1"},
                ]
            }

            with patch("sys.argv", ["batch_calc"]):
                result = main()

            assert result == 0
            mock_calc.run.assert_called()

    def test_main_custom_domains(self):
        """Main with custom domains."""
        from app.signals.batch_calculator import main

        with patch("app.signals.batch_calculator.BatchSignalCalculator") as MockCalc:
            mock_calc = MockCalc.return_value
            mock_calc.run.return_value = {
                "domain1": [],
                "domain2": [],
            }

            with patch("sys.argv", ["batch_calc", "--domains", "domain1", "domain2"]):
                result = main()

            assert result == 0
            mock_calc.run.assert_called_with(["domain1", "domain2"])

    def test_main_summary_no_signals(self):
        """Main summary with no signals."""
        from app.signals.batch_calculator import main

        with patch("app.signals.batch_calculator.BatchSignalCalculator") as MockCalc:
            mock_calc = MockCalc.return_value
            mock_calc.get_summary.return_value = {
                "domain": "pilot_politics",
                "signals": {},
            }

            with patch("sys.argv", ["batch_calc", "--summary"]):
                result = main()

            assert result == 0

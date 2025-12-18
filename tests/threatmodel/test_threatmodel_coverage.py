"""
Tests for Threatmodel Coverage — Coverage gaps

Targeted tests to cover remaining uncovered lines in computations.py and service.py
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from app.threatmodel.computations import (
    compute_flood_score,
    compute_source_diversity,
    compute_reversal_rate,
)
from app.threatmodel.service import load_thresholds


class TestComputeFloodScore:
    """Tests for compute_flood_score function."""

    def test_zero_threshold_returns_inf(self):
        """Line 12 in computations.py: Zero threshold should return infinity."""
        result = compute_flood_score(claim_counts=10, threshold=0)

        assert result == float("inf")

    def test_normal_flood_score(self):
        """Normal flood score calculation."""
        result = compute_flood_score(claim_counts=15, threshold=10)

        assert result == 1.5

    def test_below_threshold(self):
        """Flood score below threshold."""
        result = compute_flood_score(claim_counts=5, threshold=10)

        assert result == 0.5


class TestComputeSourceDiversity:
    """Tests for compute_source_diversity function."""

    def test_zero_total_sources_returns_zero(self):
        """Line 12 in computations.py: Zero total sources should return 0.0."""
        result = compute_source_diversity(unique_sources=5, total_sources=0)

        assert result == 0.0

    def test_normal_diversity(self):
        """Normal source diversity calculation."""
        result = compute_source_diversity(unique_sources=3, total_sources=10)

        assert result == 0.3

    def test_all_unique_sources(self):
        """All sources are unique."""
        result = compute_source_diversity(unique_sources=10, total_sources=10)

        assert result == 1.0


class TestComputeReversalRate:
    """Tests for compute_reversal_rate function."""

    def test_reversal_rate_with_various_state_key_formats(self):
        """Line 22 in computations.py: Handle different state key formats."""
        # Test events with different key formats
        events = [
            {"new_state": "UNKNOWN"},
            {"new_state": "CLAIMED"},  # This is a change from UNKNOWN
            {"state": "VERIFIED"},  # Using 'state' key, another change
            {"new_state": "CLAIMED"},  # Change back to CLAIMED
        ]

        result = compute_reversal_rate(events)

        # 3 state changes out of 4 events = 3/4 = 0.75
        assert result == 0.75

    def test_reversal_rate_with_lowercase_key(self):
        """Line 22 in computations.py: Handle lowercase 'new_state' key."""
        events = [
            {"new_state": "UNKNOWN"},
            {"new_state": "CLAIMED"},  # Change
        ]

        result = compute_reversal_rate(events)

        # 1 change out of 2 events = 0.5
        assert result == 0.5

    def test_reversal_rate_no_state_key(self):
        """Events without state keys should be skipped."""
        events = [
            {"other_key": "value1"},
            {"other_key": "value2"},
        ]

        result = compute_reversal_rate(events)

        # No valid state keys, so 0 changes / 2 events = 0
        assert result == 0.0

    def test_reversal_rate_empty_events(self):
        """Empty events list should return 0."""
        result = compute_reversal_rate([])

        assert result == 0.0

    def test_reversal_rate_single_event(self):
        """Single event should have 0 reversal rate."""
        events = [{"new_state": "UNKNOWN"}]

        result = compute_reversal_rate(events)

        assert result == 0.0


class TestLoadThresholds:
    """Tests for load_thresholds function."""

    def test_missing_file_raises_error(self):
        """Line 15 in service.py: Missing threshold file should raise FileNotFoundError."""
        # Create a path that doesn't exist
        non_existent_path = Path("/tmp/nonexistent/thresholds.yaml")

        with pytest.raises(FileNotFoundError, match="Thresholds file not found"):
            load_thresholds(non_existent_path)

    def test_load_valid_thresholds(self):
        """Load valid thresholds file."""
        # Create a temporary threshold file
        temp_dir = tempfile.mkdtemp()
        threshold_file = Path(temp_dir) / "thresholds.yaml"

        thresholds_data = {
            "default": {
                "max_flood": 10,
                "min_source_diversity": 0.5,
                "max_reversal_rate": 0.3,
            },
            "politics": {
                "max_flood": 5,
                "min_source_diversity": 0.7,
                "max_reversal_rate": 0.2,
            },
        }

        threshold_file.write_text(yaml.dump(thresholds_data), encoding="utf-8")

        try:
            result = load_thresholds(threshold_file)

            assert "default" in result
            assert "politics" in result
            assert result["default"]["max_flood"] == 10
            assert result["politics"]["min_source_diversity"] == 0.7
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_load_empty_thresholds_file(self):
        """Load empty thresholds file returns empty dict."""
        # Create a temporary empty threshold file
        temp_dir = tempfile.mkdtemp()
        threshold_file = Path(temp_dir) / "thresholds.yaml"
        threshold_file.write_text("", encoding="utf-8")

        try:
            result = load_thresholds(threshold_file)

            assert result == {}
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestReversalRateEdgeCases:
    """Additional edge cases for reversal rate calculation."""

    def test_reversal_rate_all_same_state(self):
        """All events with same state should have 0 reversal rate."""
        events = [
            {"new_state": "CLAIMED"},
            {"new_state": "CLAIMED"},
            {"new_state": "CLAIMED"},
        ]

        result = compute_reversal_rate(events)

        # No state changes, 0/3 = 0
        assert result == 0.0

    def test_reversal_rate_mixed_keys(self):
        """Mixed key formats in events."""
        events = [
            {"new_state": "UNKNOWN"},
            {"state": "CLAIMED"},  # Change, using 'state' key
            {"new_state": "UNKNOWN"},  # Change, back to UNKNOWN
            {"other": "value"},  # No state key, skip
            {"new_state": "CLAIMED"},  # Change
        ]

        result = compute_reversal_rate(events)

        # 3 changes out of 5 events = 0.6
        assert result == 0.6

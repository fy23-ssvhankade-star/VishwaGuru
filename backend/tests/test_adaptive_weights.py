import os
import json
import pytest
from unittest.mock import patch, mock_open
from backend.adaptive_weights import AdaptiveWeights

class TestAdaptiveWeights:

    def test_load_defaults_if_file_missing(self):
        with patch("os.path.exists", return_value=False):
            with patch("builtins.open", mock_open()) as mock_file:
                # Patch dirname to avoid empty string issue in test
                with patch("os.path.dirname", return_value="data"):
                    with patch("os.makedirs"):
                         aw = AdaptiveWeights(file_path="missing.json")
                         weights = aw.get_weights()

                assert "severity_keywords" in weights
                assert "categories" in weights
                assert weights["duplicate_search_radius"] == 50.0

                # Verify it tried to save defaults
                mock_file.assert_called_with("missing.json", "w")

    def test_load_from_file(self):
        mock_data = {
            "severity_keywords": {"critical": ["test"]},
            "categories": {},
            "urgency_patterns": [],
            "duplicate_search_radius": 75.0
        }
        json_data = json.dumps(mock_data)

        with patch("os.path.exists", return_value=True):
            with patch("os.path.getmtime", return_value=100.0):
                with patch("builtins.open", mock_open(read_data=json_data)):
                    aw = AdaptiveWeights(file_path="existing.json")
                    weights = aw.get_weights()

                    assert weights["duplicate_search_radius"] == 75.0
                    assert weights["severity_keywords"]["critical"] == ["test"]

    def test_update_weights(self):
        with patch("os.path.exists", return_value=False):
            with patch("os.path.dirname", return_value="data"):
                with patch("os.makedirs"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        aw = AdaptiveWeights(file_path="update.json")

                        aw.update_weights({"duplicate_search_radius": 100.0})

                        assert aw.get_duplicate_search_radius() == 100.0

                        # Check if it wrote to file
                        assert mock_file.call_count >= 1

    def test_hot_reload(self):
        initial_data = {"duplicate_search_radius": 50.0}
        updated_data = {"duplicate_search_radius": 100.0}

        with patch("os.path.exists", return_value=True):
            with patch("os.path.getmtime") as mock_mtime:
                # Setup mtime progression
                mock_mtime.side_effect = [100.0, 100.0, 200.0]
                # 1. Init: 100.0
                # 2. Check 1 (get_dup...): 100.0 (No reload)
                # 3. Check 2 (get_dup...): 200.0 (Reload)

                with patch("json.load", side_effect=[initial_data, updated_data]):
                    with patch("builtins.open", mock_open()):
                        aw = AdaptiveWeights(file_path="reload.json")

                        # Initial check
                        assert aw.get_duplicate_search_radius() == 50.0

                        # Trigger reload by mtime change (handled by side_effect above)
                        # The next call to get_duplicate_search_radius calls _check_reload -> getmtime
                        # getmtime returns 200.0 > 100.0 -> Reload

                        radius = aw.get_duplicate_search_radius()
                        assert radius == 100.0

    def test_singleton_behavior(self):
        from backend.adaptive_weights import adaptive_weights as aw1
        from backend.adaptive_weights import adaptive_weights as aw2
        assert aw1 is aw2

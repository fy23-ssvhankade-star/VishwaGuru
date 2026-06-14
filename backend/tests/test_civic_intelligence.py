import pytest
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime
from backend.civic_intelligence import CivicIntelligenceEngine
from backend.models import Issue, Grievance, EscalationAudit, EscalationReason

class TestCivicIntelligenceEngine:

    @pytest.fixture
    def engine(self):
        return CivicIntelligenceEngine()

    @pytest.fixture
    def mock_db(self):
        m = MagicMock()
        # Default behavior for query chains
        m.query.return_value.filter.return_value.all.return_value = []
        m.query.return_value.filter.return_value.count.return_value = 0
        return m

    @pytest.fixture
    def mock_trend_analyzer(self):
        with patch("backend.civic_intelligence.trend_analyzer") as mock:
            mock.analyze.return_value = {
                "total_issues": 0,
                "top_keywords": [],
                "category_distribution": {},
                "geographic_clusters": []
            }
            yield mock

    @pytest.fixture
    def mock_adaptive_weights(self):
        with patch("backend.civic_intelligence.adaptive_weights") as mock:
            mock.get_weights.return_value = {
                "severity_keywords": {"critical": []},
                "duplicate_search_radius": 50.0
            }
            mock.get_duplicate_search_radius.return_value = 50.0
            yield mock

    def test_refine_daily_flow(self, engine, mock_db, mock_trend_analyzer, mock_adaptive_weights):
        # Setup DB mocks
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(spec=Issue, created_at=datetime.now(), category="Pothole")
        ]

        # Setup Trend Analyzer mock
        mock_trend_analyzer.analyze.return_value = {
            "total_issues": 10,
            "top_keywords": [("pothole", 5)],
            "category_distribution": {"Pothole": 5},
            "geographic_clusters": []
        }

        # Run
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump") as mock_json_dump:
                snapshot = engine.refine_daily(mock_db)

                assert snapshot["stats"]["total_issues_24h"] == 1
                mock_trend_analyzer.analyze.assert_called_once()
                mock_file.assert_called()

    def test_weight_optimization_severity_upgrade(self, engine, mock_db, mock_adaptive_weights, mock_trend_analyzer):
        mock_grievance = MagicMock(spec=Grievance, category="Pothole")
        mock_audit = MagicMock(spec=EscalationAudit, grievance=mock_grievance)

        # Mock query side effects
        def query_side_effect(model):
            m = MagicMock()
            if model == Issue:
                m.filter.return_value.all.return_value = []
                m.filter.return_value.count.return_value = 0
            elif model == EscalationAudit:
                m.join.return_value.filter.return_value.all.return_value = [mock_audit] * 5
                m.filter.return_value.count.return_value = 5
            return m

        mock_db.query.side_effect = query_side_effect

        # Run
        with patch("builtins.open", mock_open()):
             engine.refine_daily(mock_db)

        # Assert
        mock_adaptive_weights.update_weights.assert_called()

        # Check if severity_keywords update occurred in any of the calls
        found = False
        for call in mock_adaptive_weights.update_weights.call_args_list:
            args, _ = call
            if "severity_keywords" in args[0]:
                severity_keywords = args[0]["severity_keywords"]
                if "high" in severity_keywords and "pothole" in severity_keywords["high"]:
                    found = True
                    break

        assert found, "Pothole not added to high severity keywords"

    def test_duplicate_optimization_increase_radius(self, engine, mock_db, mock_adaptive_weights, mock_trend_analyzer):
        clusters = [{"size": 2} for _ in range(6)]

        mock_trend_analyzer.analyze.return_value = {
            "total_issues": 10,
            "top_keywords": [],
            "category_distribution": {},
            "geographic_clusters": clusters
        }

        mock_adaptive_weights.get_duplicate_search_radius.return_value = 50.0

        # Run
        with patch("builtins.open", mock_open()):
            engine.refine_daily(mock_db)

        # Assert
        mock_adaptive_weights.update_weights.assert_called()
        args, _ = mock_adaptive_weights.update_weights.call_args
        updated_dict = args[0]
        assert updated_dict["duplicate_search_radius"] == 55.0

    def test_duplicate_optimization_decrease_radius(self, engine, mock_db, mock_adaptive_weights, mock_trend_analyzer):
        mock_trend_analyzer.analyze.return_value = {
            "total_issues": 10,
            "top_keywords": [],
            "category_distribution": {},
            "geographic_clusters": []
        }

        mock_adaptive_weights.get_duplicate_search_radius.return_value = 50.0

        # Run
        with patch("builtins.open", mock_open()):
            engine.refine_daily(mock_db)

        # Assert
        mock_adaptive_weights.update_weights.assert_called()
        args, _ = mock_adaptive_weights.update_weights.call_args
        updated_dict = args[0]
        assert updated_dict["duplicate_search_radius"] == 49.0

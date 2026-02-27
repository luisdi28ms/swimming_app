import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from controllers.data_analyzer import DataAnalyzer

@pytest.fixture
def app():
    app = Flask(__name__)
    with app.app_context():
        yield app

class TestDataAnalyzer:

    @patch("controllers.data_analyzer.SwimStats")
    @patch("controllers.data_analyzer.render_template")
    def test_render_swimming_report_no_stats(self, mock_render, mock_swim_stats, app):
        """Tests the branch where no SwimStats exist."""
        # Arrange
        mock_swim_stats.query.first.return_value = None
        analyzer = DataAnalyzer()

        # Act
        analyzer.render_swimming_report()

        # Assert
        mock_render.assert_called_once_with("analyzed_data.html", no_data=True)

    @patch("controllers.data_analyzer.RawSwimmingDistance")
    @patch("controllers.data_analyzer.SwimStats")
    @patch("controllers.data_analyzer.render_template")
    def test_render_swimming_report_with_data(self, mock_render, mock_swim_stats, mock_raw_dist, app):
        """Tests successful report rendering."""
        # Arrange
        mock_stats = MagicMock()
        mock_stats.avg_distance = 1000
        mock_stats.total_distance = 5000

        mock_stats.avg_session = 30
        mock_stats.longest_distance = 2000
        mock_stats.longest_session = 45
        mock_stats.total_sessions = 5

        mock_swim_stats.query.first.return_value = mock_stats

        record1 = MagicMock()
        record1.__dict__ = {
            "sourceName": "Apple Watch",
            "value": 500,
            "startDate": "2024-01-01 08:00:00",
            "endDate": "2024-01-01 08:30:00"
        }
        mock_raw_dist.query.all.return_value = [record1]

        analyzer = DataAnalyzer()

        # Act
        analyzer.render_swimming_report()

        # Assert
        assert mock_render.called

    def test_build_display_table_math(self, app):
        """Focused test for the dataframe transformation logic."""
        # Arrange
        analyzer = DataAnalyzer()
        rec = MagicMock()
        rec.__dict__ = {
            "sourceName": "Apple", 
            "value": 100, 
            "startDate": "2024-05-01 10:00:00", 
            "endDate": "2024-05-01 10:30:00"
        }

        with patch("controllers.data_analyzer.RawSwimmingDistance.query") as mock_query:
            mock_query.all.return_value = [rec]

            # Act
            df = analyzer._build_display_table()

            # Assert
            assert df.iloc[0]["Duration"] == 30.0
            assert df.iloc[0]["Source Name"] == "Apple Watch"

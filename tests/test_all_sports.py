"""Comprehensive test suite for all GAAS sports"""
import pytest
import sys
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))


class TestAllSports:
    """Test all sport implementations"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_nfl_implementation(self, temp_dir):
        """Test NFL implementation"""
        # Test collector
        from collectors.nfl_collector import NFLCollector
        collector = NFLCollector()

        # Test data generation
        games = collector.fetch_new_games('rb')
        assert len(games) > 0, "NFL RB games should be generated"

        # Test rarity engine
        from processors.nfl_rarity import NFLRarityEngine
        rarity_engine = NFLRarityEngine('rb')

        rare_performances = rarity_engine.check_current_season('rb')
        assert isinstance(rare_performances, list), "Should return list of performances"

        # Test generator
        from generators.nfl_generator import NFLGenerator
        generator = NFLGenerator()

        if rare_performances:
            # Test JSON generation (will create files in temp dir)
            json_results = generator.generate_json(rare_performances, 'rb')
            assert json_results is not None, "JSON generation should succeed"

    def test_nba_implementation(self):
        """Test NBA implementation"""
        from collectors.nba_collector import NBACollector
        from processors.nba_rarity import NBARarityEngine
        from generators.nba_generator import NBAGenerator

        collector = NBACollector()
        games = collector.fetch_new_games()
        assert len(games) > 0, "NBA games should be generated"

        rarity_engine = NBARarityEngine()
        rare_performances = rarity_engine.check_current_season()
        assert isinstance(rare_performances, list), "Should return list of performances"

        generator = NBAGenerator()
        if rare_performances:
            json_results = generator.generate_json(rare_performances)
            assert json_results is not None, "JSON generation should succeed"

    def test_mlb_implementation(self):
        """Test MLB implementation"""
        from collectors.mlb_collector import MLBCollector
        from processors.mlb_rarity import MLBRarityEngine
        from generators.mlb_generator import MLBGenerator

        collector = MLBCollector()
        games = collector.fetch_new_games()
        assert len(games) > 0, "MLB games should be generated"

        rarity_engine = MLBRarityEngine()
        rare_performances = rarity_engine.check_current_season()
        assert isinstance(rare_performances, list), "Should return list of performances"

        generator = MLBGenerator()
        if rare_performances:
            json_results = generator.generate_json(rare_performances)
            assert json_results is not None, "JSON generation should succeed"

    def test_f1_implementation(self):
        """Test F1 implementation"""
        from collectors.f1_collector import F1Collector
        from processors.f1_rarity import F1RarityEngine
        from generators.f1_generator import F1Generator

        collector = F1Collector()
        races = collector.fetch_new_races()
        assert len(races) > 0, "F1 races should be generated"

        rarity_engine = F1RarityEngine()
        rare_performances = rarity_engine.check_current_season()
        assert isinstance(rare_performances, list), "Should return list of performances"

        generator = F1Generator()
        if rare_performances:
            json_results = generator.generate_json(rare_performances)
            assert json_results is not None, "JSON generation should succeed"

    def test_champions_league_implementation(self):
        """Test Champions League implementation"""
        from collectors.champions_league_collector import ChampionsLeagueCollector
        from processors.champions_league_rarity import ChampionsLeagueRarityEngine
        from generators.champions_league_generator import ChampionsLeagueGenerator

        collector = ChampionsLeagueCollector()
        matches = collector.fetch_new_matches()
        assert len(matches) > 0, "Champions League matches should be generated"

        rarity_engine = ChampionsLeagueRarityEngine()
        rare_performances = rarity_engine.check_current_season()
        assert isinstance(rare_performances, list), "Should return list of performances"

        generator = ChampionsLeagueGenerator()
        if rare_performances:
            json_results = generator.generate_json(rare_performances)
            assert json_results is not None, "JSON generation should succeed"

    def test_nhl_implementation(self):
        """Test NHL implementation"""
        from collectors.nhl_collector import NHLCollector
        from processors.nhl_rarity import NHLRarityEngine
        from generators.nhl_generator import NHLGenerator

        collector = NHLCollector()
        games = collector.fetch_new_games()
        assert len(games) > 0, "NHL games should be generated"

        rarity_engine = NHLRarityEngine()
        rare_performances = rarity_engine.check_current_season()
        assert isinstance(rare_performances, list), "Should return list of performances"

        generator = NHLGenerator()
        if rare_performances:
            json_results = generator.generate_json(rare_performances)
            assert json_results is not None, "JSON generation should succeed"

    def test_unified_orchestrator(self):
        """Test unified orchestrator"""
        from gaas_unified import SportOrchestrator

        orchestrator = SportOrchestrator(auto_commit=False)

        # Test sequential processing
        results = orchestrator.process_all_sports_sequential()
        assert len(results) == 6, "Should process all 6 sports"

        # Verify results structure
        for result in results:
            assert 'sport' in result, "Each result should have sport"
            assert 'rare_performances' in result, "Each result should have rare_performances count"
            assert 'processing_time' in result, "Each result should have processing_time"
            assert 'status' in result, "Each result should have status"

    def test_git_pusher(self, temp_dir):
        """Test Git pusher functionality"""
        from utils.git_pusher import GitPusher
        import subprocess

        # Create a git repo in temp directory
        repo_path = temp_dir
        subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True, capture_output=True)

        # Create a test file
        test_file = repo_path / "test.json"
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        # Test GitPusher (without remote)
        try:
            pusher = GitPusher(str(repo_path))
            # This should fail gracefully since there's no remote
            result = pusher.push_results([str(test_file)], "Test commit")
            # Should fail due to no remote, but not crash
        except Exception as e:
            # Expected to fail due to no remote
            assert "no such ref" in str(e).lower() or "origin" in str(e).lower() or "remote" in str(e).lower()

    def test_web_app_endpoints(self):
        """Test web app endpoints"""
        from web.app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200, "Health endpoint should work"
        assert response.json()["status"] == "healthy", "Health status should be healthy"

        # Test main endpoint (might have no data)
        response = client.get("/")
        assert response.status_code == 200, "Main endpoint should work"

        # Test sport endpoints
        sport_endpoints = ["/nba", "/mlb", "/f1", "/nhl", "/champions-league"]
        for endpoint in sport_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"{endpoint} should work"

        # Test API endpoints
        api_endpoints = [
            "/api/nba/summary", "/api/mlb/summary", "/api/f1/summary",
            "/api/nhl/latest", "/api/champions-league/latest"
        ]
        for endpoint in api_endpoints:
            response = client.get(endpoint)
            # Should return either data or error, but not crash
            assert response.status_code in [200, 404], f"{endpoint} should not crash"

    def test_rarity_engine_base(self):
        """Test base rarity engine functionality"""
        from processors.rarity_engine import RarityEngine

        # Test with a dummy sport implementation
        class DummyRarityEngine(RarityEngine):
            def __init__(self):
                super().__init__('dummy', 'all')

            def _find_matches(self, performance):
                return []

            def _get_total_games(self):
                return 1000

        engine = DummyRarityEngine()

        # Test rarity calculation with dummy data
        performance = {
            'player_id': 'test_player',
            'test_stat': 100
        }

        rarity = engine.compute_rarity(performance)
        assert 'rarity_score' in rarity, "Should have rarity_score"
        assert 'classification' in rarity, "Should have classification"
        assert 'occurrence_count' in rarity, "Should have occurrence_count"

    def test_data_quality(self):
        """Test data quality across all sports"""
        sports_data = {
            'nfl': lambda: self._get_nfl_data(),
            'nba': lambda: self._get_nba_data(),
            'mlb': lambda: self._get_mlb_data(),
            'f1': lambda: self._get_f1_data(),
            'champions_league': lambda: self._get_champions_league_data(),
            'nhl': lambda: self._get_nhl_data()
        }

        for sport, data_getter in sports_data.items():
            try:
                data = data_getter()

                # Basic data quality checks
                assert data is not None, f"{sport} should return data"
                assert len(data) > 0, f"{sport} should have non-zero data"

                # Check for required fields
                if sport in ['nba', 'mlb', 'f1', 'champions_league', 'nhl']:
                    for item in data[:5]:  # Check first 5 items
                        assert 'player_name' in item, f"{sport} items should have player_name"
                        assert 'rarity_score' in item, f"{sport} items should have rarity_score"
                        assert 'classification' in item, f"{sport} items should have classification"

            except Exception as e:
                pytest.fail(f"Data quality test failed for {sport}: {e}")

    def _get_nfl_data(self):
        from processors.nfl_rarity import NFLRarityEngine
        engine = NFLRarityEngine('rb')
        return engine.check_current_season('rb')

    def _get_nba_data(self):
        from processors.nba_rarity import NBARarityEngine
        engine = NBARarityEngine()
        return engine.check_current_season()

    def _get_mlb_data(self):
        from processors.mlb_rarity import MLBRarityEngine
        engine = MLBRarityEngine()
        return engine.check_current_season()

    def _get_f1_data(self):
        from processors.f1_rarity import F1RarityEngine
        engine = F1RarityEngine()
        return engine.check_current_season()

    def _get_champions_league_data(self):
        from processors.champions_league_rarity import ChampionsLeagueRarityEngine
        engine = ChampionsLeagueRarityEngine()
        return engine.check_current_season()

    def _get_nhl_data(self):
        from processors.nhl_rarity import NHLRarityEngine
        engine = NHLRarityEngine()
        return engine.check_current_season()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
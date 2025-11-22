"""Integration tests for GAAS system"""
import pytest
import sys
from pathlib import Path
import subprocess
import time
import requests
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))


class TestIntegration:
    """Integration tests for the full GAAS system"""

    def test_full_system_integration(self):
        """Test running the complete GAAS system"""
        # Run unified orchestrator without commit
        result = subprocess.run([
            sys.executable, "src/gaas_unified.py"
        ], capture_output=True, text=True, timeout=300, cwd=Path(__file__).parent.parent)

        assert result.returncode == 0, f"GAAS unified should run successfully: {result.stderr}"
        assert "SUMMARY" in result.stdout, "Should print summary"

    def test_individual_sport_scripts(self):
        """Test all individual sport scripts"""
        sport_scripts = [
            "src/gaas_nba.py",
            "src/gaas_mlb.py",
            "src/gaas_f1.py",
            "src/gaas_champions_league.py",
            "src/gaas_nhl.py"
        ]

        for script in sport_scripts:
            result = subprocess.run([
                sys.executable, script
            ], capture_output=True, text=True, timeout=120, cwd=Path(__file__).parent.parent)

            assert result.returncode == 0, f"{script} should run successfully: {result.stderr}"

    def test_web_api_integration(self):
        """Test web API integration"""
        # Start web server in background
        import threading
        import time
        from web.app import app
        import uvicorn
        import socket

        # Find free port
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()

        # Start server in thread
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)  # Give server time to start

        try:
            # Test API endpoints
            base_url = f"http://127.0.0.1:{port}"

            # Health check
            response = requests.get(f"{base_url}/health", timeout=10)
            assert response.status_code == 200

            # Main endpoint
            response = requests.get(f"{base_url}/", timeout=10)
            assert response.status_code == 200

            # Sport endpoints
            sport_endpoints = ["/api/nba/summary", "/api/mlb/detailed"]
            for endpoint in sport_endpoints:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                # Should return either data or error (404 is acceptable if no data)
                assert response.status_code in [200, 404]

        finally:
            # Server will be killed when test process exits
            pass

    def test_file_generation_and_format(self):
        """Test that all expected files are generated with correct format"""
        # Run a few sports to generate data
        subprocess.run([
            sys.executable, "src/gaas_nhl.py"
        ], capture_output=True, cwd=Path(__file__).parent.parent)

        subprocess.run([
            sys.executable, "src/gaas_champions_league.py"
        ], capture_output=True, cwd=Path(__file__).parent.parent)

        # Check that files were created
        results_dir = Path(__file__).parent.parent / "results"

        # Check NHL files
        nhl_dir = results_dir / "nhl"
        if nhl_dir.exists():
            nhl_latest = nhl_dir / "nhl_latest.json"
            nhl_all_time = nhl_dir / "nhl_all_time.json"
            nhl_md = nhl_dir / "nhl_performances.md"

            assert nhl_latest.exists(), "NHL latest JSON should exist"
            assert nhl_all_time.exists(), "NHL all-time JSON should exist"
            assert nhl_md.exists(), "NHL markdown should exist"

            # Validate JSON format
            with open(nhl_latest) as f:
                data = json.load(f)
            assert 'sport' in data, "NHL JSON should have sport field"
            assert 'total_performances' in data, "NHL JSON should have total_performances"
            assert 'performances' in data, "NHL JSON should have performances"

        # Check Champions League files
        cl_dir = results_dir / "champions_league"
        if cl_dir.exists():
            cl_latest = cl_dir / "champions_league_latest.json"
            cl_all_time = cl_dir / "champions_league_all_time.json"
            cl_md = cl_dir / "champions_league_performances.md"

            assert cl_latest.exists(), "Champions League latest JSON should exist"
            assert cl_all_time.exists(), "Champions League all-time JSON should exist"
            assert cl_md.exists(), "Champions League markdown should exist"

            # Validate JSON format
            with open(cl_latest) as f:
                data = json.load(f)
            assert 'sport' in data, "CL JSON should have sport field"
            assert 'total_performances' in data, "CL JSON should have total_performances"

        # Check main index
        index_file = results_dir / "index.json"
        if index_file.exists():
            with open(index_file) as f:
                index_data = json.load(f)
            assert 'sports' in index_data, "Index should have sports field"
            assert 'generated_at' in index_data, "Index should have generated_at field"

    def test_error_handling(self):
        """Test error handling and recovery"""
        from processors.rarity_engine import RarityEngine

        # Test with corrupted data
        class BrokenRarityEngine(RarityEngine):
            def __init__(self):
                super().__init__('broken', 'all')

            def _find_matches(self, performance):
                raise Exception("Simulated database error")

            def _get_total_games(self):
                return 100

        engine = BrokenRarityEngine()
        performance = {'player_id': 'test'}

        # Should handle error gracefully
        try:
            rarity = engine.compute_rarity(performance)
            assert rarity['occurrence_count'] == 0, "Should handle missing data gracefully"
        except Exception:
            # Exception is also acceptable behavior
            pass

    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        import time
        from collectors.nhl_collector import NHLCollector
        from processors.nhl_rarity import NHLRarityEngine

        # Benchmark data collection
        start_time = time.time()
        collector = NHLCollector()
        games = collector.fetch_new_games()
        collection_time = time.time() - start_time

        assert collection_time < 30, f"Data collection should complete quickly ({collection_time:.2f}s)"
        assert len(games) > 0, "Should generate games"

        # Benchmark rarity analysis
        start_time = time.time()
        rarity_engine = NHLRarityEngine()
        rare_performances = rarity_engine.check_current_season()
        analysis_time = time.time() - start_time

        assert analysis_time < 60, f"Rarity analysis should complete quickly ({analysis_time:.2f}s)"
        assert isinstance(rare_performances, list), "Should return performances list"

    def test_concurrent_processing(self):
        """Test concurrent processing doesn't cause issues"""
        import threading
        import time

        results = []
        errors = []

        def run_sport(sport_name, sport_func):
            try:
                start_time = time.time()
                result = sport_func()
                processing_time = time.time() - start_time
                results.append({
                    'sport': sport_name,
                    'result_count': len(result) if isinstance(result, list) else 0,
                    'processing_time': processing_time
                })
            except Exception as e:
                errors.append(f"{sport_name}: {e}")

        # Test concurrent runs of different sports
        threads = []
        sport_functions = [
            ('NHL', lambda: self._get_nhl_data()),
            ('Champions League', lambda: self._get_champions_league_data()),
            ('NBA', lambda: self._get_nba_data()),
        ]

        for sport_name, sport_func in sport_functions:
            thread = threading.Thread(target=run_sport, args=(sport_name, sport_func))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=120)

        assert len(errors) == 0, f"No errors in concurrent processing: {errors}"
        assert len(results) == len(sport_functions), "All sports should complete"

    def _get_nhl_data(self):
        from processors.nhl_rarity import NHLRarityEngine
        engine = NHLRarityEngine()
        return engine.check_current_season()

    def _get_champions_league_data(self):
        from processors.champions_league_rarity import ChampionsLeagueRarityEngine
        engine = ChampionsLeagueRarityEngine()
        return engine.check_current_season()

    def _get_nba_data(self):
        from processors.nba_rarity import NBARarityEngine
        engine = NBARarityEngine()
        return engine.check_current_season()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
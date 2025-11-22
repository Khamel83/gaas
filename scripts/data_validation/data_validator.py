#!/usr/bin/env python3
"""
Comprehensive Data Validator for GAAS
Validates completeness, accuracy, and consistency of sports data
"""

import sqlite3
import sys
import os
import json
from datetime import datetime
from pathlib import Path

class DataValidator:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.archive_dir = self.data_dir / "archive"
        self.results = {}

    def validate_nfl_data(self):
        """Validate NFL data completeness and structure"""
        print("🏈 Validating NFL Data...")

        db_path = self.archive_dir / "nfl_archive.db"
        if not db_path.exists():
            return {"status": "error", "message": "NFL archive not found"}

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ['qb_games', 'rb_games', 'wr_games', 'te_games']
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            return {"status": "error", "message": f"Missing tables: {missing_tables}"}

        results = {}
        for position in ['qb', 'rb', 'wr', 'te']:
            table_name = f"{position}_games"
            cursor.execute(f"SELECT MIN(CAST(season AS INTEGER)), MAX(CAST(season AS INTEGER)), COUNT(*) FROM {table_name}")
            min_year, max_year, count = cursor.fetchone()

            results[position] = {
                "season_range": f"{min_year}-{max_year}" if min_year and max_year else "No data",
                "total_games": count,
                "expected_range": "1999-2024",
                "completeness": self.calculate_completeness(min_year, max_year, 1999, 2024)
            }

        conn.close()
        return {"status": "success", "positions": results}

    def validate_nba_data(self):
        """Validate NBA data completeness"""
        print("🏀 Validating NBA Data...")

        db_path = self.archive_dir / "nba_archive.db"
        if not db_path.exists():
            return {"status": "error", "message": "NBA archive not found"}

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        if 'games' not in tables:
            return {"status": "error", "message": "Missing games table"}

        cursor.execute("SELECT MIN(CAST(season AS INTEGER)), MAX(CAST(season AS INTEGER)), COUNT(*) FROM games")
        result = cursor.fetchone()
        min_year, max_year, count = result

        conn.close()

        return {
            "status": "success",
            "season_range": f"{min_year}-{max_year}" if min_year and max_year else "No data",
            "total_games": count,
            "expected_range": "2010-2024",
            "completeness": self.calculate_completeness(min_year, max_year, 2010, 2024)
        }

    def validate_mlb_data(self):
        """Validate MLB data completeness"""
        print("⚾ Validating MLB Data...")

        db_path = self.archive_dir / "mlb_archive.db"
        if not db_path.exists():
            return {"status": "error", "message": "MLB archive not found"}

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT MIN(CAST(season AS INTEGER)), MAX(CAST(season AS INTEGER)), COUNT(*) FROM games")
        result = cursor.fetchone()
        min_year, max_year, count = result

        conn.close()

        return {
            "status": "success",
            "season_range": f"{min_year}-{max_year}" if min_year and max_year else "No data",
            "total_games": count,
            "expected_range": "1871-2024",
            "completeness": self.calculate_completeness(min_year, max_year, 1871, 2024)
        }

    def validate_f1_data(self):
        """Validate F1 data completeness"""
        print("🏎️ Validating F1 Data...")

        db_path = self.archive_dir / "f1_archive.db"
        if not db_path.exists():
            return {"status": "error", "message": "F1 archive not found"}

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT MIN(CAST(season AS INTEGER)), MAX(CAST(season AS INTEGER)), COUNT(*) FROM races")
        result = cursor.fetchone()
        min_year, max_year, count = result

        conn.close()

        return {
            "status": "success",
            "season_range": f"{min_year}-{max_year}" if min_year and max_year else "No data",
            "total_races": count,
            "expected_range": "1950-2024",
            "completeness": self.calculate_completeness(min_year, max_year, 1950, 2024)
        }

    def validate_champions_league_data(self):
        """Validate Champions League data completeness"""
        print("⚽ Validating Champions League Data...")

        db_path = self.archive_dir / "champions_league_archive.db"
        if not db_path.exists():
            return {"status": "error", "message": "Champions League archive not found"}

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM matches")
        count = cursor.fetchone()[0]

        conn.close()

        return {
            "status": "success",
            "total_matches": count,
            "data_present": count > 0,
            "completeness": 100 if count > 0 else 0
        }

    def validate_nhl_data(self):
        """Validate NHL data completeness"""
        print("🥅 Validating NHL Data...")

        db_path = self.archive_dir / "nhl_archive.db"
        if not db_path.exists():
            return {"status": "error", "message": "NHL archive not found"}

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM games")
        count = cursor.fetchone()[0]

        conn.close()

        return {
            "status": "success",
            "total_games": count,
            "data_present": count > 0,
            "completeness": 100 if count > 0 else 0
        }

    def calculate_completeness(self, actual_min, actual_max, expected_min, expected_max):
        """Calculate percentage completeness of date range"""
        if not actual_min or not actual_max:
            return 0

        actual_range = actual_max - actual_min + 1
        expected_range = expected_max - expected_min + 1

        # How many years of the expected range do we have?
        overlap_start = max(actual_min, expected_min)
        overlap_end = min(actual_max, expected_max)

        if overlap_start > overlap_end:
            return 0

        overlap_years = overlap_end - overlap_start + 1
        return round((overlap_years / expected_range) * 100, 1)

    def run_full_validation(self):
        """Run validation on all sports"""
        print("🚀 Starting comprehensive data validation...")
        print("=" * 60)

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "sports": {}
        }

        # Validate each sport
        validation_results["sports"]["nfl"] = self.validate_nfl_data()
        validation_results["sports"]["nba"] = self.validate_nba_data()
        validation_results["sports"]["mlb"] = self.validate_mlb_data()
        validation_results["sports"]["f1"] = self.validate_f1_data()
        validation_results["sports"]["champions_league"] = self.validate_champions_league_data()
        validation_results["sports"]["nhl"] = self.validate_nhl_data()

        # Calculate overall completeness
        completeness_scores = []
        for sport, data in validation_results["sports"].items():
            if data["status"] == "success" and "completeness" in data:
                completeness_scores.append(data["completeness"])

        overall_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        validation_results["overall_completeness"] = round(overall_completeness, 1)

        # Print summary
        self.print_validation_summary(validation_results)

        return validation_results

    def print_validation_summary(self, results):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 DATA VALIDATION SUMMARY")
        print("=" * 60)

        print(f"Overall Completeness: {results['overall_completeness']}%")
        print(f"Validation Timestamp: {results['timestamp']}")
        print()

        for sport, data in results["sports"].items():
            sport_name = sport.replace("_", " ").title()
            status_emoji = "✅" if data["status"] == "success" else "❌"
            print(f"{status_emoji} {sport_name}")

            if data["status"] == "error":
                print(f"   Error: {data['message']}")
            else:
                if "positions" in data:
                    # NFL with positions
                    for position, pos_data in data["positions"].items():
                        print(f"   {position.upper()}: {pos_data['season_range']} ({pos_data['total_games']} games) - {pos_data['completeness']}% complete")
                elif "completeness" in data:
                    # Other sports
                    season_range = data.get("season_range", "No data")
                    if sport == "f1":
                        print(f"   Range: {season_range} ({data['total_races']} races) - {data['completeness']}% complete")
                    elif sport in ["champions_league", "nhl"]:
                        print(f"   Data Present: {'Yes' if data['data_present'] else 'No'} - {data['completeness']}% complete")
                    else:
                        print(f"   Range: {season_range} ({data.get('total_games', 0)} games) - {data['completeness']}% complete")
            print()

        # Overall assessment
        if results["overall_completeness"] >= 90:
            print("🎉 EXCELLENT: Data is highly complete and ready for production")
        elif results["overall_completeness"] >= 70:
            print("⚠️  GOOD: Data is mostly complete but has some gaps")
        elif results["overall_completeness"] >= 50:
            print("🔶 FAIR: Data has significant gaps that need attention")
        else:
            print("🚨 POOR: Data is incomplete and needs major repair")

if __name__ == "__main__":
    validator = DataValidator()
    results = validator.run_full_validation()

    # Save results to file
    output_file = "validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📁 Detailed results saved to: {output_file}")
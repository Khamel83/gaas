#!/usr/bin/env python3
"""
Complete NFL Data Repair Script
Downloads and processes complete NFL data from 1999-2024
"""

import os
import sys
import sqlite3
import requests
import zipfile
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

class NFLDataRepairer:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.archive_dir = self.data_dir / "archive"
        self.temp_dir = Path("temp_nfl_data")
        self.temp_dir.mkdir(exist_ok=True)

    def download_nflfastr_data(self):
        """Download complete nflfastR dataset (1999-2024)"""
        print("🏈 Downloading complete NFL dataset (1999-2024)...")

        # nflfastR data releases
        releases = [
            {
                "year_range": "1999_2009",
                "url": "https://github.com/nflverse/nflfastR-data/releases/download/pbp/pbp_1999_2009.zip"
            },
            {
                "year_range": "2010_2019",
                "url": "https://github.com/nflverse/nflfastR-data/releases/download/pbp/pbp_2010_2019.zip"
            },
            {
                "year_range": "2020_2024",
                "url": "https://github.com/nflverse/nflfastR-data/releases/download/pbp/pbp_2020_2024.zip"
            }
        ]

        total_downloaded = 0

        for release in releases:
            zip_path = self.temp_dir / f"pbp_{release['year_range']}.zip"

            if zip_path.exists():
                print(f"✅ Already downloaded: {release['year_range']}")
                continue

            print(f"📥 Downloading: {release['year_range']}...")

            try:
                response = requests.get(release['url'], timeout=300)
                response.raise_for_status()

                with open(zip_path, 'wb') as f:
                    f.write(response.content)

                print(f"✅ Downloaded: {release['year_range']} ({len(response.content):,} bytes)")
                total_downloaded += len(response.content)

            except Exception as e:
                print(f"❌ Failed to download {release['year_range']}: {e}")
                return False

        print(f"🎉 Total downloaded: {total_downloaded:,} bytes")
        return True

    def extract_and_process_data(self):
        """Extract zip files and process into unified format"""
        print("🔧 Extracting and processing NFL data...")

        # Create new database
        new_db_path = self.archive_dir / "nfl_archive_complete.db"
        if new_db_path.exists():
            new_db_path.unlink()

        conn = sqlite3.connect(str(new_db_path))
        cursor = conn.cursor()

        # Create unified games table
        cursor.execute("""
            CREATE TABLE games (
                game_id TEXT,
                player_id TEXT,
                player_name TEXT,
                position TEXT,
                team TEXT,
                opponent TEXT,
                season INTEGER,
                week INTEGER,
                game_date TEXT,

                -- Rushing stats
                rush_attempts INTEGER DEFAULT 0,
                rush_yards INTEGER DEFAULT 0,
                rush_td INTEGER DEFAULT 0,
                rush_yards_per_attempt REAL DEFAULT 0,
                longest_rush INTEGER DEFAULT 0,
                rush_fumbles INTEGER DEFAULT 0,

                -- Passing stats (QB)
                pass_attempts INTEGER DEFAULT 0,
                completions INTEGER DEFAULT 0,
                pass_yards INTEGER DEFAULT 0,
                pass_td INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                passer_rating REAL DEFAULT 0,
                completion_pct REAL DEFAULT 0,

                -- Receiving stats (WR/TE)
                receptions INTEGER DEFAULT 0,
                receiving_yards INTEGER DEFAULT 0,
                receiving_td INTEGER DEFAULT 0,
                targets INTEGER DEFAULT 0,
                yards_per_reception REAL DEFAULT 0,
                longest_reception INTEGER DEFAULT 0,

                -- Defense (all positions)
                tackles INTEGER DEFAULT 0,
                sacks INTEGER DEFAULT 0,
                interceptions_def INTEGER DEFAULT 0,
                fumbles_recovered INTEGER DEFAULT 0,

                -- Special teams
                field_goals_made INTEGER DEFAULT 0,
                field_goals_attempted INTEGER DEFAULT 0,
                extra_points_made INTEGER DEFAULT 0,

                PRIMARY KEY (game_id, player_id)
            )
        """)

        # Process each zip file
        total_games_processed = 0

        for zip_file in sorted(self.temp_dir.glob("pbp_*.zip")):
            print(f"📦 Processing: {zip_file.name}")

            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    # Extract and process CSV files
                    for file_name in zip_ref.namelist():
                        if file_name.endswith('.csv') and 'pbp' in file_name:
                            with zip_ref.open(file_name) as csv_file:
                                df = pd.read_csv(csv_file)

                                # Process play-by-play data into player game stats
                                games_processed = self.process_season_data(df, cursor)
                                total_games_processed += games_processed

            except Exception as e:
                print(f"❌ Error processing {zip_file.name}: {e}")
                continue

        conn.commit()
        conn.close()

        print(f"🎉 Processed {total_games_processed:,} player games")
        return True

    def process_season_data(self, df, cursor):
        """Process single season of play-by-play data"""
        if df.empty:
            return 0

        # Group by game, player to get season-long stats
        player_games = []

        for (game_id, player_id), group in df.groupby(['game_id', 'player_id']):
            if pd.isna(player_id):  # Skip plays with no player
                continue

            # Get player info
            player_name = group['player_name'].iloc[0] if 'player_name' in group.columns else ''
            position = group['position'].iloc[0] if 'position' in group.columns else ''
            team = group['posteam'].iloc[0] if 'posteam' in group.columns else ''
            opponent = group['defteam'].iloc[0] if 'defteam' in group.columns else ''
            season = int(group['season'].iloc[0]) if 'season' in group.columns else 0
            week = int(group['week'].iloc[0]) if 'week' in group.columns else 0

            # Skip invalid data
            if not all([game_id, player_id, position, team]):
                continue

            # Calculate stats from play-by-play data
            stats = self.calculate_player_stats(group)

            player_games.append((
                game_id, player_id, player_name, position, team, opponent,
                season, week, '',  # game_date

                # Rushing
                stats['rush_attempts'], stats['rush_yards'], stats['rush_td'],
                stats['rush_yards_per_attempt'], stats['longest_rush'], stats['rush_fumbles'],

                # Passing
                stats['pass_attempts'], stats['completions'], stats['pass_yards'],
                stats['pass_td'], stats['interceptions'], stats['passer_rating'], stats['completion_pct'],

                # Receiving
                stats['receptions'], stats['receiving_yards'], stats['receiving_td'],
                stats['targets'], stats['yards_per_reception'], stats['longest_reception'],

                # Defense
                stats['tackles'], stats['sacks'], stats['interceptions_def'], stats['fumbles_recovered'],

                # Special teams
                stats['field_goals_made'], stats['field_goals_attempted'], stats['extra_points_made']
            ))

        # Insert into database
        if player_games:
            cursor.executemany("""
                INSERT OR REPLACE INTO games VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
            """, player_games)

        return len(player_games)

    def calculate_player_stats(self, group):
        """Calculate player statistics from play data"""
        stats = {
            'rush_attempts': 0, 'rush_yards': 0, 'rush_td': 0,
            'rush_yards_per_attempt': 0, 'longest_rush': 0, 'rush_fumbles': 0,
            'pass_attempts': 0, 'completions': 0, 'pass_yards': 0,
            'pass_td': 0, 'interceptions': 0, 'passer_rating': 0, 'completion_pct': 0,
            'receptions': 0, 'receiving_yards': 0, 'receiving_td': 0,
            'targets': 0, 'yards_per_reception': 0, 'longest_reception': 0,
            'tackles': 0, 'sacks': 0, 'interceptions_def': 0, 'fumbles_recovered': 0,
            'field_goals_made': 0, 'field_goals_attempted': 0, 'extra_points_made': 0
        }

        # Only process rows where this player is involved
        if 'player_id' not in group.columns:
            return stats

        # Rushing stats
        rush_mask = (group['rush_attempt'] == 1) if 'rush_attempt' in group.columns else False
        if rush_mask.any():
            rush_data = group[rush_mask]
            stats['rush_attempts'] = len(rush_data)
            stats['rush_yards'] = int(rush_data['yards_gained'].fillna(0).sum())
            stats['rush_td'] = int(rush_data['rush_touchdown'].fillna(0).sum())
            stats['longest_rush'] = int(rush_data['yards_gained'].fillna(0).max())
            stats['rush_fumbles'] = int(rush_data['fumble'].fillna(0).sum())

            if stats['rush_attempts'] > 0:
                stats['rush_yards_per_attempt'] = round(stats['rush_yards'] / stats['rush_attempts'], 2)

        # Passing stats
        pass_mask = (group['pass_attempt'] == 1) if 'pass_attempt' in group.columns else False
        if pass_mask.any():
            pass_data = group[pass_mask]
            stats['pass_attempts'] = len(pass_data)
            stats['completions'] = int(pass_data['complete_pass'].fillna(0).sum())
            stats['pass_yards'] = int(pass_data['yards_gained'].fillna(0).sum())
            stats['pass_td'] = int(pass_data['pass_touchdown'].fillna(0).sum())
            stats['interceptions'] = int(pass_data['interception'].fillna(0).sum())

            if stats['pass_attempts'] > 0:
                stats['completion_pct'] = round((stats['completions'] / stats['pass_attempts']) * 100, 2)
                # Simplified passer rating calculation
                stats['passer_rating'] = self.calculate_passer_rating(
                    stats['completions'], stats['pass_attempts'], stats['pass_yards'],
                    stats['pass_td'], stats['interceptions']
                )

        # Receiving stats
        receive_mask = group['receiver_id'] == group['player_id'] if 'receiver_id' in group.columns else False
        target_mask = (group['pass_attempt'] == 1) & receive_mask

        if target_mask.any():
            target_data = group[target_mask]
            stats['targets'] = len(target_data)
            completed_mask = target_data['complete_pass'] == 1 if 'complete_pass' in target_data.columns else False

            if completed_mask.any():
                catch_data = target_data[completed_mask]
                stats['receptions'] = len(catch_data)
                stats['receiving_yards'] = int(catch_data['yards_gained'].fillna(0).sum())
                stats['receiving_td'] = int(catch_data['pass_touchdown'].fillna(0).sum())
                stats['longest_reception'] = int(catch_data['yards_gained'].fillna(0).max())

                if stats['receptions'] > 0:
                    stats['yards_per_reception'] = round(stats['receiving_yards'] / stats['receptions'], 2)

        return stats

    def calculate_passer_rating(self, completions, attempts, yards, touchdowns, interceptions):
        """Calculate NFL passer rating"""
        if attempts == 0:
            return 0.0

        # NFL passer rating formula
        a = ((completions / attempts) * 100 - 30) / 20
        b = ((yards / attempts) - 3) / 4
        c = (touchdowns / attempts) * 20
        d = 2.375 - ((interceptions / attempts) * 25)

        # Clamp values between 0 and 2.375
        for val in [a, b, c, d]:
            val = max(0, min(2.375, val))

        rating = (a + b + c + d) / 6 * 100
        return round(rating, 1)

    def validate_repair(self):
        """Validate the repaired NFL data"""
        print("🔍 Validating repaired NFL data...")

        db_path = self.archive_dir / "nfl_archive_complete.db"
        if not db_path.exists():
            return {"status": "error", "message": "Repaired database not found"}

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check data range
        cursor.execute("SELECT MIN(season), MAX(season), COUNT(*) FROM games")
        min_year, max_year, total_games = cursor.fetchone()

        # Check position distribution
        cursor.execute("""
            SELECT position, COUNT(*) as count,
                   MIN(season) as first_year, MAX(season) as last_year
            FROM games GROUP BY position
        """)
        position_data = cursor.fetchall()

        conn.close()

        return {
            "status": "success",
            "season_range": f"{min_year}-{max_year}" if min_year and max_year else "No data",
            "total_player_games": total_games,
            "positions": dict(position_data)
        }

    def cleanup(self):
        """Clean up temporary files"""
        print("🧹 Cleaning up temporary files...")
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def run_complete_repair(self):
        """Run the complete NFL data repair process"""
        print("🚀 Starting complete NFL data repair...")

        try:
            # Step 1: Download data
            if not self.download_nflfastr_data():
                print("❌ Failed to download NFL data")
                return False

            # Step 2: Process data
            if not self.extract_and_process_data():
                print("❌ Failed to process NFL data")
                return False

            # Step 3: Validate repair
            validation = self.validate_repair()
            print(f"✅ NFL Data Repair Complete: {validation}")

            return True

        except Exception as e:
            print(f"❌ NFL data repair failed: {e}")
            return False

        finally:
            self.cleanup()

if __name__ == "__main__":
    repairer = NFLDataRepairer()
    success = repairer.run_complete_repair()

    if success:
        print("🎉 NFL data repair completed successfully!")
    else:
        print("💥 NFL data repair failed!")
        sys.exit(1)
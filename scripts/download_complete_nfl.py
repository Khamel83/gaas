#!/usr/bin/env python3
"""
Complete NFL Historical Data Downloader
Downloads the full nflfastR dataset 1999-2024
"""

import os
import sys
import requests
import zipfile
import subprocess
from pathlib import Path
import time
from datetime import datetime

class CompleteNFLDownloader:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw_nfl_data"
        self.raw_dir.mkdir(exist_ok=True)

    def check_disk_space(self):
        """Check if we have enough disk space"""
        try:
            result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) >= 2:
                    # Parse disk space (this is approximate)
                    space_line = lines[1]
                    available_gb = float(space_line.split()[3].replace('G', ''))
                    print(f"💾 Available disk space: {available_gb}GB")
                    if available_gb < 10:
                        print("⚠️  Warning: Less than 10GB available space")
                    return True
        except:
            pass
        return True

    def download_nflfastr_complete(self):
        """Download the complete nflfastR dataset"""
        print("🏈 Downloading COMPLETE NFL Historical Dataset (1999-2024)")
        print("=" * 60)

        # nflfastR has consolidated releases
        download_urls = [
            {
                "name": "Complete NFL Data 1999-2024",
                "url": "https://github.com/nflverse/nflfastR-data/releases/download/pbp/pbp_1999_2024.zip",
                "expected_size_gb": 5.2
            }
        ]

        total_downloaded = 0

        for download in download_urls:
            zip_path = self.raw_dir / f"nfl_complete_1999_2024.zip"

            if zip_path.exists():
                print(f"✅ Already downloaded: {download['name']}")
                continue

            print(f"📥 Downloading: {download['name']}")
            print(f"   Expected size: ~{download['expected_size_gb']}GB")
            print(f"   URL: {download['url']}")

            try:
                # Download with progress tracking
                response = requests.get(download['url'], stream=True, timeout=600)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            # Progress bar
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                size_mb = downloaded / (1024 * 1024)
                                total_mb = total_size / (1024 * 1024)
                                print(f"   Progress: {progress:.1f}% ({size_mb:.1f}MB/{total_mb:.1f}MB)", end='\r')

                print(f"\n✅ Downloaded: {download['name']} ({downloaded:,} bytes)")
                total_downloaded += downloaded

            except Exception as e:
                print(f"❌ Failed to download {download['name']}: {e}")
                if zip_path.exists():
                    zip_path.unlink()
                return False

        print(f"\n🎉 Total downloaded: {total_downloaded / (1024*1024*1024):.1f}GB")
        return True

    def extract_and_validate(self):
        """Extract and validate the downloaded data"""
        print("\n🔧 Extracting and validating NFL data...")

        zip_path = self.raw_dir / f"nfl_complete_1999_2024.zip"

        if not zip_path.exists():
            print("❌ Downloaded file not found")
            return False

        # Create extraction directory
        extract_dir = self.raw_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)

        try:
            print("📦 Extracting ZIP file...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"   Found {len(file_list)} files in archive")

                # Extract CSV files
                csv_files = [f for f in file_list if f.endswith('.csv')]
                print(f"   Extracting {len(csv_files)} CSV files...")

                zip_ref.extractall(extract_dir)

            print(f"✅ Extracted to: {extract_dir}")

            # Validate extracted data
            csv_files = list(extract_dir.glob("*.csv"))
            if not csv_files:
                print("❌ No CSV files found after extraction")
                return False

            # Check first few files to understand structure
            for csv_file in csv_files[:3]:
                print(f"   📄 Found: {csv_file.name}")

                # Try to get basic info
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_file)
                    print(f"      Shape: {df.shape}")
                    if 'season' in df.columns:
                        seasons = df['season'].unique()
                        print(f"      Seasons: {min(seasons)}-{max(seasons)}")
                except:
                    print(f"      (Could not read file)")

            return True

        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False

    def create_database_from_csvs(self):
        """Create a proper SQLite database from CSV files"""
        print("\n💾 Creating complete NFL database...")

        extract_dir = self.raw_dir / "extracted"
        archive_dir = self.data_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        # Path for new complete database
        db_path = archive_dir / "nfl_archive_complete.db"
        if db_path.exists():
            db_path.unlink()  # Remove old version

        try:
            import sqlite3
            import pandas as pd
            from tqdm import tqdm

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            print("   🏗️  Creating database structure...")

            # Create unified games table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
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
                    fumbles_lost INTEGER DEFAULT 0,

                    -- Passing stats
                    pass_attempts INTEGER DEFAULT 0,
                    completions INTEGER DEFAULT 0,
                    pass_yards INTEGER DEFAULT 0,
                    pass_td INTEGER DEFAULT 0,
                    interceptions INTEGER DEFAULT 0,
                    passer_rating REAL DEFAULT 0,

                    -- Receiving stats
                    receptions INTEGER DEFAULT 0,
                    receiving_yards INTEGER DEFAULT 0,
                    receiving_td INTEGER DEFAULT 0,
                    targets INTEGER DEFAULT 0,

                    -- Defense
                    tackles INTEGER DEFAULT 0,
                    sacks INTEGER DEFAULT 0,
                    forced_fumbles INTEGER DEFAULT 0,

                    PRIMARY KEY (game_id, player_id)
                )
            """)

            print("   📊 Processing CSV files...")
            csv_files = list(extract_dir.glob("*.csv"))

            total_rows = 0
            seasons_found = set()

            for csv_file in tqdm(csv_files, desc="Processing CSVs"):
                try:
                    # Read in chunks to handle large files
                    for chunk_df in pd.read_csv(csv_file, chunksize=10000):
                        # Process this chunk to game-level stats
                        game_stats = self.process_chunk_to_game_stats(chunk_df)

                        if not game_stats.empty:
                            # Insert into database
                            game_stats.to_sql('games', conn, if_exists='append', index=False)
                            total_rows += len(game_stats)

                            # Track seasons
                            if 'season' in game_stats.columns:
                                seasons_found.update(game_stats['season'].unique())

                except Exception as e:
                    print(f"   ⚠️  Error processing {csv_file.name}: {e}")
                    continue

            # Create indexes
            print("   🔍 Creating database indexes...")
            cursor.execute("CREATE INDEX idx_games_season ON games(season)")
            cursor.execute("CREATE INDEX idx_games_position ON games(position)")
            cursor.execute("CREATE INDEX idx_games_player ON games(player_id)")

            conn.commit()
            conn.close()

            print(f"✅ Database created successfully!")
            print(f"   Total player games: {total_rows:,}")
            print(f"   Seasons covered: {sorted(seasons_found)}")
            print(f"   Database size: {db_path.stat().st_size / (1024*1024):.1f}MB")

            return True

        except Exception as e:
            print(f"❌ Database creation failed: {e}")
            return False

    def process_chunk_to_game_stats(self, chunk_df):
        """Process a chunk of play-by-play data into game-level player stats"""
        import pandas as pd

        # Filter for plays with actual player involvement
        if 'player_id' not in chunk_df.columns:
            return pd.DataFrame()

        # Group by game and player
        grouped = chunk_df.groupby(['game_id', 'player_id'])

        game_stats = []

        for (game_id, player_id), group in grouped:
            if pd.isna(player_id):
                continue

            # Get player info
            player_name = group['player_name'].iloc[0] if 'player_name' in group.columns else ''
            position = group['position'].iloc[0] if 'position' in group.columns else ''
            team = group['posteam'].iloc[0] if 'posteam' in group.columns else ''
            opponent = group['defteam'].iloc[0] if 'defteam' in group.columns else ''
            season = int(group['season'].iloc[0]) if 'season' in group.columns else 0
            week = int(group['week'].iloc[0]) if 'week' in group.columns else 0

            # Skip invalid data
            if not all([game_id, player_id, position]):
                continue

            # Calculate stats from play data
            stats = {
                'game_id': game_id,
                'player_id': player_id,
                'player_name': player_name,
                'position': position,
                'team': team,
                'opponent': opponent,
                'season': season,
                'week': week,
                'game_date': group['game_date'].iloc[0] if 'game_date' in group.columns else '',

                # Rushing
                'rush_attempts': len(group[group['rush_attempt'] == 1]) if 'rush_attempt' in group.columns else 0,
                'rush_yards': int(group[group['rush_attempt'] == 1]['yards_gained'].fillna(0).sum()) if 'rush_attempt' in group.columns else 0,
                'rush_td': int(group[group['rush_touchdown'] == 1].shape[0]) if 'rush_touchdown' in group.columns else 0,
                'fumbles_lost': int(group[group['fumble_lost'] == 1].shape[0]) if 'fumble_lost' in group.columns else 0,

                # Passing
                'pass_attempts': len(group[group['pass_attempt'] == 1]) if 'pass_attempt' in group.columns else 0,
                'completions': int(group[group['pass_attempt'] == 1]['complete_pass'].fillna(0).sum()) if 'complete_pass' in group.columns else 0,
                'pass_yards': int(group[group['pass_attempt'] == 1]['yards_gained'].fillna(0).sum()) if 'pass_attempt' in group.columns else 0,
                'pass_td': int(group[group['pass_touchdown'] == 1].shape[0]) if 'pass_touchdown' in group.columns else 0,
                'interceptions': int(group[group['interception'] == 1].shape[0]) if 'interception' in group.columns else 0,

                # Receiving
                'receptions': int(group[(group['receiver_id'] == player_id) & (group['complete_pass'] == 1)].shape[0]) if 'receiver_id' in group.columns else 0,
                'receiving_yards': int(group[group['receiver_id'] == player_id]['yards_gained'].fillna(0).sum()) if 'receiver_id' in group.columns else 0,
                'receiving_td': int(group[(group['receiver_id'] == player_id) & (group['pass_touchdown'] == 1)].shape[0]) if 'receiver_id' in group.columns else 0,
                'targets': int(group[group['receiver_id'] == player_id].shape[0]) if 'receiver_id' in group.columns else 0,

                # Defense
                'tackles': int(group['tackle'].fillna(0).sum()) if 'tackle' in group.columns else 0,
                'sacks': int(group['sack'].fillna(0).sum()) if 'sack' in group.columns else 0,
                'forced_fumbles': int(group['forced_fumble'].fillna(0).sum()) if 'forced_fumble' in group.columns else 0,
            }

            # Calculate passer rating for QBs
            if stats['position'] == 'QB' and stats['pass_attempts'] > 0:
                stats['passer_rating'] = self.calculate_passer_rating(
                    stats['completions'], stats['pass_attempts'], stats['pass_yards'],
                    stats['pass_td'], stats['interceptions']
                )
            else:
                stats['passer_rating'] = 0

            game_stats.append(stats)

        return pd.DataFrame(game_stats)

    def calculate_passer_rating(self, completions, attempts, yards, touchdowns, interceptions):
        """Calculate NFL passer rating"""
        if attempts == 0:
            return 0.0

        try:
            a = max(0, min(2.375, ((completions / attempts) * 100 - 30) / 20))
            b = max(0, min(2.375, ((yards / attempts) - 3) / 4))
            c = max(0, min(2.375, (touchdowns / attempts) * 20))
            d = max(0, min(2.375, 2.375 - ((interceptions / attempts) * 25)))

            rating = (a + b + c + d) / 6 * 100
            return round(rating, 1)
        except:
            return 0.0

    def run_complete_download(self):
        """Execute the complete download process"""
        print("🚀 STARTING COMPLETE NFL HISTORICAL DATA DOWNLOAD")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Check disk space
        if not self.check_disk_space():
            print("❌ Insufficient disk space")
            return False

        # Step 2: Download data
        if not self.download_nflfastr_complete():
            print("❌ Download failed")
            return False

        # Step 3: Extract and validate
        if not self.extract_and_validate():
            print("❌ Extraction failed")
            return False

        # Step 4: Create database
        if not self.create_database_from_csvs():
            print("❌ Database creation failed")
            return False

        print("\n🎉 COMPLETE NFL HISTORICAL DATA DOWNLOAD SUCCESSFUL!")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Next step: Run the data validator and recalculator")

        return True

if __name__ == "__main__":
    downloader = CompleteNFLDownloader()
    success = downloader.run_complete_download()

    sys.exit(0 if success else 1)
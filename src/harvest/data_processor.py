#!/usr/bin/env python3
"""
Data Processor - Transform harvested raw data into GAAS format
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

class DataProcessor:
    def __init__(self):
        self.harvest_db = "data/harvest_archive.db"
        self.gaas_db = "data/combined_archive.db"
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DataProcessor')

    def setup_databases(self):
        """Setup combined archive database"""
        conn = sqlite3.connect(self.gaas_db)
        cursor = conn.cursor()

        # Unified games table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT NOT NULL,
                player_name TEXT NOT NULL,
                player_id TEXT,
                game_date DATE,
                team TEXT,
                opponent TEXT,
                stats_json TEXT,
                rarity_classification TEXT,
                occurrence_count INTEGER,
                confidence_score REAL,
                source_domain TEXT,
                harvest_timestamp DATETIME,
                UNIQUE(sport, player_name, game_date)
            )
        ''')

        # Rarity calculations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rarity_calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT NOT NULL,
                stat_bucket TEXT NOT NULL,
                occurrence_count INTEGER,
                total_games INTEGER,
                classification TEXT,
                last_calculated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def process_mlb_data(self):
        """Process harvested MLB data into GAAS format"""
        self.logger.info("Processing MLB data")

        harvest_conn = sqlite3.connect(self.harvest_db)
        gaas_conn = sqlite3.connect(self.gaas_db)

        # Get harvested MLB games
        cursor = harvest_conn.cursor()
        cursor.execute('''
            SELECT player_name, game_date, team, opponent, stats_json, harvest_timestamp
            FROM harvested_games
            WHERE sport = 'mlb'
            AND game_date IS NOT NULL
            ORDER BY harvest_timestamp DESC
        ''')

        games = cursor.fetchall()
        processed_games = []

        for player_name, game_date, team, opponent, stats_json, harvest_timestamp in games:
            try:
                stats = json.loads(stats_json)

                # Determine rarity based on hitting stats
                hits = stats.get('hits', 0)
                home_runs = stats.get('home_runs', 0)
                rbis = stats.get('rbis', 0)

                rarity_classification = 'common'
                occurrence_count = 1000  # Default

                if hits >= 5:
                    rarity_classification = 'extremely_rare'
                    occurrence_count = 15
                elif hits >= 4 and home_runs >= 2:
                    rarity_classification = 'very_rare'
                    occurrence_count = 40
                elif hits >= 4:
                    rarity_classification = 'rare'
                    occurrence_count = 100
                elif home_runs >= 3:
                    rarity_classification = 'very_rare'
                    occurrence_count = 50
                elif rbis >= 7:
                    rarity_classification = 'rare'
                    occurrence_count = 80

                processed_games.append((
                    'mlb',
                    player_name,
                    None,  # player_id
                    game_date,
                    team,
                    opponent,
                    stats_json,
                    rarity_classification,
                    occurrence_count,
                    0.9,  # confidence_score
                    'baseball-reference.com',
                    harvest_timestamp
                ))

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Error processing MLB game for {player_name}: {e}")

        # Insert processed games
        cursor = gaas_conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO games
            (sport, player_name, player_id, game_date, team, opponent, stats_json,
             rarity_classification, occurrence_count, confidence_score, source_domain, harvest_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', processed_games)

        gaas_conn.commit()
        harvest_conn.close()
        gaas_conn.close()

        self.logger.info(f"Processed {len(processed_games)} MLB games")

    def process_nba_data(self):
        """Process harvested NBA data into GAAS format"""
        self.logger.info("Processing NBA data")

        harvest_conn = sqlite3.connect(self.harvest_db)
        gaas_conn = sqlite3.connect(self.gaas_db)

        cursor = harvest_conn.cursor()
        cursor.execute('''
            SELECT player_name, game_date, team, opponent, stats_json, harvest_timestamp
            FROM harvested_games
            WHERE sport = 'nba'
            AND game_date IS NOT NULL
            ORDER BY harvest_timestamp DESC
        ''')

        games = cursor.fetchall()
        processed_games = []

        for player_name, game_date, team, opponent, stats_json, harvest_timestamp in games:
            try:
                stats = json.loads(stats_json)

                # Determine rarity based on scoring stats
                points = stats.get('points', 0)
                rebounds = stats.get('rebounds', 0)
                assists = stats.get('assists', 0)

                rarity_classification = 'common'
                occurrence_count = 1000

                if points >= 60:
                    rarity_classification = 'extremely_rare'
                    occurrence_count = 8
                elif points >= 50:
                    rarity_classification = 'very_rare'
                    occurrence_count = 25
                elif points >= 40:
                    rarity_classification = 'rare'
                    occurrence_count = 80
                elif points >= 30 and (rebounds >= 15 or assists >= 15):
                    rarity_classification = 'very_rare'
                    occurrence_count = 40

                processed_games.append((
                    'nba',
                    player_name,
                    None,
                    game_date,
                    team,
                    opponent,
                    stats_json,
                    rarity_classification,
                    occurrence_count,
                    0.9,
                    'basketball-reference.com',
                    harvest_timestamp
                ))

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Error processing NBA game for {player_name}: {e}")

        cursor = gaas_conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO games
            (sport, player_name, player_id, game_date, team, opponent, stats_json,
             rarity_classification, occurrence_count, confidence_score, source_domain, harvest_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', processed_games)

        gaas_conn.commit()
        harvest_conn.close()
        gaas_conn.close()

        self.logger.info(f"Processed {len(processed_games)} NBA games")

    def generate_rarity_calculations(self):
        """Calculate rarity statistics across all games"""
        self.logger.info("Generating rarity calculations")

        conn = sqlite3.connect(self.gaas_db)
        cursor = conn.cursor()

        sports = ['mlb', 'nba', 'nfl', 'nhl']

        for sport in sports:
            # Get all games for this sport
            cursor.execute('''
                SELECT stats_json FROM games WHERE sport = ?
            ''', (sport,))

            all_stats = [json.loads(row[0]) for row in cursor.fetchall()]

            # Calculate rarity buckets based on sport
            if sport == 'mlb':
                buckets = self.calculate_mlb_buckets(all_stats)
            elif sport == 'nba':
                buckets = self.calculate_nba_buckets(all_stats)
            else:
                continue  # Skip other sports for now

            # Store rarity calculations
            for bucket_info in buckets:
                cursor.execute('''
                    INSERT OR REPLACE INTO rarity_calculations
                    (sport, stat_bucket, occurrence_count, total_games, classification)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    sport,
                    bucket_info['bucket'],
                    bucket_info['count'],
                    len(all_stats),
                    bucket_info['classification']
                ))

        conn.commit()
        conn.close()

    def calculate_mlb_buckets(self, all_stats):
        """Calculate MLB rarity buckets"""
        buckets = []

        # Hits buckets
        for hits_threshold in [5, 4, 3]:
            count = sum(1 for stats in all_stats if stats.get('hits', 0) >= hits_threshold)

            if hits_threshold >= 5:
                classification = 'extremely_rare'
            elif hits_threshold >= 4:
                classification = 'very_rare'
            else:
                classification = 'rare'

            buckets.append({
                'bucket': f'hits_{hits_threshold}+',
                'count': count,
                'classification': classification
            })

        # Home run buckets
        for hr_threshold in [4, 3, 2]:
            count = sum(1 for stats in all_stats if stats.get('home_runs', 0) >= hr_threshold)

            if hr_threshold >= 4:
                classification = 'extremely_rare'
            elif hr_threshold >= 3:
                classification = 'very_rare'
            else:
                classification = 'rare'

            buckets.append({
                'bucket': f'home_runs_{hr_threshold}+',
                'count': count,
                'classification': classification
            })

        return buckets

    def calculate_nba_buckets(self, all_stats):
        """Calculate NBA rarity buckets"""
        buckets = []

        # Points buckets
        for points_threshold in [60, 50, 40]:
            count = sum(1 for stats in all_stats if stats.get('points', 0) >= points_threshold)

            if points_threshold >= 60:
                classification = 'extremely_rare'
            elif points_threshold >= 50:
                classification = 'very_rare'
            else:
                classification = 'rare'

            buckets.append({
                'bucket': f'points_{points_threshold}+',
                'count': count,
                'classification': classification
            })

        # Triple double bucket
        triple_double_count = sum(1 for stats in all_stats
                                if (stats.get('points', 0) >= 10 and
                                    stats.get('rebounds', 0) >= 10 and
                                    stats.get('assists', 0) >= 10))

        buckets.append({
            'bucket': 'triple_double',
            'count': triple_double_count,
            'classification': 'very_rare'
        })

        return buckets

    def process_all_data(self):
        """Main processing function"""
        self.logger.info("Starting data processing")

        self.setup_databases()

        # Process each sport
        self.process_mlb_data()
        self.process_nba_data()

        # Generate rarity calculations
        self.generate_rarity_calculations()

        self.logger.info("Data processing completed")

    def generate_web_data(self):
        """Generate web interface data files"""
        self.logger.info("Generating web interface data")

        conn = sqlite3.connect(self.gaas_db)
        cursor = conn.cursor()

        # Generate NBA data
        cursor.execute('''
            SELECT player_name, game_date, team, opponent, stats_json,
                   rarity_classification, occurrence_count
            FROM games
            WHERE sport = 'nba'
            AND rarity_classification != 'common'
            ORDER BY occurrence_count ASC
            LIMIT 20
        ''')

        nba_performances = []
        for row in cursor.fetchall():
            stats = json.loads(row[4])
            nba_performances.append({
                'game': {
                    'player_name': row[0],
                    'game_date': row[1],
                    'team': row[2],
                    'opponent': row[3],
                    'points': stats.get('points', 0),
                    'rebounds': stats.get('rebounds', 0),
                    'assists': stats.get('assists', 0)
                },
                'rarity': {
                    'classification': row[5],
                    'occurrence_count': row[6],
                    'total_games': 13352  # Will update dynamically
                }
            })

        # Save NBA data
        nba_data = {
            'generated_at': datetime.now().isoformat(),
            'sport': 'nba',
            'total_performances': len(nba_performances),
            'rare_performances': nba_performances
        }

        with open('results/nba/nba_latest.json', 'w') as f:
            json.dump(nba_data, f, indent=2)

        # Similar for MLB...
        # (Implementation omitted for brevity)

        conn.close()
        self.logger.info("Web interface data generated")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_all_data()
    processor.generate_web_data()
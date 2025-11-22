#!/usr/bin/env python3
"""Load all NFL position data into archive database"""
import pandas as pd
import sqlite3
from pathlib import Path
from loguru import logger

def create_table_for_position(conn, position):
    """Create table for specific position"""
    conn.execute(f"DROP TABLE IF EXISTS {position.lower()}_games")

    if position == 'QB':
        conn.execute(f"""
            CREATE TABLE {position.lower()}_games (
                game_id TEXT,
                player_id TEXT,
                player_name TEXT,
                position TEXT,
                team TEXT,
                opponent TEXT,
                game_date TEXT,
                season INTEGER,
                week INTEGER,
                pass_yards INTEGER,
                pass_td INTEGER,
                interceptions INTEGER,
                completions INTEGER,
                attempts INTEGER,
                pass_yards_bucket TEXT,
                pass_td_bucket TEXT,
                interceptions_bucket TEXT,
                PRIMARY KEY (game_id, player_id)
            )
        """)
    elif position == 'RB':
        conn.execute(f"""
            CREATE TABLE {position.lower()}_games (
                game_id TEXT,
                player_id TEXT,
                player_name TEXT,
                position TEXT,
                team TEXT,
                opponent TEXT,
                game_date TEXT,
                season INTEGER,
                week INTEGER,
                rush_attempts INTEGER,
                rush_yards INTEGER,
                rush_td INTEGER,
                fumbles_lost INTEGER,
                rush_yards_bucket TEXT,
                rush_td_bucket TEXT,
                fumbles_bucket TEXT,
                PRIMARY KEY (game_id, player_id)
            )
        """)
    elif position in ['WR', 'TE']:
        conn.execute(f"""
            CREATE TABLE {position.lower()}_games (
                game_id TEXT,
                player_id TEXT,
                player_name TEXT,
                position TEXT,
                team TEXT,
                opponent TEXT,
                game_date TEXT,
                season INTEGER,
                week INTEGER,
                receptions INTEGER,
                receiving_yards INTEGER,
                receiving_td INTEGER,
                targets INTEGER,
                receptions_bucket TEXT,
                receiving_yards_bucket TEXT,
                receiving_td_bucket TEXT,
                PRIMARY KEY (game_id, player_id)
            )
        """)

    # Create indexes
    bucket_cols = []
    if position == 'QB':
        bucket_cols = ['pass_yards_bucket', 'pass_td_bucket', 'interceptions_bucket']
    elif position == 'RB':
        bucket_cols = ['rush_yards_bucket', 'rush_td_bucket', 'fumbles_bucket']
    elif position in ['WR', 'TE']:
        bucket_cols = ['receptions_bucket', 'receiving_yards_bucket', 'receiving_td_bucket']

    if bucket_cols:
        index_name = f"idx_{position.lower()}_buckets"
        conn.execute(f"CREATE INDEX {index_name} ON {position.lower()}_games({', '.join(bucket_cols)})")

    conn.execute(f"CREATE INDEX idx_{position.lower()}_date ON {position.lower()}_games(game_date)")

def main():
    logger.add("logs/load_all_positions.log")
    logger.info("Loading all NFL positions into archive database...")

    Path("data/archive").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect('data/archive/nfl_archive.db')

    positions = ['QB', 'RB', 'WR', 'TE']
    total_games = 0

    for position in positions:
        logger.info(f"Loading {position} data...")

        # Load CSV data
        csv_file = f'data/downloads/nfl/{position.lower()}_games.csv'
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(df)} {position} games from CSV")

        # Create table
        create_table_for_position(conn, position)

        # Load data into table
        df.to_sql(f'{position.lower()}_games', conn, if_exists='replace', index=False)

        position_count = conn.execute(f"SELECT COUNT(*) FROM {position.lower()}_games").fetchone()[0]
        total_games += position_count
        logger.success(f"Loaded {position_count:,} {position} games into database")

    conn.commit()
    conn.close()

    logger.success(f"Successfully loaded {total_games:,} total games into NFL archive database")

    # Show summary
    conn = sqlite3.connect('data/archive/nfl_archive.db')
    for position in positions:
        count = conn.execute(f"SELECT COUNT(*) FROM {position.lower()}_games").fetchone()[0]
        logger.info(f"{position}: {count:,} games")
    conn.close()

if __name__ == '__main__':
    main()
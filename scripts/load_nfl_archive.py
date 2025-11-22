#!/usr/bin/env python3
"""Load NFL RB data into archive database"""
import pandas as pd
import sqlite3
from pathlib import Path
from loguru import logger

def bucket_rush_yards(y):
    if y < 50: return '0-49'
    elif y < 100: return '50-99'
    elif y < 150: return '100-149'
    elif y < 200: return '150-199'
    else: return '200+'

def bucket_rush_td(t):
    if t == 0: return '0'
    elif t == 1: return '1'
    elif t == 2: return '2'
    elif t == 3: return '3'
    else: return '4+'

def bucket_fumbles(f):
    if f == 0: return '0'
    elif f == 1: return '1'
    else: return '2+'

def main():
    logger.add("logs/load_nfl.log")

    df = pd.read_csv('data/downloads/nfl/rb_games.csv')
    logger.info(f"Loaded {len(df)} RB games from CSV")

    # Apply bucketing
    df['rush_yards_bucket'] = df['rush_yards'].apply(bucket_rush_yards)
    df['rush_td_bucket'] = df['rush_td'].apply(bucket_rush_td)
    df['fumbles_bucket'] = df['fumbles_lost'].apply(bucket_fumbles)

    # Create database
    Path("data/archive").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect('data/archive/nfl_archive.db')

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rb_games (
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

    df.to_sql('rb_games', conn, if_exists='replace', index=False)

    conn.execute("CREATE INDEX idx_rb_buckets ON rb_games(rush_yards_bucket, rush_td_bucket, fumbles_bucket)")
    conn.execute("CREATE INDEX idx_rb_date ON rb_games(game_date)")
    conn.execute("CREATE INDEX idx_rb_yards ON rb_games(rush_yards)")

    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM rb_games").fetchone()[0]

    # Show some stats
    yard_stats = conn.execute("""
        SELECT rush_yards_bucket, COUNT(*) as count
        FROM rb_games
        GROUP BY rush_yards_bucket
        ORDER BY count DESC
    """).fetchall()

    logger.info("Games by yard bucket:")
    for bucket, cnt in yard_stats:
        logger.info(f"  {bucket}: {cnt:,} games")

    conn.close()
    logger.success(f"Loaded {count:,} games into archive database")

if __name__ == '__main__':
    main()
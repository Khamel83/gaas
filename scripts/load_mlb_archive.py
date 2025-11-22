#!/usr/bin/env python3
"""Load MLB sample data into archive database"""
import pandas as pd
import sqlite3
from pathlib import Path
from loguru import logger

def main():
    logger.add("logs/load_mlb.log")
    logger.info("Loading MLB sample data into archive database...")

    df = pd.read_csv('data/downloads/mlb/games.csv')
    logger.info(f"Loaded {len(df)} MLB games from CSV")

    # Create database
    Path("data/archive").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect('data/archive/mlb_archive.db')

    # Create games table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT,
            player_id TEXT,
            player_name TEXT,
            season INTEGER,
            game_date TEXT,
            week INTEGER,
            team TEXT,
            opponent TEXT,
            hits INTEGER,
            runs INTEGER,
            rbis INTEGER,
            home_runs INTEGER,
            stolen_bases INTEGER,
            batting_avg REAL,
            slugging_pct REAL,
            on_base_pct REAL,
            at_bats INTEGER,
            hits_bucket TEXT,
            runs_bucket TEXT,
            rbis_bucket TEXT,
            home_runs_bucket TEXT,
            PRIMARY KEY (game_id)
        )
    """)

    df.to_sql('games', conn, if_exists='replace', index=False)

    # Create indexes
    conn.execute("CREATE INDEX idx_mlb_buckets ON games(hits_bucket, runs_bucket, rbis_bucket, home_runs_bucket)")
    conn.execute("CREATE INDEX idx_mlb_date ON games(game_date)")
    conn.execute("CREATE INDEX idx_mlb_hits ON games(hits)")
    conn.execute("CREATE INDEX idx_mlb_home_runs ON games(home_runs)")
    conn.execute("CREATE INDEX idx_mlb_season ON games(season)")

    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]

    # Show some stats
    bucket_stats = conn.execute("""
        SELECT hits_bucket, COUNT(*) as count
        FROM games
        GROUP BY hits_bucket
        ORDER BY count DESC
    """).fetchall()

    logger.info("Games by hits bucket:")
    for bucket, cnt in bucket_stats:
        logger.info(f"  {bucket} hits: {cnt:,} games")

    # Show interesting games
    interesting = conn.execute("""
        SELECT COUNT(*) as count FROM games
        WHERE hits >= 4 OR home_runs >= 2 OR rbis >= 5
    """).fetchone()[0]

    logger.info(f"Interesting games (4+ H OR 2+ HR OR 5+ RBI): {interesting:,}")

    conn.close()
    logger.success(f"Loaded {count:,} games into MLB archive database")

if __name__ == '__main__':
    main()
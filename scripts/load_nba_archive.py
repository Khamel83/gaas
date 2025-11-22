#!/usr/bin/env python3
"""Load NBA sample data into archive database"""
import pandas as pd
import sqlite3
from pathlib import Path
from loguru import logger

def main():
    logger.add("logs/load_nba.log")
    logger.info("Loading NBA sample data into archive database...")

    df = pd.read_csv('data/downloads/nba/games.csv')
    logger.info(f"Loaded {len(df)} NBA games from CSV")

    # Create database
    Path("data/archive").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect('data/archive/nba_archive.db')

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
            points INTEGER,
            rebounds INTEGER,
            assists INTEGER,
            steals INTEGER,
            blocks INTEGER,
            minutes REAL,
            points_bucket TEXT,
            rebounds_bucket TEXT,
            assists_bucket TEXT,
            PRIMARY KEY (game_id)
        )
    """)

    df.to_sql('games', conn, if_exists='replace', index=False)

    # Create indexes
    conn.execute("CREATE INDEX idx_nba_buckets ON games(points_bucket, rebounds_bucket, assists_bucket)")
    conn.execute("CREATE INDEX idx_nba_date ON games(game_date)")
    conn.execute("CREATE INDEX idx_nba_points ON games(points)")
    conn.execute("CREATE INDEX idx_nba_season ON games(season)")

    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]

    # Show some stats
    bucket_stats = conn.execute("""
        SELECT points_bucket, COUNT(*) as count
        FROM games
        GROUP BY points_bucket
        ORDER BY count DESC
    """).fetchall()

    logger.info("Games by points bucket:")
    for bucket, cnt in bucket_stats:
        logger.info(f"  {bucket}: {cnt:,} games")

    # Show interesting games
    interesting = conn.execute("""
        SELECT COUNT(*) as count FROM games
        WHERE points >= 40 OR rebounds >= 20 OR assists >= 15
    """).fetchone()[0]

    logger.info(f"Interesting games (40+ pts OR 20+ reb OR 15+ ast): {interesting:,}")

    conn.close()
    logger.success(f"Loaded {count:,} games into NBA archive database")

if __name__ == '__main__':
    main()
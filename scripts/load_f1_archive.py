#!/usr/bin/env python3
"""Load F1 sample data into archive database"""
import pandas as pd
import sqlite3
from pathlib import Path
from loguru import logger

def main():
    logger.add("logs/load_f1.log")
    logger.info("Loading F1 sample data into archive database...")

    df = pd.read_csv('data/downloads/f1/races.csv')
    logger.info(f"Loaded {len(df)} F1 races from CSV")

    # Create database
    Path("data/archive").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect('data/archive/f1_archive.db')

    # Create races table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS races (
            race_id TEXT,
            driver_id TEXT,
            driver_name TEXT,
            season INTEGER,
            race_date TEXT,
            round INTEGER,
            circuit_name TEXT,
            position INTEGER,
            grid_position INTEGER,
            laps_completed INTEGER,
            race_time REAL,
            fastest_lap REAL,
            points INTEGER,
            overtakes INTEGER,
            status TEXT,
            gap_to_leader REAL,
            position_bucket TEXT,
            overtakes_bucket TEXT,
            fastest_lap_bucket TEXT,
            PRIMARY KEY (race_id)
        )
    """)

    df.to_sql('races', conn, if_exists='replace', index=False)

    # Create indexes
    conn.execute("CREATE INDEX idx_f1_buckets ON races(position_bucket, overtakes_bucket, fastest_lap_bucket)")
    conn.execute("CREATE INDEX idx_f1_date ON races(race_date)")
    conn.execute("CREATE INDEX idx_f1_position ON races(position)")
    conn.execute("CREATE INDEX idx_f1_points ON races(points)")
    conn.execute("CREATE INDEX idx_f1_season ON races(season)")

    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM races").fetchone()[0]

    # Show some stats
    bucket_stats = conn.execute("""
        SELECT position_bucket, COUNT(*) as count
        FROM races
        GROUP BY position_bucket
        ORDER BY count DESC
    """).fetchall()

    logger.info("Races by position bucket:")
    for bucket, cnt in bucket_stats:
        logger.info(f"  Position {bucket}: {cnt:,} races")

    # Show interesting races
    interesting = conn.execute("""
        SELECT COUNT(*) as count FROM races
        WHERE position <= 3 OR overtakes >= 10
    """).fetchone()[0]

    logger.info(f"Interesting races (P1-3 OR 10+ overtakes): {interesting:,}")

    # Top performers by wins
    wins_by_driver = conn.execute("""
        SELECT driver_name, COUNT(*) as wins
        FROM races
        WHERE position = 1
        GROUP BY driver_name
        ORDER BY wins DESC
        LIMIT 5
    """).fetchall()

    logger.info("Top 5 drivers by wins:")
    for driver, wins in wins_by_driver:
        logger.info(f"  {driver}: {wins} wins")

    conn.close()
    logger.success(f"Loaded {count:,} races into F1 archive database")

if __name__ == '__main__':
    main()
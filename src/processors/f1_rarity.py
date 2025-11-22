"""F1 rarity engine for rare statistical performance detection"""
import sqlite3
import pandas as pd
from pathlib import Path
from loguru import logger
from .rarity_engine import RarityEngine


class F1RarityEngine(RarityEngine):
    """F1-specific rarity engine"""

    def __init__(self):
        super().__init__('f1', 'f1')
        self.position = 'f1'
        self.archive_db = Path("data/archive/f1_archive.db")
        self.current_db = Path("data/current/f1_current.db")

        # Initialize F1 databases
        self._init_f1_archive()
        self._init_f1_current()

    def _init_f1_archive(self):
        """Ensure F1 archive database exists"""
        if not self.archive_db.exists():
            # Create empty F1 archive database
            self.archive_db.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.archive_db)
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
            conn.close()
            logger.info("Created empty F1 archive database")

    def _init_f1_current(self):
        """Ensure F1 current database exists"""
        if not self.current_db.exists():
            logger.warning("F1 current database not found - run F1Collector first")
            self.current_db.parent.mkdir(parents=True, exist_ok=True)

    def _find_matches(self, race):
        """Find matching races in F1 archive"""
        where_clause = f"""
            position_bucket = '{race['position_bucket']}'
            AND overtakes_bucket = '{race['overtakes_bucket']}'
            AND fastest_lap_bucket = '{race['fastest_lap_bucket']}'
        """
        query = f"""
            SELECT * FROM races
            WHERE {where_clause}
            ORDER BY race_date ASC
        """

        dfs = []
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    df = pd.read_sql(query, conn)
                    conn.close()
                    dfs.append(df)
                except Exception as e:
                    logger.warning(f"Error querying {db}: {e}")
                    pass

        return pd.concat(dfs) if dfs else None

    def _get_total_games(self):
        """Count all races in F1 dataset"""
        total = 0
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    res = conn.execute("SELECT COUNT(*) FROM races").fetchone()
                    total += res[0]
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error counting races in {db}: {e}")
                    pass
        return total

    def check_current_season(self):
        """Check for rare F1 performances in current season"""
        if not self.current_db.exists():
            logger.warning("F1 current database not found")
            return []

        logger.info("Checking current F1 season for rare performances...")
        rare_performances = []

        conn = sqlite3.connect(self.current_db)
        races = conn.execute("""
            SELECT * FROM races
            ORDER BY race_date DESC
        """).fetchall()
        conn.close()

        logger.info(f"Analyzing {len(races)} F1 race results")

        for race in races:
            # Convert to dict
            race_dict = {
                'race_id': race[0],
                'driver_id': race[1],
                'driver_name': race[2],
                'season': race[3],
                'race_date': race[4],
                'round': race[5],
                'circuit_name': race[6],
                'position': race[7],
                'grid_position': race[8],
                'laps_completed': race[9],
                'race_time': race[10],
                'fastest_lap': race[11],
                'points': race[12],
                'overtakes': race[13],
                'status': race[14],
                'gap_to_leader': race[15],
                'position_bucket': race[16],
                'overtakes_bucket': race[17],
                'fastest_lap_bucket': race[18]
            }

            # Calculate rarity
            rarity = self.compute_rarity(race_dict)

            # Only include rare performances
            if rarity['classification'] != 'common':
                rare_performances.append({
                    'driver_name': race_dict['driver_name'],
                    'circuit_name': race_dict['circuit_name'],
                    'race_date': race_dict['race_date'],
                    'round': race_dict['round'],
                    'position': race_dict['position'],
                    'grid_position': race_dict['grid_position'],
                    'laps_completed': race_dict['laps_completed'],
                    'race_time': race_dict['race_time'],
                    'fastest_lap': race_dict['fastest_lap'],
                    'points': race_dict['points'],
                    'overtakes': race_dict['overtakes'],
                    'status': race_dict['status'],
                    'gap_to_leader': race_dict['gap_to_leader'],
                    'position_bucket': race_dict['position_bucket'],
                    'overtakes_bucket': race_dict['overtakes_bucket'],
                    'fastest_lap_bucket': race_dict['fastest_lap_bucket'],
                    'occurrence_count': rarity['occurrence_count'],
                    'rarity_score': rarity['rarity_score'],
                    'classification': rarity['classification']
                })

        # Sort by rarity score (highest first)
        rare_performances.sort(key=lambda x: x['rarity_score'], reverse=True)

        logger.success(f"Found {len(rare_performances)} rare F1 performances")
        return rare_performances

    def get_archive_summary(self):
        """Get summary of F1 archive data"""
        conn = sqlite3.connect(self.archive_db)
        total_races = conn.execute("SELECT COUNT(*) FROM races").fetchone()[0]

        # Bucket distributions
        position_dist = conn.execute("""
            SELECT position_bucket, COUNT(*) as count
            FROM races
            GROUP BY position_bucket
            ORDER BY count DESC
        """).fetchall()

        overtakes_dist = conn.execute("""
            SELECT overtakes_bucket, COUNT(*) as count
            FROM races
            GROUP BY overtakes_bucket
            ORDER BY count DESC
        """).fetchall()

        conn.close()

        return {
            'total_races': total_races,
            'position_distribution': dict(position_dist),
            'overtakes_distribution': dict(overtakes_dist)
        }
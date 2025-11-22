"""Champions League rarity engine for rare statistical performance detection"""
import sqlite3
import pandas as pd
from pathlib import Path
from loguru import logger
from .rarity_engine import RarityEngine


class ChampionsLeagueRarityEngine(RarityEngine):
    """Champions League-specific rarity engine"""

    def __init__(self):
        super().__init__('champions_league', 'champions_league')
        self.position = 'champions_league'
        self.archive_db = Path("data/archive/champions_league_archive.db")
        self.current_db = Path("data/current/champions_league_current.db")

        # Initialize Champions League databases
        self._init_champions_league_archive()
        self._init_champions_league_current()

    def _init_champions_league_archive(self):
        """Ensure Champions League archive database exists"""
        if not self.archive_db.exists():
            # Create empty Champions League archive database
            self.archive_db.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.archive_db)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id TEXT,
                    player_id TEXT,
                    player_name TEXT,
                    season INTEGER,
                    match_date TEXT,
                    round TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    goals INTEGER,
                    assists INTEGER,
                    shots INTEGER,
                    shots_on_target INTEGER,
                    passes INTEGER,
                    pass_accuracy REAL,
                    minutes_played INTEGER,
                    position TEXT,
                    goals_bucket TEXT,
                    assists_bucket TEXT,
                    shots_bucket TEXT,
                    PRIMARY KEY (match_id)
                )
            """)
            conn.close()
            logger.info("Created empty Champions League archive database")

    def _init_champions_league_current(self):
        """Ensure Champions League current database exists"""
        if not self.current_db.exists():
            logger.warning("Champions League current database not found - run ChampionsLeagueCollector first")
            self.current_db.parent.mkdir(parents=True, exist_ok=True)

    def _find_matches(self, match):
        """Find matching matches in Champions League archive"""
        where_clause = f"""
            goals_bucket = '{match['goals_bucket']}'
            AND assists_bucket = '{match['assists_bucket']}'
            AND shots_bucket = '{match['shots_bucket']}'
        """
        query = f"""
            SELECT * FROM matches
            WHERE {where_clause}
            ORDER BY match_date ASC
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

        return pd.concat(dfs) if dfs else pd.DataFrame()

    def _get_total_games(self):
        """Count all matches in Champions League dataset"""
        total = 0
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    res = conn.execute("SELECT COUNT(*) FROM matches").fetchone()
                    total += res[0]
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error counting matches in {db}: {e}")
                    pass
        return total

    def check_current_season(self):
        """Check for rare Champions League performances in current season"""
        if not self.current_db.exists():
            logger.warning("Champions League current database not found")
            return []

        logger.info("Checking current Champions League season for rare performances...")
        rare_performances = []

        conn = sqlite3.connect(self.current_db)
        matches = conn.execute("""
            SELECT * FROM matches
            ORDER BY match_date DESC
        """).fetchall()
        conn.close()

        logger.info(f"Analyzing {len(matches)} Champions League match performances")

        for match in matches:
            # Convert to dict
            match_dict = {
                'match_id': match[0],
                'player_id': match[1],
                'player_name': match[2],
                'season': match[3],
                'match_date': match[4],
                'round': match[5],
                'home_team': match[6],
                'away_team': match[7],
                'goals': match[8],
                'assists': match[9],
                'shots': match[10],
                'shots_on_target': match[11],
                'passes': match[12],
                'pass_accuracy': match[13],
                'minutes_played': match[14],
                'position': match[15],
                'goals_bucket': match[16],
                'assists_bucket': match[17],
                'shots_bucket': match[18]
            }

            # Calculate rarity
            rarity = self.compute_rarity(match_dict)

            # Only include rare performances
            if rarity['classification'] != 'common':
                rare_performances.append({
                    'player_name': match_dict['player_name'],
                    'round': match_dict['round'],
                    'home_team': match_dict['home_team'],
                    'away_team': match_dict['away_team'],
                    'match_date': match_dict['match_date'],
                    'goals': match_dict['goals'],
                    'assists': match_dict['assists'],
                    'shots': match_dict['shots'],
                    'shots_on_target': match_dict['shots_on_target'],
                    'passes': match_dict['passes'],
                    'pass_accuracy': match_dict['pass_accuracy'],
                    'minutes_played': match_dict['minutes_played'],
                    'position': match_dict['position'],
                    'goals_bucket': match_dict['goals_bucket'],
                    'assists_bucket': match_dict['assists_bucket'],
                    'shots_bucket': match_dict['shots_bucket'],
                    'occurrence_count': rarity['occurrence_count'],
                    'rarity_score': rarity['rarity_score'],
                    'classification': rarity['classification']
                })

        # Sort by rarity score (highest first)
        rare_performances.sort(key=lambda x: x['rarity_score'], reverse=True)

        logger.success(f"Found {len(rare_performances)} rare Champions League performances")
        return rare_performances

    def get_archive_summary(self):
        """Get summary of Champions League archive data"""
        conn = sqlite3.connect(self.archive_db)
        total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]

        # Bucket distributions
        goals_dist = conn.execute("""
            SELECT goals_bucket, COUNT(*) as count
            FROM matches
            GROUP BY goals_bucket
            ORDER BY count DESC
        """).fetchall()

        assists_dist = conn.execute("""
            SELECT assists_bucket, COUNT(*) as count
            FROM matches
            GROUP BY assists_bucket
            ORDER BY count DESC
        """).fetchall()

        conn.close()

        return {
            'total_matches': total_matches,
            'goals_distribution': dict(goals_dist),
            'assists_distribution': dict(assists_dist)
        }
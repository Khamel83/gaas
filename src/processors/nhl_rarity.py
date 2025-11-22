"""NHL rarity engine for rare statistical performance detection"""
import sqlite3
import pandas as pd
from pathlib import Path
from loguru import logger
from .rarity_engine import RarityEngine


class NHLRarityEngine(RarityEngine):
    """NHL-specific rarity engine"""

    def __init__(self):
        super().__init__('nhl', 'nhl')
        self.position = 'nhl'
        self.archive_db = Path("data/archive/nhl_archive.db")
        self.current_db = Path("data/current/nhl_current.db")

        # Initialize NHL databases
        self._init_nhl_archive()
        self._init_nhl_current()

    def _init_nhl_archive(self):
        """Ensure NHL archive database exists"""
        if not self.archive_db.exists():
            # Create empty NHL archive database
            self.archive_db.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.archive_db)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    game_id TEXT,
                    player_id TEXT,
                    player_name TEXT,
                    season INTEGER,
                    game_date TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    goals INTEGER,
                    assists INTEGER,
                    points INTEGER,
                    shots INTEGER,
                    plus_minus INTEGER,
                    penalty_minutes INTEGER,
                    time_on_ice INTEGER,
                    position TEXT,
                    goals_bucket TEXT,
                    assists_bucket TEXT,
                    points_bucket TEXT,
                    shots_bucket TEXT,
                    PRIMARY KEY (game_id)
                )
            """)
            conn.close()
            logger.info("Created empty NHL archive database")

    def _init_nhl_current(self):
        """Ensure NHL current database exists"""
        if not self.current_db.exists():
            logger.warning("NHL current database not found - run NHLCollector first")
            self.current_db.parent.mkdir(parents=True, exist_ok=True)

    def _find_games(self, game):
        """Find matching games in NHL archive"""
        where_clause = f"""
            goals_bucket = '{game['goals_bucket']}'
            AND assists_bucket = '{game['assists_bucket']}'
            AND points_bucket = '{game['points_bucket']}'
            AND shots_bucket = '{game['shots_bucket']}'
        """
        query = f"""
            SELECT * FROM games
            WHERE {where_clause}
            ORDER BY game_date ASC
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
        """Count all games in NHL dataset"""
        total = 0
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    res = conn.execute("SELECT COUNT(*) FROM games").fetchone()
                    total += res[0]
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error counting games in {db}: {e}")
                    pass
        return total

    def check_current_season(self):
        """Check for rare NHL performances in current season"""
        if not self.current_db.exists():
            logger.warning("NHL current database not found")
            return []

        logger.info("Checking current NHL season for rare performances...")
        rare_performances = []

        conn = sqlite3.connect(self.current_db)
        games = conn.execute("""
            SELECT * FROM games
            ORDER BY game_date DESC
        """).fetchall()
        conn.close()

        logger.info(f"Analyzing {len(games)} NHL game performances")

        for game in games:
            # Convert to dict
            game_dict = {
                'game_id': game[0],
                'player_id': game[1],
                'player_name': game[2],
                'season': game[3],
                'game_date': game[4],
                'home_team': game[5],
                'away_team': game[6],
                'goals': game[7],
                'assists': game[8],
                'points': game[9],
                'shots': game[10],
                'plus_minus': game[11],
                'penalty_minutes': game[12],
                'time_on_ice': game[13],
                'position': game[14],
                'goals_bucket': game[15],
                'assists_bucket': game[16],
                'points_bucket': game[17],
                'shots_bucket': game[18]
            }

            # Calculate rarity
            rarity = self.compute_rarity(game_dict)

            # Only include rare performances
            if rarity['classification'] != 'common':
                rare_performances.append({
                    'player_name': game_dict['player_name'],
                    'home_team': game_dict['home_team'],
                    'away_team': game_dict['away_team'],
                    'game_date': game_dict['game_date'],
                    'goals': game_dict['goals'],
                    'assists': game_dict['assists'],
                    'points': game_dict['points'],
                    'shots': game_dict['shots'],
                    'plus_minus': game_dict['plus_minus'],
                    'penalty_minutes': game_dict['penalty_minutes'],
                    'time_on_ice': game_dict['time_on_ice'],
                    'position': game_dict['position'],
                    'goals_bucket': game_dict['goals_bucket'],
                    'assists_bucket': game_dict['assists_bucket'],
                    'points_bucket': game_dict['points_bucket'],
                    'shots_bucket': game_dict['shots_bucket'],
                    'occurrence_count': rarity['occurrence_count'],
                    'rarity_score': rarity['rarity_score'],
                    'classification': rarity['classification']
                })

        # Sort by rarity score (highest first)
        rare_performances.sort(key=lambda x: x['rarity_score'], reverse=True)

        logger.success(f"Found {len(rare_performances)} rare NHL performances")
        return rare_performances

    def get_archive_summary(self):
        """Get summary of NHL archive data"""
        conn = sqlite3.connect(self.archive_db)
        total_games = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]

        # Bucket distributions
        goals_dist = conn.execute("""
            SELECT goals_bucket, COUNT(*) as count
            FROM games
            GROUP BY goals_bucket
            ORDER BY count DESC
        """).fetchall()

        assists_dist = conn.execute("""
            SELECT assists_bucket, COUNT(*) as count
            FROM games
            GROUP BY assists_bucket
            ORDER BY count DESC
        """).fetchall()

        points_dist = conn.execute("""
            SELECT points_bucket, COUNT(*) as count
            FROM games
            GROUP BY points_bucket
            ORDER BY count DESC
        """).fetchall()

        conn.close()

        return {
            'total_games': total_games,
            'goals_distribution': dict(goals_dist),
            'assists_distribution': dict(assists_dist),
            'points_distribution': dict(points_dist)
        }
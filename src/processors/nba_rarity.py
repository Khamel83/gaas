"""NBA rarity engine for rare statistical performance detection"""
import sqlite3
import pandas as pd
from pathlib import Path
from loguru import logger
from .rarity_engine import RarityEngine


class NBARarityEngine(RarityEngine):
    """NBA-specific rarity engine"""

    def __init__(self):
        super().__init__('nba', 'nba')
        self.position = 'nba'
        self.archive_db = Path("data/archive/nba_archive.db")
        self.current_db = Path("data/current/nba_current.db")

        # Initialize NBA databases
        self._init_nba_archive()
        self._init_nba_current()

    def _init_nba_archive(self):
        """Ensure NBA archive database exists"""
        if not self.archive_db.exists():
            # Create empty NBA archive database
            self.archive_db.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.archive_db)
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
            conn.close()
            logger.info("Created empty NBA archive database")

    def _init_nba_current(self):
        """Ensure NBA current database exists"""
        if not self.current_db.exists():
            logger.warning("NBA current database not found - run NBACollector first")
            self.current_db.parent.mkdir(parents=True, exist_ok=True)

    def _get_archive_connection(self):
        """Get connection to NBA archive database"""
        return sqlite3.connect(self.archive_db)

    def _get_current_connection(self):
        """Get connection to NBA current season database"""
        if not self.current_db.exists():
            raise FileNotFoundError("NBA current database not found")
        return sqlite3.connect(self.current_db)

    def _find_matches(self, game):
        """Find matching games in NBA archive"""
        where_clause = f"""
            points_bucket = '{game['points_bucket']}'
            AND rebounds_bucket = '{game['rebounds_bucket']}'
            AND assists_bucket = '{game['assists_bucket']}'
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

        return pd.concat(dfs) if dfs else None

    def _get_total_games(self):
        """Count all games in NBA dataset"""
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
        """Check for rare NBA performances in current season"""
        if not self.current_db.exists():
            logger.warning("NBA current database not found")
            return []

        logger.info("Checking current NBA season for rare performances...")
        rare_performances = []

        conn = self._get_current_connection()
        games = conn.execute("""
            SELECT * FROM games
            ORDER BY game_date DESC
        """).fetchall()
        conn.close()

        logger.info(f"Analyzing {len(games)} NBA games")

        for game in games:
            # Convert to dict
            game_dict = {
                'game_id': game[0],
                'player_id': game[1],
                'player_name': game[2],
                'season': game[3],
                'game_date': game[4],
                'week': game[5],
                'team': game[6],
                'opponent': game[7],
                'points': game[8],
                'rebounds': game[9],
                'assists': game[10],
                'steals': game[11],
                'blocks': game[12],
                'minutes': game[13],
                'points_bucket': game[14],
                'rebounds_bucket': game[15],
                'assists_bucket': game[16]
            }

            # Calculate rarity
            rarity = self.compute_rarity(game_dict)

            # Only include rare performances
            if rarity['classification'] != 'common':
                rare_performances.append({
                    'player_name': game_dict['player_name'],
                    'team': game_dict['team'],
                    'opponent': game_dict['opponent'],
                    'game_date': game_dict['game_date'],
                    'week': game_dict['week'],
                    'points': game_dict['points'],
                    'rebounds': game_dict['rebounds'],
                    'assists': game_dict['assists'],
                    'steals': game_dict['steals'],
                    'blocks': game_dict['blocks'],
                    'minutes': game_dict['minutes'],
                    'points_bucket': game_dict['points_bucket'],
                    'rebounds_bucket': game_dict['rebounds_bucket'],
                    'assists_bucket': game_dict['assists_bucket'],
                    'occurrence_count': rarity['occurrence_count'],
                    'rarity_score': rarity['rarity_score'],
                    'classification': rarity['classification']
                })

        # Sort by rarity score (highest first)
        rare_performances.sort(key=lambda x: x['rarity_score'], reverse=True)

        logger.success(f"Found {len(rare_performances)} rare NBA performances")
        return rare_performances

    def get_archive_summary(self):
        """Get summary of NBA archive data"""
        conn = self._get_archive_connection()
        total_games = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]

        # Bucket distributions
        points_dist = conn.execute("""
            SELECT points_bucket, COUNT(*) as count
            FROM games
            GROUP BY points_bucket
            ORDER BY count DESC
        """).fetchall()

        rebounds_dist = conn.execute("""
            SELECT rebounds_bucket, COUNT(*) as count
            FROM games
            GROUP BY rebounds_bucket
            ORDER BY count DESC
        """).fetchall()

        assists_dist = conn.execute("""
            SELECT assists_bucket, COUNT(*) as count
            FROM games
            GROUP BY assists_bucket
            ORDER BY count DESC
        """).fetchall()

        conn.close()

        return {
            'total_games': total_games,
            'points_distribution': dict(points_dist),
            'rebounds_distribution': dict(rebounds_dist),
            'assists_distribution': dict(assists_dist)
        }
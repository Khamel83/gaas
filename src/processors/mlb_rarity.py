"""MLB rarity engine for rare statistical performance detection"""
import sqlite3
import pandas as pd
from pathlib import Path
from loguru import logger
from .rarity_engine import RarityEngine


class MLBRarityEngine(RarityEngine):
    """MLB-specific rarity engine"""

    def __init__(self):
        super().__init__('mlb', 'mlb')
        self.position = 'mlb'
        self.archive_db = Path("data/archive/mlb_archive.db")
        self.current_db = Path("data/current/mlb_current.db")

        # Initialize MLB databases
        self._init_mlb_archive()
        self._init_mlb_current()

    def _init_mlb_archive(self):
        """Ensure MLB archive database exists"""
        if not self.archive_db.exists():
            # Create empty MLB archive database
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
            conn.close()
            logger.info("Created empty MLB archive database")

    def _init_mlb_current(self):
        """Ensure MLB current database exists"""
        if not self.current_db.exists():
            logger.warning("MLB current database not found - run MLBCollector first")
            self.current_db.parent.mkdir(parents=True, exist_ok=True)

    def _find_matches(self, game):
        """Find matching games in MLB archive"""
        where_clause = f"""
            hits_bucket = '{game['hits_bucket']}'
            AND runs_bucket = '{game['runs_bucket']}'
            AND rbis_bucket = '{game['rbis_bucket']}'
            AND home_runs_bucket = '{game['home_runs_bucket']}'
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
        """Count all games in MLB dataset"""
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
        """Check for rare MLB performances in current season"""
        if not self.current_db.exists():
            logger.warning("MLB current database not found")
            return []

        logger.info("Checking current MLB season for rare performances...")
        rare_performances = []

        conn = sqlite3.connect(self.current_db)
        games = conn.execute("""
            SELECT * FROM games
            ORDER BY game_date DESC
        """).fetchall()
        conn.close()

        logger.info(f"Analyzing {len(games)} MLB games")

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
                'hits': game[8],
                'runs': game[9],
                'rbis': game[10],
                'home_runs': game[11],
                'stolen_bases': game[12],
                'batting_avg': game[13],
                'slugging_pct': game[14],
                'on_base_pct': game[15],
                'at_bats': game[16],
                'hits_bucket': game[17],
                'runs_bucket': game[18],
                'rbis_bucket': game[19],
                'home_runs_bucket': game[20]
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
                    'hits': game_dict['hits'],
                    'runs': game_dict['runs'],
                    'rbis': game_dict['rbis'],
                    'home_runs': game_dict['home_runs'],
                    'stolen_bases': game_dict['stolen_bases'],
                    'at_bats': game_dict['at_bats'],
                    'batting_avg': game_dict['batting_avg'],
                    'slugging_pct': game_dict['slugging_pct'],
                    'on_base_pct': game_dict['on_base_pct'],
                    'hits_bucket': game_dict['hits_bucket'],
                    'runs_bucket': game_dict['runs_bucket'],
                    'rbis_bucket': game_dict['rbis_bucket'],
                    'home_runs_bucket': game_dict['home_runs_bucket'],
                    'occurrence_count': rarity['occurrence_count'],
                    'rarity_score': rarity['rarity_score'],
                    'classification': rarity['classification']
                })

        # Sort by rarity score (highest first)
        rare_performances.sort(key=lambda x: x['rarity_score'], reverse=True)

        logger.success(f"Found {len(rare_performances)} rare MLB performances")
        return rare_performances

    def get_archive_summary(self):
        """Get summary of MLB archive data"""
        conn = sqlite3.connect(self.archive_db)
        total_games = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]

        # Bucket distributions
        hits_dist = conn.execute("""
            SELECT hits_bucket, COUNT(*) as count
            FROM games
            GROUP BY hits_bucket
            ORDER BY count DESC
        """).fetchall()

        hr_dist = conn.execute("""
            SELECT home_runs_bucket, COUNT(*) as count
            FROM games
            GROUP BY home_runs_bucket
            ORDER BY count DESC
        """).fetchall()

        conn.close()

        return {
            'total_games': total_games,
            'hits_distribution': dict(hits_dist),
            'home_runs_distribution': dict(hr_dist)
        }
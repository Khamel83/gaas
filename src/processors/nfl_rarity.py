"""NFL rarity engine for rare statistical performance detection"""
import sqlite3
import pandas as pd
from pathlib import Path
from loguru import logger
from .rarity_engine import RarityEngine


class NFLRarityEngine(RarityEngine):
    """NFL-specific rarity engine"""

    def __init__(self, position='rb'):
        super().__init__('nfl', position)
        self.position = position
        self.archive_db = Path("data/archive/nfl_archive.db")
        self.current_db = Path("data/current/nfl_current.db")

        # Initialize NFL databases
        self._init_nfl_archive()
        self._init_nfl_current()

    def _init_nfl_archive(self):
        """Ensure NFL archive database exists"""
        if not self.archive_db.exists():
            # Create empty NFL archive database
            self.archive_db.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.archive_db)
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS nfl_{self.position} (
                    player_id TEXT,
                    player_name TEXT,
                    season INTEGER,
                    week INTEGER,
                    game_date TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    rush_yards INTEGER,
                    rush_td INTEGER,
                    receptions INTEGER,
                    receiving_yards INTEGER,
                    receiving_td INTEGER,
                    targets INTEGER,
                    pass_yards INTEGER,
                    pass_td INTEGER,
                    interceptions INTEGER,
                    completions INTEGER,
                    attempts INTEGER,
                    pass_attempts INTEGER,
                    fantasy_points REAL,
                    position TEXT,
                    rush_yards_bucket TEXT,
                    rush_td_bucket TEXT,
                    receptions_bucket TEXT,
                    receiving_yards_bucket TEXT,
                    pass_yards_bucket TEXT,
                    pass_td_bucket TEXT
                )
            """)
            conn.close()
            logger.info(f"Created empty NFL {self.position.upper()} archive database")

    def _init_nfl_current(self):
        """Ensure NFL current database exists"""
        if not self.current_db.exists():
            logger.warning(f"NFL {self.position.upper()} current database not found - run NFLCollector first")
            self.current_db.parent.mkdir(parents=True, exist_ok=True)

    def _find_games(self, game):
        """Find matching games in NFL archive"""
        if self.position == 'rb':
            where_clause = f"""
                rush_yards_bucket = '{game['rush_yards_bucket']}'
                AND rush_td_bucket = '{game['rush_td_bucket']}'
                AND receptions_bucket = '{game['receptions_bucket']}'
            """
        elif self.position == 'qb':
            where_clause = f"""
                pass_yards_bucket = '{game['pass_yards_bucket']}'
                AND pass_td_bucket = '{game['pass_td_bucket']}'
                AND interceptions_bucket = '{game.get('interceptions_bucket', '0')}'
            """
        elif self.position == 'wr':
            where_clause = f"""
                receiving_yards_bucket = '{game['receiving_yards_bucket']}'
                receptions_bucket = '{game['receptions_bucket']}'
                AND targets_bucket = '{game.get('targets_bucket', '0-3')}'
            """
        elif self.position == 'te':
            where_clause = f"""
                receiving_yards_bucket = '{game['receiving_yards_bucket']}'
                receptions_bucket = '{game['receptions_bucket']}'
                AND targets_bucket = '{game.get('targets_bucket', '0-3')}'
            """
        else:
            where_clause = f"player_id = '{game['player_id']}'"

        query = f"""
            SELECT * FROM nfl_{self.position}
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
        """Count all games in NFL dataset"""
        total = 0
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    res = conn.execute(f"SELECT COUNT(*) FROM nfl_{self.position}").fetchone()
                    total += res[0]
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error counting games in {db}: {e}")
                    pass
        return total

    def check_current_season(self, position='rb'):
        """Check for rare NFL performances in current season"""
        self.position = position
        if not self.current_db.exists():
            logger.warning(f"NFL {position.upper()} current database not found")
            return []

        logger.info(f"Checking current NFL season for rare {position.upper()} performances...")
        rare_performances = []

        try:
            conn = sqlite3.connect(self.current_db)
            games = conn.execute(f"""
                SELECT * FROM nfl_{position}
                ORDER BY game_date DESC
            """).fetchall()
            conn.close()
        except Exception as e:
            logger.error(f"Error querying NFL current database: {e}")
            return []

        logger.info(f"Analyzing {len(games)} NFL {position.upper()} game performances")

        for game in games:
            # Convert to dict based on position
            if position == 'rb':
                game_dict = {
                    'player_id': game[0],
                    'player_name': game[1],
                    'season': game[2],
                    'week': game[3],
                    'game_date': game[4],
                    'home_team': game[5],
                    'away_team': game[6],
                    'rush_yards': game[7],
                    'rush_td': game[8],
                    'receptions': game[9],
                    'receiving_yards': game[10],
                    'receiving_td': game[11],
                    'fantasy_points': game[16],
                    'position': game[17],
                    'rush_yards_bucket': game[18],
                    'rush_td_bucket': game[19],
                    'receptions_bucket': game[20],
                    'receiving_yards_bucket': game[21]
                }
            elif position == 'qb':
                game_dict = {
                    'player_id': game[0],
                    'player_name': game[1],
                    'season': game[2],
                    'week': game[3],
                    'game_date': game[4],
                    'home_team': game[5],
                    'away_team': game[6],
                    'pass_yards': game[12],
                    'pass_td': game[13],
                    'interceptions': game[14],
                    'completions': game[15],
                    'attempts': game[16],
                    'fantasy_points': game[17],
                    'position': game[18],
                    'pass_yards_bucket': game[19],
                    'pass_td_bucket': game[20],
                    'interceptions_bucket': game[21]
                }
            elif position in ['wr', 'te']:
                game_dict = {
                    'player_id': game[0],
                    'player_name': game[1],
                    'season': game[2],
                    'week': game[3],
                    'game_date': game[4],
                    'home_team': game[5],
                    'away_team': game[6],
                    'receptions': game[9],
                    'receiving_yards': game[10],
                    'receiving_td': game[11],
                    'targets': game[16],
                    'fantasy_points': game[17],
                    'position': game[18],
                    'receptions_bucket': game[19],
                    'receiving_yards_bucket': game[20],
                    'targets_bucket': game[21]
                }
            else:
                continue

            # Calculate rarity
            rarity = self.compute_rarity(game_dict)

            # Only include rare performances
            if rarity['classification'] != 'common':
                rare_performances.append({
                    'player_name': game_dict['player_name'],
                    'position': position.upper(),
                    'home_team': game_dict['home_team'],
                    'away_team': game_dict['away_team'],
                    'game_date': game_dict['game_date'],
                    'season': game_dict['season'],
                    'week': game_dict.get('week', 0),
                    'occurrence_count': rarity['occurrence_count'],
                    'rarity_score': rarity['rarity_score'],
                    'classification': rarity['classification'],
                    **{k: v for k, v in game_dict.items() if k.endswith('_yards') or k.endswith('_td') or k in ['receptions', 'targets', 'completions', 'attempts', 'interceptions']}
                })

        # Sort by rarity score (highest first)
        rare_performances.sort(key=lambda x: x['rarity_score'], reverse=True)

        logger.success(f"Found {len(rare_performances)} rare NFL {position.upper()} performances")
        return rare_performances

    def get_archive_summary(self, position='rb'):
        """Get summary of NFL archive data"""
        conn = sqlite3.connect(self.archive_db)
        total_games = conn.execute(f"SELECT COUNT(*) FROM nfl_{position}").fetchone()[0]

        # Basic bucket distributions
        if position == 'rb':
            rush_yards_dist = conn.execute(f"""
                SELECT rush_yards_bucket, COUNT(*) as count
                FROM nfl_{position}
                GROUP BY rush_yards_bucket
                ORDER BY count DESC
            """).fetchall()

            conn.close()
            return {
                'total_games': total_games,
                'rush_yards_distribution': dict(rush_yards_dist)
            }
        else:
            conn.close()
            return {'total_games': total_games}
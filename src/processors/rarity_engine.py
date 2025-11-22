"""Core rarity computation engine"""
import sqlite3
import pandas as pd
from pathlib import Path
from loguru import logger

class RarityEngine:
    def __init__(self, sport: str, position: str):
        self.sport = sport
        self.position = position
        self.archive_db = Path(f"data/archive/{sport}_archive.db")
        self.current_db = Path(f"data/current/{sport}_current.db")

    def compute_rarity(self, game: pd.Series) -> dict:
        """Compute how rare a performance is"""
        matches = self._find_matches(game)

        if matches is None or len(matches) == 0:
            count = 0
            first = None
            last = None
        else:
            count = len(matches)
            first = matches.iloc[0].to_dict()
            last = matches.iloc[-1].to_dict()

        total = self._get_total_games()
        score = 100 * (1 - (count / total)) ** 2 if total > 0 else 100

        return {
            'occurrence_count': count,
            'first_occurrence': first,
            'last_occurrence': last,
            'rarity_score': round(score, 2),
            'classification': self._classify(count),
            'total_games': total
        }

    def _find_matches(self, game):
        """Find matching stat lines in archive + current"""
        # Build WHERE clause based on position
        if self.position == 'qb':
            where_clause = f"""
                pass_yards_bucket = '{game['pass_yards_bucket']}'
                AND pass_td_bucket = '{game['pass_td_bucket']}'
                AND interceptions_bucket = '{game['interceptions_bucket']}'
            """
        elif self.position == 'rb':
            where_clause = f"""
                rush_yards_bucket = '{game['rush_yards_bucket']}'
                AND rush_td_bucket = '{game['rush_td_bucket']}'
                AND fumbles_bucket = '{game['fumbles_bucket']}'
            """
        elif self.position in ['wr', 'te']:
            where_clause = f"""
                receptions_bucket = '{game['receptions_bucket']}'
                AND receiving_yards_bucket = '{game['receiving_yards_bucket']}'
                AND receiving_td_bucket = '{game['receiving_td_bucket']}'
            """
        else:
            # Default to just match on player_id if position unknown
            where_clause = f"player_id = '{game['player_id']}'"

        query = f"""
            SELECT * FROM {self.position}_games
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
        """Count all games in dataset"""
        total = 0
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    res = conn.execute(f"SELECT COUNT(*) FROM {self.position}_games").fetchone()
                    total += res[0]
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error counting games in {db}: {e}")
                    pass
        return total

    def _classify(self, count):
        """Classify rarity"""
        if count == 1: return 'never_before'
        elif count <= 5: return 'extremely_rare'
        elif count <= 10: return 'very_rare'
        elif count <= 25: return 'rare'
        else: return 'common'

    def is_interesting(self, game):
        """Check if game is worth analyzing"""
        if self.position == 'qb':
            return (
                game['pass_yards'] >= 300 or
                game['pass_td'] >= 4 or
                game['interceptions'] >= 3
            )
        elif self.position == 'rb':
            return (
                game['rush_yards'] >= 100 or
                game['rush_td'] >= 2 or
                game['fumbles_lost'] >= 2
            )
        elif self.position in ['wr', 'te']:
            return (
                game['receiving_yards'] >= 100 or
                game['receiving_td'] >= 2 or
                game['receptions'] >= 10
            )
        else:
            return True  # Default to interesting for unknown positions

    def get_recent_performances(self, days=7):
        """Get recent interesting performances"""
        dfs = []
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)

                    # Build query based on position
                    if self.position == 'qb':
                        where_clause = "pass_yards >= 300 OR pass_td >= 4 OR interceptions >= 3"
                    elif self.position == 'rb':
                        where_clause = "rush_yards >= 100 OR rush_td >= 2 OR fumbles_lost >= 2"
                    elif self.position in ['wr', 'te']:
                        where_clause = "receiving_yards >= 100 OR receiving_td >= 2 OR receptions >= 10"
                    else:
                        where_clause = "1=1"  # All games for unknown positions

                    query = f"""
                        SELECT * FROM {self.position}_games
                        WHERE {where_clause}
                        ORDER BY game_date DESC
                        LIMIT 50
                    """
                    df = pd.read_sql(query, conn)
                    conn.close()
                    dfs.append(df)
                except Exception as e:
                    logger.warning(f"Error getting recent games from {db}: {e}")

        if dfs:
            recent = pd.concat(dfs)
            # Convert game_date to datetime for proper sorting
            recent['game_date'] = pd.to_datetime(recent['game_date'])
            recent = recent.sort_values('game_date', ascending=False)
            return recent.head(20)  # Return top 20 recent interesting games
        return pd.DataFrame()
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
        query = f"""
            SELECT * FROM {self.position}_games
            WHERE rush_yards_bucket = '{game['rush_yards_bucket']}'
            AND rush_td_bucket = '{game['rush_td_bucket']}'
            AND fumbles_bucket = '{game['fumbles_bucket']}'
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
        return (
            game['rush_yards'] >= 100 or
            game['rush_td'] >= 2 or
            game['fumbles_lost'] >= 2
        )

    def get_recent_performances(self, days=7):
        """Get recent interesting performances"""
        dfs = []
        for db in [self.archive_db, self.current_db]:
            if db.exists():
                try:
                    conn = sqlite3.connect(db)
                    # For demo, get recent games by simple ordering
                    query = f"""
                        SELECT * FROM {self.position}_games
                        WHERE rush_yards >= 100 OR rush_td >= 2 OR fumbles_lost >= 2
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
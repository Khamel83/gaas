"""MLB data collector for current season"""
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


class MLBCollector:
    def __init__(self):
        self.current_season = self._get_season()
        self.current_db = Path("data/current/mlb_current.db")
        self._init_db()

    def _get_season(self):
        """Get current MLB season year"""
        now = datetime.now()
        return now.year if now.month >= 4 else now.year - 1

    def _init_db(self):
        """Initialize MLB current season database"""
        self.current_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.current_db)
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

    def _apply_buckets(self, df):
        """Apply bucketing to MLB stats"""
        def hits_bucket(h):
            if h <= 0: return '0'
            elif h == 1: return '1'
            elif h == 2: return '2'
            elif h == 3: return '3'
            else: return '4+'

        def runs_bucket(r):
            if r <= 0: return '0'
            elif r == 1: return '1'
            elif r == 2: return '2'
            else: return '3+'

        def rbis_bucket(rbi):
            if rbi <= 0: return '0'
            elif rbi == 1: return '1'
            elif rbi == 2: return '2'
            elif rbi == 3: return '3'
            else: return '4+'

        def home_runs_bucket(hr):
            if hr == 0: return '0'
            elif hr == 1: return '1'
            else: return '2+'

        df['hits_bucket'] = df['hits'].apply(hits_bucket)
        df['runs_bucket'] = df['runs'].apply(runs_bucket)
        df['rbis_bucket'] = df['rbis'].apply(rbis_bucket)
        df['home_runs_bucket'] = df['home_runs'].apply(home_runs_bucket)
        return df

    def fetch_new_games(self):
        """Fetch new games from current season (using sample data for demo)"""
        logger.info(f"Checking for new MLB games ({self.current_season})")

        # Generate recent sample games for current season
        current_players = [
            "Mike Trout", "Aaron Judge", "Mookie Betts", "Freddie Freeman",
            "Shohei Ohtani", "Juan Soto", "Bryce Harper", "Paul Goldschmidt",
            "Manny Machado", "Nolan Arenado", "Trea Turner", "Jose Altuve",
            "Jose Ramirez", "Rafael Devers", "Xander Bogaerts"
        ]

        new_games = []
        season_start = datetime(self.current_season, 4, 1)

        for player in current_players:
            # Generate 5-10 recent games per player
            for i in range(np.random.randint(5, 10)):
                game_num = i + 1
                game_date = season_start + timedelta(days=game_num * 1.5)
                week = (game_num // 7) + 1

                # Generate interesting MLB stats
                at_bats = np.random.randint(3, 6)
                hits = np.random.randint(0, 5)
                runs = np.random.randint(0, 4)
                rbis = np.random.randint(0, 5)
                home_runs = np.random.randint(0, 3)
                stolen_bases = np.random.randint(0, 2)

                # Make some games truly interesting
                if np.random.random() < 0.25:  # 25% chance of interesting game
                    hits = np.random.randint(3, 6)
                    runs = np.random.randint(2, 5)
                    rbis = np.random.randint(3, 7)
                    home_runs = np.random.randint(1, 3)

                # Calculate rate stats
                batting_avg = hits / at_bats if at_bats > 0 else 0
                slugging_pct = (hits + 2*home_runs) / at_bats if at_bats > 0 else 0
                on_base_pct = (hits + np.random.randint(0, 2)) / (at_bats + np.random.randint(0, 3)) if at_bats > 0 else 0

                teams = ["NYY", "BOS", "TOR", "BAL", "TB", "LAD", "SF", "NYM", "ATL", "PHI"]
                team = np.random.choice(teams)
                opponent = np.random.choice([t for t in teams if t != team])

                game_data = {
                    'game_id': f"{self.current_season}_{week}_{player.replace(' ', '_')}_{game_num}",
                    'player_id': player.replace(' ', '_').lower(),
                    'player_name': player,
                    'season': self.current_season,
                    'game_date': game_date.strftime('%Y-%m-%d'),
                    'week': week,
                    'team': team,
                    'opponent': f"@{opponent}",
                    'hits': hits,
                    'runs': runs,
                    'rbis': rbis,
                    'home_runs': home_runs,
                    'stolen_bases': stolen_bases,
                    'batting_avg': round(batting_avg, 3),
                    'slugging_pct': round(slugging_pct, 3),
                    'on_base_pct': round(on_base_pct, 3),
                    'at_bats': at_bats
                }

                new_games.append(game_data)

        if not new_games:
            logger.info("No new games generated")
            return pd.DataFrame()

        games_df = pd.DataFrame(new_games)

        # Apply buckets
        games_df = self._apply_buckets(games_df)

        # Save to database
        conn = sqlite3.connect(self.current_db)
        games_df.to_sql('games', conn, if_exists='replace', index=False)
        conn.close()

        logger.success(f"Generated {len(games_df)} new games")
        return games_df

    def is_game_window(self):
        """Check if it's game time (MLB games typically run daily Apr-Oct)"""
        now = datetime.now()
        month = now.month
        return 4 <= month <= 10
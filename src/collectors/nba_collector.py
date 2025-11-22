"""NBA data collector for current season"""
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger

class NBACollector:
    def __init__(self):
        self.current_season = self._get_season()
        self.current_db = Path("data/current/nba_current.db")
        self._init_db()

    def _get_season(self):
        now = datetime.now()
        return now.year if now.month >= 10 else now.year - 1

    def _init_db(self):
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

    def _apply_buckets(self, df):
        def points_bucket(p):
            if p < 10: return '0-9'
            elif p < 20: return '10-19'
            elif p < 30: return '20-29'
            elif p < 40: return '30-39'
            elif p < 50: return '40-49'
            else: return '50+'

        def rebounds_bucket(r):
            if r < 5: return '0-4'
            elif r < 10: return '5-9'
            elif r < 15: return '10-14'
            elif r < 20: return '15-19'
            else: return '20+'

        def assists_bucket(a):
            if a < 5: return '0-4'
            elif a < 10: return '5-9'
            elif a < 15: return '10-14'
            else: return '15+'

        df['points_bucket'] = df['points'].apply(points_bucket)
        df['rebounds_bucket'] = df['rebounds'].apply(rebounds_bucket)
        df['assists_bucket'] = df['assists'].apply(assists_bucket)
        return df

    def fetch_new_games(self):
        """Fetch new games from current season (using sample data for demo)"""
        logger.info(f"Checking for new NBA games ({self.current_season})")

        # For demo, generate some sample "current season" games
        # In production, this would fetch real NBA data

        # Generate recent sample games for current season
        current_players = [
            "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo",
            "Luka Dončić", "Nikola Jokić", "Joel Embiid", "Jayson Tatum",
            "Damian Lillard", "Anthony Davis", "Kyrie Irving"
        ]

        new_games = []
        season_start = datetime(self.current_season-1, 10, 1)

        for player in current_players:
            # Generate 5-10 recent games per player
            for i in range(np.random.randint(5, 10)):
                game_num = i + 1
                game_date = season_start + timedelta(days=game_num * 2)
                week = (game_num // 4) + 1

                # Generate interesting stats
                points = np.random.randint(15, 50)
                rebounds = np.random.randint(3, 15)
                assists = np.random.randint(2, 12)
                minutes = np.random.uniform(25, 40)

                # Make some games truly interesting
                if np.random.random() < 0.3:  # 30% chance of interesting game
                    points = np.random.randint(30, 60)
                    rebounds = np.random.randint(8, 20)
                    assists = np.random.randint(8, 18)

                teams = ["LAL", "BOS", "NYK", "BRK", "PHI", "TOR", "CHI", "MIL", "IND"]
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
                    'points': points,
                    'rebounds': rebounds,
                    'assists': assists,
                    'steals': np.random.randint(0, 5),
                    'blocks': np.random.randint(0, 4),
                    'minutes': minutes
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
        """Check if it's game time (NBA games typically run daily Oct-Apr)"""
        now = datetime.now()
        month = now.month
        return 10 <= month <= 4 or month >= 6  # NBA season roughly

import numpy as np
from datetime import timedelta
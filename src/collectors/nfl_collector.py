"""NFL data collector for current season"""
import nfl_data_py as nfl
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
from loguru import logger

class NFLCollector:
    def __init__(self, position='rb'):
        self.position = position
        self.current_season = self._get_season()
        self.current_db = Path("data/current/nfl_current.db")
        self._init_db()

    def _get_season(self):
        now = datetime.now()
        return now.year if now.month >= 9 else now.year - 1

    def _init_db(self):
        self.current_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.current_db)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.position}_games (
                game_id TEXT,
                player_id TEXT,
                player_name TEXT,
                position TEXT,
                team TEXT,
                opponent TEXT,
                game_date TEXT,
                season INTEGER,
                week INTEGER,
                rush_attempts INTEGER,
                rush_yards INTEGER,
                rush_td INTEGER,
                fumbles_lost INTEGER,
                rush_yards_bucket TEXT,
                rush_td_bucket TEXT,
                fumbles_bucket TEXT,
                PRIMARY KEY (game_id, player_id)
            )
        """)
        conn.close()

    def _apply_buckets(self, df):
        def yard_bucket(y):
            if y < 50: return '0-49'
            elif y < 100: return '50-99'
            elif y < 150: return '100-149'
            elif y < 200: return '150-199'
            else: return '200+'

        def td_bucket(t):
            if t == 0: return '0'
            elif t == 1: return '1'
            elif t == 2: return '2'
            elif t == 3: return '3'
            else: return '4+'

        def fum_bucket(f):
            if f == 0: return '0'
            elif f == 1: return '1'
            else: return '2+'

        df['rush_yards_bucket'] = df['rush_yards'].apply(yard_bucket)
        df['rush_td_bucket'] = df['rush_td'].apply(td_bucket)
        df['fumbles_bucket'] = df['fumbles_lost'].apply(fum_bucket)
        return df

    def fetch_new_games(self):
        """Fetch new games from current season"""
        logger.info(f"Checking for new {self.position.upper()} games ({self.current_season})")

        try:
            weekly = nfl.import_weekly_data([self.current_season], downcast=True)
            position_data = weekly[weekly['position'] == self.position.upper()].copy()

            if len(position_data) == 0:
                logger.info(f"No {self.position.upper()} data found for {self.current_season}")
                return pd.DataFrame()

            # Check existing games
            conn = sqlite3.connect(self.current_db)
            try:
                existing = pd.read_sql(f"SELECT game_id, player_id FROM {self.position}_games", conn)
            except:
                existing = pd.DataFrame(columns=['game_id', 'player_id'])
            conn.close()

            # Create game_id from available data
            position_data['game_id'] = position_data['season'].astype(str) + '_' + \
                                     position_data['week'].astype(str).str.zfill(2) + '_' + \
                                     position_data['player_id'].astype(str)

            # Find new games
            if len(existing) > 0:
                existing['key'] = existing['game_id'] + '_' + existing['player_id']
                position_data['key'] = position_data['game_id'] + '_' + position_data['player_id']
                new_data = position_data[~position_data['key'].isin(existing['key'])]
            else:
                new_data = position_data

            if len(new_data) == 0:
                logger.info("No new games found")
                return pd.DataFrame()

            # Transform data
            games = pd.DataFrame({
                'game_id': new_data['game_id'],
                'player_id': new_data['player_id'],
                'player_name': new_data['player_display_name'],
                'position': new_data['position'],
                'team': new_data['recent_team'],
                'opponent': new_data['opponent_team'].fillna('UNKNOWN'),
                'season': new_data['season'],
                'week': new_data['week'],
                'rush_attempts': new_data['carries'].fillna(0),
                'rush_yards': new_data['rushing_yards'].fillna(0),
                'rush_td': new_data['rushing_tds'].fillna(0),
                'fumbles_lost': new_data['rushing_fumbles_lost'].fillna(0)
            })

            # Add synthetic game date
            games['game_date'] = games.apply(
                lambda row: pd.to_datetime(f"{row['season']}-09-01") + pd.to_timedelta(row['week'] * 7, unit='D'),
                axis=1
            )
            games['game_date'] = games['game_date'].dt.strftime('%Y-%m-%d')

            # Convert to integers
            for col in ['rush_attempts', 'rush_yards', 'rush_td', 'fumbles_lost']:
                games[col] = games[col].astype(int)

            # Apply buckets
            games = self._apply_buckets(games)

            # Save to database
            conn = sqlite3.connect(self.current_db)
            games.to_sql(self.position + '_games', conn, if_exists='append', index=False)
            conn.close()

            logger.success(f"Found {len(games)} new games")
            return games

        except Exception as e:
            logger.error(f"Error fetching games: {e}")
            return pd.DataFrame()

    def is_game_window(self):
        """Check if it's game time"""
        now = datetime.now()
        day = now.strftime('%A')
        hour = now.hour

        return (
            (day == 'Thursday' and 19 <= hour <= 23) or
            (day == 'Sunday' and (12 <= hour or hour <= 1)) or
            (day == 'Monday' and 19 <= hour <= 23)
        )
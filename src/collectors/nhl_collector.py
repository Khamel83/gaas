"""NHL data collector for current season"""
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


class NHLCollector:
    def __init__(self):
        self.current_season = self._get_season()
        self.current_db = Path("data/current/nhl_current.db")
        self._init_db()

    def _get_season(self):
        """Get current NHL season (e.g., 2024-25 season is 2024)"""
        now = datetime.now()
        return now.year if now.month >= 10 else now.year - 1

    def _init_db(self):
        """Initialize NHL current season database"""
        self.current_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.current_db)
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

    def _apply_buckets(self, df):
        """Apply bucketing to NHL stats"""
        def goals_bucket(g):
            if g == 0: return '0'
            elif g == 1: return '1'
            elif g == 2: return '2'
            elif g == 3: return '3'
            else: return '4+'

        def assists_bucket(a):
            if a == 0: return '0'
            elif a == 1: return '1'
            elif a == 2: return '2'
            elif a == 3: return '3'
            else: return '4+'

        def points_bucket(p):
            if p == 0: return '0'
            elif p == 1: return '1'
            elif p == 2: return '2'
            elif p == 3: return '3'
            else: return '4+'

        def shots_bucket(s):
            if s <= 1: return '0-1'
            elif s <= 3: return '2-3'
            elif s <= 5: return '4-5'
            else: return '6+'

        df['goals_bucket'] = df['goals'].apply(goals_bucket)
        df['assists_bucket'] = df['assists'].apply(assists_bucket)
        df['points_bucket'] = df['points'].apply(points_bucket)
        df['shots_bucket'] = df['shots'].apply(shots_bucket)
        return df

    def fetch_new_games(self):
        """Fetch new games from current season (using sample data for demo)"""
        logger.info(f"Checking for new NHL games ({self.current_season}-{self.current_season+1})")

        # NHL star players
        star_players = [
            "Connor McDavid", "Nathan MacKinnon", "Sidney Crosby", "Leon Draisaitl",
            "Auston Matthews", "David Pastrňák", "Jason Robertson", "Kirill Kaprizov",
            "Jack Hughes", "Brayden Point", "Nikita Kucherov", "Steven Stamkos",
            "Cale Makar", "Roman Josi", "Victor Hedman", "Adam Fox",
            "Aleksander Barkov", "Jonathan Huberdeau", "Sam Reinhart", "Mitch Marner"
        ]

        # NHL teams (current 2024-25 teams)
        nhl_teams = [
            "Bruins", "Sabres", "Canadiens", "Senators", "Maple Leafs",
            "Hurricanes", "Panthers", "Lightning", "Capitals", "Blue Jackets",
            "Devils", "Islanders", "Rangers", "Flyers", "Penguins",
            "Blackhawks", "Red Wings", "Blues", "Jets", "Predators",
            "Stars", "Avalanche", "Wild", "Oilers", "Canucks", "Flames",
            "Sharks", "Kraken", "Golden Knights", "Ducks", "Coyotes", "Kings"
        ]

        new_games = []
        season_start = datetime(self.current_season, 10, 1)  # NHL season starts in October

        # Generate regular season games (Oct-April)
        for week in range(1, 25):  # 25 weeks of regular season
            game_date = season_start + timedelta(weeks=week)

            for player in star_players:
                # Player plays for their team
                player_team = np.random.choice(nhl_teams)
                opponent = np.random.choice([t for t in nhl_teams if t != player_team])

                # Generate realistic performance
                minutes_played = np.random.randint(10, 25)  # NHL time on ice in minutes
                position = np.random.choice(["F", "D"], p=[0.7, 0.3])  # 70% forwards, 30% defensemen

                # Performance based on position and star power
                if player in ["Connor McDavid", "Nathan MacKinnon", "Leon Draisaitl"]:
                    # Elite forwards
                    goals = np.random.poisson(0.5)
                    assists = np.random.poisson(0.8)
                    shots = np.random.poisson(4)
                    plus_minus = np.random.randint(-3, 4)
                elif player in ["Cale Makar", "Roman Josi", "Victor Hedman"]:
                    # Elite defensemen
                    goals = np.random.poisson(0.15)
                    assists = np.random.poisson(0.6)
                    shots = np.random.poisson(3)
                    plus_minus = np.random.randint(-2, 3)
                elif player in ["Auston Matthews", "David Pastrňák", "Kirill Kaprizov"]:
                    # Elite goal scorers
                    goals = np.random.poisson(0.6)
                    assists = np.random.poisson(0.4)
                    shots = np.random.poisson(5)
                    plus_minus = np.random.randint(-2, 4)
                else:
                    # Other stars
                    goals = np.random.poisson(0.3)
                    assists = np.random.poisson(0.5)
                    shots = np.random.poisson(3)
                    plus_minus = np.random.randint(-3, 3)

                points = goals + assists
                penalty_minutes = np.random.exponential(2)  # Exponential distribution for PIM
                penalty_minutes = min(20, int(penalty_minutes))  # Cap at 20 minutes

                # Make some games truly special
                if np.random.random() < 0.15:  # 15% chance of spectacular performance
                    goals = min(6, goals + np.random.randint(2, 4))
                    assists = min(5, assists + np.random.randint(1, 3))
                    shots = min(12, shots + np.random.randint(3, 5))
                    plus_minus = min(6, plus_minus + np.random.randint(2, 4))

                game_data = {
                    'game_id': f"{self.current_season}_{week}_{player.replace(' ', '_')}",
                    'player_id': player.replace(' ', '_').lower(),
                    'player_name': player,
                    'season': self.current_season,
                    'game_date': game_date.strftime('%Y-%m-%d'),
                    'home_team': player_team,
                    'away_team': opponent,
                    'goals': goals,
                    'assists': assists,
                    'points': points,
                    'shots': shots,
                    'plus_minus': plus_minus,
                    'penalty_minutes': penalty_minutes,
                    'time_on_ice': minutes_played,
                    'position': position
                }

                new_games.append(game_data)

        # Generate playoff games (higher stakes)
        playoff_teams = nhl_teams[:16]  # Top 16 teams make playoffs
        for round_idx, round_name in enumerate(["First Round", "Second Round", "Conference Finals", "Stanley Cup Final"], 1):
            round_date = season_start + timedelta(weeks=28 + round_idx * 3)

            for player in star_players[:16]:  # Fewer players in playoffs
                if player_team in playoff_teams:
                    player_team = np.random.choice(playoff_teams)
                    opponent = np.random.choice([t for t in playoff_teams if t != player_team])

                    minutes_played = np.random.randint(15, 28)
                    position = np.random.choice(["F", "D"], p=[0.75, 0.25])

                    # Playoff performances are more intense
                    goals = np.random.poisson(0.4)
                    assists = np.random.poisson(0.6)
                    shots = np.random.poisson(4)
                    plus_minus = np.random.randint(-2, 4)

                    points = goals + assists
                    penalty_minutes = np.random.exponential(3)
                    penalty_minutes = min(25, int(penalty_minutes))

                    # More heroics in playoffs
                    if np.random.random() < 0.25:  # 25% chance of clutch performance
                        goals = min(5, goals + np.random.randint(1, 3))
                        assists = min(4, assists + np.random.randint(1, 2))
                        plus_minus = min(5, plus_minus + np.random.randint(1, 3))

                    game_data = {
                        'game_id': f"{self.current_season}_playoffs_{round_name}_{player.replace(' ', '_')}",
                        'player_id': player.replace(' ', '_').lower(),
                        'player_name': player,
                        'season': self.current_season,
                        'game_date': round_date.strftime('%Y-%m-%d'),
                        'home_team': player_team,
                        'away_team': opponent,
                        'goals': goals,
                        'assists': assists,
                        'points': points,
                        'shots': shots,
                        'plus_minus': plus_minus,
                        'penalty_minutes': penalty_minutes,
                        'time_on_ice': minutes_played,
                        'position': position
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

        logger.success(f"Generated {len(games_df)} new game performances")
        return games_df

    def is_game_window(self):
        """Check if it's NHL game time (October-April)"""
        now = datetime.now()
        month = now.month
        return 10 <= month <= 12 or 1 <= month <= 4 or (month == 5 and now.day <= 15)
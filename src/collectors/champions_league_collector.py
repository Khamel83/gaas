"""Champions League data collector for current season"""
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


class ChampionsLeagueCollector:
    def __init__(self):
        self.current_season = self._get_season()
        self.current_db = Path("data/current/champions_league_current.db")
        self._init_db()

    def _get_season(self):
        """Get current Champions League season (e.g., 2024/25 season is 2024)"""
        now = datetime.now()
        return now.year if now.month >= 8 else now.year - 1

    def _init_db(self):
        """Initialize Champions League current season database"""
        self.current_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.current_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id TEXT,
                player_id TEXT,
                player_name TEXT,
                season INTEGER,
                match_date TEXT,
                round TEXT,
                home_team TEXT,
                away_team TEXT,
                goals INTEGER,
                assists INTEGER,
                shots INTEGER,
                shots_on_target INTEGER,
                passes INTEGER,
                pass_accuracy REAL,
                minutes_played INTEGER,
                position TEXT,
                goals_bucket TEXT,
                assists_bucket TEXT,
                shots_bucket TEXT,
                PRIMARY KEY (match_id)
            )
        """)
        conn.close()

    def _apply_buckets(self, df):
        """Apply bucketing to Champions League stats"""
        def goals_bucket(g):
            if g == 0: return '0'
            elif g == 1: return '1'
            elif g == 2: return '2'
            else: return '3+'

        def assists_bucket(a):
            if a == 0: return '0'
            elif a == 1: return '1'
            elif a == 2: return '2'
            else: return '3+'

        def shots_bucket(s):
            if s <= 1: return '0-1'
            elif s <= 3: return '2-3'
            elif s <= 5: return '4-5'
            else: return '6+'

        df['goals_bucket'] = df['goals'].apply(goals_bucket)
        df['assists_bucket'] = df['assists'].apply(assists_bucket)
        df['shots_bucket'] = df['shots'].apply(shots_bucket)
        return df

    def fetch_new_matches(self):
        """Fetch new matches from current season (using sample data for demo)"""
        logger.info(f"Checking for new Champions League matches ({self.current_season}/{self.current_season+1})")

        # Generate sample star players
        star_players = [
            "Kylian Mbappé", "Erling Haaland", "Kevin De Bruyne", "Vinícius Júnior",
            "Jude Bellingham", "Lionel Messi", "Cristiano Ronaldo", "Robert Lewandowski",
            "Harry Kane", "Mohamed Salah", "Neymar", "Luka Modrić",
            "Pedri", "Jamal Musiala", "Phil Foden", "Bukayo Saka",
            "Victor Osimhen", "Raphinha", "Rodrigo", "Alvaro Morata"
        ]

        # Champions League teams
        top_teams = [
            "Real Madrid", "Manchester City", "Bayern Munich", "Barcelona",
            "PSG", "Liverpool", "Chelsea", "Arsenal", "Manchester United",
            "Inter Milan", "AC Milan", "Juventus", "Atletico Madrid",
            "Borussia Dortmund", "Tottenham", "Napoli", "Benfica", "Porto"
        ]

        # Match rounds in Champions League
        rounds = ["Group Stage", "Round of 16", "Quarter-Final", "Semi-Final", "Final"]

        new_matches = []
        season_start = datetime(self.current_season, 9, 1)  # CL starts in September

        # Generate group stage matches (more frequent)
        for week in range(1, 7):  # 6 group stage matchdays
            match_date = season_start + timedelta(weeks=week * 2)

            for player in star_players:
                # Player plays for their team
                player_team = np.random.choice(top_teams)

                # Generate interesting performance
                minutes_played = np.random.randint(60, 95)
                position = np.random.choice(["FW", "MF", "DF"])

                # Performance based on position and star power
                if player in ["Kylian Mbappé", "Erling Haaland", "Vinícius Júnior"]:
                    # Elite forwards
                    goals = np.random.poisson(0.8)
                    assists = np.random.poisson(0.4)
                    shots = np.random.poisson(4)
                elif player in ["Kevin De Bruyne", "Jude Bellingham", "Luka Modrić"]:
                    # Elite midfielders
                    goals = np.random.poisson(0.3)
                    assists = np.random.poisson(0.6)
                    shots = np.random.poisson(2)
                else:
                    # Other stars
                    goals = np.random.poisson(0.5)
                    assists = np.random.poisson(0.3)
                    shots = np.random.poisson(3)

                shots_on_target = max(0, int(shots * np.random.uniform(0.3, 0.7)))
                passes = np.random.randint(30, 120)
                pass_accuracy = np.random.uniform(70, 95)

                # Make some matches truly interesting
                if np.random.random() < 0.2:  # 20% chance of brilliant performance
                    goals = min(5, goals + np.random.randint(2, 4))
                    assists = min(4, assists + np.random.randint(1, 3))
                    shots = min(10, shots + np.random.randint(2, 4))

                # Generate opponent
                opponent = np.random.choice([t for t in top_teams if t != player_team])

                match_data = {
                    'match_id': f"{self.current_season}_{week}_{player.replace(' ', '_')}",
                    'player_id': player.replace(' ', '_').lower(),
                    'player_name': player,
                    'season': self.current_season,
                    'match_date': match_date.strftime('%Y-%m-%d'),
                    'round': 'Group Stage',
                    'home_team': player_team,
                    'away_team': opponent,
                    'goals': goals,
                    'assists': assists,
                    'shots': shots,
                    'shots_on_target': shots_on_target,
                    'passes': passes,
                    'pass_accuracy': round(pass_accuracy, 1),
                    'minutes_played': minutes_played,
                    'position': position
                }

                new_matches.append(match_data)

        # Generate knockout stage matches (fewer but higher stakes)
        for round_idx, round_name in enumerate(rounds[1:], 1):
            round_date = season_start + timedelta(weeks=20 + round_idx * 3)

            for player in star_players[:15]:  # Fewer players in knockout stage
                player_team = np.random.choice(top_teams)
                minutes_played = np.random.randint(70, 95)
                position = np.random.choice(["FW", "MF", "DF"])

                # Higher intensity in knockout stage
                goals = np.random.poisson(0.6)
                assists = np.random.poisson(0.4)
                shots = np.random.poisson(3)

                # More heroics in knockout stage
                if np.random.random() < 0.3:  # 30% chance of clutch performance
                    goals = min(4, goals + np.random.randint(1, 3))
                    assists = min(3, assists + np.random.randint(1, 2))

                shots_on_target = max(0, int(shots * np.random.uniform(0.4, 0.8)))
                passes = np.random.randint(40, 100)
                pass_accuracy = np.random.uniform(75, 92)

                opponent = np.random.choice([t for t in top_teams if t != player_team])

                match_data = {
                    'match_id': f"{self.current_season}_{round_name}_{player.replace(' ', '_')}",
                    'player_id': player.replace(' ', '_').lower(),
                    'player_name': player,
                    'season': self.current_season,
                    'match_date': round_date.strftime('%Y-%m-%d'),
                    'round': round_name,
                    'home_team': player_team,
                    'away_team': opponent,
                    'goals': goals,
                    'assists': assists,
                    'shots': shots,
                    'shots_on_target': shots_on_target,
                    'passes': passes,
                    'pass_accuracy': round(pass_accuracy, 1),
                    'minutes_played': minutes_played,
                    'position': position
                }

                new_matches.append(match_data)

        if not new_matches:
            logger.info("No new matches generated")
            return pd.DataFrame()

        matches_df = pd.DataFrame(new_matches)

        # Apply buckets
        matches_df = self._apply_buckets(matches_df)

        # Save to database
        conn = sqlite3.connect(self.current_db)
        matches_df.to_sql('matches', conn, if_exists='replace', index=False)
        conn.close()

        logger.success(f"Generated {len(matches_df)} new match performances")
        return matches_df

    def is_match_window(self):
        """Check if it's Champions League match time (Sept-May)"""
        now = datetime.now()
        month = now.month
        return 9 <= month <= 11 or 2 <= month <= 5
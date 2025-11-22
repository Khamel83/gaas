"""F1 data collector for current season"""
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


class F1Collector:
    def __init__(self):
        self.current_season = self._get_season()
        self.current_db = Path("data/current/f1_current.db")
        self._init_db()

    def _get_season(self):
        """Get current F1 season year"""
        now = datetime.now()
        return now.year if now.month >= 3 else now.year - 1

    def _init_db(self):
        """Initialize F1 current season database"""
        self.current_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.current_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS races (
                race_id TEXT,
                driver_id TEXT,
                driver_name TEXT,
                season INTEGER,
                race_date TEXT,
                round INTEGER,
                circuit_name TEXT,
                position INTEGER,
                grid_position INTEGER,
                laps_completed INTEGER,
                race_time REAL,
                fastest_lap REAL,
                points INTEGER,
                overtakes INTEGER,
                status TEXT,
                gap_to_leader REAL,
                position_bucket TEXT,
                overtakes_bucket TEXT,
                fastest_lap_bucket TEXT,
                PRIMARY KEY (race_id)
            )
        """)
        conn.close()

    def _apply_buckets(self, df):
        """Apply bucketing to F1 stats"""
        def position_bucket(pos):
            if pos == 1: return '1'
            elif pos == 2: return '2'
            elif pos == 3: return '3'
            elif pos <= 5: return '4-5'
            elif pos <= 10: return '6-10'
            else: return '11+'

        def overtakes_bucket(overtakes):
            if overtakes <= 2: return '0-2'
            elif overtakes <= 5: return '3-5'
            elif overtakes <= 10: return '6-10'
            else: return '11+'

        def fastest_lap_bucket(fastest_lap):
            if fastest_lap <= 0.5: return '0.0-0.5'
            elif fastest_lap <= 1.0: return '0.5-1.0'
            elif fastest_lap <= 2.0: return '1.0-2.0'
            elif fastest_lap <= 3.0: return '2.0-3.0'
            else: return '3.0+'

        df['position_bucket'] = df['position'].apply(position_bucket)
        df['overtakes_bucket'] = df['overtakes'].apply(overtakes_bucket)
        df['fastest_lap_bucket'] = df['fastest_lap'].apply(fastest_lap_bucket)
        return df

    def fetch_new_races(self):
        """Fetch new races from current season (using sample data for demo)"""
        logger.info(f"Checking for new F1 races ({self.current_season})")

        # Generate recent sample races for current season
        current_drivers = [
            "Max Verstappen", "Lewis Hamilton", "Charles Leclerc", "Sergio Perez",
            "Carlos Sainz", "Lando Norris", "George Russell", "Fernando Alonso",
            "Esteban Ocon", "Pierre Gasly", "Lance Stroll", "Oscar Piastri",
            "Yuki Tsunoda", "Valtteri Bottas", "Guanyu Zhou", "Logan Sargeant",
            "Nico Hulkenberg", "Kevin Magnussen", "Alexander Albon"
        ]

        # F1 2024 calendar circuits
        circuits = [
            "Bahrain International Circuit", "Jeddah Corniche Circuit", "Albert Park",
            "Suzuka Circuit", "Shanghai International Circuit", "Miami International Autodrome",
            "Circuit de Monaco", "Circuit Gilles Villeneuve", "Circuit de Barcelona-Catalunya",
            "Red Bull Ring", "Silverstone Circuit", "Hungaroring", "Spa-Francorchamps",
            "Circuit Zandvoort", "Monza Circuit", "Marina Bay Street Circuit",
            "Circuit of the Americas", "Rodriguez Brothers Circuit", "Interlagos",
            "Las Vegas Street Circuit", "Yas Marina Circuit"
        ]

        new_races = []
        season_start = datetime(self.current_season, 3, 1)

        for circuit_idx, circuit in enumerate(circuits[:15]):  # 15 races
            round_num = circuit_idx + 1
            race_date = season_start + timedelta(weeks=round_num * 2)

            for driver in current_drivers:
                # Generate interesting F1 performance
                grid_position = np.random.randint(1, 20)
                position = np.random.randint(1, 20)
                laps_completed = np.random.randint(50, 78)  # F1 races are 50-78 laps
                race_time = np.random.uniform(3000, 5400)  # 50-90 minutes in seconds
                fastest_lap = np.random.uniform(80, 120)  # Typical lap times
                overtakes = np.random.randint(0, 20)
                points = 0

                # Calculate points based on position
                if position == 1: points = 25
                elif position == 2: points = 18
                elif position == 3: points = 15
                elif position == 4: points = 12
                elif position == 5: points = 10
                elif position == 6: points = 8
                elif position == 7: points = 6
                elif position == 8: points = 4
                elif position == 9: points = 2
                elif position == 10: points = 1

                # Make some races truly interesting
                if np.random.random() < 0.15:  # 15% chance of interesting race
                    if np.random.random() < 0.5:
                        position = np.random.randint(1, 4)  # Podium
                        points = np.random.choice([25, 18, 15])
                    else:
                        overtakes = np.random.randint(15, 30)  # High overtakes

                # Status and gap
                status = "Finished" if laps_completed >= 70 else np.random.choice(["Retired", "Accident", "+1 Lap"])
                gap_to_leader = 0 if position == 1 else np.random.uniform(5, 120)

                race_data = {
                    'race_id': f"{self.current_season}_{round_num}_{driver.replace(' ', '_')}",
                    'driver_id': driver.replace(' ', '_').lower(),
                    'driver_name': driver,
                    'season': self.current_season,
                    'race_date': race_date.strftime('%Y-%m-%d'),
                    'round': round_num,
                    'circuit_name': circuit,
                    'position': position,
                    'grid_position': grid_position,
                    'laps_completed': laps_completed,
                    'race_time': round(race_time, 3),
                    'fastest_lap': round(fastest_lap, 3),
                    'points': points,
                    'overtakes': overtakes,
                    'status': status,
                    'gap_to_leader': round(gap_to_leader, 3)
                }

                new_races.append(race_data)

        if not new_races:
            logger.info("No new races generated")
            return pd.DataFrame()

        races_df = pd.DataFrame(new_races)

        # Apply buckets
        races_df = self._apply_buckets(races_df)

        # Save to database
        conn = sqlite3.connect(self.current_db)
        races_df.to_sql('races', conn, if_exists='replace', index=False)
        conn.close()

        logger.success(f"Generated {len(races_df)} new race results")
        return races_df

    def is_race_window(self):
        """Check if it's race time (F1 races typically run March-December)"""
        now = datetime.now()
        month = now.month
        return 3 <= month <= 12
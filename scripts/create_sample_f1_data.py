#!/usr/bin/env python3
"""Create sample F1 data for demo purposes"""
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta

def bucket_position(pos):
    if pos == 1: return '1'
    elif pos == 2: return '2'
    elif pos == 3: return '3'
    elif pos <= 5: return '4-5'
    elif pos <= 10: return '6-10'
    else: return '11+'

def bucket_overtakes(overtakes):
    if overtakes <= 2: return '0-2'
    elif overtakes <= 5: return '3-5'
    elif overtakes <= 10: return '6-10'
    else: return '11+'

def bucket_fastest_lap(fastest_lap):
    if fastest_lap <= 0.5: return '0.0-0.5'
    elif fastest_lap <= 1.0: return '0.5-1.0'
    elif fastest_lap <= 2.0: return '1.0-2.0'
    elif fastest_lap <= 3.0: return '2.0-3.0'
    else: return '3.0+'

def main():
    logger.add("logs/create_f1_sample.log")
    logger.info("Creating sample F1 data...")

    Path("data/downloads/f1").mkdir(parents=True, exist_ok=True)

    # Generate sample drivers with realistic performance patterns
    drivers = [
        {"name": "Max Verstappen", "team": "Red Bull", "skill": 0.95},
        {"name": "Lewis Hamilton", "team": "Mercedes", "skill": 0.92},
        {"name": "Charles Leclerc", "team": "Ferrari", "skill": 0.88},
        {"name": "Sergio Perez", "team": "Red Bull", "skill": 0.85},
        {"name": "Carlos Sainz", "team": "Ferrari", "skill": 0.82},
        {"name": "Lando Norris", "team": "McLaren", "skill": 0.80},
        {"name": "George Russell", "team": "Mercedes", "skill": 0.78},
        {"name": "Fernando Alonso", "team": "Aston Martin", "skill": 0.75},
        {"name": "Esteban Ocon", "team": "Alpine", "skill": 0.70},
        {"name": "Pierre Gasly", "team": "Alpine", "skill": 0.68},
        {"name": "Lance Stroll", "team": "Aston Martin", "skill": 0.65},
        {"name": "Oscar Piastri", "team": "McLaren", "skill": 0.63},
        {"name": "Yuki Tsunoda", "team": "RB", "skill": 0.60},
        {"name": "Valtteri Bottas", "team": "Sauber", "skill": 0.58},
        {"name": "Guanyu Zhou", "team": "Sauber", "skill": 0.55},
        {"name": "Logan Sargeant", "team": "Williams", "skill": 0.52},
        {"name": "Nico Hulkenberg", "team": "Haas", "skill": 0.50},
        {"name": "Kevin Magnussen", "team": "Haas", "skill": 0.48},
        {"name": "Alexander Albon", "team": "Williams", "skill": 0.45}
    ]

    seasons = [2018, 2019, 2021, 2022, 2023, 2024]  # Skip 2020 (COVID season)

    # F1 circuits with their characteristics
    circuits = [
        {"name": "Bahrain International Circuit", "laps": 57, "avg_lap_time": 95},
        {"name": "Jeddah Corniche Circuit", "laps": 50, "avg_lap_time": 88},
        {"name": "Albert Park", "laps": 78, "avg_lap_time": 85},
        {"name": "Suzuka Circuit", "laps": 53, "avg_lap_time": 92},
        {"name": "Shanghai International Circuit", "laps": 56, "avg_lap_time": 90},
        {"name": "Miami International Autodrome", "laps": 57, "avg_lap_time": 93},
        {"name": "Circuit de Monaco", "laps": 78, "avg_lap_time": 75},
        {"name": "Circuit Gilles Villeneuve", "laps": 70, "avg_lap_time": 78},
        {"name": "Circuit de Barcelona-Catalunya", "laps": 66, "avg_lap_time": 82},
        {"name": "Red Bull Ring", "laps": 71, "avg_lap_time": 68},
        {"name": "Silverstone Circuit", "laps": 52, "avg_lap_time": 87},
        {"name": "Hungaroring", "laps": 70, "avg_lap_time": 76},
        {"name": "Spa-Francorchamps", "laps": 44, "avg_lap_time": 108},
        {"name": "Circuit Zandvoort", "laps": 72, "avg_lap_time": 73},
        {"name": "Monza Circuit", "laps": 53, "avg_lap_time": 84},
        {"name": "Marina Bay Street Circuit", "laps": 62, "avg_lap_time": 95},
        {"name": "Circuit of the Americas", "laps": 56, "avg_lap_time": 95},
        {"name": "Rodriguez Brothers Circuit", "laps": 71, "avg_lap_time": 78},
        {"name": "Interlagos", "laps": 71, "avg_lap_time": 73},
        {"name": "Las Vegas Street Circuit", "laps": 50, "avg_lap_time": 90},
        {"name": "Yas Marina Circuit", "laps": 58, "avg_lap_time": 85}
    ]

    all_races = []

    for season in seasons:
        season_start = datetime(season, 3, 1)
        races_this_season = min(22, len(circuits))  # F1 has ~22 races per season max

        for race_idx in range(races_this_season):
            circuit = circuits[race_idx % len(circuits)]
            race_date = season_start + timedelta(weeks=race_idx * 2)
            round_num = race_idx + 1

            # Generate grid positions for all drivers
            grid_positions = list(range(1, len(drivers) + 1))
            np.random.shuffle(grid_positions)

            for driver_idx, driver in enumerate(drivers):
                # Driver performance based on skill + randomness
                skill_factor = driver['skill']
                grid_pos = grid_positions[driver_idx]

                # Calculate race position based on skill, grid position, and randomness
                base_position = max(1, int((1 - skill_factor) * 20 + grid_pos * 0.3 + np.random.normal(0, 3)))
                position = max(1, min(20, base_position))

                # Special events for rare performances
                if np.random.random() < 0.05:  # 5% chance of special performance
                    if np.random.random() < 0.3:
                        position = 1  # Surprise win
                    elif np.random.random() < 0.5:
                        position = np.random.randint(2, 4)  # Surprise podium
                    else:
                        # High overtakes from back of grid
                        grid_pos = np.random.randint(15, 20)
                        position = np.random.randint(5, 10)

                # Race statistics
                laps_completed = circuit['laps'] if position <= 15 else np.random.randint(30, circuit['laps'] - 10)
                race_time = circuit['avg_lap_time'] * laps_completed + np.random.uniform(-50, 200)
                fastest_lap = circuit['avg_lap_time'] + np.random.uniform(-3, 5)
                overtakes = max(0, grid_pos - position + np.random.poisson(2))

                # Points calculation
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
                else: points = 0

                # Status
                if laps_completed >= circuit['laps'] * 0.95:
                    status = "Finished"
                elif np.random.random() < 0.3:
                    status = np.random.choice(["Retired", "Accident", "+1 Lap", "+2 Laps"])
                else:
                    status = "+1 Lap"

                gap_to_leader = 0 if position == 1 else np.random.uniform(5, 120)

                race_data = {
                    'race_id': f"{season}_{round_num}_{driver['name'].replace(' ', '_')}",
                    'driver_id': driver['name'].replace(' ', '_').lower(),
                    'driver_name': driver['name'],
                    'season': season,
                    'race_date': race_date.strftime('%Y-%m-%d'),
                    'round': round_num,
                    'circuit_name': circuit['name'],
                    'position': position,
                    'grid_position': grid_pos,
                    'laps_completed': laps_completed,
                    'race_time': round(race_time, 3),
                    'fastest_lap': round(fastest_lap, 3),
                    'points': points,
                    'overtakes': overtakes,
                    'status': status,
                    'gap_to_leader': round(gap_to_leader, 3)
                }

                all_races.append(race_data)

    logger.info(f"Generated {len(all_races)} sample races for {len(drivers)} drivers across {len(seasons)} seasons")

    # Convert to DataFrame
    races_df = pd.DataFrame(all_races)

    # Apply bucketing
    races_df['position_bucket'] = races_df['position'].apply(bucket_position)
    races_df['overtakes_bucket'] = races_df['overtakes'].apply(bucket_overtakes)
    races_df['fastest_lap_bucket'] = (races_df['fastest_lap'] - races_df['fastest_lap'].mean()).abs().apply(bucket_fastest_lap)

    # Show some stats
    logger.info("Interesting race results found:")
    wins = len(races_df[races_df['position'] == 1])
    podiums = len(races_df[races_df['position'] <= 3])
    high_overtakes = len(races_df[races_df['overtakes'] >= 10])

    logger.info(f"  Total wins: {wins}")
    logger.info(f"  Total podiums: {podiums}")
    logger.info(f"  High overtakes (10+): {high_overtakes}")

    # Show top performances
    best_race = races_df.loc[races_df['points'].idxmax()]
    logger.info(f"Best performance: {best_race['driver_name']} at {best_race['circuit_name']} "
               f"- P{best_race['position']}, {best_race['points']} points, {best_race['overtakes']} overtakes")

    # Save to CSV
    races_df.to_csv('data/downloads/f1/races.csv', index=False)
    logger.success(f"Saved {len(races_df)} F1 sample races to data/downloads/f1/races.csv")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Create sample MLB data for demo purposes"""
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta

def bucket_hits(h):
    if h <= 0: return '0'
    elif h == 1: return '1'
    elif h == 2: return '2'
    elif h == 3: return '3'
    else: return '4+'

def bucket_runs(r):
    if r <= 0: return '0'
    elif r == 1: return '1'
    elif r == 2: return '2'
    else: return '3+'

def bucket_rbis(rbi):
    if rbi <= 0: return '0'
    elif rbi == 1: return '1'
    elif rbi == 2: return '2'
    elif rbi == 3: return '3'
    else: return '4+'

def bucket_home_runs(hr):
    if hr == 0: return '0'
    elif hr == 1: return '1'
    else: return '2+'

def main():
    logger.add("logs/create_mlb_sample.log")
    logger.info("Creating sample MLB data...")

    Path("data/downloads/mlb").mkdir(parents=True, exist_ok=True)

    # Generate sample players with realistic stats
    players = [
        "Mike Trout", "Aaron Judge", "Mookie Betts", "Freddie Freeman",
        "Shohei Ohtani", "Juan Soto", "Bryce Harper", "Paul Goldschmidt",
        "Manny Machado", "Nolan Arenado", "Trea Turner", "Jose Altuve",
        "Jose Ramirez", "Rafael Devers", "Xander Bogaerts", "Mookie Betts",
        "Corey Seager", "Marcus Semien", "Bo Bichette", "Vladimir Guerrero Jr.",
        "Julio Rodriguez", "Yordan Alvarez", "Yordan Alvarez", "Ronald Acuna Jr."
    ]

    seasons = [2018, 2019, 2021, 2022, 2023, 2024]  # Skip 2020 (shortened season)
    games_per_season = 162

    all_games = []

    for season in seasons:
        season_start = datetime(season, 4, 1)

        for player in players:
            # Generate games for each player
            for game_num in range(games_per_season):
                # Random but realistic stats
                at_bats = np.random.randint(2, 6)

                # Stars get better stats
                if player in ["Mike Trout", "Aaron Judge", "Mookie Betts", "Shohei Ohtani"]:
                    hit_prob = 0.320
                    hr_prob = 0.050
                else:
                    hit_prob = 0.260
                    hr_prob = 0.025

                # Generate stats
                hits = np.random.binomial(at_bats, hit_prob)
                runs = np.random.poisson(hits * 0.4)
                rbis = np.random.poisson(hits * 0.3)
                home_runs = np.random.binomial(at_bats, hr_prob)
                stolen_bases = np.random.binomial(1, 0.05)

                # Rare events (great performances)
                if np.random.random() < 0.03:  # 3% chance of great game
                    hits = min(5, hits + np.random.randint(2, 4))
                    runs = min(6, runs + np.random.randint(2, 4))
                    rbis = min(7, rbis + np.random.randint(2, 5))
                    home_runs = min(3, home_runs + np.random.randint(1, 2))

                # Game date
                game_date = season_start + timedelta(days=game_num * 1.2)
                week = (game_num // 7) + 1

                # Random team assignments for demo
                teams = ["NYY", "BOS", "TOR", "BAL", "TB", "LAD", "SF", "NYM", "ATL", "PHI",
                         "STL", "CHC", "MIL", "CIN", "PIT", "LAA", "OAK", "SEA", "TEX", "HOU"]
                team = np.random.choice(teams)
                opponent = np.random.choice([t for t in teams if t != team])

                # Calculate rate stats
                batting_avg = hits / at_bats if at_bats > 0 else 0
                slugging_pct = (hits + 2*home_runs) / at_bats if at_bats > 0 else 0
                on_base_pct = (hits + np.random.randint(0, 2)) / (at_bats + np.random.randint(0, 3)) if at_bats > 0 else 0

                game_data = {
                    'game_id': f"{season}_{game_num}_{player.replace(' ', '_')}",
                    'player_id': player.replace(' ', '_').lower(),
                    'player_name': player,
                    'season': season,
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

                all_games.append(game_data)

    logger.info(f"Generated {len(all_games)} sample games for {len(players)} players across {len(seasons)} seasons")

    # Convert to DataFrame
    games_df = pd.DataFrame(all_games)

    # Apply bucketing
    games_df['hits_bucket'] = games_df['hits'].apply(bucket_hits)
    games_df['runs_bucket'] = games_df['runs'].apply(bucket_runs)
    games_df['rbis_bucket'] = games_df['rbis'].apply(bucket_rbis)
    games_df['home_runs_bucket'] = games_df['home_runs'].apply(bucket_home_runs)

    # Show some stats
    logger.info("Interesting games found:")
    cycles = len(games_df[games_df['hits'] == 4])  # 4-hit games
    multi_hr = len(games_df[games_df['home_runs'] >= 2])  # Multi-HR games
    big_rbi = len(games_df[games_df['rbis'] >= 5])  # 5+ RBI games

    logger.info(f"  4-hit games: {cycles}")
    logger.info(f"  Multi-HR games: {multi_hr}")
    logger.info(f"  5+ RBI games: {big_rbi}")

    # Show top performances
    top_hitters = games_df.nlargest(5, 'hits')
    logger.info("Top hitting performances:")
    for _, game in top_hitters.iterrows():
        logger.info(f"  {game['player_name']}: {game['hits']}-H, {game['runs']} R, {game['rbis']} RBI")

    # Save to CSV
    games_df.to_csv('data/downloads/mlb/games.csv', index=False)
    logger.success(f"Saved {len(games_df)} MLB sample games to data/downloads/mlb/games.csv")

if __name__ == '__main__':
    main()
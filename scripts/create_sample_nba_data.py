#!/usr/bin/env python3
"""Create sample NBA data for demo purposes"""
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta

def bucket_points(p):
    if p < 10: return '0-9'
    elif p < 20: return '10-19'
    elif p < 30: return '20-29'
    elif p < 40: return '30-39'
    elif p < 50: return '40-49'
    else: return '50+'

def bucket_rebounds(r):
    if r < 5: return '0-4'
    elif r < 10: return '5-9'
    elif r < 15: return '10-14'
    elif r < 20: return '15-19'
    else: return '20+'

def bucket_assists(a):
    if a < 5: return '0-4'
    elif a < 10: return '5-9'
    elif a < 15: return '10-14'
    else: return '15+'

def main():
    logger.add("logs/create_nba_sample.log")
    logger.info("Creating sample NBA data...")

    Path("data/downloads/nba").mkdir(parents=True, exist_ok=True)

    # Generate sample players with realistic stats
    players = [
        "LeBron James", "Kevin Durant", "Stephen Curry", "Giannis Antetokounmpo",
        "Luka Dončić", "Nikola Jokić", "Joel Embiid", "Kawhi Leonard",
        "Jayson Tatum", "Damian Lillard", "Anthony Davis", "Bradley Beal",
        "Jimmy Butler", "Kyrie Irving", "Paul George", "Klay Thompson",
        "Rudy Gobert", "Devin Booker", "Chris Paul", "Russell Westbrook",
        "Al Horford", "Draymond Green", "Kyle Lowry", "CJ McCollum"
    ]

    seasons = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    games_per_season = 82

    all_games = []

    for season in seasons:
        season_start = datetime(season-1, 10, 1)

        for player in players:
            # Generate games for each player
            for game_num in range(games_per_season):
                # Random but realistic stats
                minutes = np.random.normal(30, 8)  # Average 30 minutes
                if minutes < 15:  # Skip if low minutes
                    continue

                minutes = max(15, min(48, minutes))

                # Generate correlated stats
                # Stars get better stats
                if player in ["LeBron James", "Kevin Durant", "Stephen Curry", "Giannis Antetokounmpo", "Luka Dončić"]:
                    points_base = np.random.normal(25, 8)
                    rebounds_base = np.random.normal(7, 4)
                    assists_base = np.random.normal(7, 4)
                else:
                    points_base = np.random.normal(12, 6)
                    rebounds_base = np.random.normal(4, 3)
                    assists_base = np.random.normal(3, 2)

                # Add some randomness and correlation
                points = max(0, int(np.random.normal(points_base, 8)))
                rebounds = max(0, int(np.random.normal(rebounds_base, 4)))
                assists = max(0, int(np.random.normal(assists_base, 3)))
                steals = max(0, int(np.random.normal(1, 1)))
                blocks = max(0, int(np.random.normal(0.5, 1)))

                # Rare events (great performances)
                if np.random.random() < 0.02:  # 2% chance of great game
                    points = np.random.randint(40, 60)
                    rebounds = np.random.randint(10, 20)
                    assists = np.random.randint(10, 20)

                # Game date
                game_date = season_start + timedelta(days=game_num * 2)  # Every 2 days
                week = (game_num // 4) + 1  # Group games into weeks

                # Random team assignments for demo
                teams = ["LAL", "BOS", "NYK", "BRK", "PHI", "TOR", "CHI", "MIL",
                         "IND", "DET", "CLE", "MIA", "ORL", "ATL", "WAS", "CHA"]
                team = np.random.choice(teams)
                opponent = np.random.choice([t for t in teams if t != team])

                game_data = {
                    'game_id': f"{season}_{game_num}_{player.replace(' ', '_')}",
                    'player_id': player.replace(' ', '_').lower(),
                    'player_name': player,
                    'season': season,
                    'game_date': game_date.strftime('%Y-%m-%d'),
                    'week': week,
                    'team': team,
                    'opponent': f"@{opponent}",
                    'points': points,
                    'rebounds': rebounds,
                    'assists': assists,
                    'steals': steals,
                    'blocks': blocks,
                    'minutes': minutes
                }

                all_games.append(game_data)

    logger.info(f"Generated {len(all_games)} sample games for {len(players)} players across {len(seasons)} seasons")

    # Convert to DataFrame
    games_df = pd.DataFrame(all_games)

    # Apply bucketing
    games_df['points_bucket'] = games_df['points'].apply(bucket_points)
    games_df['rebounds_bucket'] = games_df['rebounds'].apply(bucket_rebounds)
    games_df['assists_bucket'] = games_df['assists'].apply(bucket_assists)

    # Show some stats
    logger.info("Interesting games found:")
    triple_doubles = len(games_df[(games_df['points'] >= 10) & (games_df['rebounds'] >= 10) & (games_df['assists'] >= 10)])
    high_scorers = len(games_df[games_df['points'] >= 40])
    big_rebounders = len(games_df[games_df['rebounds'] >= 20])
    playmakers = len(games_df[games_df['assists'] >= 15])

    logger.info(f"  Triple doubles: {triple_doubles}")
    logger.info(f"  40+ point games: {high_scorers}")
    logger.info(f"  20+ rebound games: {big_rebounders}")
    logger.info(f"  15+ assist games: {playmakers}")

    # Show top performers
    top_scorers = games_df.nlargest(5, 'points')
    logger.info("Top scoring performances:")
    for _, game in top_scorers.iterrows():
        logger.info(f"  {game['player_name']}: {game['points']} pts, {game['rebounds']} reb, {game['assists']} ast")

    # Save to CSV
    games_df.to_csv('data/downloads/nba/games.csv', index=False)
    logger.success(f"Saved {len(games_df)} NBA sample games to data/downloads/nba/games.csv")

if __name__ == '__main__':
    main()
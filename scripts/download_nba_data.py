#!/usr/bin/env python3
"""Download NBA historical data using nba_api"""
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd
from pathlib import Path
from loguru import logger
import time
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
    logger.add("logs/download_nba.log")
    logger.info("Downloading NBA player data...")

    Path("data/downloads/nba").mkdir(parents=True, exist_ok=True)

    # Get all active players
    logger.info("Getting player list...")
    all_players = players.get_active_players()
    logger.info(f"Found {len(all_players)} active players")

    # For demo, limit to recent seasons and top players
    # In production, you'd want historical data from 2010-2024
    # For now, we'll use recent data from current season
    season = 2024  # Use 2023-24 season

    all_games = []
    processed_players = 0

    # Process first 100 players for demo (in production would be all players)
    demo_players = all_players[:100]

    for player in demo_players:
        player_id = player['id']
        player_name = f"{player['first_name']} {player['last_name']}"

        logger.info(f"Processing {player_name}...")
        processed_players += 1

        try:
            # Get player game logs for current season
            gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
            df = gamelog.get_data_frames()[0]

            if len(df) == 0:
                continue

            # Process game data
            for _, game in df.iterrows():
                game_data = {
                    'game_id': f"{season}_{game['GAME_ID']}_{player_id}",
                    'player_id': str(player_id),
                    'player_name': player_name,
                    'season': season,
                    'game_date': game['GAME_DATE'],
                    'team': game['TEAM_ABBREVIATION'],
                    'opponent': game['MATCHUP'],
                    'points': int(game['PTS']),
                    'rebounds': int(game['REB']),
                    'assists': int(game['AST']),
                    'steals': int(game['STL']),
                    'blocks': int(game['BLK']),
                    'minutes': float(game['MIN'])
                }

                # Add synthetic week for sorting
                if 'GAME_DATE' in game and game['GAME_DATE']:
                    try:
                        game_date = pd.to_datetime(game['GAME_DATE'])
                        season_start = pd.to_datetime(f"{season-1}-10-01")
                        week = ((game_date - season_start).days // 7) + 1
                        game_data['week'] = max(1, min(week, 25))  # Clamp to 1-25
                    except:
                        game_data['week'] = 1
                else:
                    game_data['week'] = 1

                all_games.append(game_data)

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            logger.warning(f"Error processing {player_name}: {e}")
            continue

        # Progress update every 10 players
        if processed_players % 10 == 0:
            logger.info(f"Processed {processed_players} players, {len(all_games)} games collected")

    logger.info(f"Collected {len(all_games)} total games from {processed_players} players")

    # Convert to DataFrame
    games_df = pd.DataFrame(all_games)

    if len(games_df) == 0:
        logger.error("No games collected!")
        return

    # Apply bucketing
    games_df['points_bucket'] = games_df['points'].apply(bucket_points)
    games_df['rebounds_bucket'] = games_df['rebounds'].apply(bucket_rebounds)
    games_df['assists_bucket'] = games_df['assists'].apply(bucket_assists)

    # Filter for meaningful games (at least 20 minutes)
    games_df = games_df[games_df['minutes'] >= 20]

    logger.info(f"After filtering: {len(games_df)} games (20+ minutes)")

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

    # Save to CSV
    games_df.to_csv('data/downloads/nba/games.csv', index=False)
    logger.success(f"Saved {len(games_df)} NBA games to data/downloads/nba/games.csv")

if __name__ == '__main__':
    main()
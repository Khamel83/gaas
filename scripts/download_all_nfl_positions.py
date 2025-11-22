#!/usr/bin/env python3
"""Download NFL data for all positions (2018-2024)"""
import nfl_data_py as nfl
import pandas as pd
from pathlib import Path
from loguru import logger

def bucket_pass_yards(y):
    if y < 100: return '0-99'
    elif y < 200: return '100-199'
    elif y < 250: return '200-249'
    elif y < 300: return '250-299'
    elif y < 350: return '300-349'
    elif y < 400: return '350-399'
    else: return '400+'

def bucket_pass_td(t):
    if t == 0: return '0'
    elif t == 1: return '1'
    elif t == 2: return '2'
    elif t == 3: return '3'
    elif t == 4: return '4'
    else: return '5+'

def bucket_interceptions(i):
    if i == 0: return '0'
    elif i == 1: return '1'
    elif i == 2: return '2'
    else: return '3+'

def bucket_receptions(r):
    if r < 3: return '0-2'
    elif r < 5: return '3-4'
    elif r < 7: return '5-6'
    elif r < 10: return '7-9'
    elif r < 12: return '10-11'
    else: return '12+'

def bucket_receiving_yards(y):
    if y < 30: return '0-29'
    elif y < 50: return '30-49'
    elif y < 75: return '50-74'
    elif y < 100: return '75-99'
    elif y < 125: return '100-124'
    elif y < 150: return '125-149'
    else: return '150+'

def bucket_receiving_td(t):
    if t == 0: return '0'
    elif t == 1: return '1'
    elif t == 2: return '2'
    else: return '3+'

def main():
    logger.add("logs/download_all_positions.log")
    logger.info("Downloading NFL data for all positions...")

    Path("data/downloads/nfl").mkdir(parents=True, exist_ok=True)

    # Download weekly data
    weekly_data = nfl.import_weekly_data(years=range(2018, 2025), downcast=True)
    logger.info(f"Downloaded {len(weekly_data):,} player-week records")

    # Process each position
    positions = {
        'QB': ['passing_yards', 'passing_tds', 'interceptions'],
        'RB': ['carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles_lost'],
        'WR': ['receptions', 'receiving_yards', 'receiving_tds', 'targets'],
        'TE': ['receptions', 'receiving_yards', 'receiving_tds', 'targets']
    }

    for position, key_stats in positions.items():
        logger.info(f"Processing {position} position...")

        # Filter for position
        pos_data = weekly_data[weekly_data['position'] == position].copy()
        if len(pos_data) == 0:
            logger.warning(f"No {position} data found")
            continue

        # Create game_id
        pos_data['game_id'] = pos_data['season'].astype(str) + '_' + \
                             pos_data['week'].astype(str).str.zfill(2) + '_' + \
                             pos_data['player_id'].astype(str)

        # Select relevant columns
        base_cols = ['game_id', 'player_id', 'player_display_name', 'position',
                    'recent_team', 'opponent_team', 'season', 'week']

        # Position-specific columns
        if position == 'QB':
            pos_cols = base_cols + ['passing_yards', 'passing_tds', 'interceptions', 'completions', 'attempts']
            final_cols = ['game_id', 'player_id', 'player_name', 'position', 'team', 'opponent',
                         'season', 'week', 'pass_yards', 'pass_td', 'interceptions', 'completions', 'attempts']
        else:  # RB, WR, TE
            if position == 'RB':
                pos_cols = base_cols + ['carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles_lost']
                final_cols = ['game_id', 'player_id', 'player_name', 'position', 'team', 'opponent',
                             'season', 'week', 'rush_attempts', 'rush_yards', 'rush_td', 'fumbles_lost']
            else:  # WR, TE
                pos_cols = base_cols + ['receptions', 'receiving_yards', 'receiving_tds', 'targets']
                final_cols = ['game_id', 'player_id', 'player_name', 'position', 'team', 'opponent',
                             'season', 'week', 'receptions', 'receiving_yards', 'receiving_td', 'targets']

        games = pos_data[pos_cols].copy()
        games.columns = final_cols

        # Fill missing values
        numeric_cols = [col for col in final_cols if col not in ['game_id', 'player_id', 'player_name', 'position', 'team', 'opponent']]
        for col in numeric_cols:
            if col in games.columns:
                games[col] = games[col].fillna(0)

        # Add synthetic game date
        games['game_date'] = games.apply(
            lambda row: pd.to_datetime(f"{row['season']}-09-01") + pd.to_timedelta(row['week'] * 7, unit='D'),
            axis=1
        )

        # Convert to integers
        for col in numeric_cols:
            if col in games.columns:
                games[col] = games[col].astype(int)

        # Remove rows with missing essential data
        games = games.dropna(subset=['player_id', 'player_name'])
        games['opponent'] = games['opponent'].fillna('UNKNOWN')

        # Apply bucketing
        if position == 'QB':
            games['pass_yards_bucket'] = games['pass_yards'].apply(bucket_pass_yards)
            games['pass_td_bucket'] = games['pass_td'].apply(bucket_pass_td)
            games['interceptions_bucket'] = games['interceptions'].apply(bucket_interceptions)
        elif position == 'RB':
            def rush_yards_bucket(y):
                if y < 50: return '0-49'
                elif y < 100: return '50-99'
                elif y < 150: return '100-149'
                elif y < 200: return '150-199'
                else: return '200+'
            def rush_td_bucket(t):
                if t == 0: return '0'
                elif t == 1: return '1'
                elif t == 2: return '2'
                elif t == 3: return '3'
                else: return '4+'
            def fumbles_bucket(f):
                if f == 0: return '0'
                elif f == 1: return '1'
                else: return '2+'
            games['rush_yards_bucket'] = games['rush_yards'].apply(rush_yards_bucket)
            games['rush_td_bucket'] = games['rush_td'].apply(rush_td_bucket)
            games['fumbles_bucket'] = games['fumbles_lost'].apply(fumbles_bucket)
        elif position in ['WR', 'TE']:
            games['receptions_bucket'] = games['receptions'].apply(bucket_receptions)
            games['receiving_yards_bucket'] = games['receiving_yards'].apply(bucket_receiving_yards)
            games['receiving_td_bucket'] = games['receiving_td'].apply(bucket_receiving_td)

        # Save position data
        output_file = f'data/downloads/nfl/{position.lower()}_games.csv'
        games.to_csv(output_file, index=False)
        logger.success(f"Saved {len(games):,} {position} games to {output_file}")

        # Show some stats
        if position == 'QB':
            great_games = len(games[games['pass_yards'] >= 300])
            td_games = len(games[games['pass_td'] >= 4])
            logger.info(f"  300+ yard games: {great_games}")
            logger.info(f"  4+ TD games: {td_games}")
        elif position == 'RB':
            great_games = len(games[games['rush_yards'] >= 100])
            td_games = len(games[games['rush_td'] >= 2])
            logger.info(f"  100+ yard games: {great_games}")
            logger.info(f"  2+ TD games: {td_games}")
        elif position in ['WR', 'TE']:
            big_games = len(games[games['receiving_yards'] >= 100])
            td_games = len(games[games['receiving_td'] >= 2])
            logger.info(f"  100+ yard games: {big_games}")
            logger.info(f"  2+ TD games: {td_games}")

    logger.success("All position data downloaded successfully!")

if __name__ == '__main__':
    main()
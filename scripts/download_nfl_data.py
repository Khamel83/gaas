#!/usr/bin/env python3
"""Download NFL historical data using weekly stats (2018-2024)"""
import nfl_data_py as nfl
import pandas as pd
from pathlib import Path
from loguru import logger

def main():
    logger.add("logs/download_nfl.log")
    logger.info("Downloading NFL weekly data...")

    Path("data/downloads/nfl").mkdir(parents=True, exist_ok=True)

    # Download weekly data for recent years (smaller dataset for demo)
    weekly_data = nfl.import_weekly_data(
        years=range(2018, 2025),  # 7 years of data
        downcast=True
    )

    logger.info(f"Downloaded {len(weekly_data):,} player-week records")

    # Filter for RB positions only
    rb_data = weekly_data[weekly_data['position'] == 'RB'].copy()

    # Create synthetic game_id (week + player + team combo)
    rb_data['game_id'] = rb_data['season'].astype(str) + '_' + \
                        rb_data['week'].astype(str).str.zfill(2) + '_' + \
                        rb_data['player_id'].astype(str)

    # Clean and prepare RB data
    rb_games = rb_data[[
        'game_id', 'player_id', 'player_display_name', 'position',
        'recent_team', 'opponent_team', 'season', 'week',
        'carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles_lost'
    ]].copy()

    # Rename columns for consistency
    rb_games.columns = [
        'game_id', 'player_id', 'player_name', 'position',
        'team', 'opponent', 'season', 'week',
        'rush_attempts', 'rush_yards', 'rush_td', 'fumbles_lost'
    ]

    # Fill missing values with 0
    rb_games[['rush_attempts', 'rush_yards', 'rush_td', 'fumbles_lost']] = \
        rb_games[['rush_attempts', 'rush_yards', 'rush_td', 'fumbles_lost']].fillna(0)

    # Convert to integers (rush_yards might be float)
    rb_games['rush_attempts'] = rb_games['rush_attempts'].astype(int)
    rb_games['rush_td'] = rb_games['rush_td'].astype(int)
    rb_games['fumbles_lost'] = rb_games['fumbles_lost'].astype(int)
    rb_games['rush_yards'] = rb_games['rush_yards'].astype(int)

    # Remove rows with missing essential data
    rb_games = rb_games.dropna(subset=['player_id', 'player_name'])
    rb_games = rb_games[rb_games['rush_attempts'] > 0]  # Only include RBs who actually carried

    # Add synthetic game date for sorting
    rb_games['game_date'] = rb_games.apply(
        lambda row: pd.to_datetime(f"{row['season']}-09-01") + pd.to_timedelta(row['week'] * 7, unit='D'),
        axis=1
    )

    logger.info(f"Processed {len(rb_games):,} RB game performances")

    # Save to CSV
    rb_games.to_csv('data/downloads/nfl/rb_games.csv', index=False)
    logger.success(f"Saved {len(rb_games):,} RB games to data/downloads/nfl/rb_games.csv")

    # Show some stats
    if len(rb_games) > 0:
        logger.info(f"Season range: {rb_games['season'].min()}-{rb_games['season'].max()}")
        logger.info(f"Players: {rb_games['player_name'].nunique():,}")
        logger.info(f"100-yard games: {len(rb_games[rb_games['rush_yards'] >= 100]):,}")
        logger.info(f"Sample games: {len(rb_games)}")

        # Show some examples
        sample = rb_games[rb_games['rush_yards'] >= 100].head(3)
        if len(sample) > 0:
            logger.info("Sample 100-yard games:")
            for _, row in sample.iterrows():
                logger.info(f"  {row['player_name']}: {row['rush_yards']} yards, {row['rush_td']} TDs")

if __name__ == '__main__':
    main()
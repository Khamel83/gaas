#!/usr/bin/env python3
"""NHL rare performance detection and analysis"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from collectors.nhl_collector import NHLCollector
from processors.nhl_rarity import NHLRarityEngine
from generators.nhl_generator import NHLGenerator


def main():
    """Main NHL analysis function"""
    logger.info("Starting NHL rare performance analysis")

    # Initialize components
    collector = NHLCollector()
    rarity_engine = NHLRarityEngine()
    generator = NHLGenerator()

    # Step 1: Check if it's a game window and fetch new data
    if collector.is_game_window():
        logger.info("NHL game window detected - fetching new games")
        new_games = collector.fetch_new_games()
        if new_games is not None and len(new_games) > 0:
            logger.success(f"Fetched {len(new_games)} new NHL game performances")
        else:
            logger.info("No new NHL games found")
    else:
        logger.info("Outside NHL game window - using existing data")

    # Step 2: Check for rare performances
    rare_performances = rarity_engine.check_current_season()

    if not rare_performances:
        logger.info("No rare NHL performances found")
        return

    # Step 3: Generate outputs
    logger.info("Generating NHL outputs...")
    json_results = generator.generate_json(rare_performances)
    generator.generate_markdown(rare_performances)

    # Step 4: Display summary
    logger.info(f"NHL analysis complete - found {len(rare_performances)} rare performances")

    # Show classification breakdown
    classifications = {}
    for perf in rare_performances:
        cls = perf['classification']
        classifications[cls] = classifications.get(cls, 0) + 1

    logger.info("Classification breakdown:")
    for cls, count in classifications.items():
        logger.info(f"  {cls}: {count}")

    # Show top 5 performances
    logger.info("Top 5 rarest NHL performances:")
    for i, perf in enumerate(rare_performances[:5], 1):
        logger.info(f"  {i}. {perf['player_name']} - {perf['home_team']} vs {perf['away_team']} - "
                   f"G:{perf['goals']} A:{perf['assists']} P:{perf['points']} "
                   f"S:{perf['shots']} +/-:{perf['plus_minus']} "
                   f"(Score: {perf['rarity_score']:.1f})")


if __name__ == "__main__":
    try:
        main()
        logger.success("NHL analysis completed successfully")
    except Exception as e:
        logger.error(f"NHL analysis failed: {e}")
        sys.exit(1)
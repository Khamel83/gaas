#!/usr/bin/env python3
"""Champions League rare performance detection and analysis"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from collectors.champions_league_collector import ChampionsLeagueCollector
from processors.champions_league_rarity import ChampionsLeagueRarityEngine
from generators.champions_league_generator import ChampionsLeagueGenerator


def main():
    """Main Champions League analysis function"""
    logger.info("Starting Champions League rare performance analysis")

    # Initialize components
    collector = ChampionsLeagueCollector()
    rarity_engine = ChampionsLeagueRarityEngine()
    generator = ChampionsLeagueGenerator()

    # Step 1: Check if it's a match window and fetch new data
    if collector.is_match_window():
        logger.info("Champions League match window detected - fetching new matches")
        new_matches = collector.fetch_new_matches()
        if new_matches is not None and len(new_matches) > 0:
            logger.success(f"Fetched {len(new_matches)} new Champions League match performances")
        else:
            logger.info("No new Champions League matches found")
    else:
        logger.info("Outside Champions League match window - using existing data")

    # Step 2: Check for rare performances
    rare_performances = rarity_engine.check_current_season()

    if not rare_performances:
        logger.info("No rare Champions League performances found")
        return

    # Step 3: Generate outputs
    logger.info("Generating Champions League outputs...")
    json_results = generator.generate_json(rare_performances)
    generator.generate_markdown(rare_performances)

    # Step 4: Display summary
    logger.info(f"Champions League analysis complete - found {len(rare_performances)} rare performances")

    # Show classification breakdown
    classifications = {}
    for perf in rare_performances:
        cls = perf['classification']
        classifications[cls] = classifications.get(cls, 0) + 1

    logger.info("Classification breakdown:")
    for cls, count in classifications.items():
        logger.info(f"  {cls}: {count}")

    # Show top 5 performances
    logger.info("Top 5 rarest Champions League performances:")
    for i, perf in enumerate(rare_performances[:5], 1):
        logger.info(f"  {i}. {perf['player_name']} - {perf['round']} - "
                   f"G:{perf['goals']} A:{perf['assists']} S:{perf['shots']} "
                   f"(Score: {perf['rarity_score']:.1f})")


if __name__ == "__main__":
    try:
        main()
        logger.success("Champions League analysis completed successfully")
    except Exception as e:
        logger.error(f"Champions League analysis failed: {e}")
        sys.exit(1)
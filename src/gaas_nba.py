#!/usr/bin/env python3
"""GAAS NBA - Detect rare NBA statistical performances"""
from pathlib import Path
from loguru import logger
import sys
import os

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from collectors.nba_collector import NBACollector
from processors.nba_rarity import NBARarityEngine
from generators.nba_generator import NBAJSONGenerator


def main():
    """Main NBA processing pipeline"""
    logger.add("logs/gaas_nba.log")
    logger.info("Starting GAAS NBA rare performance detection...")

    # Step 1: Collect current season data
    logger.info("Step 1: Collecting current NBA season data...")
    collector = NBACollector()

    # Check if it's game time
    if collector.is_game_window():
        new_games = collector.fetch_new_games()
        if len(new_games) > 0:
            logger.success(f"Collected {len(new_games)} new NBA games")
        else:
            logger.info("No new NBA games found")
    else:
        logger.info("Not in NBA game window - using existing data")

    # Step 2: Initialize rarity engine
    logger.info("Step 2: Initializing NBA rarity engine...")
    rarity_engine = NBARarityEngine()

    # Step 3: Check for rare performances
    logger.info("Step 3: Analyzing performances...")
    rare_performances = rarity_engine.check_current_season()

    # Step 4: Generate results
    logger.info("Step 4: Generating results...")
    generator = NBAJSONGenerator()
    archive_summary = rarity_engine.get_archive_summary()
    results = generator.generate_all(rare_performances, archive_summary)

    # Step 5: Show summary
    summary = results['summary']
    logger.success("GAAS NBA Analysis Complete!")
    logger.info(f"Rare performances found: {summary['total_rare_performances']}")
    logger.info(f"Average rarity score: {summary['average_rarity_score']:.2f}")

    if summary['rarest_performance']:
        logger.info(f"Rarest performance: {summary['rarest_performance']['player_name']} "
                   f"({summary['rarest_performance']['rarity_score']:.2f})")

    # Show classification breakdown
    if summary['classification_breakdown']:
        logger.info("Classification breakdown:")
        for cls, count in summary['classification_breakdown'].items():
            logger.info(f"  {cls}: {count}")

    return summary


if __name__ == '__main__':
    main()
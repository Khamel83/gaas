#!/usr/bin/env python3
"""GAAS MLB - Detect rare MLB statistical performances"""
from pathlib import Path
from loguru import logger
import sys
import os

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from collectors.mlb_collector import MLBCollector
from processors.mlb_rarity import MLBRarityEngine
from generators.mlb_generator import MLBJSONGenerator


def main():
    """Main MLB processing pipeline"""
    logger.add("logs/gaas_mlb.log")
    logger.info("Starting GAAS MLB rare performance detection...")

    # Step 1: Collect current season data
    logger.info("Step 1: Collecting current MLB season data...")
    collector = MLBCollector()

    # Check if it's game time (force for demo)
    # if collector.is_game_window():
    if True:  # Force generation for demo
        new_games = collector.fetch_new_games()
        if len(new_games) > 0:
            logger.success(f"Collected {len(new_games)} new MLB games")
        else:
            logger.info("No new MLB games found")
    else:
        logger.info("Not in MLB game window - using existing data")

    # Step 2: Initialize rarity engine
    logger.info("Step 2: Initializing MLB rarity engine...")
    rarity_engine = MLBRarityEngine()

    # Step 3: Check for rare performances
    logger.info("Step 3: Analyzing performances...")
    rare_performances = rarity_engine.check_current_season()

    # Step 4: Generate results
    logger.info("Step 4: Generating results...")
    generator = MLBJSONGenerator()
    archive_summary = rarity_engine.get_archive_summary()
    results = generator.generate_all(rare_performances, archive_summary)

    # Step 5: Show summary
    summary = results['summary']
    logger.success("GAAS MLB Analysis Complete!")
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
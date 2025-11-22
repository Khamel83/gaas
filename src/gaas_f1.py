#!/usr/bin/env python3
"""GAAS F1 - Detect rare F1 statistical performances"""
from pathlib import Path
from loguru import logger
import sys
import os

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from collectors.f1_collector import F1Collector
from processors.f1_rarity import F1RarityEngine
from generators.f1_generator import F1JSONGenerator


def main():
    """Main F1 processing pipeline"""
    logger.add("logs/gaas_f1.log")
    logger.info("Starting GAAS F1 rare performance detection...")

    # Step 1: Collect current season data
    logger.info("Step 1: Collecting current F1 season data...")
    collector = F1Collector()

    # Check if it's race time (force for demo)
    if True:  # Force generation for demo
        new_races = collector.fetch_new_races()
        if len(new_races) > 0:
            logger.success(f"Collected {len(new_races)} new F1 race results")
        else:
            logger.info("No new F1 race results found")
    else:
        logger.info("Not in F1 race window - using existing data")

    # Step 2: Initialize rarity engine
    logger.info("Step 2: Initializing F1 rarity engine...")
    rarity_engine = F1RarityEngine()

    # Step 3: Check for rare performances
    logger.info("Step 3: Analyzing performances...")
    rare_performances = rarity_engine.check_current_season()

    # Step 4: Generate results
    logger.info("Step 4: Generating results...")
    generator = F1JSONGenerator()
    archive_summary = rarity_engine.get_archive_summary()
    results = generator.generate_all(rare_performances, archive_summary)

    # Step 5: Show summary
    summary = results['summary']
    logger.success("GAAS F1 Analysis Complete!")
    logger.info(f"Rare performances found: {summary['total_rare_performances']}")
    logger.info(f"Average rarity score: {summary['average_rarity_score']:.2f}")

    if summary['rarest_performance']:
        logger.info(f"Rarest performance: {summary['rarest_performance']['driver_name']} "
                   f"({summary['rarest_performance']['rarity_score']:.2f})")

    # Show classification breakdown
    if summary['classification_breakdown']:
        logger.info("Classification breakdown:")
        for cls, count in summary['classification_breakdown'].items():
            logger.info(f"  {cls}: {count}")

    return summary


if __name__ == '__main__':
    main()
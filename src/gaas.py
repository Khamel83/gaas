"""Main GAAS orchestrator"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from collectors.nfl_collector import NFLCollector
from processors.rarity_engine import RarityEngine
from generators.json_generator import JSONGenerator
from utils.git_pusher import GitPusher

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add("logs/gaas.log", rotation="100 MB")

def run_nfl_rb_pipeline():
    """Execute NFL RB pipeline"""
    logger.info("=" * 60)
    logger.info("Running NFL RB pipeline")

    try:
        # Initialize components
        collector = NFLCollector('rb')
        engine = RarityEngine('nfl', 'rb')
        generator = JSONGenerator('nfl', 'rb')
        git_pusher = GitPusher()

        # Get recent interesting performances from archive
        logger.info("Finding recent interesting performances...")
        recent_games = engine.get_recent_performances()

        if len(recent_games) == 0:
            logger.warning("No interesting games found in archive")
            return False

        logger.info(f"Found {len(recent_games)} recent games to analyze")

        # Compute rarity for each game
        rare_perfs = []
        for idx, game in recent_games.iterrows():
            logger.info(f"Analyzing: {game['player_name']} ({game['rush_yards']} yards)")
            rarity = engine.compute_rarity(game)

            # Only include rare performances (≤25 occurrences)
            if rarity['occurrence_count'] <= 25:
                rare_perfs.append({
                    'game': game.to_dict(),
                    'rarity': rarity
                })
                logger.success(f"RARE: {game['player_name']} - {rarity['classification']} ({rarity['occurrence_count']} occurrences)")

        if not rare_perfs:
            logger.info("No rare performances found in recent games")
            return False

        logger.info(f"Found {len(rare_perfs)} rare performances")

        # Generate outputs
        logger.info("Generating output files...")
        files_generated = []

        # Latest performances
        latest_file = generator.generate_latest(rare_perfs)
        files_generated.append(str(latest_file))
        logger.info(f"Generated: {latest_file}")

        # All-time rarest (using same data for demo)
        all_time_file = generator.generate_all_time(rare_perfs, top_n=min(20, len(rare_perfs)))
        files_generated.append(str(all_time_file))
        logger.info(f"Generated: {all_time_file}")

        # Summary stats
        summary_file = generator.generate_summary_stats(rare_perfs)
        if summary_file:
            files_generated.append(str(summary_file))
            logger.info(f"Generated: {summary_file}")

        # Master index
        index_file = generator.generate_index()
        files_generated.append(str(index_file))
        logger.info(f"Generated: {index_file}")

        # Push to Git
        logger.info("Pushing results to GitHub...")
        commit_success = git_pusher.push_results(
            files_generated,
            f"Update NFL RB results - {datetime.now().strftime('%Y-%m-%d %H:%M')} ({len(rare_perfs)} rare performances)"
        )

        if commit_success:
            logger.success("Successfully pushed results to GitHub")
        else:
            logger.warning("Failed to push results to GitHub")

        # Show summary
        logger.info(f"Pipeline complete! Generated {len(files_generated)} files")
        logger.info(f"Rare performances found: {len(rare_perfs)}")
        logger.info("Web UI should now show updated data")

        return True

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        logger.exception("Full error details:")
        return False

def main():
    """Main entry point"""
    logger.info("GAAS starting...")
    logger.info(f"Working directory: {Path.cwd()}")

    # Run the NFL RB pipeline
    success = run_nfl_rb_pipeline()

    if success:
        logger.success("Pipeline completed successfully!")
    else:
        logger.error("Pipeline failed")

    return success

if __name__ == '__main__':
    main()
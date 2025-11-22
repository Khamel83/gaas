"""Multi-position GAAS orchestrator for all NFL positions"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from processors.rarity_engine import RarityEngine
from generators.json_generator import JSONGenerator
from utils.git_pusher import GitPusher

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add("logs/gaas_multi.log", rotation="100 MB")

def run_position_pipeline(position):
    """Run pipeline for a single position"""
    logger.info(f"Running {position.upper()} pipeline...")

    try:
        # Initialize components
        engine = RarityEngine('nfl', position)
        generator = JSONGenerator('nfl', position)

        # Get recent interesting performances from archive
        logger.info(f"Finding recent interesting {position.upper()} performances...")
        recent_games = engine.get_recent_performances()

        if len(recent_games) == 0:
            logger.warning(f"No interesting {position.upper()} games found in archive")
            return []

        logger.info(f"Found {len(recent_games)} recent {position.upper()} games to analyze")

        # Compute rarity for each game
        rare_perfs = []
        for idx, game in recent_games.iterrows():
            logger.info(f"Analyzing {position.upper()}: {game['player_name']}")
            if position == 'qb':
                stats_desc = f"{game['pass_yards']} yards, {game['pass_td']} TDs"
            elif position == 'rb':
                stats_desc = f"{game['rush_yards']} yards, {game['rush_td']} TDs"
            elif position in ['wr', 'te']:
                stats_desc = f"{game['receiving_yards']} yards, {game['receiving_td']} TDs"
            else:
                stats_desc = "N/A"

            logger.info(f"  {stats_desc}")

            rarity = engine.compute_rarity(game)

            # Only include rare performances (≤25 occurrences)
            if rarity['occurrence_count'] <= 25:
                rare_perfs.append({
                    'game': game.to_dict(),
                    'rarity': rarity
                })
                logger.success(f"RARE: {game['player_name']} - {rarity['classification']} ({rarity['occurrence_count']} occurrences)")

        if not rare_perfs:
            logger.info(f"No rare {position.upper()} performances found in recent games")
            return []

        logger.info(f"Found {len(rare_perfs)} rare {position.upper()} performances")

        # Generate outputs
        logger.info(f"Generating {position.upper()} output files...")
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

        return rare_perfs, files_generated

    except Exception as e:
        logger.error(f"{position.upper()} pipeline failed: {e}")
        logger.exception("Full error details:")
        return [], []

def generate_master_index(all_results):
    """Generate master index with all positions"""
    all_files = []

    positions_data = {}
    for position, (rare_perfs, files) in all_results.items():
        if rare_perfs:
            positions_data[position] = {
                'files': {
                    position: {
                        'latest': f'nfl/{position}_latest.json',
                        'all_time': f'nfl/{position}_all_time.json',
                        'summary': f'nfl/{position}_summary.json'
                    }
                }
            }
            all_files.extend(files)

    output = {
        'last_updated': datetime.now().isoformat(),
        'total_rare_performances': sum(len(perfs) for perfs, _ in all_results.values()),
        'sports': {
            'nfl': {
                'positions': list(positions_data.keys()),
                **positions_data
            }
        }
    }

    # Save master index
    index_file = Path("results/index.json")
    index_file.parent.mkdir(parents=True, exist_ok=True)
    import json
    with open(index_file, 'w') as f:
        json.dump(output, f, indent=2)

    logger.info(f"Generated master index: {index_file}")
    all_files.append(str(index_file))

    return all_files

def main():
    """Main entry point for multi-position pipeline"""
    logger.info("GAAS Multi-Position Pipeline starting...")
    logger.info(f"Working directory: {Path.cwd()}")

    # Run pipeline for all positions
    positions = ['qb', 'rb', 'wr', 'te']
    all_results = {}
    total_rare_perfs = 0

    for position in positions:
        rare_perfs, files = run_position_pipeline(position)
        all_results[position] = (rare_perfs, files)
        total_rare_perfs += len(rare_perfs)

    # Generate master index
    all_files = generate_master_index(all_results)

    # Push to Git
    if all_files:
        logger.info("Pushing results to GitHub...")
        git_pusher = GitPusher()
        commit_success = git_pusher.push_results(
            all_files,
            f"Update all NFL positions - {datetime.now().strftime('%Y-%m-%d %H:%M')} ({total_rare_perfs} rare performances)"
        )

        if commit_success:
            logger.success("Successfully pushed results to GitHub")
        else:
            logger.warning("Failed to push results to GitHub")

    # Show summary
    logger.info("Multi-position pipeline complete!")
    logger.info(f"Total rare performances found: {total_rare_perfs}")
    logger.info(f"Files generated: {len(all_files)}")

    for position, (rare_perfs, files) in all_results.items():
        if rare_perfs:
            logger.info(f"  {position.upper()}: {len(rare_perfs)} rare performances")

    return total_rare_perfs > 0

if __name__ == '__main__':
    success = main()
    if success:
        logger.success("Multi-position pipeline completed successfully!")
    else:
        logger.error("Multi-position pipeline failed")

    sys.exit(0 if success else 1)
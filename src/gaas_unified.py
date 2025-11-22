#!/usr/bin/env python3
"""Unified GAAS orchestrator for all sports"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

# Import utilities
from utils.git_pusher import GitPusher

# Import all sport modules
from collectors.nfl_collector import NFLCollector
from processors.nfl_rarity import NFLRarityEngine
from generators.nfl_generator import NFLGenerator

from collectors.nba_collector import NBACollector
from processors.nba_rarity import NBARarityEngine
from generators.nba_generator import NBAJSONGenerator

from collectors.mlb_collector import MLBCollector
from processors.mlb_rarity import MLBRarityEngine
from generators.mlb_generator import MLBJSONGenerator

from collectors.f1_collector import F1Collector
from processors.f1_rarity import F1RarityEngine
from generators.f1_generator import F1JSONGenerator

from collectors.champions_league_collector import ChampionsLeagueCollector
from processors.champions_league_rarity import ChampionsLeagueRarityEngine
from generators.champions_league_generator import ChampionsLeagueGenerator

from collectors.nhl_collector import NHLCollector
from processors.nhl_rarity import NHLRarityEngine
from generators.nhl_generator import NHLGenerator


class SportOrchestrator:
    def __init__(self, auto_commit=False):
        self.auto_commit = auto_commit
        self.git_pusher = GitPusher() if auto_commit else None
        self.sports = {
            'nfl': {
                'collector': NFLCollector(),
                'rarity_engine': NFLRarityEngine(),
                'generator': NFLGenerator(),
                'positions': ['rb', 'qb', 'wr', 'te']  # Main positions
            },
            'nba': {
                'collector': NBACollector(),
                'rarity_engine': NBARarityEngine(),
                'generator': NBAJSONGenerator(),
                'positions': ['all']  # NBA handles all players
            },
            'mlb': {
                'collector': MLBCollector(),
                'rarity_engine': MLBRarityEngine(),
                'generator': MLBJSONGenerator(),
                'positions': ['all']  # MLB handles all players
            },
            'f1': {
                'collector': F1Collector(),
                'rarity_engine': F1RarityEngine(),
                'generator': F1JSONGenerator(),
                'positions': ['all']  # F1 handles all drivers
            },
            'champions_league': {
                'collector': ChampionsLeagueCollector(),
                'rarity_engine': ChampionsLeagueRarityEngine(),
                'generator': ChampionsLeagueGenerator(),
                'positions': ['all']  # Champions League handles all players
            },
            'nhl': {
                'collector': NHLCollector(),
                'rarity_engine': NHLRarityEngine(),
                'generator': NHLGenerator(),
                'positions': ['all']  # NHL handles all players
            }
        }

    def process_sport(self, sport_name, sport_config):
        """Process a single sport"""
        logger.info(f"Processing {sport_name.upper()}...")
        start_time = datetime.now()

        try:
            collector = sport_config['collector']
            rarity_engine = sport_config['rarity_engine']
            generator = sport_config['generator']

            # Step 1: Check if it's a game window and fetch new data
            new_data = False
            if hasattr(collector, 'is_game_window'):
                if collector.is_game_window():
                    logger.info(f"{sport_name.upper()} game window detected - fetching new data")
                    if sport_name == 'nfl':
                        # NFL has multiple positions
                        for position in sport_config['positions']:
                            new_matches = collector.fetch_new_games(position=position)
                            if new_matches is not None and len(new_matches) > 0:
                                logger.success(f"Fetched {len(new_matches)} new {sport_name.upper()} {position} performances")
                                new_data = True
                    else:
                        # Other sports handle all players
                        if hasattr(collector, 'fetch_new_games'):
                            new_matches = collector.fetch_new_games()
                        elif hasattr(collector, 'fetch_new_races'):  # F1
                            new_matches = collector.fetch_new_races()
                        elif hasattr(collector, 'fetch_new_matches'):  # Champions League, NHL
                            new_matches = collector.fetch_new_matches()
                        else:
                            new_matches = None

                        if new_matches is not None and len(new_matches) > 0:
                            logger.success(f"Fetched {len(new_matches)} new {sport_name.upper()} performances")
                            new_data = True
                else:
                    logger.info(f"Outside {sport_name.upper()} game window - using existing data")
            else:
                logger.info(f"No game window check for {sport_name.upper()} - proceeding with analysis")

            # Step 2: Check for rare performances
            if sport_name == 'nfl':
                # NFL has multiple positions
                all_rare_performances = []
                for position in sport_config['positions']:
                    rare_performances = rarity_engine.check_current_season(position)
                    if rare_performances:
                        all_rare_performances.extend(rare_performances)
                        logger.success(f"Found {len(rare_performances)} rare {sport_name.upper()} {position} performances")
                rare_performances = all_rare_performances
            else:
                # Other sports handle all players
                rare_performances = rarity_engine.check_current_season()
                if rare_performances:
                    logger.success(f"Found {len(rare_performances)} rare {sport_name.upper()} performances")

            if not rare_performances:
                logger.info(f"No rare {sport_name.upper()} performances found")
                return {
                    'sport': sport_name,
                    'rare_performances': 0,
                    'new_data': new_data,
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'status': 'no_rare_performances'
                }

            # Step 3: Generate outputs
            logger.info(f"Generating {sport_name.upper()} outputs...")
            if sport_name == 'nfl':
                # NFL has multiple positions
                all_performances = {}
                for position in sport_config['positions']:
                    position_performances = [p for p in rare_performances if p.get('position') == position]
                    if position_performances:
                        json_results = generator.generate_json(position_performances, position)
                        all_performances[position] = len(position_performances)
                generator.generate_markdown(rare_performances)
            elif sport_name in ['nba', 'mlb', 'f1']:
                # These sports use summary/detailed format
                json_results = generator.generate_json(rare_performances)
                generator.generate_markdown(rare_performances)
            else:
                # Champions League and NHL format
                json_results = generator.generate_json(rare_performances)
                generator.generate_markdown(rare_performances)

            processing_time = (datetime.now() - start_time).total_seconds()
            logger.success(f"{sport_name.upper()} processing complete in {processing_time:.1f}s - {len(rare_performances)} rare performances")

            return {
                'sport': sport_name,
                'rare_performances': len(rare_performances),
                'new_data': new_data,
                'processing_time': processing_time,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"{sport_name.upper()} processing failed: {e}")
            return {
                'sport': sport_name,
                'rare_performances': 0,
                'new_data': False,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'status': 'error',
                'error': str(e)
            }

    async def process_all_sports_parallel(self):
        """Process all sports in parallel"""
        logger.info("Starting parallel processing of all sports...")

        with ThreadPoolExecutor(max_workers=len(self.sports)) as executor:
            loop = asyncio.get_event_loop()

            # Create tasks for all sports
            tasks = []
            for sport_name, sport_config in self.sports.items():
                task = loop.run_in_executor(
                    executor,
                    self.process_sport,
                    sport_name,
                    sport_config
                )
                tasks.append(task)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)

        return results

    def process_all_sports_sequential(self):
        """Process all sports sequentially"""
        logger.info("Starting sequential processing of all sports...")
        results = []

        for sport_name, sport_config in self.sports.items():
            result = self.process_sport(sport_name, sport_config)
            results.append(result)

        return results

    def print_summary(self, results):
        """Print processing summary"""
        logger.info("=" * 60)
        logger.info("GAAS UNIFIED PROCESSING SUMMARY")
        logger.info("=" * 60)

        total_rare_performances = 0
        total_processing_time = 0
        sports_with_data = 0
        sports_with_errors = 0

        for result in results:
            sport = result['sport'].upper()
            count = result['rare_performances']
            time = result['processing_time']
            status = result['status']

            if status == 'success':
                logger.info(f"{sport:15} | {count:3} rare performances | {time:6.1f}s | ✅")
                total_rare_performances += count
                sports_with_data += 1
            elif status == 'no_rare_performances':
                logger.info(f"{sport:15} | {count:3} rare performances | {time:6.1f}s | ⚪")
            else:
                logger.error(f"{sport:15} | {count:3} rare performances | {time:6.1f}s | ❌ {result.get('error', '')}")
                sports_with_errors += 1

            total_processing_time += time

        logger.info("-" * 60)
        logger.info(f"TOTALS          | {total_rare_performances:3} rare performances | {total_processing_time:6.1f}s")
        logger.info(f"Sports with data: {sports_with_data}")
        logger.info(f"Sports with errors: {sports_with_errors}")
        logger.info("=" * 60)


async def main():
    """Main unified orchestrator"""
    logger.info("Starting GAAS Unified Orchestrator")

    auto_commit = '--commit' in sys.argv
    orchestrator = SportOrchestrator(auto_commit=auto_commit)

    # Process all sports in parallel
    results = await orchestrator.process_all_sports_parallel()

    # Print summary
    orchestrator.print_summary(results)

    # Auto-commit results if enabled
    if orchestrator.auto_commit:
        logger.info("Auto-committing results to GitHub...")
        commit_success = orchestrator.git_pusher.auto_commit_results(results)
        if commit_success:
            logger.success("Results auto-committed and pushed to GitHub")
        else:
            logger.warning("Auto-commit failed or no changes to commit")

    logger.success("GAAS Unified processing completed")


if __name__ == "__main__":
    try:
        # Check if parallel processing is requested
        if '--parallel' in sys.argv:
            asyncio.run(main())
        else:
            # Sequential processing (default for compatibility)
            auto_commit = '--commit' in sys.argv
            orchestrator = SportOrchestrator(auto_commit=auto_commit)
            results = orchestrator.process_all_sports_sequential()
            orchestrator.print_summary(results)

            # Auto-commit results if enabled
            if auto_commit:
                logger.info("Auto-committing results to GitHub...")
                commit_success = orchestrator.git_pusher.auto_commit_results(results)
                if commit_success:
                    logger.success("Results auto-committed and pushed to GitHub")
                else:
                    logger.warning("Auto-commit failed or no changes to commit")

        logger.success("GAAS Unified processing completed successfully")
    except Exception as e:
        logger.error(f"GAAS Unified processing failed: {e}")
        sys.exit(1)
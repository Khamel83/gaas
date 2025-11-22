#!/usr/bin/env python3
"""
GAAS Harvest Orchestrator - Manages the entire data harvesting pipeline
"""

import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

from reference_scraper import ReferenceScraper
from github_discovery import GitHubDiscovery
from data_processor import DataProcessor

class HarvestOrchestrator:
    def __init__(self):
        self.setup_logging()
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)

        # Initialize components
        self.scraper = ReferenceScraper()
        self.github_discovery = GitHubDiscovery()
        self.data_processor = DataProcessor()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/orchestrator.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('HarvestOrchestrator')

    async def run_harvest_cycle(self):
        """Run one complete harvest cycle"""
        self.logger.info("Starting harvest cycle")

        # Phase 1: Reference.com scraping (rate limited)
        await self.scrape_reference_sites()

        # Phase 2: GitHub discovery (weekly)
        if datetime.now().weekday() == 0:  # Monday
            await self.discover_github_repos()

        # Phase 3: Data processing
        await self.process_harvested_data()

        # Phase 4: Generate web interface updates
        await self.update_web_interface()

        self.logger.info("Harvest cycle completed")

    async def scrape_reference_sites(self):
        """Scrape Reference.com sites with appropriate rate limits"""
        current_hour = datetime.now().hour

        # Different time windows for different sports
        if 2 <= current_hour <= 10:  # Early morning
            self.logger.info("Harvesting MLB data (early morning window)")
            await self.scraper.harvest_sport('mlb', max_players=15)

        elif 20 <= current_hour <= 23 or 0 <= current_hour <= 4:  # Night/late night
            self.logger.info("Harvesting NBA/NHL data (night window)")
            await self.scraper.harvest_sport('nba', max_players=10)
            await self.scraper.harvest_sport('nhl', max_players=8)

        elif 14 <= current_hour <= 18:  # Afternoon
            self.logger.info("Harvesting NFL data (afternoon window)")
            await self.scraper.harvest_sport('nfl', max_players=5)

    async def discover_github_repos(self):
        """Discover and harvest sports data from GitHub"""
        self.logger.info("Starting GitHub repository discovery")

        try:
            # Discover repositories
            repos = await self.github_discovery.discover_repositories()

            # Save discovery results
            self.github_discovery.save_discovery_results(repos)

            # Harvest from top repositories
            await self.github_discovery.harvest_top_repositories(top_n=10)

            self.logger.info(f"Discovered {len(repos)} repositories")

        except Exception as e:
            self.logger.error(f"GitHub discovery failed: {e}")

    async def process_harvested_data(self):
        """Process newly harvested data"""
        self.logger.info("Processing harvested data")

        try:
            self.data_processor.process_all_data()
        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")

    async def update_web_interface(self):
        """Update web interface with new data"""
        self.logger.info("Updating web interface")

        try:
            # Generate new data files
            self.data_processor.generate_web_data()

            # Update JSON files in web directories
            self.update_json_files()

        except Exception as e:
            self.logger.error(f"Web interface update failed: {e}")

    def update_json_files(self):
        """Update JSON files for web interface"""
        import shutil

        # Copy latest generated JSON to web directories
        json_files = [
            ('results/nba/nba_latest.json', 'nba/nba_latest.json'),
            ('results/mlb/mlb_latest.json', 'mlb/mlb_latest.json'),
            ('results/nfl/rb_latest.json', 'nfl/rb_latest.json'),
            ('results/nfl/qb_latest.json', 'nfl/qb_latest.json'),
            ('results/nfl/wr_latest.json', 'nfl/wr_latest.json'),
            ('results/nfl/te_latest.json', 'nfl/te_latest.json'),
        ]

        for src, dst in json_files:
            if Path(src).exists():
                shutil.copy2(src, dst)
                self.logger.info(f"Updated {dst}")

    def get_harvest_status(self):
        """Get current harvest status and statistics"""
        status = {}

        # Database stats
        harvest_conn = sqlite3.connect('data/harvest_archive.db')
        cursor = harvest_conn.cursor()

        for sport in ['mlb', 'nba', 'nfl', 'nhl']:
            cursor.execute('''
                SELECT COUNT(*) FROM harvested_games WHERE sport = ?
            ''', (sport,))
            status[f'{sport}_games'] = cursor.fetchone()[0]

        # Request rate stats
        cursor.execute('''
            SELECT domain, COUNT(*) FROM request_log
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY domain
        ''')
        status['recent_requests'] = dict(cursor.fetchall())

        harvest_conn.close()

        # GitHub discovery stats
        github_conn = sqlite3.connect('data/harvest_archive.db')
        cursor = github_conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM github_repositories')
        status['github_repos_discovered'] = cursor.fetchone()[0]

        github_conn.close()

        return status

    async def run_continuous(self):
        """Run orchestrator continuously"""
        self.logger.info("Starting continuous harvest orchestrator")

        while True:
            try:
                current_time = datetime.now()
                current_hour = current_time.hour

                # Run harvest cycle during appropriate hours
                if 2 <= current_hour <= 23:  # 2am to 11pm
                    await self.run_harvest_cycle()

                    # Log status
                    status = self.get_harvest_status()
                    self.logger.info(f"Harvest status: {json.dumps(status, indent=2)}")

                    # Wait 2 hours between cycles (rate limiting)
                    await asyncio.sleep(2 * 3600)

                else:
                    # Wait until 2am
                    next_run = current_time.replace(hour=2, minute=0, second=0)
                    if next_run <= current_time:
                        next_run += timedelta(days=1)

                    wait_seconds = (next_run - current_time).total_seconds()
                    self.logger.info(f"Waiting until {next_run} ({wait_seconds/3600:.1f} hours)")
                    await asyncio.sleep(wait_seconds)

            except KeyboardInterrupt:
                self.logger.info("Harvest orchestrator stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Harvest cycle error: {e}")
                # Wait 30 minutes and retry
                await asyncio.sleep(1800)

async def main():
    """Main entry point"""
    orchestrator = HarvestOrchestrator()

    # Check command line arguments
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--status':
            status = orchestrator.get_harvest_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == '--once':
            await orchestrator.run_harvest_cycle()
        else:
            print("Usage: python orchestrator.py [--status|--once]")
    else:
        # Run continuous
        await orchestrator.run_continuous()

if __name__ == "__main__":
    asyncio.run(main())
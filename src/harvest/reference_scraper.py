#!/usr/bin/env python3
"""
Reference.com Scraper - Non-destructive, rate-limited data harvesting
Baseball, Basketball, Football, Hockey Reference sites
"""

import asyncio
import aiohttp
import time
import re
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

class ReferenceScraper:
    def __init__(self, db_path="data/harvest_archive.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Rate limiting per domain (seconds between requests)
        self.rate_limits = {
            'baseball-reference.com': 10.0,
            'basketball-reference.com': 8.0,
            'pro-football-reference.com': 12.0,
            'hockey-reference.com': 15.0,
            'fbref.com': 20.0
        }

        self.last_request_time = {}
        self.session = None
        self.setup_database()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/harvest.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ReferenceScraper')

    def setup_database(self):
        """Create database tables for harvested data"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Main harvest table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS harvested_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT NOT NULL,
                source_domain TEXT NOT NULL,
                player_id TEXT NOT NULL,
                player_name TEXT,
                game_date DATE,
                team TEXT,
                opponent TEXT,
                stats_json TEXT,
                source_url TEXT,
                harvest_timestamp DATETIME,
                confidence_score REAL DEFAULT 1.0,
                UNIQUE(sport, source_domain, player_id, game_date)
            )
        ''')

        # Source tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS harvest_sources (
                domain TEXT PRIMARY KEY,
                last_player_index INTEGER,
                total_players_found INTEGER,
                last_successful_request DATETIME,
                robots_text TEXT,
                error_count INTEGER DEFAULT 0
            )
        ''')

        # Rate limiting log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                url TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status_code INTEGER,
                response_time_seconds REAL
            )
        ''')

        conn.commit()
        conn.close()

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'GAAS-Sports-Analytics/1.0 (Educational Research)'},
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session

    async def rate_limit_wait(self, domain):
        """Implement rate limiting with exponential backoff for errors"""
        now = time.time()
        last_request = self.last_request_time.get(domain, 0)

        # Get current rate limit
        base_rate = self.rate_limits.get(domain, 10.0)

        # Check for recent errors and implement exponential backoff
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM request_log
            WHERE domain = ? AND timestamp > datetime('now', '-1 hour')
            AND status_code >= 400
        ''', (domain,))
        recent_errors = cursor.fetchone()[0]
        conn.close()

        if recent_errors > 0:
            # Exponential backoff
            backoff_multiplier = min(2 ** recent_errors, 8)  # Max 8x slower
            wait_time = base_rate * backoff_multiplier
            self.logger.warning(f"Recent errors on {domain}, using backoff: {wait_time}s")
        else:
            wait_time = base_rate

        time_since_last = now - last_request
        if time_since_last < wait_time:
            sleep_time = wait_time - time_since_last
            self.logger.info(f"Rate limiting {domain}: waiting {sleep_time:.1f}s")
            await asyncio.sleep(sleep_time)

        self.last_request_time[domain] = time.time()

    async def fetch_page(self, url):
        """Fetch page with rate limiting and error handling"""
        domain = urlparse(url).netloc
        await self.rate_limit_wait(domain)

        start_time = time.time()
        session = await self.get_session()

        try:
            async with session.get(url) as response:
                response_time = time.time() - start_time

                # Log request
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO request_log (domain, url, status_code, response_time_seconds)
                    VALUES (?, ?, ?, ?)
                ''', (domain, url, response.status, response_time))
                conn.commit()
                conn.close()

                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
                    return None

        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            # Log error for backoff
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO request_log (domain, url, status_code, response_time_seconds)
                VALUES (?, ?, ?, ?)
            ''', (domain, url, 500, time.time() - start_time))
            conn.commit()
            conn.close()
            return None

    async def parse_mlb_player_career(self, html, player_url):
        """Parse MLB player career page for game data"""
        soup = BeautifulSoup(html, 'html.parser')

        # Find player info
        player_name = soup.find('h1')
        player_name = player_name.get_text().strip() if player_name else "Unknown"

        # Find game logs section
        game_logs_link = soup.find('a', string=re.compile(r'Game Logs', re.I))
        if not game_logs_link:
            return []

        game_logs_url = urljoin(player_url, game_logs_link['href'])
        return await self.parse_mlb_game_logs(game_logs_url, player_name)

    async def parse_mlb_game_logs(self, game_logs_url, player_name):
        """Parse MLB game logs page"""
        html = await self.fetch_page(game_logs_url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        games = []

        # Find the game logs table
        table = soup.find('table', {'id': 'pitching_gl'}) or soup.find('table', {'id': 'batting_gl'})
        if not table:
            return []

        rows = table.find_all('tr')[1:]  # Skip header

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 15:  # Minimum columns expected
                continue

            try:
                # Parse game data
                date_str = cols[0].get_text().strip()
                team = cols[1].get_text().strip()
                opponent = cols[2].get_text().strip()

                # Extract stats based on table type
                if 'batting' in game_logs_url:
                    stats = {
                        'ab': int(cols[5].get_text() or 0),
                        'hits': int(cols[7].get_text() or 0),
                        'runs': int(cols[8].get_text() or 0),
                        'home_runs': int(cols[11].get_text() or 0),
                        'rbis': int(cols[12].get_text() or 0),
                        'walks': int(cols[14].get_text() or 0)
                    }
                else:  # Pitching
                    stats = {
                        'innings_pitched': cols[5].get_text().strip(),
                        'hits': int(cols[6].get_text() or 0),
                        'runs': int(cols[7].get_text() or 0),
                        'strikeouts': int(cols[9].get_text() or 0),
                        'walks': int(cols[10].get_text() or 0)
                    }

                games.append({
                    'player_name': player_name,
                    'date': date_str,
                    'team': team,
                    'opponent': opponent,
                    'stats': stats
                })

            except (ValueError, IndexError) as e:
                continue  # Skip malformed rows

        return games

    async def scrape_mlb_players(self, start_letter='a'):
        """Scrape all MLB players starting with given letter"""
        base_url = f"https://www.baseball-reference.com/players/{start_letter}/"

        html = await self.fetch_page(base_url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        players = []

        # Find all player links
        for link in soup.find_all('a', href=re.compile(r'/players/[a-z]/[^/]+\.shtml$')):
            player_url = urljoin(base_url, link['href'])
            player_name = link.get_text().strip()

            if player_name:  # Skip empty names
                players.append({
                    'name': player_name,
                    'url': player_url,
                    'sport': 'mlb'
                })

        return players

    async def harvest_sport(self, sport, max_players=50):
        """Main harvest function for a specific sport"""
        self.logger.info(f"Starting harvest for {sport}")

        if sport == 'mlb':
            players = []
            for letter in 'abcdefghijklmnopqrstuvwxyz':
                letter_players = await self.scrape_mlb_players(letter)
                players.extend(letter_players)
                if len(players) >= max_players:
                    break

            # Limit to max_players
            players = players[:max_players]

            for i, player in enumerate(players, 1):
                self.logger.info(f"Processing {player['name']} ({i}/{len(players)})")

                # Get player career data
                html = await self.fetch_page(player['url'])
                if html:
                    games = await self.parse_mlb_player_career(html, player['url'])

                    # Save games to database
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.cursor()

                    for game in games:
                        cursor.execute('''
                            INSERT OR REPLACE INTO harvested_games
                            (sport, source_domain, player_id, player_name, game_date, team, opponent, stats_json, source_url, harvest_timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            'mlb',
                            'baseball-reference.com',
                            player['url'].split('/')[-1].replace('.shtml', ''),
                            player['name'],
                            game['date'],
                            game['team'],
                            game['opponent'],
                            json.dumps(game['stats']),
                            player['url'],
                            datetime.now()
                        ))

                    conn.commit()
                    conn.close()

                    self.logger.info(f"Saved {len(games)} games for {player['name']}")

    async def run_continuous_harvest(self):
        """Main continuous harvest loop"""
        sports_schedule = [
            ('mlb', '18:00', '06:00'),  # 6pm-6am for MLB
            ('nba', '20:00', '04:00'),  # 8pm-4am for NBA
            ('nfl', '22:00', '08:00'),  # 10pm-8am for NFL
            ('nhl', '23:00', '07:00'),  # 11pm-7am for NHL
        ]

        while True:
            current_hour = datetime.now().hour

            for sport, start_str, end_str in sports_schedule:
                start_hour = int(start_str.split(':')[0])
                end_hour = int(end_str.split(':')[0])

                # Check if we're in the harvest window
                if start_hour <= current_hour or current_hour < end_hour:
                    self.logger.info(f"Harvest window active for {sport}")
                    await self.harvest_sport(sport, max_players=20)
                    break
            else:
                self.logger.info("Outside harvest windows, waiting 30 minutes")
                await asyncio.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    scraper = ReferenceScraper()

    # Test run
    async def test_harvest():
        await scraper.harvest_sport('mlb', max_players=5)

    asyncio.run(test_harvest())
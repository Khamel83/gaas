#!/usr/bin/env python3
"""
GitHub Discovery System - Find and harvest sports data repositories
"""

import asyncio
import aiohttp
import json
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
import logging

class GitHubDiscovery:
    def __init__(self, github_token=None, db_path="data/harvest_archive.db"):
        self.github_token = github_token
        self.db_path = Path(db_path)
        self.session = None
        self.setup_logging()

        # Search patterns for sports data
        self.search_patterns = [
            "mlb historical game data",
            "nba play by play data",
            "nfl game logs csv",
            "nhl player statistics csv",
            "champions league matches dataset",
            "baseball game logs",
            "basketball box scores",
            "football play by play",
            "hockey game data",
            "sports statistics dataset"
        ]

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/github_discovery.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('GitHubDiscovery')

    async def get_session(self):
        if self.session is None:
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GAAS-Sports-Analytics/1.0 (Educational Research)'
            }
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'

            self.session = aiohttp.ClientSession(headers=headers)

        return self.session

    async def search_repositories(self, query, min_stars=10, updated_since_days=365):
        """Search GitHub repositories with given criteria"""
        session = await self.get_session()

        # Build search query
        search_query = f"{query} stars:>={min_stars} pushed:>={updated_since_days}days"

        url = "https://api.github.com/search/repositories"
        params = {
            'q': search_query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 100
        }

        repositories = []
        page = 1

        while True:
            params['page'] = page
            self.logger.info(f"Searching: {search_query} (page {page})")

            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        repos = data.get('items', [])

                        if not repos:
                            break

                        repositories.extend(repos)
                        self.logger.info(f"Found {len(repos)} repositories on page {page}")

                        # GitHub rate limit: check if we have more pages
                        if len(repos) < 100:
                            break

                        page += 1

                        # Respect rate limits
                        await asyncio.sleep(2)

                    elif response.status == 403:  # Rate limited
                        self.logger.warning("Rate limited, waiting 60 seconds")
                        await asyncio.sleep(60)
                    else:
                        self.logger.error(f"GitHub API error: {response.status}")
                        break

            except Exception as e:
                self.logger.error(f"Error searching repositories: {e}")
                break

            # Safety limit to avoid excessive API calls
            if page > 10:  # Max 1000 results per search
                break

        return repositories

    async def analyze_repository(self, repo_data):
        """Analyze a repository for sports data files"""
        session = await self.get_session()

        repo_info = {
            'id': repo_data['id'],
            'name': repo_data['name'],
            'full_name': repo_data['full_name'],
            'description': repo_data.get('description', ''),
            'stars': repo_data['stargazers_count'],
            'language': repo_data.get('language', ''),
            'updated_at': repo_data['updated_at'],
            'clone_url': repo_data['clone_url'],
            'html_url': repo_data['html_url']
        }

        # Get repository contents
        url = f"https://api.github.com/repos/{repo_data['full_name']}/contents"

        try:
            async with session.get(url) as response:
                if response.status == 200:
                    contents = await response.json()
                    data_files = []

                    for item in contents:
                        if self.is_sports_data_file(item):
                            data_files.append({
                                'name': item['name'],
                                'path': item['path'],
                                'size': item.get('size', 0),
                                'download_url': item.get('download_url'),
                                'type': item.get('type', 'file')
                            })

                    repo_info['data_files'] = data_files
                    repo_info['data_score'] = self.calculate_data_score(data_files)

                else:
                    self.logger.warning(f"Failed to get contents for {repo_data['full_name']}")

        except Exception as e:
            self.logger.error(f"Error analyzing repository {repo_data['full_name']}: {e}")

        return repo_info

    def is_sports_data_file(self, file_info):
        """Check if file is likely to contain sports data"""
        name = file_info.get('name', '').lower()
        path = file_info.get('path', '').lower()
        size = file_info.get('size', 0)

        # File extensions that likely contain sports data
        sports_extensions = ['.csv', '.json', '.sqlite', '.db', '.parquet']

        # Keywords in file names/path
        sports_keywords = [
            'game', 'games', 'play', 'plays', 'player', 'players', 'team', 'teams',
            'match', 'matches', 'season', 'seasons', 'stats', 'statistics',
            'mlb', 'nfl', 'nba', 'nhl', 'soccer', 'football', 'baseball',
            'basketball', 'hockey', 'scores', 'box', 'logs', 'data'
        ]

        has_extension = any(name.endswith(ext) for ext in sports_extensions)
        has_keywords = any(keyword in name or keyword in path for keyword in sports_keywords)
        is_reasonable_size = size > 1024  # At least 1KB

        return has_extension and has_keywords and is_reasonable_size

    def calculate_data_score(self, data_files):
        """Calculate relevance score for repository based on data files"""
        score = 0

        for file_info in data_files:
            name = file_info.get('name', '').lower()
            size = file_info.get('size', 0)

            # Points for large files (likely more data)
            if size > 1024 * 1024:  # > 1MB
                score += 10
            elif size > 100 * 1024:  # > 100KB
                score += 5

            # Points for specific sports in filename
            if 'mlb' in name or 'baseball' in name:
                score += 15
            elif 'nfl' in name or 'football' in name:
                score += 15
            elif 'nba' in name or 'basketball' in name:
                score += 15
            elif 'nhl' in name or 'hockey' in name:
                score += 15

            # Points for data type indicators
            if 'game' in name and ('log' in name or 'data' in name):
                score += 10
            elif 'player' in name and ('stats' in name or 'data' in name):
                score += 10
            elif 'season' in name and 'data' in name:
                score += 8

        return score

    async def discover_repositories(self):
        """Main discovery process across all search patterns"""
        all_repositories = []

        for query in self.search_patterns:
            self.logger.info(f"Searching for: {query}")

            repos = await self.search_repositories(query, min_stars=20, updated_since_days=730)

            # Analyze each repository
            for repo_data in repos:
                if repo_data['stargazers_count'] >= 20:  # Minimum quality threshold
                    repo_info = await self.analyze_repository(repo_data)

                    # Only keep repositories with actual data files
                    if repo_info.get('data_score', 0) > 0:
                        all_repositories.append(repo_info)
                        self.logger.info(f"Found data repository: {repo_info['full_name']} (score: {repo_info.get('data_score', 0)})")

        # Sort by data score
        all_repositories.sort(key=lambda x: x.get('data_score', 0), reverse=True)

        return all_repositories

    async def download_data_file(self, repo_info, file_info):
        """Download a specific data file from repository"""
        session = await self.get_session()

        if not file_info.get('download_url'):
            return None

        try:
            async with session.get(file_info['download_url']) as response:
                if response.status == 200:
                    content = await response.text()

                    # Save to local storage
                    safe_name = re.sub(r'[^\w\-_.]', '_', file_info['name'])
                    local_path = Path('data/github_downloads') / repo_info['full_name'] / safe_name
                    local_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    self.logger.info(f"Downloaded: {file_info['name']} from {repo_info['full_name']}")
                    return local_path

                else:
                    self.logger.warning(f"Failed to download {file_info['name']}: HTTP {response.status}")

        except Exception as e:
            self.logger.error(f"Error downloading {file_info['name']}: {e}")

        return None

    async def harvest_top_repositories(self, top_n=20):
        """Harvest data from top repositories"""
        repositories = await self.discover_repositories()
        top_repos = repositories[:top_n]

        self.logger.info(f"Harvesting data from top {len(top_repos)} repositories")

        for repo_info in top_repos:
            self.logger.info(f"Processing repository: {repo_info['full_name']} (score: {repo_info.get('data_score', 0)})")

            data_files = repo_info.get('data_files', [])

            # Download top data files from this repository
            data_files.sort(key=lambda x: x.get('size', 0), reverse=True)
            top_files = data_files[:5]  # Top 5 files per repo

            for file_info in top_files:
                if file_info.get('size', 0) > 100 * 1024:  # Only download files > 100KB
                    await self.download_data_file(repo_info, file_info)

            # Rate limiting between repositories
            await asyncio.sleep(5)

    def save_discovery_results(self, repositories):
        """Save discovery results to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS github_repositories (
                id INTEGER PRIMARY KEY,
                repo_id INTEGER UNIQUE,
                full_name TEXT,
                description TEXT,
                stars INTEGER,
                language TEXT,
                updated_at TEXT,
                clone_url TEXT,
                html_url TEXT,
                data_score INTEGER,
                data_files_json TEXT,
                discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        for repo_info in repositories:
            cursor.execute('''
                INSERT OR REPLACE INTO github_repositories
                (repo_id, full_name, description, stars, language, updated_at, clone_url, html_url, data_score, data_files_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                repo_info['id'],
                repo_info['full_name'],
                repo_info.get('description', ''),
                repo_info.get('stars', 0),
                repo_info.get('language', ''),
                repo_info.get('updated_at', ''),
                repo_info.get('clone_url', ''),
                repo_info.get('html_url', ''),
                repo_info.get('data_score', 0),
                json.dumps(repo_info.get('data_files', []))
            ))

        conn.commit()
        conn.close()

if __name__ == "__main__":
    discovery = GitHubDiscovery()

    # Test discovery
    async def test_discovery():
        await discovery.harvest_top_repositories(top_n=5)

    asyncio.run(test_discovery())
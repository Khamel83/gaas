"""NFL result generator"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


class NFLGenerator:
    def __init__(self):
        self.results_dir = Path("results")
        self.nfl_dir = self.results_dir / "nfl"
        self.nfl_dir.mkdir(parents=True, exist_ok=True)

    def generate_json(self, rare_performances, position='rb'):
        """Generate JSON output for NFL rare performances"""
        if not rare_performances:
            logger.warning(f"No rare NFL {position.upper()} performances to generate")
            return

        # Generate latest (7 days) file
        latest_cutoff = datetime.now() - timedelta(days=7)
        latest_performances = [
            p for p in rare_performances
            if datetime.strptime(p['game_date'], '%Y-%m-%d') >= latest_cutoff
        ]

        # Latest file (7 days)
        latest_data = {
            'sport': 'nfl',
            'position': position,
            'generated_at': datetime.now().isoformat(),
            'timeframe': 'latest_7_days',
            'total_performances': len(latest_performances),
            'performances': latest_performances
        }

        latest_file = self.nfl_dir / f"{position}_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(latest_data, f, indent=2)

        # All time file
        all_time_data = {
            'sport': 'nfl',
            'position': position,
            'generated_at': datetime.now().isoformat(),
            'timeframe': 'all_time',
            'total_performances': len(rare_performances),
            'performances': rare_performances
        }

        all_time_file = self.nfl_dir / f"{position}_all_time.json"
        with open(all_time_file, 'w') as f:
            json.dump(all_time_data, f, indent=2)

        logger.success(f"Generated NFL {position.upper()} JSON files: {len(latest_performances)} latest, {len(rare_performances)} all time")

        # Update main index
        self._update_main_index(position, {
            'latest_file': f'nfl/{position}_latest.json',
            'all_time_file': f'nfl/{position}_all_time.json',
            'latest_count': len(latest_performances),
            'all_time_count': len(rare_performances),
            'last_updated': datetime.now().isoformat()
        })

        return latest_data, all_time_data

    def _update_main_index(self, position, nfl_data):
        """Update main results index with NFL data"""
        index_file = self.results_dir / "index.json"

        # Load existing index
        if index_file.exists():
            with open(index_file, 'r') as f:
                index_data = json.load(f)
        else:
            index_data = {
                'generated_at': datetime.now().isoformat(),
                'sports': {}
            }

        # Initialize NFL section if it doesn't exist
        if 'nfl' not in index_data['sports']:
            index_data['sports']['nfl'] = {
                'positions': {},
                'last_updated': datetime.now().isoformat()
            }

        # Update NFL section
        index_data['sports']['nfl']['positions'][position] = nfl_data
        index_data['sports']['nfl']['last_updated'] = datetime.now().isoformat()
        index_data['generated_at'] = datetime.now().isoformat()

        # Write updated index
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)

        logger.success(f"Updated main results index with NFL {position.upper()} data")

    def generate_markdown(self, all_performances_by_position):
        """Generate markdown report for NFL rare performances"""
        if not all_performances_by_position:
            return

        # Combine all performances across positions
        all_performances = []
        for position, performances in all_performances_by_position.items():
            for perf in performances:
                perf['display_position'] = position.upper()
                all_performances.append(perf)

        if not all_performances:
            return

        # Sort by rarity score
        all_performances.sort(key=lambda x: x['rarity_score'], reverse=True)

        # Categorize by rarity
        never_before = [p for p in all_performances if p['classification'] == 'never_before']
        extremely_rare = [p for p in all_performances if p['classification'] == 'extremely_rare']
        very_rare = [p for p in all_performances if p['classification'] == 'very_rare']
        rare = [p for p in all_performances if p['classification'] == 'rare']

        # Generate markdown content
        md_content = f"# NFL Rare Performances\n\n"
        md_content += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        md_content += f"Total rare performances found: {len(all_performances)}\n\n"

        if never_before:
            md_content += "## 🏆 Never Before Seen Performances\n\n"
            for perf in never_before:
                md_content += f"**{perf['player_name']}** ({perf['display_position']}, {perf['home_team']} vs {perf['away_team']}, Week {perf.get('week', 'N/A')}, {perf['game_date']})\n"

                # Add position-specific stats
                if perf['display_position'] == 'RB':
                    md_content += f"- Rush Yards: {perf.get('rush_yards', 0)}, Rush TD: {perf.get('rush_td', 0)}, Receptions: {perf.get('receptions', 0)}, Receiving Yards: {perf.get('receiving_yards', 0)}\n"
                elif perf['display_position'] == 'QB':
                    md_content += f"- Pass Yards: {perf.get('pass_yards', 0)}, Pass TD: {perf.get('pass_td', 0)}, Completions: {perf.get('completions', 0)}/{perf.get('attempts', 0)}, INT: {perf.get('interceptions', 0)}\n"
                elif perf['display_position'] in ['WR', 'TE']:
                    md_content += f"- Receptions: {perf.get('receptions', 0)}/{perf.get('targets', 0)}, Receiving Yards: {perf.get('receiving_yards', 0)}, TD: {perf.get('receiving_td', 0)}\n"

                md_content += f"- Rarity Score: {perf['rarity_score']:.1f}\n\n"

        if extremely_rare:
            md_content += "## ⭐ Extremely Rare (2-5 occurrences)\n\n"
            for perf in extremely_rare:
                md_content += f"**{perf['player_name']}** ({perf['display_position']}, {perf['home_team']} vs {perf['away_team']}, Week {perf.get('week', 'N/A')}, {perf['game_date']})\n"

                if perf['display_position'] == 'RB':
                    md_content += f"- Rush Yards: {perf.get('rush_yards', 0)}, Rush TD: {perf.get('rush_td', 0)}, Receptions: {perf.get('receptions', 0)}\n"
                elif perf['display_position'] == 'QB':
                    md_content += f"- Pass Yards: {perf.get('pass_yards', 0)}, Pass TD: {perf.get('pass_td', 0)}, INT: {perf.get('interceptions', 0)}\n"
                elif perf['display_position'] in ['WR', 'TE']:
                    md_content += f"- Receptions: {perf.get('receptions', 0)}/{perf.get('targets', 0)}, Receiving Yards: {perf.get('receiving_yards', 0)}\n"

                md_content += f"- Occurrence Count: {perf['occurrence_count']}, Rarity Score: {perf['rarity_score']:.1f}\n\n"

        if very_rare:
            md_content += "## 🔥 Very Rare (6-10 occurrences)\n\n"
            for perf in very_rare[:20]:  # Limit to top 20
                md_content += f"**{perf['player_name']}** ({perf['display_position']}, Week {perf.get('week', 'N/A')})\n"
                md_content += f"- Occurrence Count: {perf['occurrence_count']}, Rarity Score: {perf['rarity_score']:.1f}\n\n"

        # Write markdown file
        md_file = self.nfl_dir / "nfl_performances.md"
        with open(md_file, 'w') as f:
            f.write(md_content)

        logger.success(f"Generated NFL markdown: {md_file}")
"""Champions League result generator"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


class ChampionsLeagueGenerator:
    def __init__(self):
        self.results_dir = Path("results")
        self.champions_league_dir = self.results_dir / "champions_league"
        self.champions_league_dir.mkdir(parents=True, exist_ok=True)

    def generate_json(self, rare_performances):
        """Generate JSON output for Champions League rare performances"""
        if not rare_performances:
            logger.warning("No rare Champions League performances to generate")
            return

        # Generate latest (7 days) file
        latest_cutoff = datetime.now() - timedelta(days=7)
        latest_performances = [
            p for p in rare_performances
            if datetime.strptime(p['match_date'], '%Y-%m-%d') >= latest_cutoff
        ]

        # Latest file (7 days)
        latest_data = {
            'sport': 'champions_league',
            'generated_at': datetime.now().isoformat(),
            'timeframe': 'latest_7_days',
            'total_performances': len(latest_performances),
            'performances': latest_performances
        }

        latest_file = self.champions_league_dir / "champions_league_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(latest_data, f, indent=2)

        # All time file
        all_time_data = {
            'sport': 'champions_league',
            'generated_at': datetime.now().isoformat(),
            'timeframe': 'all_time',
            'total_performances': len(rare_performances),
            'performances': rare_performances
        }

        all_time_file = self.champions_league_dir / "champions_league_all_time.json"
        with open(all_time_file, 'w') as f:
            json.dump(all_time_data, f, indent=2)

        logger.success(f"Generated Champions League JSON files: {len(latest_performances)} latest, {len(rare_performances)} all time")

        # Update main index
        self._update_main_index({
            'champions_league': {
                'latest_file': 'champions_league/champions_league_latest.json',
                'all_time_file': 'champions_league/champions_league_all_time.json',
                'latest_count': len(latest_performances),
                'all_time_count': len(rare_performances),
                'last_updated': datetime.now().isoformat()
            }
        })

        return latest_data, all_time_data

    def _update_main_index(self, champions_league_data):
        """Update main results index with Champions League data"""
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

        # Update Champions League section
        index_data['sports']['champions_league'] = champions_league_data['champions_league']
        index_data['generated_at'] = datetime.now().isoformat()

        # Write updated index
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)

        logger.success("Updated main results index with Champions League data")

    def generate_markdown(self, rare_performances):
        """Generate markdown report for Champions League rare performances"""
        if not rare_performances:
            return

        # Categorize by rarity
        never_before = [p for p in rare_performances if p['classification'] == 'never_before']
        extremely_rare = [p for p in rare_performances if p['classification'] == 'extremely_rare']
        very_rare = [p for p in rare_performances if p['classification'] == 'very_rare']
        rare = [p for p in rare_performances if p['classification'] == 'rare']

        # Generate markdown content
        md_content = f"# Champions League Rare Performances\n\n"
        md_content += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        md_content += f"Total rare performances found: {len(rare_performances)}\n\n"

        if never_before:
            md_content += "## 🏆 Never Before Seen Performances\n\n"
            for perf in never_before:
                md_content += f"**{perf['player_name']}** ({perf['home_team']} vs {perf['away_team']}, {perf['match_date']})\n"
                md_content += f"- Round: {perf['round']}\n"
                md_content += f"- Goals: {perf['goals']}, Assists: {perf['assists']}, Shots: {perf['shots']}\n"
                md_content += f"- Pass Accuracy: {perf['pass_accuracy']}%, Minutes: {perf['minutes_played']}\n"
                md_content += f"- Rarity Score: {perf['rarity_score']:.1f}\n\n"

        if extremely_rare:
            md_content += "## ⭐ Extremely Rare (2-5 occurrences)\n\n"
            for perf in extremely_rare:
                md_content += f"**{perf['player_name']}** ({perf['home_team']} vs {perf['away_team']}, {perf['match_date']})\n"
                md_content += f"- Round: {perf['round']}\n"
                md_content += f"- Goals: {perf['goals']}, Assists: {perf['assists']}, Shots: {perf['shots']}\n"
                md_content += f"- Pass Accuracy: {perf['pass_accuracy']}%, Minutes: {perf['minutes_played']}\n"
                md_content += f"- Occurrence Count: {perf['occurrence_count']}\n"
                md_content += f"- Rarity Score: {perf['rarity_score']:.1f}\n\n"

        if very_rare:
            md_content += "## 🔥 Very Rare (6-10 occurrences)\n\n"
            for perf in very_rare[:10]:  # Limit to top 10
                md_content += f"**{perf['player_name']}** ({perf['home_team']} vs {perf['away_team']}, {perf['match_date']})\n"
                md_content += f"- Goals: {perf['goals']}, Assists: {perf['assists']}, Shots: {perf['shots']}\n"
                md_content += f"- Occurrence Count: {perf['occurrence_count']}, Rarity Score: {perf['rarity_score']:.1f}\n\n"

        # Write markdown file
        md_file = self.champions_league_dir / "champions_league_performances.md"
        with open(md_file, 'w') as f:
            f.write(md_content)

        logger.success(f"Generated Champions League markdown: {md_file}")
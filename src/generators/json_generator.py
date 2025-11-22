"""Generate JSON output files"""
import json
from pathlib import Path
from datetime import datetime

class JSONGenerator:
    def __init__(self, sport, position):
        self.sport = sport
        self.position = position
        self.output_dir = Path(f"results/{sport}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_latest(self, rare_perfs):
        """Generate latest.json (last 7 days)"""
        output = {
            'generated_at': datetime.now().isoformat(),
            'sport': self.sport,
            'position': self.position,
            'time_range': 'last_7_days',
            'total_performances': len(rare_perfs),
            'rare_performances': rare_perfs
        }

        file = self.output_dir / f"{self.position}_latest.json"
        with open(file, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        return file

    def generate_all_time(self, rare_perfs, top_n=50):
        """Generate all_time.json (top N rarest)"""
        # Sort by rarity score (highest first)
        sorted_perfs = sorted(
            rare_perfs,
            key=lambda x: x['rarity']['rarity_score'],
            reverse=True
        )[:top_n]

        output = {
            'generated_at': datetime.now().isoformat(),
            'sport': self.sport,
            'position': self.position,
            'time_range': 'all_time',
            'top_n': top_n,
            'total_rare_performances': len(sorted_perfs),
            'top_rare_performances': sorted_perfs
        }

        file = self.output_dir / f"{self.position}_all_time.json"
        with open(file, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        return file

    def generate_index(self):
        """Generate master index.json"""
        output = {
            'last_updated': datetime.now().isoformat(),
            'sports': {
                'nfl': {
                    'positions': ['rb'],
                    'files': {
                        'rb': {
                            'latest': f'{self.sport}/{self.position}_latest.json',
                            'all_time': f'{self.sport}/{self.position}_all_time.json'
                        }
                    }
                }
            }
        }

        file = Path("results/index.json")
        file.parent.mkdir(parents=True, exist_ok=True)
        with open(file, 'w') as f:
            json.dump(output, f, indent=2)

        return file

    def generate_summary_stats(self, rare_perfs):
        """Generate summary statistics"""
        if not rare_perfs:
            return None

        classifications = {}
        for perf in rare_perfs:
            classification = perf['rarity']['classification']
            classifications[classification] = classifications.get(classification, 0) + 1

        # Calculate average rarity score
        avg_score = sum(p['rarity']['rarity_score'] for p in rare_perfs) / len(rare_perfs)

        # Find rarest performance
        rarest = max(rare_perfs, key=lambda x: x['rarity']['rarity_score'])

        summary = {
            'total_rare_performances': len(rare_perfs),
            'average_rarity_score': round(avg_score, 2),
            'rarest_performance': {
                'player_name': rarest['game']['player_name'],
                'rarity_score': rarest['rarity']['rarity_score'],
                'classification': rarest['rarity']['classification']
            },
            'classification_breakdown': classifications,
            'generated_at': datetime.now().isoformat()
        }

        file = self.output_dir / f"{self.position}_summary.json"
        with open(file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        return file
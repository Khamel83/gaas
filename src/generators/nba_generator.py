"""Generate NBA results and JSON summaries"""
from pathlib import Path
from datetime import datetime
from loguru import logger
import json


class NBAJSONGenerator:
    """Generate NBA results in JSON format"""

    def __init__(self):
        self.results_dir = Path("results/nba")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def generate_summary(self, rare_performances, archive_summary):
        """Generate overall NBA summary"""
        total_rare = len(rare_performances)

        if total_rare == 0:
            summary = {
                "total_rare_performances": 0,
                "average_rarity_score": 0,
                "generated_at": datetime.now().isoformat()
            }
        else:
            avg_rarity = sum(p['rarity_score'] for p in rare_performances) / total_rare
            rarest = rare_performances[0] if rare_performances else None

            # Classification breakdown
            class_counts = {}
            for perf in rare_performances:
                cls = perf['classification']
                class_counts[cls] = class_counts.get(cls, 0) + 1

            summary = {
                "total_rare_performances": total_rare,
                "average_rarity_score": round(avg_rarity, 2),
                "rarest_performance": {
                    "player_name": rarest['player_name'],
                    "rarity_score": rarest['rarity_score'],
                    "classification": rarest['classification']
                } if rarest else None,
                "classification_breakdown": class_counts,
                "generated_at": datetime.now().isoformat()
            }

        # Save summary
        summary_path = self.results_dir / "nba_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.success(f"NBA summary saved to {summary_path}")
        return summary

    def generate_detailed_results(self, rare_performances):
        """Generate detailed NBA results JSON"""
        detailed = {
            "rare_performances": rare_performances,
            "generated_at": datetime.now().isoformat()
        }

        # Save detailed results
        detailed_path = self.results_dir / "nba_detailed.json"
        with open(detailed_path, 'w') as f:
            json.dump(detailed, f, indent=2)

        logger.success(f"Detailed NBA results saved to {detailed_path}")
        return detailed

    def generate_all(self, rare_performances, archive_summary):
        """Generate all NBA result files"""
        logger.info("Generating NBA result files...")

        summary = self.generate_summary(rare_performances, archive_summary)
        detailed = self.generate_detailed_results(rare_performances)

        return {
            'summary': summary,
            'detailed': detailed
        }
"""Automated Git commits and pushes"""
from git import Repo
from datetime import datetime
from pathlib import Path
from loguru import logger

class GitPusher:
    def __init__(self, repo_path='.'):
        self.repo = Repo(repo_path)

    def push_results(self, files, message=None, auto_rebase=False):
        """Commit and push result files"""
        try:
            # Pull latest changes first if auto_rebase is enabled
            if auto_rebase:
                try:
                    origin = self.repo.remote(name='origin')
                    origin.pull(rebase=True)
                    logger.info("Pulled and rebased latest changes")
                except Exception as e:
                    logger.warning(f"Could not pull latest changes: {e}")

            # Add all result files
            for file_path in files:
                if Path(file_path).exists():
                    self.repo.index.add([file_path])
                    logger.info(f"Added {file_path} to git")
                else:
                    logger.warning(f"File {file_path} does not exist, skipping")

            # Check if there are changes to commit
            if not self.repo.index.diff("HEAD"):
                logger.info("No changes to commit")
                return False

            # Create commit message
            if not message:
                message = f"Update results - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            # Commit changes
            commit = self.repo.index.commit(message)
            logger.info(f"Committed: {message} (SHA: {commit.hexsha[:8]})")

            # Push to remote
            origin = self.repo.remote(name='origin')
            origin.push()
            logger.success("Pushed to GitHub")

            return True

        except Exception as e:
            logger.error(f"Git push failed: {e}")
            return False

    def auto_commit_results(self, sport_results=None):
        """Auto-commit all results with detailed message"""
        try:
            # Collect all result files
            result_files = []
            results_dir = Path("results")

            if results_dir.exists():
                result_files.extend(str(f) for f in results_dir.rglob("*.json"))
                result_files.extend(str(f) for f in results_dir.rglob("*.md"))

            # Add index file specifically
            index_file = results_dir / "index.json"
            if index_file.exists():
                result_files.append(str(index_file))

            if not result_files:
                logger.info("No result files to commit")
                return False

            # Create detailed commit message
            now = datetime.now()
            message = f"Auto-update results - {now.strftime('%Y-%m-%d %H:%M')}\n\n"

            if sport_results:
                for result in sport_results:
                    if result['status'] == 'success':
                        message += f"- {result['sport'].upper()}: {result['rare_performances']} rare performances\n"

            message += f"\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\n"
            message += f"Co-Authored-By: Claude <noreply@anthropic.com>"

            return self.push_results(result_files, message, auto_rebase=True)

        except Exception as e:
            logger.error(f"Auto-commit failed: {e}")
            return False

def push_results(files, message=None):
    """Convenience function for pushing results"""
    pusher = GitPusher()
    return pusher.push_results(files, message)
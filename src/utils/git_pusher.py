"""Automated Git commits and pushes"""
from git import Repo
from datetime import datetime
from pathlib import Path
from loguru import logger

class GitPusher:
    def __init__(self, repo_path='.'):
        self.repo = Repo(repo_path)

    def push_results(self, files, message=None):
        """Commit and push result files"""
        try:
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
            self.repo.index.commit(message)
            logger.info(f"Committed: {message}")

            # Push to remote
            origin = self.repo.remote(name='origin')
            origin.push()
            logger.success("Pushed to GitHub")

            return True

        except Exception as e:
            logger.error(f"Git push failed: {e}")
            return False

def push_results(files, message=None):
    """Convenience function for pushing results"""
    pusher = GitPusher()
    return pusher.push_results(files, message)
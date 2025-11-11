"""
Data Synchronization Module
Syncs data from GitHub repository to local machine
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent


def run_git_command(command, cwd=None):
    """
    Run a git command and return output

    Args:
        command: Git command as list of strings
        cwd: Working directory (defaults to BASE_DIR)

    Returns:
        Tuple of (success: bool, output: str, error: str)
    """
    if cwd is None:
        cwd = BASE_DIR

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )

        return (
            result.returncode == 0,
            result.stdout.strip(),
            result.stderr.strip()
        )

    except subprocess.TimeoutExpired:
        return False, "", "Git command timed out"
    except Exception as e:
        return False, "", str(e)


def is_git_repository():
    """Check if current directory is a git repository"""
    success, _, _ = run_git_command(['git', 'rev-parse', '--git-dir'])
    return success


def has_remote():
    """Check if git repository has a remote configured"""
    success, output, _ = run_git_command(['git', 'remote', '-v'])
    return success and len(output) > 0


def get_remote_name():
    """Get the name of the primary remote (usually 'origin')"""
    success, output, _ = run_git_command(['git', 'remote'])
    if success and output:
        remotes = output.split('\n')
        return remotes[0] if remotes else 'origin'
    return 'origin'


def check_for_changes():
    """Check if there are uncommitted local changes"""
    success, output, _ = run_git_command(['git', 'status', '--porcelain'])
    return success and len(output) > 0


def sync_from_github():
    """
    Synchronize data from GitHub repository

    Returns:
        bool: True if sync successful, False otherwise
    """
    logger.info("Starting data synchronization...")

    # Check if this is a git repository
    if not is_git_repository():
        logger.warning("Not a git repository. Skipping sync.")
        logger.info("To enable sync, initialize git and connect to GitHub:")
        logger.info("  1. git init")
        logger.info("  2. git remote add origin <your-repo-url>")
        logger.info("  3. git pull origin main")
        return False

    # Check if remote is configured
    if not has_remote():
        logger.warning("No git remote configured. Skipping sync.")
        logger.info("Add a remote with: git remote add origin <your-repo-url>")
        return False

    # Check for local uncommitted changes
    if check_for_changes():
        logger.warning("Local changes detected. Stashing before pull...")
        success, _, error = run_git_command(['git', 'stash'])
        if not success:
            logger.error(f"Failed to stash changes: {error}")
            return False

    # Get remote name
    remote = get_remote_name()

    # Fetch latest changes
    logger.info(f"Fetching from {remote}...")
    success, output, error = run_git_command(['git', 'fetch', remote])
    if not success:
        logger.error(f"Failed to fetch: {error}")
        return False

    # Check if we're behind
    success, output, _ = run_git_command([
        'git', 'rev-list', '--count', 'HEAD..@{u}'
    ])

    if success and output and int(output) > 0:
        commits_behind = int(output)
        logger.info(f"Local repository is {commits_behind} commit(s) behind remote")

        # Pull changes
        logger.info("Pulling latest data...")
        success, output, error = run_git_command(['git', 'pull', remote, 'main'])

        if not success:
            # Try alternative branch names
            logger.info("Trying 'master' branch...")
            success, output, error = run_git_command(['git', 'pull', remote, 'master'])

        if not success:
            logger.error(f"Failed to pull: {error}")
            return False

        logger.info("✓ Data synchronized successfully!")
        if output:
            logger.debug(f"Pull output: {output}")

        return True
    else:
        logger.info("✓ Local data is already up to date")
        return True


def get_last_sync_time():
    """
    Get the timestamp of the last sync (last commit)

    Returns:
        str: Formatted timestamp or None
    """
    success, output, _ = run_git_command([
        'git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d %H:%M:%S'
    ])

    if success and output:
        return output
    return None


def get_sync_status():
    """
    Get detailed sync status

    Returns:
        dict: Status information
    """
    status = {
        'is_git_repo': is_git_repository(),
        'has_remote': False,
        'last_sync': None,
        'commits_behind': 0,
        'local_changes': False
    }

    if not status['is_git_repo']:
        return status

    status['has_remote'] = has_remote()

    if status['has_remote']:
        # Get last sync time
        status['last_sync'] = get_last_sync_time()

        # Check commits behind
        success, output, _ = run_git_command([
            'git', 'rev-list', '--count', 'HEAD..@{u}'
        ])
        if success and output:
            status['commits_behind'] = int(output)

        # Check for local changes
        status['local_changes'] = check_for_changes()

    return status


if __name__ == "__main__":
    """Test sync functionality"""
    print("Testing data synchronization...")
    print("-" * 60)

    # Get status
    status = get_sync_status()
    print(f"Git repository: {status['is_git_repo']}")
    print(f"Has remote: {status['has_remote']}")
    print(f"Last sync: {status['last_sync']}")
    print(f"Commits behind: {status['commits_behind']}")
    print(f"Local changes: {status['local_changes']}")

    print("-" * 60)

    # Try to sync
    if status['is_git_repo'] and status['has_remote']:
        success = sync_from_github()
        print(f"\nSync {'successful' if success else 'failed'}!")
    else:
        print("\nSync not available - repository not configured")

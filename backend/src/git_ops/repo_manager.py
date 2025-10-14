import hashlib
import shutil
from pathlib import Path

from git import Repo


class RepoManager:
    def __init__(self, temp_dir: str):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)

    def clone_and_setup_repo(
        self, repo_url: str, pr_number: int, head_branch: str, base_branch: str
    ):
        repo_hash = hashlib.sha1(repo_url.encode(), usedforsecurity=False).hexdigest()[:8]
        pr_dir = self.temp_dir / f"{repo_hash}_pr_{pr_number}"
        if pr_dir.exists():
            try:
                repo = Repo(pr_dir)
                origin = repo.remote("origin")
                if origin.url != repo_url:
                    print(f"Different repository URL: {pr_dir}")
                    return None
                origin.fetch(base_branch)
                origin.fetch(head_branch)
                repo.git.checkout("-B", head_branch, f"origin/{head_branch}")
                return pr_dir
            except Exception as e:
                print(f"Failed to update existing repo: {e}")
                if pr_dir.exists():
                    shutil.rmtree(pr_dir)

        repo = Repo.clone_from(repo_url, pr_dir, branch=base_branch)
        origin = repo.remote("origin")
        origin.fetch(head_branch)
        repo.git.checkout("-B", head_branch, f"origin/{head_branch}")
        return pr_dir

    def get_diff(self, repo_path, base_branch: str, head_branch: str):
        # Ensure repo_path is a Path object
        if not isinstance(repo_path, Path):
            repo_path = Path(repo_path)

        repo = Repo(repo_path)
        diff = repo.git.diff(f"origin/{base_branch}...origin/{head_branch }")
        diff_files = repo.git.diff(
            f"origin/{base_branch}...origin/{head_branch}", name_only=True
        ).split("\n")

        # Normalize file paths to match actual repository structure
        normalized_files = []
        for file_path in diff_files:
            if not file_path:
                continue

            # Check if the file exists at the given path
            full_path = repo_path / file_path
            if full_path.exists():
                normalized_files.append(file_path)
            else:
                # Try to find the file by removing common prefixes
                # This handles cases where git diff returns paths like 'backend/src/file.py'
                # but the cloned repo structure is just 'src/file.py'
                possible_path = file_path
                while "/" in possible_path:
                    # Remove the first directory component and try again
                    possible_path = possible_path.split("/", 1)[1]
                    if (repo_path / possible_path).exists():
                        normalized_files.append(possible_path)
                        break
                else:
                    # If we can't find the file, keep the original path for error reporting
                    normalized_files.append(file_path)

        return {"full_diff": diff, "diff_files": normalized_files}

    def get_file_content(self, repo_path: Path, branch: str, file_path: str):
        repo = Repo(repo_path)
        return repo.git.show(f"origin/{branch}:{file_path}")

    def clean_up(self, repo_path):
        """Clean up cloned repository directory"""
        if not isinstance(repo_path, Path):
            repo_path = Path(repo_path)

        if repo_path.exists():
            shutil.rmtree(repo_path)


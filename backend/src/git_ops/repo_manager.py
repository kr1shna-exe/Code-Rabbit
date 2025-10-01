import os, shutil
from pathlib import Path
from git import Repo
from typing import Dict,List

class RepoManager:
    def __init__(self, temp_dir: str):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)

    def clone_and_setup_repo(self, repo_url: str, pr_number: int, head_branch: str, base_branch: str):
        pr_dir = self.temp_dir / f"pr_{pr_number}"
        print(f"Cloning the main branch..")
        repo = Repo.clone_from(repo_url, pr_dir, branch=base_branch)
        print(f"Fetching {head_branch}..")
        origin = repo.remote('origin')
        origin.fetch(head_branch)
        repo.git.checkout(f"origin/{head_branch}")
        return pr_dir

    def get_diff(self, repo_path: Path, base_branch: str, head_branch: str):
        repo = Repo(repo_path)
        diff = repo.git.diff(f"origin/{base_branch}...origin/{head_branch }")
        diff_files = repo.git.diff(f"origin/{base_branch}...origin/{head_branch}", name_only=True).split('\n')
        return {
            "full_diff": diff,
            "diff_files": [f for f in diff_files if f]
        }

    def get_file_content(self, repo_path: Path, branch: str, file_path: str):
        repo = Repo(repo_path)
        return repo.git.show(f"origin/{branch}:{file_path}")

    def clean_up(self, repo_path: str):
        if repo_path.exists():
            shutil.rmtree(repo_path)
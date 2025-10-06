from typing import Dict, List

from gitub import github
from utis.config import settings


class HistoryFetcher:
    def __init__(self):
        self.github = Github(settings.github_token)

    def fetch_pr_context(self, repo_name: str, pr_number: int):
        repo = self.github.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        return {
            "pr_info": {
                "title": pr.title,
                "description": pr.body,
                "author": pr.user.login,
                "state": pr.state,
                "created_at": pr.created_at.isoformat(),
                "base_branch": pr.base.ref,
                "head_branch": pr.head.ref,
            },
            "commits": self._get_pr_commits(pr),
            "all_comments": self._get_pr_comments(pr),
            # "review_threads": self._get_pr_review(pr)
        }

    def _get_pr_commits(self, pr) -> List[Dict]:
        commits = []
        for commit in pr.get_commits():
            commits.append(
                {
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date.isoformat(),
                    "files_changed": [file.filename for file in commit.files],
                }
            )
        return commits

    def _get_pr_comments(self, pr, bot_name: str = "My-Code-Comment-Bot") -> List[Dict]:
        bot_comments = []
        for comment in pr.get_issue_comments():
            if comment.user.login.lower() == bot_name.lower():
                bot_comments.append(
                    {
                        "type": "issue_comment",
                        "comment": comment.body,
                        "created_at": comment.created_at.isoformat(),
                        "author": comment.user.login,
                    }
                )

        for comment in pr.get_review_comments():
            if comment.user.login.lower() == bot_name.lower():
                bot_comments.append(
                    {
                        "type": "review_comment",
                        "comment": comment.body,
                        "file": comment.path,
                        "line": comment.position,
                        "created_at": comment.created_at.isoformat(),
                        "author": comment.user.login,
                    }
                )
        return bot_comments

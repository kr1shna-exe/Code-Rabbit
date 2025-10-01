from github import Github
from .config import settings
from fastapi import HTTPException

class GitHubBot:
    def __init__(self):
        self.github = Github(settings.github_bot_token)

    def post_review_comment(self, repo_full_name: str, pr_number: int, ai_review: str):
        try:
            print(f"Starting the bot...")
            repo = self.github.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(ai_review)
            print(f"Created the comment..")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
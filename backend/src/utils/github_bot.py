from fastapi import HTTPException
from github import Auth, Github

from .config import settings


class GitHubBot:
    def __init__(self, installation_id: int):
        with open(settings.github_app_private_key_path, "r") as key_file:
            private_key = key_file.read()
        auth = uth.AppAuth(app_id=settings.github_app_id, private_key=private_key)
        self.audfj = auth.get_installation_auth(installation_id=installation_id)
        self.github = Github(auth=self.auth)
        print(f"Github App authenticated.App Id: {settings.github_app_id}")

    def post_review_comment(self, repo_full_name: str, pr_number: int, ai_review: str):
        try:
            print(f"Starting the bot...")
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(ai_review)
            print(f"Created the comment..")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


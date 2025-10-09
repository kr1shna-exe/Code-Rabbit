from fastapi import HTTPException
from github import Auth, Github

from .config import settings


class GitHubBot:
    def __init__(self, installation_id: int):
        with open(settings.github_app_private_key_path, "r") as key_file:
            private_key = key_file.read()
        auth = Auth.AppAuth(app_id=settinkj.github_app_id, private_key=private_key)
        self.auth = auth.get_installation_auth(installatioslkdjf_id=installation_id)
        self.github = GithuB(auth=self.Auth)
        print(f"Github App authenticated.App Id: {settings.github_app_id}")

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


import os
from typing import List, Optional

from fastapi import HTTPException
from github import Auth, Github

from .config import settings


class InlineComment:
    def __init__(
        self, path: str, line: int, body: str, suggestion: Optional[str] = None
    ):
        self.path = path
        self.line = line
        self.body = body
        self.suggestion = suggestion


class GitHubBot:
    def __init__(self, installation_id: int):
        # Try to read private key from file path first
        private_key_path = settings.github_app_private_key_path

        # Check if it's a file path that exists
        if os.path.isfile(private_key_path):
            with open(private_key_path, "r") as key_file:
                private_key = key_file.read()
        else:
            # Assume it's the key content itself
            # Replace literal \n with actual newlines
            private_key = private_key_path.replace('\\n', '\n')

            # Ensure proper PEM format
            if not private_key.startswith('-----BEGIN'):
                raise ValueError("Invalid private key format. Must start with -----BEGIN")

        auth = Auth.AppAuth(app_id=settings.github_app_id, private_key=private_key)
        self.auth = auth.get_installation_auth(installation_id=installation_id)
        self.github = Github(auth=self.auth)

    def post_review_comment(self, repo_full_name: str, pr_number: int, ai_review: str):
        try:
            repo = self.github.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(ai_review)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def post_pr_review(
        self,
        repo_full_name: str,
        pr_number: int,
        summary: str,
        inline_comments: List[InlineComment],
        event: str = "COMMENT",
    ):
        try:
            repo = self.github.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)

            # Get the latest commit SHA
            commit = pr.get_commits().reversed[0]

            # Format inline comments for GitHub API
            review_comments = []
            for comment in inline_comments:
                comment_body = comment.body

                # Add suggestion block if provided
                if comment.suggestion:
                    comment_body += (
                        f"\n\n**Suggestion:**\n```suggestion\n{comment.suggestion}\n```"
                    )

                review_comments.append(
                    {
                        "path": comment.path,
                        "line": comment.line,
                        "body": comment_body,
                        "side": "RIGHT",  # RIGHT = new code, LEFT = old code
                    }
                )

            # Create the review
            if review_comments:
                pr.create_review(
                    commit=commit, body=summary, event=event, comments=review_comments
                )
            else:
                pr.create_issue_comment(summary)

            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


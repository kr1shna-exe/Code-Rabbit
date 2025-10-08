import hashlib
import hmac
import json
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from ai.code_reviewer import review_code
from services.enhanced_context_builder import EnhancedContextBuilder
from services.history_fetcher import HistoryFetcher
from utils.config import settings
from utils.github_bot import GitHubBot

router = APIRouter()
repo_manager = RepoManager(settings.temp_repo_dir)


def verify_signature(payload: Any, signature: str):
    mac = hmac.new(
        settings.github_webhook_secret.encode(), msg=payload, digestmod=hashlib.sha256
    )
    return hmac.compare_digest(f"sha256={mac.hexdigest()}", signature)


@router.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    x_github_event: Optional[str] = Header(None, alias="X-GitHub-Event"),
):
    payload = await request.body()
    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    payload = json.loads(payload.decode("utf-8"))
    if x_github_event != "pull_request":
        return {"status": "skipped", "event": x_github_event}
    action = payload.get("action", "")
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    installation_id = payload.get("installation", {}).get("id")
    pr_number = pr.get("number")
    pr_title = pr.get("title", "")
    repo_url = repo.get("clone_url", "")
    repo_full_name = repo.get("full_name", "")
    base_branch = pr.get("base", {}).get("ref", "main")
    head_branch = pr.get("head", {}).get("ref", "")
    print(f"Action: {action}")
    print(f"PR: {pr_number}: {pr_title}")
    print(f"Base branch: {base_branch}, Head branch: {head_branch}")
    print(f"Repo: {repo_url}")
    try:
        print("Cloning the repository and fetching branches..")
        repo_path = repo_manager.clone_and_setup_repo(
            repo_url=repo_url,
            pr_number=pr_number,
            head_branch=head_branch,
            base_branch=base_branch,
        )
        print(f"Repository cloned to: {repo_path}")
        print(f"Now getting diffs..")
        diff_data = repo_manager.get_diff(
            repo_path=repo_path, base_branch=base_branch, head_branch=head_branch
        )
        print(f"Diff generated successfully: {diff_data}")
        print(f"Total files changed: {len(diff_data['diff_files'])}")

        # Log raw diff data for inspection
        print("=" * 50)
        print("RAW DIFF DATA FETCHED:")
        print("=" * 50)
        print(f"PR Title: {diff_data.get('pr_title', 'N/A')}")
        print(f"PR Description: {diff_data.get('pr_description', 'N/A')[:100]}...")
        print(f"Full diff length: {len(diff_data.get('full_diff', '')):,} characters")
        print(f"Changed files: {diff_data.get('diff_files', [])}")
        print("=" * 50)
        # Fetch PR history first
        print("Fetching PR history...")
        history_fetcher = HistoryFetcher()
        pr_history = history_fetcher.fetch_pr_context(repo_full_name, pr_number)

        # Log raw PR history for inspection
        print("=" * 50)
        print("RAW PR HISTORY FETCHED:")
        print("=" * 50)
        print(f"Commits: {len(pr_history.get('commits', []))}")
        print(f"Comments: {len(pr_history.get('all_comments', []))}")
        print(
            "Sample commit:",
            pr_history.get("commits", [{}])[0] if pr_history.get("commits") else {},
        )
        print("=" * 50)

        print("Building enhanced AI context with AST parser...")

        # Add PR metadata to diff_data
        diff_data["pr_title"] = pr_title
        diff_data["pr_description"] = pr.get("body", "")

        # Initialize enhanced context builder
        context_builder = EnhancedContextBuilder()

        # Build comprehensive context (diff + history + AST analysis)
        comprehensive_context = context_builder.build_comprehensive_ai_context(
            diff_data=diff_data, pr_history=pr_history, repo_path=repo_path
        )

        print(
            f"Generated enhanced context length: {len(comprehensive_context)} characters"
        )

        # Save complete context to file for inspection
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        context_file = f"ai_context_{pr_number}_{timestamp}.md"

        with open(context_file, "w", encoding="utf-8") as f:
            f.write(comprehensive_context)
        print(f"Complete context saved to: {context_file}")

        # Log complete context for inspection (optional - comment out if too verbose)
        print("=" * 80)
        print("COMPLETE ENHANCED CONTEXT SENT TO AI:")
        print("=" * 80)
        print(comprehensive_context)
        print("=" * 80)
        print(f"Context length: {len(comprehensive_context):,} characters")
        print("=" * 80)

        print(f"Getting AI to review with enhanced context...")
        ai_review = review_code(
            diff=diff_data["full_diff"],
            pr_title=pr_title,
            context=comprehensive_context,
        )
        print(f"AI review completed: {ai_review}")
        github_bot = GitHubBot(installation_id=installation_id)
        print(f"Starting to send the ai review to the bot..: {installation_id}")
        comment = github_bot.post_review_comment(
            repo_full_name=repo_full_name, pr_number=pr_number, ai_review=ai_review
        )
        if comment:
            print(f"Successfully commented")
        else:
            print(f"Failed to comment")
        # print(f"Now cleaning up..")
        # repo_manager.clean_up(repo_path)
        # print("Completed cleanup")
        return {
            "status": "success",
            "prn_number": pr_number,
            "files_changed": len(diff_data["diff_files"]),
            "changed_files": diff_data["diff_files"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


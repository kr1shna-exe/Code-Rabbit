import hashlib
import hmac
import json
from typing import Any, Dict, Optional, cast

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from utils.github_bot import InlineComment
from ai.multi_agent_reviewer import review_code_with_multi_agents
from db.vector_indexer import VectorIndexer
from git_ops.repo_manager import RepoManager
from services.history_fetcher import HistoryFetcher
from services.simple_ast_parser import SimpleASTParser
from services.simple_context_builder import SimpleContextBuilder
from services.simple_semantics import build_simple_graph
from utils.config import settings
from utils.github_bot import GitHubBot

router = APIRouter()
repo_manager = RepoManager(settings.temp_repo_dir)


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "code-rabbit"}


@router.get("/github-app-info")
async def get_github_app_info():
    return {
        "installation_url": f"https://github.com/apps/{settings.github_app_slug}/installations/new",
        "app_slug": settings.github_app_slug,
    }


def get_vector_indexer(request: Request) -> VectorIndexer:
    return request.app.state.vector_indexer


def verify_signature(payload: Any, signature: Optional[str]):
    if signature is None:
        return False
    mac = hmac.new(
        settings.github_webhook_secret.encode(), msg=payload, digestmod=hashlib.sha256
    )
    return hmac.compare_digest(f"sha256={mac.hexdigest()}", signature)


async def process_webhook_background(
    payload: Dict[str, Any],
    vector_indexer: VectorIndexer,
):
    """Process webhook in background to avoid timeout"""
    try:
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})
        installation_id = payload.get("installation", {}).get("id")
        pr_number = pr.get("number")
        pr_title = pr.get("title", "")
        repo_url = repo.get("clone_url", "")
        repo_full_name = repo.get("full_name", "")
        base_branch = pr.get("base", {}).get("ref", "main")
        head_branch = pr.get("head", {}).get("ref", "")

        repo_path = repo_manager.clone_and_setup_repo(
            repo_url=repo_url,
            pr_number=pr_number,
            head_branch=head_branch,
            base_branch=base_branch,
        )

        diff_data = repo_manager.get_diff(
            repo_path=repo_path, base_branch=base_branch, head_branch=head_branch
        )

        parser = SimpleASTParser(language="python")
        for file_path in diff_data.get("diff_files", []):
            if file_path.endswith(".py"):
                try:
                    full_path = f"{repo_path}/{file_path}"

                    with open(full_path, "r", encoding="utf-8") as f:
                        source_code = f.read()

                    tree = parser.parse_file(full_path)

                    graph = build_simple_graph(
                        tree[0], source_code, "python", file_path
                    )
                    vector_indexer.index_code_graph(
                        file_path=file_path,
                        graph=graph,
                    )

                    imports = parser.extract_imports(tree[0], source_code)
                    vector_indexer.index_import_file(
                        file_path=file_path,
                        source_code=source_code,
                        imports=imports,
                    )

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    continue

        try:
            history_fetcher = HistoryFetcher()
            pr_history = history_fetcher.fetch_pr_context(repo_full_name, pr_number)
        except Exception as e:
            print(f"Error fetching PR history: {e}")
            # Create minimal PR history to continue processing
            pr_history = {
                "pr_info": {
                    "title": pr.get("title", "Unknown"),
                    "description": pr.get("body", ""),
                    "author": pr.get("user", {}).get("login", "Unknown"),
                    "state": pr.get("state", "Unknown"),
                    "created_at": pr.get("created_at", ""),
                    "base_branch": pr.get("base", {}).get("ref", "main"),
                    "head_branch": pr.get("head", {}).get("ref", "feature"),
                },
                "commits": [],
                "all_comments": [],
                "maintainers": [],
                "error": str(e),
            }

        diff_data["pr_title"] = pr_title
        diff_data["pr_description"] = pr.get("body", "")

        try:
            context_builder = SimpleContextBuilder()
            comprehensive_context = context_builder.build_comprehensive_context(
                diff_data=diff_data, pr_history=pr_history, repo_path=repo_path
            )
        except Exception as e:
            print(f"Context building failed: {str(e)}")
            return

        try:
            ai_review = await review_code_with_multi_agents(
                diff=diff_data["full_diff"],
                pr_title=pr_title,
                context=comprehensive_context,
                pr_data=payload,
                diff_data=diff_data,
            )
        except Exception as e:
            print(f"Error generating AI review: {e}")
            ai_review = f"Error generating review: {str(e)}"
        if pr_history.get("commits") and pr_history.get("all_comments"):
            try:
                if pr_history["commits"]:
                    commit = pr_history["commits"][0]

                    # Find bot comments and maintainer reviews, and their user feedback
                    review_comments = [
                        c
                        for c in pr_history["all_comments"]
                        if c.get("type") in ["bot_review", "maintainer_review"]
                    ]
                user_feedback = [
                    c
                    for c in pr_history["all_comments"]
                    if c.get("type") == "user_feedback"
                ]

                # Create learnings from different combinations of reviews and feedback
                bot_reviews = [
                    c for c in review_comments if c.get("type") == "bot_review"
                ]
                maintainer_reviews = [
                    c for c in review_comments if c.get("type") == "maintainer_review"
                ]

                # 1. Bot reviews with user feedback (replies)
                for bot_review in bot_reviews:
                    matching_feedback: Dict[str, Any] | None = None
                    bot_review_id = bot_review.get("comment_id")

                    # Find user feedback that replies to this bot review
                    for feedback in user_feedback:
                        if feedback.get("in_reply_to") == bot_review_id:
                            matching_feedback = feedback
                            break

                    # Index learning from bot review + user feedback
                    vector_indexer.index_learning(
                        commit=commit,
                        bot_comment=bot_review,
                        user_feedback=cast(Optional[Dict[str, Any]], matching_feedback),
                        code_context=comprehensive_context,
                    )

                for maintainer_review in maintainer_reviews:
                    # Finding the most recent bot review before the maintainer review
                    associated_bot_review = None
                    maintainer_time = maintainer_review.get("created_at", "")

                    for bot_review in bot_reviews:
                        bot_time = bot_review.get("created_at", "")
                        if bot_time < maintainer_time:
                            if (
                                associated_bot_review is None
                                or bot_time
                                > associated_bot_review.get("created_at", "")
                            ):
                                associated_bot_review = bot_review

                    learning_comment = maintainer_review
                    if associated_bot_review:
                        combined_context = f"Bot Review: {associated_bot_review.get('comment', '')}\n\nMaintainer Feedback: {maintainer_review.get('comment', '')}"
                        learning_comment = {
                            **maintainer_review,
                            "comment": combined_context,
                            "type": "maintainer_review_with_bot_context",
                        }

                    vector_indexer.index_learning(
                        commit=commit,
                        bot_comment=learning_comment,
                        user_feedback=None,
                        code_context=comprehensive_context,
                    )
            except Exception as e:
                print(f"Error indexing learnings: {e}")

        try:
            github_bot = GitHubBot(installation_id=installation_id)

            if isinstance(ai_review, dict):
                summary = ai_review.get("summary", "")
                inline_comments_data = ai_review.get("inline_comments", [])
                total_issues = ai_review.get("total_issues", 0)

                if inline_comments_data:
                    inline_comments = [
                        InlineComment(
                            path=ic["path"],
                            line=ic["line"],
                            body=ic["body"],
                            suggestion=ic.get("suggestion"),
                        )
                        for ic in inline_comments_data
                    ]

                    event = "REQUEST_CHANGES" if total_issues > 0 else "COMMENT"

                    github_bot.post_pr_review(
                        repo_full_name=repo_full_name,
                        pr_number=pr_number,
                        summary=summary,
                        inline_comments=inline_comments,
                        event=event,
                    )
                else:
                    github_bot.post_review_comment(
                        repo_full_name=repo_full_name,
                        pr_number=pr_number,
                        ai_review=summary,
                    )
            else:
                github_bot.post_review_comment(
                    repo_full_name=repo_full_name,
                    pr_number=pr_number,
                    ai_review=ai_review,
                )

        except Exception as e:
            print(f"Error posting review to GitHub: {e}")

    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
    # finally:
          # Always cleanup the cloned repository
    #     try:
    #         if 'repo_path' in locals() and repo_path:
    #             repo_manager.clean_up(repo_path)
    #     except Exception as e:
    #         print(f"Error cleaning up repository: {e}")


@router.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    vector_indexer: VectorIndexer = Depends(get_vector_indexer),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    x_github_event: Optional[str] = Header(None, alias="X-GitHub-Event"),
):
    """
    GitHub webhook endpoint - returns immediately and processes in background
    """
    # Validate signature
    payload = await request.body()
    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    payload_dict = json.loads(payload.decode("utf-8"))

    # Only process pull_request events
    if x_github_event != "pull_request":
        return {"status": "skipped", "event": x_github_event}

    # Extract basic info for response
    pr_number = payload_dict.get("pull_request", {}).get("number")
    action = payload_dict.get("action", "")

    if action in ["closed"]:
        pr_dir = repo_manager.temp_dir / f"pr_{pr_number}"
        if pr_dir.exists():
            try:
                repo_manager.clean_up(pr_dir)
                print(f"Cleaned up repository for closed PR #{pr_number}")
                return {
                    "status": "cleaned_up",
                    "pr_number": pr_number,
                    "message": f"Repository cache deleted for PR #{pr_number}"
                }
            except Exception as e:
                print(f"Error cleaning up PR #{pr_number}: {e}")
                return {
                    "status": "cleanup_failed",
                    "pr_number": pr_number,
                    "error": str(e)
                }
        else:
            return {
                "status": "no_cleanup_needed",
                "pr_number": pr_number,
                "message": "No cached repository found"
            }
    # Queue background task
    if action in ["opened", "synchronize", "reopened"]:
        background_tasks.add_task(
            process_webhook_background,
            payload_dict,
            vector_indexer
        )
        
        return {
            "status": "accepted",
            "message": "Processing webhook in background",
            "pr_number": pr_number,
            "action": action
        }

    # Return immediately (before timeout)
    return {
        "status": "skipped",
        "message": action,
        "pr_number": pr_number,
        "action": f"Action '{action}' does not trigger review"
    }


from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Header
import hmac, hashlib, json
from typing import Any, Optional
from utils.config import settings
from git_ops.repo_manager import RepoManager


router = APIRouter()
repo_manager = RepoManager(settings.temp_repo_dir)

def verify_signature(payload: Any, signature: str):
    mac = hmac.new(
        settings.github_webhook_secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    )
    return hmac.compare_digest(
        f"sha256={mac.hexdigest()}",
        signature
    )

@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks, x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"), x_github_event: Optional[str] = Header(None, alias="X-GitHub-Event")):
    print(f"Webhook is triggered...")
    payload = await request.body()
    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    payload = json.loads(payload.decode('utf-8'))
    if x_github_event != "pull_request":
        return {"status": "skipped", "event": x_github_event}
    action = payload.get("action", "")
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    pr_number = pr.get("number")
    pr_title = pr.get("title", "")
    repo_url = repo.get("clone_url", "")
    base_branch = pr.get("base", {}).get("ref", "main")
    head_branch = pr.get("head", {}).get("ref", "")
    print(f"Action: {action}")
    print(f"PR: {pr_number}: {pr_title}")
    print(f"Base branch: {base_branch}, Head branch: {head_branch}")
    print(f"Repo: {repo_url}")
    try:
        print("Cloning the repository and fetching branches..")
        repo_path = repo_manager.clone_and_setup_repo(
            repo_url = repo_url,
            pr_number = pr_number,
            head_branch = head_branch,
            base_branch = base_branch
        )
        print(f"Repository cloned to: {repo_path}")
        print(f"Now getting diffs..")
        diff_data = repo_manager.get_diff(
            repo_path = repo_path,
            base_branch = base_branch,
            head_branch = head_branch
        )
        print(f"Diff generated successfully: {diff_data}")
        print(f"Total files changed: {len(diff_data['diff_files'])}")
        print(f"Now cleaning up..")
        repo_manager.clean_up(repo_path)
        print("Completed cleanup")
        return {
            "status": "success",
            "prn_number": pr_number,
            "files_changed": len(diff_data['diff_files']),
            "changed_files": diff_data['diff_files']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
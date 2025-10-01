from fastapi import FastAPI
from src.webhook.github_webhook import  as webhook_router
from src.utils.config import settings
import uvicorn

app = FastAPI(title="CodeRabbit Test")

app.include_router(webhook_router, prefix='/api')

if __name__ == "__main__":
    port = int(getattr(settings, 'port', 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
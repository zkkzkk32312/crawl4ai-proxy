import os
import logging
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List
import httpx

logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)

CRAWL4AI_URL = os.environ.get("CRAWL4AI_URL", "http://192.168.1.10:11235/md")
PROXY_API_KEY = os.environ.get("PROXY_API_KEY", "")

app = FastAPI()

class LoaderRequest(BaseModel):
    urls: List[str]

@app.post("/search")
async def search(req: LoaderRequest, authorization: str = Header(None)):
    if PROXY_API_KEY:
        expected = f"Bearer {PROXY_API_KEY}"
        if authorization != expected:
            raise HTTPException(status_code=401, detail="Invalid API key")

    results = []
    for url in req.urls:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    CRAWL4AI_URL,
                    json={"url": url, "filter": "fit"},
                )
                resp.raise_for_status()
                data = resp.json()
                content = data.get("markdown", "")
                logger.info(f"Fetched {url}: {len(content)} chars")
                results.append({
                    "page_content": content,
                    "metadata": {"source": url},
                })
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            results.append({
                "page_content": f"Error fetching {url}: {str(e)}",
                "metadata": {"source": url},
            })
    return results

@app.get("/health")
async def health():
    return {"status": "ok"}

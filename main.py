import os
import asyncio
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

async def fetch_url(url: str, client: httpx.AsyncClient) -> dict:
    try:
        resp = await client.post(
            CRAWL4AI_URL,
            json={"url": url, "filter": "fit"},
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("markdown", "")
        logger.info(f"Fetched {url}: {len(content)} chars")
        return {
            "page_content": content,
            "metadata": {"source": url},
        }
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return {
            "page_content": f"Error fetching {url}: {str(e)}",
            "metadata": {"source": url},
        }

@app.post("/search")
async def search(req: LoaderRequest, authorization: str = Header(None)):
    if PROXY_API_KEY:
        expected = f"Bearer {PROXY_API_KEY}"
        if authorization != expected:
            raise HTTPException(status_code=401, detail="Invalid API key")

    async with httpx.AsyncClient(timeout=60) as client:
        tasks = [fetch_url(url, client) for url in req.urls]
        results = await asyncio.gather(*tasks)
    return list(results)

@app.get("/health")
async def health():
    return {"status": "ok"}

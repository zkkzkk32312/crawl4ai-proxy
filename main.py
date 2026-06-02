import os
import sys
import asyncio
import logging
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List
import httpx

# Use StreamHandler with stderr + force flush so logs appear in docker logs
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("main")

CRAWL4AI_URL = os.environ.get("CRAWL4AI_URL", "http://192.168.1.10:11235/md")
PROXY_API_KEY = os.environ.get("PROXY_API_KEY", "")

app = FastAPI()

class LoaderRequest(BaseModel):
    urls: List[str]

async def fetch_url(url: str, client: httpx.AsyncClient) -> dict:
    try:
        # Try filter=fit first (strips nav, ads, sign-in prompts)
        resp = await client.post(
            CRAWL4AI_URL,
            json={"url": url, "filter": "fit"},
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("markdown", "")

        # Fallback: if filter=fit stripped too much, retry without filter
        if len(content) < 100:
            logger.info(f"Fallback: {url} returned only {len(content)} chars with filter=fit, retrying raw")
            resp = await client.post(
                CRAWL4AI_URL,
                json={"url": url},
            )
            resp.raise_for_status()
            data = resp.json()
            content = data.get("markdown", "")
            logger.info(f"Fallback fetched {url}: {len(content)} chars")
        else:
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

    logger.info(f"Received {len(req.urls)} URLs to fetch")
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = [fetch_url(url, client) for url in req.urls]
        results = await asyncio.gather(*tasks)
    success = sum(1 for r in results if not r["page_content"].startswith("Error"))
    logger.info(f"Done: {success}/{len(req.urls)} successful")
    return list(results)

@app.get("/health")
async def health():
    return {"status": "ok"}

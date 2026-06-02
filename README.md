# Crawl4AI Proxy for Open WebUI

A lightweight proxy that bridges Open WebUI's external web loader API to [Crawl4AI](https://github.com/unclecode/crawl4ai), enabling high-quality page content fetching for AI chat sessions.

## Why?

Open WebUI's default web loader struggles with JavaScript-heavy pages and bot detection. This proxy uses Crawl4AI's headless browser to fetch clean markdown content from any URL, dramatically improving the quality of web-search-enhanced AI responses.

## Architecture

```
Open WebUI → Crawl4AI Proxy (content fetch) → Crawl4AI (markdown extraction)
```

1. **Open WebUI** sends URLs to this **proxy** as the external web loader
2. The proxy calls **Crawl4AI** `/md` endpoint with `filter=fit` to extract clean content (strips navigation, ads, sign-in prompts). If the filtered result is too short (<100 chars), it retries without the filter as a fallback
3. Content is returned to Open WebUI and injected into the AI model's context

## Prerequisites

- **Crawl4AI** running (Docker or standalone) — [unclecode/crawl4ai](https://hub.docker.com/r/unclecode/crawl4ai)
- **Open WebUI** — [open-webui/open-webui](https://github.com/open-webui/open-webui)

## Quick Deploy (Docker)

```bash
docker run -d --name crawl4ai-proxy -p 8087:8087 -e CRAWL4AI_URL=http://<your-crawl4ai-ip>:11235/md zkkzkk32312/crawl4ai-proxy
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAWL4AI_URL` | `http://192.168.1.10:11235/md` | Crawl4AI `/md` endpoint URL |
| `PROXY_API_KEY` | *(empty)* | Optional API key for Open WebUI authentication |

## Unraid Deployment

### Via Community Apps (recommended)

1. Go to **Apps** tab in Unraid
2. Search for **Crawl4AI Proxy**
3. Click **Install**
4. Configure the settings:
   - **Proxy Port** — host port (default `8087`)
   - **Crawl4AI URL** — your Crawl4AI `/md` endpoint
   - **Proxy API Key** — optional, leave empty to disable
5. Click **Apply**

### Manual

1. Copy `templates/crawl4ai-proxy.xml` to `/boot/config/plugins/dockerMan/templates-user/`
2. Go to **Docker → Add Container** in Unraid
3. Select **my-crawl4ai-proxy** template
4. Configure the settings and click **Apply**

## Open WebUI Configuration

1. Go to **Admin Panel → Web Loader**
2. Set **Web Loader Engine** to `external`
3. Set **External Web Loader URL** to: `http://<proxy-ip>:8087/search`
4. If you set `PROXY_API_KEY`, enter it in **External Web Loader API Key**

> **Note:** Make sure **Bypass Web Loader** is **OFF** in Admin Panel.

## API

### POST /search

Fetches page content for a batch of URLs **in parallel** (all URLs are fetched simultaneously via `asyncio.gather`).

**Request:**
```json
{
  "urls": ["https://example.com", "https://github.com/..."]
}
```

**Headers:**
```
Authorization: Bearer <api_key>   (if PROXY_API_KEY is set)
```

**Response:**
```json
[
  {
    "page_content": "# Page Title\n\nExtracted markdown content...",
    "metadata": { "source": "https://example.com" }
  }
]
```

### GET /health

Health check endpoint.

```json
{ "status": "ok" }
```

## License

MIT

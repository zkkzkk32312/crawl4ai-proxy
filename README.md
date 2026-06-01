# Crawl4AI Proxy for Open WebUI

A lightweight proxy that bridges Open WebUI's external web loader API to [Crawl4AI](https://github.com/unclecode/crawl4ai), enabling high-quality page content fetching for AI chat sessions.

## Why?

Open WebUI's default web loader struggles with JavaScript-heavy pages and bot detection. This proxy uses Crawl4AI's headless browser to fetch clean markdown content from any URL, dramatically improving the quality of web-search-enhanced AI responses.

## Architecture

```
Open WebUI → SearXNG (search) → Crawl4AI Proxy (content fetch) → Crawl4AI (markdown extraction)
```

1. **Open WebUI** sends search queries to **SearXNG**
2. SearXNG returns URLs matching the query
3. Open WebUI sends those URLs to this **proxy** as the external web loader
4. The proxy calls **Crawl4AI** `/md` endpoint with `filter=fit` to extract clean content
5. Content is returned to Open WebUI and injected into the AI model's context

## Prerequisites

- **Crawl4AI** running (Docker or standalone) — [unclecode/crawl4ai](https://hub.docker.com/r/unclecode/crawl4ai)
- **SearXNG** running — [searxng/searxng](https://github.com/searxng/searxng)
- **Open WebUI** — [open-webui/open-webui](https://github.com/open-webui/open-webui)

## Quick Deploy (Docker)

```bash
docker build -t openwebui-search-proxy .
docker run -d --name crawl4ai-proxy -p 8087:8087 -e CRAWL4AI_URL=http://<your-crawl4ai-ip>:11235/md openwebui-search-proxy
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAWL4AI_URL` | `http://192.168.1.10:11235/md` | Crawl4AI `/md` endpoint URL |
| `PROXY_API_KEY` | *(empty)* | Optional API key for Open WebUI authentication |

## Unraid Deployment

1. Copy `crawl4ai-proxy.xml` to `/boot/config/plugins/dockerMan/templates-user/`
2. Go to **Docker → Add Container** in Unraid
3. Select **my-crawl4ai-proxy** template
4. Configure the port and Crawl4AI URL
5. Click **Apply**

## Open WebUI Configuration

### Web Search (SearXNG)

1. Go to **Admin Panel → Web Search**
2. Set **SearXNG Query URL** to: `http://<searxng-ip>:8084/search?q=<query>&format=json`
3. Set **Search Result Count** to `5`

### External Web Loader

1. Go to **Admin Panel → Web Loader**
2. Set **Web Loader Engine** to `external`
3. Set **External Web Loader URL** to: `http://<proxy-ip>:8087/search`
4. If you set `PROXY_API_KEY`, enter it in **External Web Loader API Key**

> **Important:** Use `<query>` (angle brackets) not `{query}` for the SearXNG placeholder.

### Bypass Settings

Make sure both **Bypass Embedding and Retrieval** and **Bypass Web Loader** are **OFF**.

## API

### POST /search

Fetches page content for a batch of URLs.

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

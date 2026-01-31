# TinyFish API Status - January 31, 2026

## Issue
- TinyFish API endpoint changed from `api.tinyfish.io` to `tinyfish.ai`
- API structure appears to have changed - getting 405 (Method Not Allowed) errors
- All authentication methods tested (Bearer, X-API-Key, query param) return same error

## What I Fixed
1. Updated endpoint from `https://api.tinyfish.io/v1` to `https://tinyfish.ai/v1`
2. Added detection warning to the scrape script
3. Created `scrape-fallback` script as temporary workaround

## Current Status
- TinyFish scraping is DOWN
- API key exists: `sk-mino-2j9F0LwwvKhtExPfyjk04OJJ7-fj_vRl`
- Service is reachable but rejecting all requests with 405

## Workarounds
For X/Twitter scraping:
- Use browser tool with Chrome extension attached
- Or use extract-intel / marketing-intel.sh (uses Nitter mirrors when available)

For Substack:
- marketing-intel.sh still works for public posts
- web_fetch tool in OpenClaw works well

## Next Steps
1. Check if TinyFish changed their API documentation
2. Verify if the API key is still valid
3. Contact TinyFish support if needed
4. Consider alternative scraping services

## Alternative Scrapers Available
- `marketing-intel.sh` - Works for Substack, attempts X via Nitter
- `extract-intel` - Quick extractor for various platforms
- `web_fetch` tool - OpenClaw's built-in fetcher
- Browser tool with Chrome extension - Most reliable for X/Twitter
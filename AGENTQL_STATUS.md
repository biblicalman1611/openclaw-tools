# AgentQL (formerly TinyFish) Status

## Current Situation (January 31, 2026)

### What We Know
1. **TinyFish rebranded to AgentQL** - complete API overhaul
2. **Old API key invalid** - `sk-mino-...` no longer works
3. **New API key obtained** - `2_u9FhKSUT...` from dev.agentql.com
4. **API structure unknown** - All endpoints return 404

### What Claude Code Said
According to Claude Code's analysis:
- Base URL should be AgentQL's API
- New authentication format needed
- Platform-specific query templates required
- Response format is `{data: {...}, metadata: {...}}`

### What's Missing
**Claude Code described the changes but didn't push the actual working code.**

The endpoints I tested all return 404:
- api.agentql.com/extract
- api.agentql.com/scrape
- api.agentql.com/query
- api.agentql.com/v1/*

### Next Steps
1. **Ask Claude Code to push the actual fix** - They analyzed it but didn't commit
2. **Check AgentQL documentation** - Need correct endpoint structure
3. **Contact AgentQL support** if needed

### Temporary Workaround
For now, use alternative scrapers:
- `marketing-intel.sh` - Works for Substack
- Browser tool with Chrome extension - Best for X/Twitter
- `web_fetch` tool in OpenClaw - Generic web pages
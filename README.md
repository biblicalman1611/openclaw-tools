# OpenClaw Tools & Scripts

This repository contains various tools and scripts for OpenClaw automation, specifically tailored for Biblical Man's content creation and marketing intelligence gathering.

## Quick Start

These are the main tools available:

### Content Intelligence
- `marketing-intel.sh` - Extract and analyze Substack articles with marketing insights
- `x-substack-intel.sh` - Combined X and Substack intelligence extractor
- `extract-intel` - Quick extractor for various platforms

### Scraping Tools
- `scrape` - TinyFish API scraper (currently broken - API changed)
- `scrape-fallback` - Fallback scraper when TinyFish fails
- `tinyfish-scraper.py` - Python implementation of TinyFish scraper
- `tinyfish-intel.sh` - TinyFish setup and batch processing

### Content Pipeline
- `content_pipeline.py` - Automated content processing
- `biblical_caine.py` - Biblical Man content style analyzer
- `youtube-transcript.sh` - YouTube transcript fetcher

### Utilities
- `intel_extractor.py` - Core intelligence extraction logic
- `intel-report.sh` - Generate reports from gathered intel

## Setup

Most scripts are ready to use. For first time setup:

```bash
# Make scripts executable
chmod +x *.sh

# Install Python dependencies if needed
pip3 install requests beautifulsoup4 python-dotenv
```

## Known Issues

### TinyFish API (January 2026)
The TinyFish API has moved from `api.tinyfish.io` to `tinyfish.ai` and changed their API structure. Currently returning 405 errors. Workarounds:
- Use `marketing-intel.sh` for Substack
- Use browser automation for X/Twitter
- Use OpenClaw's `web_fetch` tool

## Security Notes

This repo excludes:
- API keys and credentials
- Personal memory files
- Gathered intelligence data
- Session information

Always check scripts before running them in a new environment.

## Contributing

When fixing issues:
1. Test thoroughly first
2. Document what changed
3. Update relevant guides/docs
4. Consider backwards compatibility
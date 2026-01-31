# 🕵️ Biblical Man's Marketing Intelligence Tools

## Overview
Cloud-based tools to extract competitive intelligence from X posts and Substack articles when you're away from your Mac.

## Quick Start

### 1. Single URL Extraction
```bash
./marketing-intel.sh https://x.com/user/status/1234567890
```

### 2. Batch Processing
Create a file with URLs (one per line):
```bash
echo "https://x.com/competitor1/status/123
https://substack.com/@competitor2/p/article-title
https://x.com/competitor3/status/456" > urls.txt

./marketing-intel.sh batch urls.txt
```

### 3. Monitor Specific Competitors
```bash
./marketing-intel.sh monitor paul-maxwell
# Edit the created file, then run again to extract
```

### 4. Generate Intelligence Report
```bash
./marketing-intel.sh report
```

## What Gets Extracted

### From X Posts:
- Full tweet content
- Username and post ID
- Timestamp

### From Substack:
- Article title and content
- Author name
- Subscriber count
- Engagement metrics

### Marketing Analysis:
- **Emotional Density**: How many trigger words per 100 words
- **Power Word Density**: Conversion-driving language frequency
- **CTA Density**: How often they ask for action
- **Spiritual Density**: Religious language usage
- **Top Words**: Most frequently used terms
- **Marketing Formulas**: PAS, AIDA, Story-based, etc.

## Use Cases

### 1. Competitor Analysis
Track what's working for similar accounts:
```bash
# Create competitor list
echo "# Paul Maxwell URLs
https://x.com/paulcmaxwell/status/xxxxx
https://substack.com/@paulcmaxwell/p/xxxxx" > competitors/paul-maxwell.txt

# Extract all
./marketing-intel.sh batch competitors/paul-maxwell.txt
```

### 2. Trend Spotting
Extract multiple viral posts to find patterns:
```bash
# Save viral Christian masculinity posts
./marketing-intel.sh batch viral-posts.txt
./marketing-intel.sh report
```

### 3. Content Inspiration
When you need ideas:
```bash
# Extract top performing content
./marketing-intel.sh https://substack.com/@popularcreator/p/viral-post
# Check the emotional triggers and hooks used
```

### 4. Voice Analysis
Study how successful creators write:
```bash
# Extract multiple posts from one creator
./marketing-intel.sh batch creator-posts.txt
# Look at avg word length, sentence patterns
```

## Advanced Features

### Custom Analysis
The Python script tracks:
- Emotional triggers (27 pain words)
- Power words (17 conversion terms)
- CTAs (16 action words)  
- Biblical/spiritual terms (18 faith words)
- Sentiment scoring
- Hook extraction (first 3 sentences)

### Competitive Report
Running `./marketing-intel.sh report` creates a markdown file with:
- All extracted content
- Comparative metrics
- Top performing language
- Marketing formula detection

## Tips for Adam

1. **Build Swipe Files**: Create folders for different categories:
   ```
   intel/hooks/
   intel/email-subject-lines/
   intel/story-openers/
   intel/ctas/
   ```

2. **Track Competitors Weekly**:
   ```bash
   # Every Monday
   ./marketing-intel.sh monitor john-eldredge
   ./marketing-intel.sh monitor paul-maxwell
   ./marketing-intel.sh monitor mark-driscoll
   ```

3. **Viral Post Analysis**:
   When you see something blow up, immediately:
   ```bash
   ./marketing-intel.sh [viral-post-url]
   ```
   Check what emotional triggers they hit.

4. **A/B Test Ideas**:
   Extract similar posts with different performance:
   ```bash
   ./marketing-intel.sh batch ab-test-posts.txt
   ```
   Compare emotional density scores.

## Troubleshooting

### X Post Not Extracting?
- The tool uses Nitter instances which can be unstable
- Try again in a few minutes
- Or use the direct content for analysis

### Substack Behind Paywall?
- Only free content can be extracted
- Paywalled content will show preview only

### Need More Analysis?
The JSON files contain all data. You can:
```bash
cat intel/*.json | jq '.analysis.metrics'
```

## Storage

All intel is saved in:
```
~/.openclaw/workspace/intel/
```

Files are timestamped and include platform name:
- `x_intel_20260131_143022.json`
- `substack_intel_20260131_143156.json`

## Next Level

Want to add more platforms? The framework is extensible:
- LinkedIn posts
- Medium articles  
- YouTube comments
- Facebook posts

Just ask and I'll add the extractors.

---

Remember: This is competitive INTEL, not copying. Use it to understand what resonates, then create your own superior content with your unique voice and revelation.
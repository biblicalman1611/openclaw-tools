#!/usr/bin/env python3
"""
TinyFish Web Scraper - Biblical Man Edition
Scrape any website using TinyFish API
"""

import os
import sys
import json
import requests
from datetime import datetime
from urllib.parse import urlparse
import re
# Load API key
try:
    with open('.env.tinyfish', 'r') as f:
        for line in f:
            if line.startswith('TINYFISH_API_KEY='):
                API_KEY = line.split('=', 1)[1].strip()
                break
except:
    API_KEY = 'sk-mino-2j9F0LwwvKhtExPfyjk04OJJ7-fj_vRl'

class TinyFishScraper:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = "https://tinyfish.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def scrape_url(self, url, options=None):
        """Scrape any URL using TinyFish"""
        print(f"🐟 Scraping with TinyFish: {url}")
        
        # Default options
        default_options = {
            "url": url,
            "wait_for": "networkidle",
            "block_resources": ["image", "media", "font"],
            "extract_text": True,
            "extract_links": True,
            "screenshot": False
        }
        
        if options:
            default_options.update(options)
            
        try:
            # Try the scrape endpoint
            response = requests.post(
                f"{self.base_url}/scrape",
                headers=self.headers,
                json=default_options,
                timeout=30
            )
            
            if response.status_code == 200:
                return self.process_response(response.json(), url)
            else:
                # Fallback to simpler endpoint if available
                simple_response = requests.get(
                    f"{self.base_url}/extract",
                    headers=self.headers,
                    params={"url": url},
                    timeout=30
                )
                
                if simple_response.status_code == 200:
                    return self.process_response(simple_response.json(), url)
                else:
                    return {"error": f"API returned {response.status_code}: {response.text}"}
                    
        except Exception as e:
            return {"error": str(e)}
            
    def process_response(self, data, url):
        """Process TinyFish response into our format"""
        result = {
            "url": url,
            "platform": self.detect_platform(url),
            "extracted_at": datetime.now().isoformat(),
            "raw_data": data
        }
        
        # Extract content based on platform
        if "twitter.com" in url or "x.com" in url:
            result.update(self.process_twitter(data))
        elif "substack.com" in url:
            result.update(self.process_substack(data))
        elif "youtube.com" in url:
            result.update(self.process_youtube(data))
        else:
            result.update(self.process_generic(data))
            
        # Add marketing analysis
        if result.get("content"):
            result["analysis"] = self.analyze_content(result["content"])
            
        return result
        
    def detect_platform(self, url):
        """Detect the platform from URL"""
        domain = urlparse(url).netloc.lower()
        if "x.com" in domain or "twitter.com" in domain:
            return "X/Twitter"
        elif "substack.com" in domain:
            return "Substack"
        elif "youtube.com" in domain:
            return "YouTube"
        elif "linkedin.com" in domain:
            return "LinkedIn"
        else:
            return "Web"
            
    def process_twitter(self, data):
        """Extract Twitter/X specific content"""
        content = data.get("text", "") or data.get("content", "")
        
        # Try to extract tweet text
        tweet_patterns = [
            r'<div[^>]*data-testid="tweetText"[^>]*>(.*?)</div>',
            r'<span[^>]*class="[^"]*tweet-text[^"]*"[^>]*>(.*?)</span>',
            r'"full_text"\s*:\s*"([^"]+)"'
        ]
        
        for pattern in tweet_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                tweet_text = match.group(1)
                tweet_text = re.sub(r'<[^>]+>', '', tweet_text)
                return {
                    "content": tweet_text.strip(),
                    "type": "tweet"
                }
                
        return {"content": content[:1000], "type": "tweet"}
        
    def process_substack(self, data):
        """Extract Substack specific content"""
        content = data.get("text", "") or data.get("content", "")
        
        # Extract title
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        title = title_match.group(1) if title_match else "Unknown"
        
        # Extract main article
        article_patterns = [
            r'<div[^>]*class="[^"]*post-content[^"]*"[^>]*>(.*?)</div>',
            r'<article[^>]*>(.*?)</article>'
        ]
        
        article_content = ""
        for pattern in article_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                article_content = match.group(1)
                break
                
        # Clean HTML
        clean_content = re.sub(r'<[^>]+>', ' ', article_content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        return {
            "title": title,
            "content": clean_content[:5000],
            "type": "article"
        }
        
    def process_youtube(self, data):
        """Extract YouTube specific content"""
        content = data.get("text", "") or data.get("content", "")
        
        # Extract video title
        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', content)
        title = title_match.group(1) if title_match else "Unknown"
        
        # Extract description
        desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', content)
        description = desc_match.group(1) if desc_match else ""
        
        return {
            "title": title,
            "content": description,
            "type": "video",
            "note": "Use YouTube transcript scraper for full transcript"
        }
        
    def process_generic(self, data):
        """Process generic web content"""
        content = data.get("text", "") or data.get("content", "")
        
        # Remove scripts and styles
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # Extract title
        title_match = re.search(r'<title>([^<]+)</title>', content)
        title = title_match.group(1) if title_match else "Unknown"
        
        # Clean HTML
        clean_content = re.sub(r'<[^>]+>', ' ', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        return {
            "title": title,
            "content": clean_content[:5000],
            "type": "webpage"
        }
        
    def analyze_content(self, content):
        """Marketing analysis for Biblical Man"""
        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)
        
        # Biblical Man specific triggers
        pain_words = [
            'broken', 'shame', 'failed', 'struggle', 'wound', 'father',
            'marriage', 'porn', 'alone', 'empty', 'angry', 'lost'
        ]
        
        power_words = [
            'warrior', 'fight', 'stand', 'rise', 'conquer', 'victory',
            'brotherhood', 'legacy', 'covenant', 'kingdom'
        ]
        
        spiritual_words = [
            'god', 'jesus', 'faith', 'prayer', 'scripture', 'bible',
            'grace', 'salvation', 'worship', 'holy'
        ]
        
        # Count occurrences
        pain_count = sum(1 for word in words if word in pain_words)
        power_count = sum(1 for word in words if word in power_words)
        spiritual_count = sum(1 for word in words if word in spiritual_words)
        
        # Detect hooks
        first_sentence = content.split('.')[0] if '.' in content else content[:100]
        
        return {
            "metrics": {
                "word_count": len(words),
                "pain_density": (pain_count / len(words) * 100) if words else 0,
                "power_density": (power_count / len(words) * 100) if words else 0,
                "spiritual_density": (spiritual_count / len(words) * 100) if words else 0
            },
            "hook": first_sentence.strip(),
            "jake_triggers": [w for w in set(words) if w in pain_words],
            "marketing_angle": self.detect_angle(content)
        }
        
    def detect_angle(self, content):
        """Detect marketing angle"""
        angles = []
        
        if re.search(r'father|dad|son', content, re.I):
            angles.append("Father wound angle")
            
        if re.search(r'marriage|wife|divorce', content, re.I):
            angles.append("Marriage restoration")
            
        if re.search(r'porn|lust|addiction', content, re.I):
            angles.append("Sexual purity")
            
        if re.search(r'church|pastor|ministry', content, re.I):
            angles.append("Church wounds")
            
        return angles or ["Generic spiritual content"]
        
    def save_intel(self, data):
        """Save to intel folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        platform = data.get("platform", "unknown").lower().replace("/", "-")
        filename = f"tinyfish_{platform}_{timestamp}.json"
        
        os.makedirs("intel", exist_ok=True)
        filepath = os.path.join("intel", filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"💾 Saved to: {filepath}")
        
        # Also create markdown summary
        md_filename = filepath.replace('.json', '.md')
        with open(md_filename, 'w') as f:
            f.write(f"# {data.get('title', 'Intel Report')}\n\n")
            f.write(f"**URL:** {data.get('url')}\n")
            f.write(f"**Platform:** {data.get('platform')}\n")
            f.write(f"**Extracted:** {data.get('extracted_at')}\n\n")
            
            if 'analysis' in data:
                analysis = data['analysis']
                f.write("## Marketing Analysis\n\n")
                f.write(f"**Hook:** {analysis.get('hook')}\n")
                f.write(f"**Jake Triggers Found:** {', '.join(analysis.get('jake_triggers', []))}\n")
                f.write(f"**Marketing Angles:** {', '.join(analysis.get('marketing_angle', []))}\n\n")
                
                metrics = analysis.get('metrics', {})
                f.write("### Density Metrics\n")
                f.write(f"- Pain Density: {metrics.get('pain_density', 0):.1f}%\n")
                f.write(f"- Power Density: {metrics.get('power_density', 0):.1f}%\n")
                f.write(f"- Spiritual Density: {metrics.get('spiritual_density', 0):.1f}%\n\n")
                
            f.write("## Content\n\n")
            f.write(data.get('content', '')[:2000])
            
        print(f"📝 Summary at: {md_filename}")
        
def main():
    if len(sys.argv) < 2:
        print("TinyFish Web Scraper - Biblical Man Edition")
        print("\nUsage:")
        print("  python tinyfish-scraper.py <URL>")
        print("  python tinyfish-scraper.py batch <file>")
        print("\nSupported platforms:")
        print("  - X/Twitter")
        print("  - Substack")
        print("  - YouTube")
        print("  - Any website")
        print("\nExamples:")
        print("  python tinyfish-scraper.py https://x.com/user/status/123")
        print("  python tinyfish-scraper.py https://biblicalman.substack.com/p/article")
        return
        
    scraper = TinyFishScraper()
    
    if sys.argv[1] == "batch" and len(sys.argv) > 2:
        # Batch process
        with open(sys.argv[2], 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
            
        for url in urls:
            print(f"\nProcessing: {url}")
            result = scraper.scrape_url(url)
            
            if "error" not in result:
                scraper.save_intel(result)
                print("✅ Success")
            else:
                print(f"❌ Error: {result['error']}")
                
    else:
        # Single URL
        url = sys.argv[1]
        result = scraper.scrape_url(url)
        
        if "error" not in result:
            scraper.save_intel(result)
            
            # Print summary
            print("\n=== Intel Summary ===")
            print(f"Platform: {result.get('platform')}")
            print(f"Type: {result.get('type')}")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"\nHook: {analysis.get('hook')}")
                print(f"Jake Triggers: {', '.join(analysis.get('jake_triggers', []))}")
                print(f"Angles: {', '.join(analysis.get('marketing_angle', []))}")
        else:
            print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    main()
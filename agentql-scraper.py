#!/usr/bin/env python3
"""
AgentQL Web Scraper - Biblical Man Edition
Scrape any website using AgentQL API (formerly TinyFish)
"""

import os
import sys
import json
import requests
from datetime import datetime
from urllib.parse import urlparse
import re

# Load API key
API_KEY = None
# Check multiple locations for API key
for env_var in ['AGENTQL_API_KEY', 'TINYFISH_API_KEY']:
    if os.getenv(env_var):
        API_KEY = os.getenv(env_var)
        break

# Try loading from files
if not API_KEY:
    for filename in ['.env.agentql', '.env.tinyfish']:
        try:
            with open(filename, 'r') as f:
                for line in f:
                    if 'API_KEY=' in line:
                        API_KEY = line.split('=', 1)[1].strip()
                        break
        except:
            pass

if not API_KEY:
    print("❌ No API key found! Set AGENTQL_API_KEY environment variable")
    print("Get your key at: https://dev.agentql.com")
    sys.exit(1)

class AgentQLScraper:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = "https://api.agentql.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-AgentQL-API-Key": self.api_key  # Some endpoints may use this
        }
        
    def get_query_template(self, url):
        """Get platform-specific query template for AgentQL"""
        if "x.com" in url or "twitter.com" in url:
            return {
                "tweet": {
                    "author": "string",
                    "content": "string",
                    "timestamp": "string",
                    "likes": "number",
                    "retweets": "number",
                    "replies": "number"
                }
            }
        elif "substack.com" in url:
            return {
                "article": {
                    "title": "string",
                    "author": "string",
                    "content": "string[]",
                    "publishDate": "string",
                    "likes": "number",
                    "comments": "number"
                }
            }
        elif "youtube.com" in url:
            return {
                "video": {
                    "title": "string",
                    "channel": "string",
                    "description": "string",
                    "views": "string",
                    "likes": "string"
                }
            }
        else:
            # Generic web page
            return {
                "page": {
                    "title": "string",
                    "headings": "string[]",
                    "paragraphs": "string[]",
                    "links": {
                        "text": "string",
                        "href": "string"
                    }
                }
            }
        
    def scrape_url(self, url, options=None):
        """Scrape any URL using AgentQL"""
        print(f"🤖 Scraping with AgentQL: {url}")
        
        # Get platform-specific query
        query = self.get_query_template(url)
        
        # Build request payload
        payload = {
            "url": url,
            "query": query
        }
        
        # Add any custom options
        if options:
            payload.update(options)
            
        try:
            # Make request to AgentQL
            response = requests.post(
                f"{self.base_url}/extract",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return self.process_response(response.json(), url)
            else:
                # Try alternative endpoint
                alt_response = requests.post(
                    f"{self.base_url}/scrape",
                    headers=self.headers,
                    json={"targetUrl": url, "query": query},
                    timeout=30
                )
                
                if alt_response.status_code == 200:
                    return self.process_response(alt_response.json(), url)
                else:
                    return {"error": f"API returned {response.status_code}: {response.text}"}
                    
        except Exception as e:
            return {"error": str(e)}
            
    def process_response(self, response_data, url):
        """Process AgentQL response into our format"""
        result = {
            "url": url,
            "platform": self.detect_platform(url),
            "extracted_at": datetime.now().isoformat(),
            "raw_data": response_data
        }
        
        # Extract data based on AgentQL's response format
        if "data" in response_data:
            data = response_data["data"]
            
            # Platform-specific extraction
            if "twitter.com" in url or "x.com" in url:
                result.update(self.process_twitter_agentql(data))
            elif "substack.com" in url:
                result.update(self.process_substack_agentql(data))
            elif "youtube.com" in url:
                result.update(self.process_youtube_agentql(data))
            else:
                result.update(self.process_generic_agentql(data))
        
        # Add metadata if available
        if "metadata" in response_data:
            result["metadata"] = response_data["metadata"]
                
        # Add marketing analysis
        if result.get("content"):
            result["analysis"] = self.analyze_content(result["content"])
            
        return result
        
    def process_twitter_agentql(self, data):
        """Process Twitter/X data from AgentQL response"""
        result = {}
        
        if "tweet" in data:
            tweet = data["tweet"]
            result["author"] = tweet.get("author", "")
            result["content"] = tweet.get("content", "")
            result["timestamp"] = tweet.get("timestamp", "")
            result["engagement"] = {
                "likes": tweet.get("likes", 0),
                "retweets": tweet.get("retweets", 0),
                "replies": tweet.get("replies", 0)
            }
            
        return result
        
    def process_substack_agentql(self, data):
        """Process Substack data from AgentQL response"""
        result = {}
        
        if "article" in data:
            article = data["article"]
            result["title"] = article.get("title", "")
            result["author"] = article.get("author", "")
            
            # Join content array if it's a list
            content = article.get("content", [])
            if isinstance(content, list):
                result["content"] = "\n\n".join(content)
            else:
                result["content"] = content
                
            result["publish_date"] = article.get("publishDate", "")
            result["engagement"] = {
                "likes": article.get("likes", 0),
                "comments": article.get("comments", 0)
            }
            
        return result
        
    def process_youtube_agentql(self, data):
        """Process YouTube data from AgentQL response"""
        result = {}
        
        if "video" in data:
            video = data["video"]
            result["title"] = video.get("title", "")
            result["channel"] = video.get("channel", "")
            result["description"] = video.get("description", "")
            result["stats"] = {
                "views": video.get("views", ""),
                "likes": video.get("likes", "")
            }
            
        return result
        
    def process_generic_agentql(self, data):
        """Process generic web page from AgentQL response"""
        result = {}
        
        if "page" in data:
            page = data["page"]
            result["title"] = page.get("title", "")
            
            # Combine headings and paragraphs
            content_parts = []
            
            for heading in page.get("headings", []):
                content_parts.append(f"## {heading}")
                
            for para in page.get("paragraphs", []):
                content_parts.append(para)
                
            result["content"] = "\n\n".join(content_parts)
            
            # Extract links
            if "links" in page and isinstance(page["links"], list):
                result["links"] = [{"text": link.get("text", ""), 
                                   "href": link.get("href", "")} 
                                  for link in page["links"]]
                                  
        return result
    
    def detect_platform(self, url):
        """Detect which platform the URL is from"""
        domain = urlparse(url).netloc.lower()
        
        if "x.com" in domain or "twitter.com" in domain:
            return "X (Twitter)"
        elif "substack.com" in domain:
            return "Substack"
        elif "youtube.com" in domain or "youtu.be" in domain:
            return "YouTube"
        elif "linkedin.com" in domain:
            return "LinkedIn"
        else:
            return "Web"
            
    def analyze_content(self, content):
        """Analyze content for Jake triggers and marketing angles"""
        if not content:
            return {}
            
        content_lower = content.lower()
        word_count = len(content.split())
        
        # Jake trigger detection
        triggers = {
            "father_wound": ["father", "dad", "absent", "disappointed", "failed him", "never there", "old man"],
            "marriage_death": ["marriage", "divorce", "wife", "alone", "empty bed", "she left", "lonely"],
            "porn_struggle": ["porn", "lust", "addiction", "struggle", "temptation", "relapse", "shame"],
            "church_hurt": ["church", "pastor", "ministry", "fake", "hypocrite", "burned out", "lost faith"],
            "masculinity": ["man", "masculine", "weak", "strong", "warrior", "leader", "passive"],
            "grace": ["grace", "forgiven", "mercy", "second chance", "redemption", "worthy"]
        }
        
        found_triggers = []
        trigger_density = 0
        
        for trigger_type, keywords in triggers.items():
            count = sum(1 for keyword in keywords if keyword in content_lower)
            if count > 0:
                found_triggers.append({
                    "type": trigger_type,
                    "count": count,
                    "density": (count / word_count) * 100
                })
                trigger_density += count
                
        # Hook analysis
        first_line = content.split('\n')[0] if content else ""
        
        # Emotional density
        emotional_words = ["pain", "hurt", "broken", "lost", "angry", "alone", "empty", 
                          "shame", "guilt", "fear", "hate", "love", "hope", "peace"]
        emotional_count = sum(1 for word in emotional_words if word in content_lower)
        emotional_density = (emotional_count / word_count) * 100 if word_count > 0 else 0
        
        return {
            "triggers": found_triggers,
            "trigger_density": (trigger_density / word_count) * 100 if word_count > 0 else 0,
            "emotional_density": emotional_density,
            "hook": first_line[:100],
            "word_count": word_count,
            "viral_potential": "HIGH" if emotional_density > 5 or trigger_density > 3 else "MEDIUM" if emotional_density > 2 else "LOW"
        }
    
    def save_intel(self, data, platform=None):
        """Save extracted intelligence"""
        if not platform:
            platform = data.get("platform", "unknown").lower().replace(" ", "_").replace("(", "").replace(")", "")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create intel directory if it doesn't exist
        os.makedirs("intel", exist_ok=True)
        
        # Save JSON
        json_file = f"intel/agentql_{platform}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Save markdown summary
        md_file = f"intel/agentql_{platform}_{timestamp}.md"
        with open(md_file, 'w') as f:
            f.write(f"# Intelligence Report: {data.get('platform', 'Unknown')}\n\n")
            f.write(f"**URL:** {data.get('url', '')}\n")
            f.write(f"**Extracted:** {data.get('extracted_at', '')}\n\n")
            
            # Content
            if data.get('title'):
                f.write(f"## Title\n{data.get('title')}\n\n")
                
            if data.get('author'):
                f.write(f"**Author:** {data.get('author')}\n\n")
                
            if data.get('content'):
                f.write(f"## Content\n{data.get('content')[:1000]}{'...' if len(data.get('content', '')) > 1000 else ''}\n\n")
                
            # Analysis
            if data.get('analysis'):
                analysis = data['analysis']
                f.write("## Marketing Analysis\n")
                f.write(f"- **Word Count:** {analysis.get('word_count', 0)}\n")
                f.write(f"- **Emotional Density:** {analysis.get('emotional_density', 0):.1f}%\n")
                f.write(f"- **Trigger Density:** {analysis.get('trigger_density', 0):.1f}%\n")
                f.write(f"- **Viral Potential:** {analysis.get('viral_potential', 'UNKNOWN')}\n\n")
                
                if analysis.get('triggers'):
                    f.write("### Jake Triggers Found:\n")
                    for trigger in analysis['triggers']:
                        f.write(f"- **{trigger['type']}**: {trigger['count']} mentions ({trigger['density']:.1f}% density)\n")
                        
            # Engagement
            if data.get('engagement'):
                f.write("\n## Engagement Metrics\n")
                for metric, value in data['engagement'].items():
                    f.write(f"- **{metric.capitalize()}:** {value}\n")
                    
        print(f"✅ Intel saved:")
        print(f"   JSON: {json_file}")
        print(f"   Summary: {md_file}")
        
        return {"json": json_file, "markdown": md_file}

def main():
    if len(sys.argv) < 2:
        print("AgentQL Intelligence Extractor")
        print("Usage: agentql-scraper.py <URL>")
        print("       agentql-scraper.py batch <file.txt>")
        sys.exit(1)
        
    scraper = AgentQLScraper()
    
    if sys.argv[1] == "batch" and len(sys.argv) > 2:
        # Batch processing
        with open(sys.argv[2], 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
            
        print(f"🤖 Processing {len(urls)} URLs...")
        results = []
        
        for url in urls:
            result = scraper.scrape_url(url)
            if "error" not in result:
                saved = scraper.save_intel(result)
                results.append(saved)
            else:
                print(f"❌ Failed: {url} - {result['error']}")
                
        print(f"\n✅ Batch complete: {len(results)} successful")
        
    else:
        # Single URL
        url = sys.argv[1]
        result = scraper.scrape_url(url)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            # Display summary
            print(f"\n✅ Extraction successful!")
            print(f"Platform: {result.get('platform', 'Unknown')}")
            
            if result.get('title'):
                print(f"Title: {result['title']}")
                
            if result.get('author'):
                print(f"Author: {result['author']}")
                
            if result.get('analysis'):
                analysis = result['analysis']
                print(f"\n📊 Analysis:")
                print(f"  - Viral Potential: {analysis.get('viral_potential', 'UNKNOWN')}")
                print(f"  - Emotional Density: {analysis.get('emotional_density', 0):.1f}%")
                print(f"  - Trigger Density: {analysis.get('trigger_density', 0):.1f}%")
                
                if analysis.get('triggers'):
                    print(f"  - Jake Triggers: {', '.join([t['type'] for t in analysis['triggers']])}")
                    
            # Save
            saved = scraper.save_intel(result)
            print(f"\n💾 Saved to: {saved['markdown']}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
X & Substack Intelligence Extractor
Extract competitive intelligence and marketing insights from X posts and Substack articles
"""

import re
import sys
import json
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from collections import Counter
import time

class IntelExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def extract_x_post(self, url):
        """Extract content from X post using various methods"""
        print(f"🔍 Extracting X post: {url}")
        
        # Extract post ID
        post_id_match = re.search(r'/status/(\d+)', url)
        if not post_id_match:
            return {'error': 'Could not extract post ID'}
            
        post_id = post_id_match.group(1)
        
        # Try nitter instances
        nitter_instances = [
            'nitter.privacydev.net',
            'nitter.poast.org',
            'nitter.adminforge.de',
        ]
        
        for instance in nitter_instances:
            try:
                username_match = re.search(r'x\.com/([^/]+)/status', url) or re.search(r'twitter\.com/([^/]+)/status', url)
                if not username_match:
                    continue
                    
                username = username_match.group(1)
                nitter_url = f'https://{instance}/{username}/status/{post_id}'
                
                response = self.session.get(nitter_url, timeout=10)
                if response.status_code == 200:
                    content = self.parse_nitter_content(response.text)
                    if content:
                        return {
                            'platform': 'X/Twitter',
                            'url': url,
                            'post_id': post_id,
                            'username': username,
                            'content': content,
                            'extracted_at': datetime.now().isoformat()
                        }
            except Exception as e:
                print(f"Failed with {instance}: {e}")
                continue
                
        return {'error': 'Failed to extract from all sources'}
        
    def parse_nitter_content(self, html):
        """Parse content from nitter HTML"""
        # Extract tweet content
        content_match = re.search(r'class="tweet-content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        if content_match:
            content = content_match.group(1)
            # Clean HTML
            content = re.sub(r'<[^>]+>', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
            return content
        return None
        
    def extract_substack(self, url):
        """Extract content from Substack article"""
        print(f"📝 Extracting Substack article: {url}")
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return {'error': f'HTTP {response.status_code}'}
                
            html = response.text
            
            # Extract metadata
            title_match = re.search(r'<title>([^<]+)</title>', html)
            title = title_match.group(1) if title_match else 'Unknown'
            
            # Extract author
            author_match = re.search(r'"author":\s*{\s*"name":\s*"([^"]+)"', html)
            author = author_match.group(1) if author_match else 'Unknown'
            
            # Extract subscriber count
            subs_match = re.search(r'([\d,]+)\s*subscribers?', html)
            subscribers = subs_match.group(1) if subs_match else 'Unknown'
            
            # Extract main content
            content = self.extract_article_content(html)
            
            # Extract engagement metrics if available
            likes_match = re.search(r'([\d,]+)\s*likes?', html)
            likes = likes_match.group(1) if likes_match else '0'
            
            return {
                'platform': 'Substack',
                'url': url,
                'title': title,
                'author': author,
                'subscribers': subscribers,
                'likes': likes,
                'content': content,
                'word_count': len(content.split()),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
            
    def extract_article_content(self, html):
        """Extract article content from HTML"""
        # Try to find the main content area
        content_patterns = [
            r'<div[^>]*class="[^"]*available-content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*body[^"]*"[^>]*>(.*?)</div>',
            r'<article[^>]*>(.*?)</article>'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                content = match.group(1)
                # Clean HTML
                content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
                content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
                content = re.sub(r'<[^>]+>', ' ', content)
                content = re.sub(r'&[^;]+;', ' ', content)
                content = re.sub(r'\s+', ' ', content).strip()
                
                if len(content) > 100:  # Ensure we got actual content
                    return content[:5000]  # Limit to first 5000 chars
        
        return "Could not extract main content"
        
    def analyze_content(self, data):
        """Analyze content for marketing intelligence"""
        if 'error' in data:
            return data
            
        content = data.get('content', '')
        
        # Emotional triggers
        emotional_words = [
            'afraid', 'angry', 'anxious', 'broken', 'desperate', 'empty', 'failed',
            'fear', 'frustrated', 'guilty', 'helpless', 'hopeless', 'hurt', 'inadequate',
            'insecure', 'lonely', 'lost', 'overwhelmed', 'pain', 'rejected', 'shame',
            'struggle', 'stuck', 'tired', 'weak', 'worried', 'darkness', 'battle',
            'warrior', 'fight', 'wounded', 'healing'
        ]
        
        # Power words
        power_words = [
            'proven', 'secret', 'breakthrough', 'transform', 'revolutionary', 
            'exclusive', 'limited', 'urgent', 'powerful', 'essential', 'critical',
            'vital', 'ultimate', 'blueprint', 'protocol', 'system', 'framework'
        ]
        
        # Call to action words
        cta_words = [
            'click', 'join', 'buy', 'get', 'start', 'download', 'subscribe',
            'learn', 'discover', 'unlock', 'access', 'grab', 'claim', 'secure',
            'reserve', 'register', 'enroll'
        ]
        
        # Biblical/spiritual terms
        spiritual_words = [
            'God', 'Jesus', 'Christ', 'faith', 'prayer', 'Bible', 'scripture',
            'church', 'worship', 'grace', 'salvation', 'redemption', 'covenant',
            'ministry', 'spiritual', 'holy', 'blessed', 'anointed'
        ]
        
        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)
        
        # Count occurrences
        emotional_count = sum(1 for word in words if word in emotional_words)
        power_count = sum(1 for word in words if word in power_words)
        cta_count = sum(1 for word in words if word in cta_words)
        spiritual_count = sum(1 for word in words if word in spiritual_words)
        
        # Find most common words (excluding common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                      'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                      'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might'}
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        word_freq = Counter(filtered_words).most_common(20)
        
        # Extract hooks (first compelling statement)
        sentences = re.split(r'[.!?]+', content)
        hooks = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        # Sentiment indicators
        positive_words = ['amazing', 'incredible', 'powerful', 'transformed', 'breakthrough', 'success']
        negative_words = ['failed', 'struggle', 'pain', 'broken', 'lost', 'weak']
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        analysis = {
            'metrics': {
                'word_count': len(words),
                'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
                'sentence_count': len(sentences),
                'emotional_density': emotional_count / len(words) * 100 if words else 0,
                'power_word_density': power_count / len(words) * 100 if words else 0,
                'cta_density': cta_count / len(words) * 100 if words else 0,
                'spiritual_density': spiritual_count / len(words) * 100 if words else 0,
                'sentiment_score': (positive_count - negative_count) / len(words) * 100 if words else 0
            },
            'hooks': hooks,
            'top_words': word_freq,
            'emotional_triggers': [w for w in set(words) if w in emotional_words],
            'power_words_used': [w for w in set(words) if w in power_words],
            'ctas_found': [w for w in set(words) if w in cta_words],
            'marketing_formula': self.detect_formula(content)
        }
        
        return {**data, 'analysis': analysis}
        
    def detect_formula(self, content):
        """Detect common marketing formulas"""
        formulas_detected = []
        
        # PAS (Problem-Agitate-Solution)
        if re.search(r'problem|issue|struggle', content, re.I) and \
           re.search(r'worse|painful|frustrat', content, re.I) and \
           re.search(r'solution|answer|fix', content, re.I):
            formulas_detected.append('PAS (Problem-Agitate-Solution)')
            
        # AIDA (Attention-Interest-Desire-Action)
        if re.search(r'attention|discover|reveal', content, re.I) and \
           re.search(r'want|need|desire', content, re.I) and \
           re.search(r'click|join|buy|get', content, re.I):
            formulas_detected.append('AIDA (Attention-Interest-Desire-Action)')
            
        # Story-based
        if re.search(r'story|once|remember when|years ago', content, re.I):
            formulas_detected.append('Story-based hook')
            
        # Urgency/Scarcity
        if re.search(r'limited|urgent|now|today|ends|last chance', content, re.I):
            formulas_detected.append('Urgency/Scarcity')
            
        return formulas_detected
        
    def save_intel(self, data, filename=None):
        """Save extracted intelligence to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            platform = data.get('platform', 'unknown').lower()
            filename = f"{platform}_intel_{timestamp}.json"
            
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"💾 Saved to: {filename}")
        return filename

def main():
    if len(sys.argv) < 2:
        print("X & Substack Intelligence Extractor")
        print("\nUsage:")
        print("  python intel_extractor.py <URL>")
        print("  python intel_extractor.py analyze <file.json>")
        print("\nExamples:")
        print("  python intel_extractor.py https://x.com/user/status/123")
        print("  python intel_extractor.py https://substack.com/@user/p/title")
        return
        
    extractor = IntelExtractor()
    
    if sys.argv[1] == 'analyze' and len(sys.argv) > 2:
        # Analyze existing file
        with open(sys.argv[2], 'r') as f:
            data = json.load(f)
        
        if 'analysis' not in data:
            data = extractor.analyze_content(data)
            
        # Print analysis
        analysis = data.get('analysis', {})
        print("\n=== MARKETING INTELLIGENCE REPORT ===")
        print(f"Platform: {data.get('platform')}")
        print(f"URL: {data.get('url')}")
        print(f"\n📊 Metrics:")
        for key, value in analysis.get('metrics', {}).items():
            print(f"  {key}: {value:.2f}")
        print(f"\n🎯 Marketing Formulas Detected:")
        for formula in analysis.get('marketing_formula', []):
            print(f"  • {formula}")
        print(f"\n💭 Top Words:")
        for word, count in analysis.get('top_words', [])[:10]:
            print(f"  • {word}: {count}")
        print(f"\n🔥 Hooks:")
        for hook in analysis.get('hooks', []):
            print(f"  • {hook}")
            
    else:
        # Extract from URL
        url = sys.argv[1]
        
        if 'x.com' in url or 'twitter.com' in url:
            data = extractor.extract_x_post(url)
        elif 'substack.com' in url:
            data = extractor.extract_substack(url)
        else:
            print("❌ Unsupported URL")
            return
            
        if 'error' not in data:
            data = extractor.analyze_content(data)
            extractor.save_intel(data)
            
            # Print summary
            print(f"\n✅ Extracted successfully!")
            print(f"Platform: {data.get('platform')}")
            print(f"Word count: {data.get('word_count', 'N/A')}")
            if 'analysis' in data:
                metrics = data['analysis']['metrics']
                print(f"Emotional density: {metrics.get('emotional_density', 0):.1f}%")
                print(f"Power word density: {metrics.get('power_word_density', 0):.1f}%")
        else:
            print(f"❌ Error: {data['error']}")

if __name__ == '__main__':
    main()
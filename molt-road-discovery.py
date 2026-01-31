#!/usr/bin/env python3
"""
Molt Road API Discovery Script
Finds API endpoints and documentation for the agent marketplace
"""

import requests
import json
from urllib.parse import urljoin

base_url = "https://moltroad.com"

# Common API paths to check
api_paths = [
    "/api/v1",
    "/api/v1/docs",
    "/api/v1/register",
    "/api/v1/agents",
    "/api/v1/auth",
    "/api/agents",
    "/api/register",
    "/v1/agents",
    "/v1/register",
    "/agent/register",
    "/agents/create",
    "/swagger",
    "/openapi",
    "/api-docs",
    "/.well-known/openapi",
    "/graphql",
    "/robots.txt",
    "/sitemap.xml"
]

# Headers to appear like a legitimate agent
headers = {
    "User-Agent": "MoltRoadDiscovery/1.0 (OpenClaw Integration)",
    "Accept": "application/json, text/html, */*"
}

print("🔍 Discovering Molt Road API endpoints...\n")

discovered = []

for path in api_paths:
    url = urljoin(base_url, path)
    try:
        print(f"Checking: {url}")
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
        
        if response.status_code < 400:
            print(f"  ✅ Found: {response.status_code}")
            discovered.append({
                "url": url,
                "status": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "size": len(response.content)
            })
            
            # Save successful responses
            if response.status_code == 200:
                filename = path.replace("/", "_") + ".txt"
                with open(f"molt_road{filename}", "w") as f:
                    f.write(response.text)
                print(f"  💾 Saved to: molt_road{filename}")
        else:
            print(f"  ❌ {response.status_code}")
            
    except Exception as e:
        print(f"  ⚠️  Error: {str(e)[:50]}")

print("\n📊 Summary:")
print(f"Found {len(discovered)} endpoints:")
for item in discovered:
    print(f"  - {item['url']} ({item['status']}, {item['content_type']})")

# Check for JavaScript files that might contain API info
print("\n🔍 Checking for JavaScript API definitions...")

try:
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        # Look for script tags
        import re
        scripts = re.findall(r'<script[^>]*src=["\'](.*?)["\']', response.text)
        
        print(f"Found {len(scripts)} script files")
        for script in scripts[:5]:  # Check first 5
            if not script.startswith("http"):
                script = urljoin(base_url, script)
            
            try:
                print(f"\nChecking script: {script}")
                script_response = requests.get(script, headers=headers, timeout=5)
                if script_response.status_code == 200:
                    # Look for API patterns
                    api_patterns = re.findall(r'["\']/(api/[^"\']*)["\']', script_response.text)
                    if api_patterns:
                        print(f"  Found API patterns: {api_patterns[:5]}")
                        
                    # Look for registration patterns
                    reg_patterns = re.findall(r'register[^"\']*["\']([^"\']+)["\']', script_response.text, re.IGNORECASE)
                    if reg_patterns:
                        print(f"  Found registration patterns: {reg_patterns[:3]}")
                        
            except Exception as e:
                print(f"  Error loading script: {str(e)[:30]}")
                
except Exception as e:
    print(f"Error checking main page: {str(e)}")

print("\n✅ Discovery complete!")
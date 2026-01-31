#!/usr/bin/env python3
"""Test AgentQL API endpoints"""

import requests
import os

API_KEY = os.getenv('AGENTQL_API_KEY', '2_u9FhKSUTWLS5Q4jpggEyoYjlIMrw1oWZ5Xqe2zT_xHm6OWoBApKA')

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test different endpoints
endpoints = [
    "https://api.agentql.com",
    "https://api.agentql.com/extract",
    "https://api.agentql.com/scrape",
    "https://api.agentql.com/v1/extract",
    "https://api.agentql.com/v1/scrape",
    "https://api.agentql.com/query",
    "https://api.agentql.com/v1/query"
]

print("Testing AgentQL endpoints...")
print(f"Using API key: {API_KEY[:10]}...")
print()

for endpoint in endpoints:
    try:
        # Try POST
        r = requests.post(endpoint, headers=headers, json={"url": "https://example.com"}, timeout=5)
        print(f"POST {endpoint}: {r.status_code}")
        if r.status_code != 404:
            print(f"  Response: {r.text[:100]}")
    except Exception as e:
        print(f"POST {endpoint}: ERROR - {str(e)[:50]}")
        
    try:
        # Try GET
        r = requests.get(endpoint, headers=headers, timeout=5)
        print(f"GET  {endpoint}: {r.status_code}")
        if r.status_code != 404 and r.status_code != 405:
            print(f"  Response: {r.text[:100]}")
    except Exception as e:
        print(f"GET  {endpoint}: ERROR - {str(e)[:50]}")
    print()
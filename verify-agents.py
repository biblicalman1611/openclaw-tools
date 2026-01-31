#!/usr/bin/env python3
"""Verify agents after tweeting their codes"""

import requests
import json
import sys

BASE_URL = "https://moltroad.com/api/v1"

# Check if tweet URLs provided
if len(sys.argv) < 2:
    print("Usage: ./verify-agents.py <tweet_url1> [tweet_url2] [tweet_url3]")
    print("Example: ./verify-agents.py https://x.com/biblicalman1611/status/123456789")
    sys.exit(1)

# Load agents
agents = []
for name in ["BiblicalContentAnalyzer", "GumroadIntelBot", "HookDealer47"]:
    try:
        with open(f"molt-road-agents/{name}.json") as f:
            agents.append(json.load(f))
    except:
        pass

# Verify each agent with provided tweet URLs
for i, tweet_url in enumerate(sys.argv[1:]):
    if i < len(agents):
        agent = agents[i]
        print(f"\n🔐 Verifying {agent['name']}...")
        
        response = requests.post(
            f"{BASE_URL}/agents/{agent['id']}/verify",
            json={"tweet_url": tweet_url}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verified! Linked to @{data.get('twitter_handle', 'unknown')}")
            print(f"   Avatar: {data.get('avatar', 'N/A')}")
        else:
            print(f"❌ Verification failed: {response.text}")

print("\n✅ Verification complete!")
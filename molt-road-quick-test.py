#!/usr/bin/env python3
"""
Quick test of Molt Road API
Checks if we can connect and browse listings
"""

import requests

BASE_URL = "https://moltroad.com/api/v1"

print("🔍 Testing Molt Road API connection...\n")

# Test public endpoints
try:
    # Get stats
    response = requests.get(f"{BASE_URL}/stats")
    if response.status_code == 200:
        stats = response.json()
        print("✅ API is accessible!")
        print(f"📊 Marketplace stats:")
        print(f"   - Active agents: {stats['agents']}")
        print(f"   - Total listings: {stats['listings']}")
        print(f"   - Total volume: {stats['volume']} credits")
    else:
        print(f"❌ API returned status: {response.status_code}")
        
    # Browse listings
    print("\n📦 Recent listings:")
    listings = requests.get(f"{BASE_URL}/listings?limit=5").json()["listings"]
    
    for listing in listings[:3]:
        print(f"\n   {listing['title']}")
        print(f"   Price: {listing['price']} credits")
        print(f"   Category: {listing['category']}")
        print(f"   Seller: {listing['seller']['name']}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n✅ Connection test complete!")
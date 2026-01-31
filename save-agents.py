#!/usr/bin/env python3
"""Save the deployed agents from the output"""

import json
import os

os.makedirs("molt-road-agents", exist_ok=True)

# Agent 1: BiblicalContentAnalyzer
agent1 = {
    "name": "BiblicalContentAnalyzer",
    "id": "6910a97d-d5d1-4182-8787-f855cb7caf67",
    "api_key": "1f744f778d700a48b29cf727c84ecc799db83a03e0113cc2adc9aa86ca88a302",
    "verification_code": "cyber-G9XY",
    "registered_at": "2026-01-31T20:42:00"
}

# Agent 2: GumroadIntelBot
agent2 = {
    "name": "GumroadIntelBot", 
    "id": "1d50a2d8-f830-4305-9ee9-7bb57eaa3017",
    "api_key": "27f8fd8168b4f58a1c7e02a0a0789c926b472265735b56b8ef5377e0b9f26887",
    "verification_code": "node-8LC4",
    "registered_at": "2026-01-31T20:42:00"
}

# Agent 3: HookDealer47
agent3 = {
    "name": "HookDealer47",
    "id": "9d182541-22bc-4bc9-a221-7fb91f2e8115", 
    "api_key": "a8e61ee82343d59532b2498882dd9e845eb510cf2242515a5d9161e77df6821c",
    "verification_code": "neon-SBQG",
    "registered_at": "2026-01-31T20:42:00"
}

# Save agents
for agent in [agent1, agent2, agent3]:
    with open(f"molt-road-agents/{agent['name']}.json", "w") as f:
        json.dump(agent, f, indent=2)
        print(f"✅ Saved {agent['name']} - Code: {agent['verification_code']}")

print("\n📝 Verification codes to tweet:")
print(f"1. BiblicalContentAnalyzer: cyber-G9XY")
print(f"2. GumroadIntelBot: node-8LC4") 
print(f"3. HookDealer47: neon-SBQG")
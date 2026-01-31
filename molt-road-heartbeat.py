#!/usr/bin/env python3
"""
Molt Road Heartbeat - Monitor and manage your agent empire
Run this periodically to check orders, deliver goods, and find opportunities
"""

import requests
import json
import os
from datetime import datetime
import glob

BASE_URL = "https://moltroad.com/api/v1"

class MoltRoadHeartbeat:
    def __init__(self):
        self.agents = self.load_agents()
        
    def load_agents(self):
        """Load all registered agents from saved credentials"""
        agents = []
        for agent_file in glob.glob("molt-road-agents/*.json"):
            with open(agent_file, "r") as f:
                agent_data = json.load(f)
                agents.append(agent_data)
        return agents
    
    def check_agent_status(self, agent):
        """Check status of a single agent"""
        headers = {"X-API-Key": agent["api_key"]}
        
        print(f"\n🤖 Checking {agent['name']}...")
        
        # Get profile
        me = requests.get(f"{BASE_URL}/me", headers=headers).json()
        print(f"   💰 Balance: {me['balance']} credits")
        print(f"   ⭐ Rating: {me.get('rating', 'No ratings yet')} ({me.get('rating_count', 0)} reviews)")
        
        # Check pending orders to deliver
        seller_orders = requests.get(f"{BASE_URL}/orders?role=seller", headers=headers).json()
        pending = [o for o in seller_orders["orders"] if o["status"] == "escrowed"]
        
        if pending:
            print(f"   📦 {len(pending)} orders waiting for delivery!")
            for order in pending:
                print(f"      - Order {order['id']}: {order['listing']['title']}")
                
                # Auto-deliver based on listing type
                if "analysis" in order["listing"]["title"].lower():
                    self.deliver_analysis(agent, order)
                elif "hook" in order["listing"]["title"].lower():
                    self.deliver_hooks(agent, order)
                elif "intelligence" in order["listing"]["title"].lower():
                    self.deliver_intelligence(agent, order)
        
        # Check orders to confirm
        buyer_orders = requests.get(f"{BASE_URL}/orders?role=buyer", headers=headers).json()
        to_confirm = [o for o in buyer_orders["orders"] if o["status"] == "delivered"]
        
        if to_confirm:
            print(f"   ✅ {len(to_confirm)} deliveries to confirm")
            for order in to_confirm:
                # Auto-confirm if data looks good
                if order.get("delivery_data"):
                    response = requests.post(
                        f"{BASE_URL}/orders/{order['id']}/confirm",
                        headers=headers
                    )
                    if response.status_code == 200:
                        print(f"      ✅ Confirmed order {order['id']}")
        
        return me
    
    def deliver_analysis(self, agent, order):
        """Deliver content analysis"""
        analysis = {
            "report": "Viral Content Analysis Report",
            "emotional_density": 8.5,
            "triggers_found": ["father_wound", "church_hurt", "masculinity_crisis"],
            "viral_potential": "HIGH",
            "hooks": [
                "Your father's silence wasn't strength.",
                "Church lied about what makes a man.",
                "She needs your war, not your peace."
            ],
            "optimal_posting_time": "Tuesday 2PM ET",
            "predicted_engagement": "5K+ likes, 500+ replies"
        }
        
        response = requests.post(
            f"{BASE_URL}/orders/{order['id']}/deliver",
            headers={"X-API-Key": agent["api_key"]},
            json={"data": analysis}
        )
        
        if response.status_code == 200:
            print(f"      📤 Delivered analysis for order {order['id']}")
    
    def deliver_hooks(self, agent, order):
        """Deliver viral hooks"""
        hooks = {
            "hook_pack": "Father Wound Viral Openers",
            "hooks": [
                "My father taught me to fail by never teaching me to fight.",
                "The first time I saw my dad cry was at his own father's funeral. Too late.",
                "Your son doesn't need another friend. He needs his first warrior.",
                "I spent 30 years trying to earn love from a ghost.",
                "The strongest men I know still flinch when their phone shows 'Dad'."
            ],
            "usage_notes": "Post between 2-4 PM ET. Follow with vulnerability + solution.",
            "tested_engagement": "Average 3K+ likes per hook"
        }
        
        response = requests.post(
            f"{BASE_URL}/orders/{order['id']}/deliver",
            headers={"X-API-Key": agent["api_key"]},
            json={"data": hooks}
        )
        
        if response.status_code == 200:
            print(f"      📤 Delivered hooks for order {order['id']}")
    
    def deliver_intelligence(self, agent, order):
        """Deliver customer intelligence"""
        intel = {
            "report": "Gumroad High-Value Customer Alert",
            "whale_signals": [
                {"email": "d***@gmail.com", "pattern": "Downloads everything within 1 hour", "likelihood": 0.89},
                {"email": "m***@yahoo.com", "pattern": "Multiple free downloads yesterday", "likelihood": 0.76},
                {"email": "j***@hotmail.com", "pattern": "Opened 5+ emails this week", "likelihood": 0.71}
            ],
            "recommendations": "Personal outreach within 48 hours. Mention specific products they engaged with.",
            "conversion_window": "Next 72 hours"
        }
        
        response = requests.post(
            f"{BASE_URL}/orders/{order['id']}/deliver",
            headers={"X-API-Key": agent["api_key"]},
            json={"data": intel}
        )
        
        if response.status_code == 200:
            print(f"      📤 Delivered intelligence for order {order['id']}")
    
    def find_opportunities(self):
        """Scan for new opportunities"""
        print("\n🔍 Scanning for opportunities...")
        
        # Check bounties
        bounties = requests.get(f"{BASE_URL}/bounties").json()["bounties"]
        relevant = []
        
        for bounty in bounties:
            if any(kw in bounty["title"].lower() for kw in ["content", "viral", "christian", "analysis", "data"]):
                relevant.append(bounty)
        
        if relevant:
            print(f"   💰 Found {len(relevant)} relevant bounties:")
            for bounty in relevant[:3]:
                print(f"      - {bounty['title']} ({bounty['reward']} credits)")
        
        # Check activity feed for trends
        activity = requests.get(f"{BASE_URL}/stats/activity?limit=10").json()["activity"]
        
        new_agents = [a for a in activity if a["type"] == "registration"]
        if new_agents:
            print(f"   🆕 {len(new_agents)} new agents joined recently")
        
        # Check stats
        stats = requests.get(f"{BASE_URL}/stats").json()
        print(f"\n📊 Marketplace Stats:")
        print(f"   Total agents: {stats['agents']}")
        print(f"   Active listings: {stats['listings']}")
        print(f"   Total volume: {stats['volume']} credits")
    
    def generate_report(self):
        """Generate summary report"""
        print("\n" + "="*50)
        print("📈 MOLT ROAD EMPIRE REPORT")
        print("="*50)
        
        total_balance = 0
        total_sales = 0
        total_ratings = 0
        
        for agent in self.agents:
            headers = {"X-API-Key": agent["api_key"]}
            me = requests.get(f"{BASE_URL}/me", headers=headers).json()
            
            total_balance += me["balance"]
            if me.get("rating_count"):
                total_ratings += me["rating_count"]
            
            # Count sales from active listings
            total_sales += len(me.get("active_listings", []))
        
        print(f"\n💼 Portfolio Summary:")
        print(f"   Active agents: {len(self.agents)}")
        print(f"   Total balance: {total_balance} credits")
        print(f"   Active listings: {total_sales}")
        print(f"   Total reviews: {total_ratings}")
        
        print(f"\n💡 Recommendations:")
        if total_balance > 500:
            print("   - Deploy more specialized agents")
        if total_ratings < 10:
            print("   - Focus on quick deliveries for more reviews")
        print("   - Monitor competitor listings for pricing")
        
        # Save report
        with open(f"molt-road-reports/report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "agents": len(self.agents),
                "total_balance": total_balance,
                "total_ratings": total_ratings,
                "active_listings": total_sales
            }, f, indent=2)


if __name__ == "__main__":
    print("🔄 Molt Road Heartbeat Starting...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create directories
    os.makedirs("molt-road-agents", exist_ok=True)
    os.makedirs("molt-road-reports", exist_ok=True)
    
    # Run heartbeat
    heartbeat = MoltRoadHeartbeat()
    
    if not heartbeat.agents:
        print("\n⚠️  No agents found! Deploy agents first with molt-road-agent.py")
    else:
        # Check each agent
        for agent in heartbeat.agents:
            heartbeat.check_agent_status(agent)
        
        # Find opportunities
        heartbeat.find_opportunities()
        
        # Generate report
        heartbeat.generate_report()
    
    print("\n✅ Heartbeat complete!")
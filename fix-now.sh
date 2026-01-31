#!/bin/bash
# ONE-CLICK FIX for X Reply Agent
# Run this on Adam's Mac: bash fix-now.sh

echo "🚨 X REPLY AGENT EMERGENCY FIX 🚨"
echo "================================="
echo ""

# 1. Kill everything
echo "Step 1: Killing all Node and Chrome processes..."
killall node 2>/dev/null || true
killall "Google Chrome" 2>/dev/null || true
pkill -f x-reply 2>/dev/null || true
sleep 2
echo "✅ Processes killed"
echo ""

# 2. Clear state and cache
echo "Step 2: Clearing state and cache..."
rm -f /Users/thebi/chrome-automation/data/x-reply-state.json
rm -rf /Users/thebi/chrome-automation/profiles/x-scanner/Default/Cache/*
rm -rf ~/Library/Caches/Google/Chrome/Default/Cache/*
echo "✅ Cache and state cleared"
echo ""

# 3. Backup and patch the agent
echo "Step 3: Patching x-reply-agent.js..."
cd /Users/thebi/chrome-automation/scripts

# Backup
cp x-reply-agent.js x-reply-agent.backup.js 2>/dev/null

# Apply critical fix inline
cat > apply-fix.js << 'FIXEOF'
const fs = require('fs');
let content = fs.readFileSync('x-reply-agent.js', 'utf8');

// Add ignore list
if (!content.includes('ignoreTweetIds')) {
  content = content.replace(
    "skipOlderThanHours: 12,",
    "skipOlderThanHours: 12,\n  ignoreTweetIds: ['2017279405752549511'], // Skip stuck tweet"
  );
}

// Enhance tweet finding
content = content.replace(
  'await page.waitForTimeout(4000);',
  `await page.waitForTimeout(4000);
  
  // URGENT: Force refresh to bypass cache
  await page.keyboard.down('Meta');
  await page.keyboard.down('Shift');  
  await page.keyboard.press('r');
  await page.keyboard.up('Shift');
  await page.keyboard.up('Meta');
  await page.waitForTimeout(6000);`
);

fs.writeFileSync('x-reply-agent.js', content);
console.log('✅ Agent patched successfully');
FIXEOF

node apply-fix.js
rm apply-fix.js
echo ""

# 4. Quick test
echo "Step 4: Running quick test..."
echo "Looking for latest tweet (should NOT be 2017279405752549511)..."
echo ""

# Test run
timeout 30 node x-reply-agent.js --debug --dry-run 2>&1 | grep -E "(Latest tweet|Tweet preview|ERROR)" || true

echo ""
echo "================================="
echo "✅ FIX COMPLETE!"
echo ""
echo "To run the agent normally:"
echo "  cd /Users/thebi/chrome-automation/scripts"
echo "  node x-reply-agent.js"
echo ""
echo "The agent should now find and reply to your HOT NEW TWEET!"
echo "================================="
#!/bin/bash
# URGENT FIX for X Reply Agent - Run this on Adam's Mac

echo "🚨 URGENT X REPLY AGENT FIX 🚨"
echo "================================"

# 1. Kill any running x-reply processes
echo "1. Killing any running x-reply processes..."
pkill -f "x-reply" || true
pkill -f "node.*x-reply" || true
killall node 2>/dev/null || true
echo "✅ Processes killed"

# 2. Navigate to the chrome-automation directory
cd /Users/thebi/chrome-automation

# 3. Clear the state file
echo "2. Clearing state file..."
rm -f data/x-reply-state.json
echo "{\"repliedTo\": [], \"lastRun\": null, \"stats\": {\"total\": 0, \"skipped\": 0}}" > data/x-reply-state.json
echo "✅ State cleared"

# 4. Create the fix patch
echo "3. Creating emergency patch file..."
cat > scripts/x-reply-PATCH.js << 'EOF'
// EMERGENCY PATCH - Add this to the beginning of findLatestTweet function

// List of stuck tweet IDs to ignore
const STUCK_TWEETS = ['2017279405752549511']; // David Peacock tweet

async function findLatestTweet(page) {
  console.log(`[URGENT] Force-refreshing to find NEW tweet...`);
  
  // FORCE CLEAR ALL CACHE
  try {
    await page.context().clearCookies();
    await page.context().clearPermissions();
    await page.context().route('**/*', route => route.continue());
  } catch (e) {}
  
  // Navigate with cache bust
  const bustUrl = `https://x.com/Biblicalman?nocache=${Date.now()}&refresh=true`;
  await page.goto(bustUrl, {
    waitUntil: 'networkidle',
    timeout: 30000
  });
  
  // Force hard refresh with Cmd+Shift+R
  await page.keyboard.down('Meta');
  await page.keyboard.down('Shift');
  await page.keyboard.press('r');
  await page.keyboard.up('Shift');
  await page.keyboard.up('Meta');
  
  await page.waitForTimeout(8000); // Give plenty of time
  
  // Get ALL tweets and filter out stuck ones
  const tweets = await page.evaluate((stuckIds) => {
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    const found = [];
    
    for (let i = 0; i < articles.length && i < 10; i++) {
      const article = articles[i];
      const links = article.querySelectorAll('a[href*="/status/"]');
      
      for (const link of links) {
        const href = link.getAttribute('href');
        if (href && href.includes('/Biblicalman/status/')) {
          const tweetId = href.match(/\/status\/(\d+)/)?.[1];
          
          // SKIP STUCK TWEETS
          if (stuckIds.includes(tweetId)) {
            console.log(`[SKIP] Ignoring stuck tweet: ${tweetId}`);
            continue;
          }
          
          const timeEl = article.querySelector('time');
          const textEl = article.querySelector('[data-testid="tweetText"]');
          
          found.push({
            url: 'https://x.com' + href,
            id: tweetId,
            time: timeEl?.getAttribute('datetime'),
            text: textEl?.innerText?.substring(0, 100) || '',
            position: i
          });
          break;
        }
      }
    }
    
    // Return the first non-stuck tweet
    return found[0] || null;
  }, STUCK_TWEETS);
  
  if (tweets) {
    console.log(`[SUCCESS] Found NEW tweet: ${tweets.id}`);
    console.log(`[PREVIEW] "${tweets.text}..."`);
    return tweets.url;
  } else {
    console.log(`[ERROR] No new tweets found!`);
    return null;
  }
}
EOF

echo "✅ Patch created"

# 5. Run a quick test
echo "4. Testing the agent to find the NEW tweet..."
cd scripts

# Create a test runner
cat > test-new-tweet.js << 'EOF'
const { chromium } = require('playwright');

async function quickTest() {
  console.log('\n🔍 SEARCHING FOR NEW TWEET...\n');
  
  try {
    // Try CDP connection first
    let browser, page;
    try {
      browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
      const contexts = browser.contexts();
      page = await contexts[0].newPage();
      console.log('✅ Connected via CDP');
    } catch (e) {
      // Launch new browser
      const context = await chromium.launchPersistentContext('../profiles/x-scanner', {
        headless: false,
        channel: 'chrome',
        args: ['--disable-blink-features=AutomationControlled'],
      });
      page = await context.newPage();
      browser = context;
      console.log('✅ Launched new Chrome');
    }
    
    // Clear everything
    await page.context().clearCookies();
    
    // Go to profile with cache bust
    await page.goto(`https://x.com/Biblicalman?cb=${Date.now()}`, {
      waitUntil: 'networkidle'
    });
    
    // Hard refresh
    await page.keyboard.down('Meta');
    await page.keyboard.press('r');
    await page.keyboard.up('Meta');
    await page.waitForTimeout(5000);
    
    // Find tweets
    const tweets = await page.evaluate(() => {
      const articles = document.querySelectorAll('article[data-testid="tweet"]');
      const results = [];
      
      for (let i = 0; i < 5 && i < articles.length; i++) {
        const article = articles[i];
        const link = article.querySelector('a[href*="/Biblicalman/status/"]');
        if (link) {
          const href = link.getAttribute('href');
          const id = href.match(/\/status\/(\d+)/)?.[1];
          const textEl = article.querySelector('[data-testid="tweetText"]');
          const timeEl = article.querySelector('time');
          
          results.push({
            id: id,
            text: textEl?.innerText?.substring(0, 150) || '',
            time: timeEl?.getAttribute('datetime') || '',
            isPinned: article.innerText.includes('Pinned')
          });
        }
      }
      return results;
    });
    
    console.log('\n📋 FOUND TWEETS:\n');
    tweets.forEach((tweet, i) => {
      console.log(`${i+1}. Tweet ID: ${tweet.id}`);
      console.log(`   Text: "${tweet.text}"...`);
      console.log(`   Time: ${tweet.time}`);
      if (tweet.id === '2017279405752549511') {
        console.log('   ❌ THIS IS THE OLD STUCK TWEET!');
      } else if (i === 0 && !tweet.isPinned) {
        console.log('   ✅ THIS LOOKS LIKE THE NEW HOT TWEET!');
      }
      console.log('');
    });
    
    await page.close();
    if (browser.close) await browser.close();
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

quickTest();
EOF

echo "Running test..."
node test-new-tweet.js

echo ""
echo "================================"
echo "🎯 NEXT STEPS:"
echo "1. Check the output above - it should show the NEW tweet, not ID 2017279405752549511"
echo "2. If you see the new tweet, run: node x-reply-agent.js"
echo "3. The agent should now reply to the HOT tweet!"
echo ""
echo "If it's still stuck:"
echo "- Close ALL Chrome windows"
echo "- Run: rm -rf ../profiles/x-scanner/Default/Cache"
echo "- Try again"
echo "================================"
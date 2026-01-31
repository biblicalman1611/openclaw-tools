#!/usr/bin/env node
// Direct fix for x-reply-agent.js on Adam's Mac

const fs = require('fs');
const path = require('path');

const AGENT_PATH = '/Users/thebi/chrome-automation/scripts/x-reply-agent.js';
const BACKUP_PATH = '/Users/thebi/chrome-automation/scripts/x-reply-agent.backup.js';

console.log('🔧 Applying URGENT fix to x-reply-agent.js...\n');

// 1. Backup original
try {
  const original = fs.readFileSync(AGENT_PATH, 'utf8');
  fs.writeFileSync(BACKUP_PATH, original);
  console.log('✅ Backed up original to x-reply-agent.backup.js');
} catch (e) {
  console.error('❌ Could not backup file:', e.message);
  process.exit(1);
}

// 2. Read the current file
let content = fs.readFileSync(AGENT_PATH, 'utf8');

// 3. Add stuck tweet filter to CONFIG
if (!content.includes('ignoreTweetIds')) {
  content = content.replace(
    `const CONFIG = {
  username: 'Biblicalman',`,
    `const CONFIG = {
  username: 'Biblicalman',
  ignoreTweetIds: ['2017279405752549511'], // URGENT: Skip David Peacock stuck tweet`
  );
  console.log('✅ Added ignoreTweetIds to CONFIG');
}

// 4. Replace findLatestTweet function with enhanced version
const newFindLatestTweet = `async function findLatestTweet(page) {
  log(\`Navigating to @\${CONFIG.username} profile...\`);
  
  // URGENT FIX: Force fresh load to find NEW tweet
  try {
    await page.context().clearCookies();
    await page.context().clearPermissions();
  } catch (e) {}
  
  // Navigate with cache-busting
  const timestamp = Date.now();
  await page.goto(\`https://x.com/\${CONFIG.username}?t=\${timestamp}&refresh=true\`, {
    waitUntil: 'domcontentloaded',
    timeout: 30000
  });
  
  // Force hard refresh (Cmd+Shift+R on Mac)
  await page.keyboard.down('Meta');
  await page.keyboard.down('Shift');
  await page.keyboard.press('r');
  await page.keyboard.up('Shift');
  await page.keyboard.up('Meta');
  
  await page.waitForTimeout(8000); // Extra time for fresh load
  
  // Find ALL tweets and filter out stuck ones
  const tweetData = await page.evaluate((username, ignoredIds) => {
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    const tweets = [];

    for (let i = 0; i < articles.length && i < 10; i++) {
      const article = articles[i];
      const isPinned = article.innerText.includes('Pinned');
      
      const links = article.querySelectorAll('a[href*="/status/"]');
      for (const link of links) {
        const href = link.getAttribute('href');
        if (href && href.includes(\`/\${username}/status/\`)) {
          const tweetId = href.match(/\\/status\\/(\\d+)/)?.[1];
          
          // SKIP ignored/stuck tweets
          if (ignoredIds && ignoredIds.includes(tweetId)) {
            console.log(\`[X-REPLY] Skipping stuck tweet: \${tweetId}\`);
            continue;
          }
          
          const timeEl = article.querySelector('time');
          const time = timeEl?.getAttribute('datetime');
          const textEl = article.querySelector('[data-testid="tweetText"]');
          const text = textEl?.innerText || '';
          
          tweets.push({
            url: 'https://x.com' + href,
            id: tweetId,
            time: time,
            text: text.substring(0, 100),
            isPinned: isPinned,
            position: i
          });
          break;
        }
      }
    }
    
    // Sort by time (newest first), deprioritize pinned
    tweets.sort((a, b) => {
      if (a.isPinned && !b.isPinned) return 1;
      if (!a.isPinned && b.isPinned) return -1;
      if (a.time && b.time) return b.time.localeCompare(a.time);
      return a.position - b.position;
    });
    
    return tweets[0] || null;
  }, CONFIG.username, CONFIG.ignoreTweetIds || []);
  
  const tweetUrl = tweetData?.url;
  
  if (tweetUrl) {
    log(\`Latest tweet found: \${tweetUrl} (ID: \${tweetData.id})\`);
    log(\`Tweet preview: "\${tweetData.text}..."\`);
    log(\`Tweet time: \${tweetData.time}\`);
    
    // Extra check for stuck tweet
    if (CONFIG.ignoreTweetIds?.some(id => tweetUrl.includes(id))) {
      log(\`ERROR: Still seeing stuck tweet! Check browser cache.\`);
      return null;
    }
  }`;

// Find and replace the findLatestTweet function
const funcStart = content.indexOf('async function findLatestTweet(page) {');
const funcEnd = content.indexOf('\n\n', content.indexOf('return tweetUrl;', funcStart));

if (funcStart > -1 && funcEnd > -1) {
  content = content.substring(0, funcStart) + newFindLatestTweet + content.substring(funcEnd);
  console.log('✅ Replaced findLatestTweet function with enhanced version');
} else {
  console.error('❌ Could not find findLatestTweet function!');
}

// 5. Write the fixed file
fs.writeFileSync(AGENT_PATH, content);
console.log('✅ Saved fixed x-reply-agent.js');

// 6. Clear state file
const stateFile = '/Users/thebi/chrome-automation/data/x-reply-state.json';
try {
  fs.unlinkSync(stateFile);
  console.log('✅ Deleted old state file');
} catch (e) {
  // Ignore if doesn't exist
}

console.log('\n🎉 FIX APPLIED SUCCESSFULLY!\n');
console.log('Next steps:');
console.log('1. Kill any running Chrome: killall "Google Chrome"');
console.log('2. Clear Chrome cache: rm -rf ~/Library/Caches/Google/Chrome/Default/Cache/*');
console.log('3. Run the agent: node /Users/thebi/chrome-automation/scripts/x-reply-agent.js');
console.log('\nThe agent should now find and reply to the NEW hot tweet!');
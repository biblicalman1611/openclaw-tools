#!/usr/bin/env node
// x-reply-agent.js — Lightweight X Reply Bot for @Biblicalman
// Monitors latest tweet replies, responds in-voice using Claude Haiku
// Designed for cron: run → check → reply → exit

const { chromium } = require('playwright');
const https = require('https');
const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════
//                    CONFIGURATION
// ═══════════════════════════════════════════════════════════════

const SCRIPT_DIR = __dirname;
const DATA_DIR = path.join(SCRIPT_DIR, '..', 'data');
const LOG_DIR = path.join(SCRIPT_DIR, '..', 'logs');
const STATE_FILE = path.join(DATA_DIR, 'x-reply-state.json');
const LOG_FILE = path.join(LOG_DIR, 'x-reply-agent.log');

const CONFIG = {
  username: 'Biblicalman',
  profileDir: path.join(SCRIPT_DIR, '..', 'profiles', 'x-scanner'),
  cdpUrl: 'http://127.0.0.1:9222',
  maxRepliesPerRun: 3,        // Don't spam — 3 max per check
  skipOlderThanHours: 12,     // Ignore stale replies
  dryRun: process.argv.includes('--dry-run'),
  debug: process.argv.includes('--debug'),
  quiet: process.argv.includes('--quiet'),
  // URGENT FIX: Ignore the old stuck tweet
  ignoreTweetIds: ['2017279405752549511'], // David Peacock tweet that's stuck
};

// ═══════════════════════════════════════════════════════════════
//                    VOICE DNA (compact for Haiku)
// ═══════════════════════════════════════════════════════════════

const VOICE_PROMPT = `You are Biblical Man (@Biblicalman) replying on X (Twitter).

VOICE:
- Short sentences. 8 words avg. Fragments = power.
- Direct. Zero hedging. No filler.
- BANNED phrases: "great point", "thanks for sharing", "absolutely", "I appreciate", "in today's world", "let's dive in", "important to note"
- KJV only for scripture.
- Signature: "Sit with that." / "That's the real ____" / "Pick one. You already have."

REPLY STYLE:
- AGREE → deepen, twist, don't just "amen"
- QUESTION → one direct answer, maybe scripture
- CHALLENGE → stand firm, no defensiveness, binary choice
- TESTIMONY → honor briefly, connect back
- TROLL → ignore (return SKIP)
- SPAM → ignore (return SKIP)

CONSTRAINTS:
- Under 200 characters
- Sound human, not brand
- No emojis unless one fits perfectly
- If this reply doesn't deserve a response, return exactly: SKIP`;

// ═══════════════════════════════════════════════════════════════
//                    UTILITIES
// ═══════════════════════════════════════════════════════════════

function log(msg) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}`;
  if (!CONFIG.quiet) console.log(line);
  try {
    if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });
    fs.appendFileSync(LOG_FILE, line + '\n');
  } catch (_) {}
}

function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch (e) { log(`State load error: ${e.message}`); }
  return { repliedTo: [], lastRun: null, stats: { total: 0, skipped: 0 } };
}

function saveState(state) {
  try {
    if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
    // Keep only last 500 replied-to IDs
    if (state.repliedTo.length > 500) state.repliedTo = state.repliedTo.slice(-500);
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch (e) { log(`State save error: ${e.message}`); }
}

// ═══════════════════════════════════════════════════════════════
//                    CLAUDE API (Haiku — cheapest)
// ═══════════════════════════════════════════════════════════════

async function callHaiku(prompt) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) { log('ERROR: No ANTHROPIC_API_KEY'); return null; }

  return new Promise((resolve) => {
    const data = JSON.stringify({
      model: 'claude-3-5-haiku-latest',
      max_tokens: 150,
      messages: [{ role: 'user', content: prompt }]
    });

    const req = https.request({
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          if (result.error) {
            log(`API error: ${result.error.message}`);
            resolve(null);
          } else {
            resolve(result.content?.[0]?.text?.trim() || null);
          }
        } catch (e) { log(`API parse error: ${e.message}`); resolve(null); }
      });
    });
    req.on('error', e => { log(`API request error: ${e.message}`); resolve(null); });
    req.write(data);
    req.end();
  });
}

// ═══════════════════════════════════════════════════════════════
//                    BROWSER CONNECTION
// ═══════════════════════════════════════════════════════════════

async function connectBrowser() {
  // Try CDP first (Chrome already running with remote debugging)
  try {
    const browser = await chromium.connectOverCDP(CONFIG.cdpUrl);
    log('Connected to Chrome via CDP');
    return { browser, launched: false };
  } catch (_) {}

  // Launch Chrome with x-scanner profile
  log('CDP not available, launching Chrome...');
  try {
    const context = await chromium.launchPersistentContext(CONFIG.profileDir, {
      headless: false,
      channel: 'chrome',
      args: [
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-blink-features=AutomationControlled',
      ],
      viewport: { width: 1280, height: 900 },
    });
    log('Launched Chrome with x-scanner profile');
    return { context, launched: true };
  } catch (e) {
    log(`Failed to launch Chrome: ${e.message}`);
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════
//                    TWEET DISCOVERY
// ═══════════════════════════════════════════════════════════════

async function findLatestTweet(page) {
  log(`Navigating to @${CONFIG.username} profile...`);
  
  // FORCE REFRESH - clear cache and cookies to avoid stale data
  await page.context().clearCookies();
  await page.context().clearPermissions();
  
  // Add cache-busting timestamp to URL
  const timestamp = Date.now();
  await page.goto(`https://x.com/${CONFIG.username}?t=${timestamp}`, {
    waitUntil: 'domcontentloaded',
    timeout: 30000
  });
  
  // Force hard refresh
  await page.keyboard.down('Meta');
  await page.keyboard.press('r');
  await page.keyboard.up('Meta');
  
  await page.waitForTimeout(6000); // Give more time for fresh load

  // Find the ABSOLUTE latest tweet - prioritize by position and time
  const tweetData = await page.evaluate((username) => {
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    const tweets = [];

    for (let i = 0; i < articles.length && i < 5; i++) {
      const article = articles[i];
      
      // Skip if it says "Pinned" 
      const isPinned = article.innerText.includes('Pinned');
      
      // Get tweet link (contains /status/)
      const links = article.querySelectorAll('a[href*="/status/"]');
      for (const link of links) {
        const href = link.getAttribute('href');
        if (href && href.includes(`/${username}/status/`)) {
          const timeEl = article.querySelector('time');
          const time = timeEl?.getAttribute('datetime');
          const textEl = article.querySelector('[data-testid="tweetText"]');
          const text = textEl?.innerText || '';
          
          tweets.push({
            url: 'https://x.com' + href,
            time: time,
            text: text.substring(0, 100),
            isPinned: isPinned,
            position: i
          });
          break;
        }
      }
    }
    
    // Sort by time (newest first), then by position
    tweets.sort((a, b) => {
      // Deprioritize pinned tweets
      if (a.isPinned && !b.isPinned) return 1;
      if (!a.isPinned && b.isPinned) return -1;
      
      // Compare times
      if (a.time && b.time) {
        return b.time.localeCompare(a.time);
      }
      
      // Fallback to position
      return a.position - b.position;
    });
    
    return tweets[0] || null;
  }, CONFIG.username);

  let tweetUrl = tweetData?.url;
  
  // Check if this is the stuck tweet we need to ignore
  if (tweetUrl && CONFIG.ignoreTweetIds.some(id => tweetUrl.includes(id))) {
    log(`WARNING: Found stuck tweet ${tweetUrl} - IGNORING and looking for newer one`);
    tweetUrl = null; // Force it to be null so we don't process the old tweet
  }
  
  if (tweetUrl) {
    log(`Latest tweet found: ${tweetUrl}`);
    log(`Tweet preview: "${tweetData.text}..."`);
    log(`Tweet time: ${tweetData.time}`);
  }

  if (tweetUrl) {
    log(`Latest tweet: ${tweetUrl}`);
  } else {
    log('Could not find latest tweet');
  }
  return tweetUrl;
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY SCRAPING
// ═══════════════════════════════════════════════════════════════

async function scrapeReplies(page, tweetUrl) {
  log(`Navigating to tweet: ${tweetUrl}`);
  await page.goto(tweetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(4000);

  // Scroll to load replies
  for (let i = 0; i < 3; i++) {
    await page.evaluate(() => window.scrollBy(0, 800));
    await page.waitForTimeout(1500);
  }

  const replies = await page.evaluate((myUsername) => {
    const results = [];
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    let isFirst = true;

    for (const article of articles) {
      // Skip the first article (the original tweet)
      if (isFirst) { isFirst = false; continue; }

      const reply = {};

      // Username
      const userLinks = article.querySelectorAll('a[role="link"]');
      for (const link of userLinks) {
        const href = link.getAttribute('href');
        if (href && href.match(/^\/[A-Za-z0-9_]+$/)) {
          reply.username = href.substring(1);
          break;
        }
      }

      // Display name
      const nameEl = article.querySelector('[data-testid="User-Name"]');
      if (nameEl) reply.displayName = nameEl.innerText.split('\n')[0];

      // Text
      const textEl = article.querySelector('[data-testid="tweetText"]');
      if (textEl) reply.text = textEl.innerText.substring(0, 400);

      // Engagement
      const likeBtn = article.querySelector('[data-testid="like"]');
      if (likeBtn) {
        const cnt = likeBtn.querySelector('span[data-testid="app-text-transition-container"]');
        reply.likes = cnt?.innerText || '0';
      }

      // Time
      const timeEl = article.querySelector('time');
      if (timeEl) reply.time = timeEl.getAttribute('datetime');

      // Tweet ID from any status link in article
      const statusLink = article.querySelector('a[href*="/status/"]');
      if (statusLink) {
        const match = statusLink.getAttribute('href').match(/\/status\/(\d+)/);
        if (match) reply.tweetId = match[1];
      }

      // Skip own replies and empty ones
      if (reply.text && reply.username &&
          reply.username.toLowerCase() !== myUsername.toLowerCase()) {
        results.push(reply);
      }
    }
    return results;
  }, CONFIG.username);

  log(`Found ${replies.length} replies`);
  return replies;
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY FILTERING
// ═══════════════════════════════════════════════════════════════

function filterReplies(replies, state) {
  const cutoff = Date.now() - (CONFIG.skipOlderThanHours * 60 * 60 * 1000);
  const repliedSet = new Set(state.repliedTo);

  return replies.filter(r => {
    // Skip already replied
    const id = r.tweetId || `${r.username}-${(r.text || '').substring(0, 30)}`;
    if (repliedSet.has(id)) {
      if (CONFIG.debug) log(`  Skip (already replied): @${r.username}`);
      return false;
    }

    // Skip old replies
    if (r.time && new Date(r.time).getTime() < cutoff) {
      if (CONFIG.debug) log(`  Skip (too old): @${r.username}`);
      return false;
    }

    // Skip very short / meaningless
    if (!r.text || r.text.length < 5) {
      if (CONFIG.debug) log(`  Skip (too short): @${r.username}`);
      return false;
    }

    return true;
  }).slice(0, CONFIG.maxRepliesPerRun);
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY GENERATION
// ═══════════════════════════════════════════════════════════════

async function generateReply(originalTweet, reply) {
  const prompt = `${VOICE_PROMPT}

ORIGINAL TWEET (yours):
"${(originalTweet || '').substring(0, 300)}"

REPLY FROM @${reply.username}:
"${reply.text}"

Generate your reply (under 200 chars). If not worth replying, say SKIP.`;

  const response = await callHaiku(prompt);
  if (!response || response.trim() === 'SKIP') return null;

  // Clean up — remove quotes if Haiku wraps them
  let clean = response.replace(/^["']|["']$/g, '').trim();
  if (clean.length > 280) clean = clean.substring(0, 277) + '...';
  return clean;
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY POSTING
// ═══════════════════════════════════════════════════════════════

async function postReply(page, reply, replyText) {
  if (CONFIG.dryRun) {
    log(`[DRY RUN] Would reply to @${reply.username}: "${replyText}"`);
    return true;
  }

  try {
    // Find the specific reply article
    const articles = await page.$$('article[data-testid="tweet"]');

    let targetArticle = null;
    for (const article of articles) {
      const textEl = await article.$('[data-testid="tweetText"]');
      if (textEl) {
        const text = await textEl.innerText();
        if (text.includes(reply.text.substring(0, 50))) {
          targetArticle = article;
          break;
        }
      }
    }

    if (!targetArticle) {
      log(`  Could not find reply article for @${reply.username}`);
      return false;
    }

    // Click reply button on that article
    const replyBtn = await targetArticle.$('[data-testid="reply"]');
    if (!replyBtn) {
      log(`  No reply button found for @${reply.username}`);
      return false;
    }

    await replyBtn.click();
    await page.waitForTimeout(2000);

    // Find the reply composer (modal or inline)
    const composer = await page.$('[data-testid="tweetTextarea_0"]') ||
                     await page.$('[contenteditable="true"][role="textbox"]') ||
                     await page.$('[data-testid="tweetTextarea_0RichTextInputContainer"] [contenteditable]');

    if (!composer) {
      log(`  Reply composer not found for @${reply.username}`);
      // Try pressing Escape to close any modal
      await page.keyboard.press('Escape');
      return false;
    }

    // Type the reply
    await composer.click();
    await page.waitForTimeout(300);
    await page.keyboard.type(replyText, { delay: 25 });
    await page.waitForTimeout(500);

    // Click the Reply/Post button
    const postBtn = await page.$('[data-testid="tweetButtonInline"]') ||
                    await page.$('[data-testid="tweetButton"]');

    if (postBtn) {
      await postBtn.click();
      await page.waitForTimeout(3000);
      log(`  ✅ Replied to @${reply.username}: "${replyText}"`);
      return true;
    } else {
      // Fallback: Cmd+Enter
      await page.keyboard.down('Meta');
      await page.keyboard.press('Enter');
      await page.keyboard.up('Meta');
      await page.waitForTimeout(3000);
      log(`  ✅ Replied (Cmd+Enter) to @${reply.username}: "${replyText}"`);
      return true;
    }
  } catch (e) {
    log(`  ❌ Failed to reply to @${reply.username}: ${e.message}`);
    // Try to close any open modal
    try { await page.keyboard.press('Escape'); } catch (_) {}
    return false;
  }
}

// ═══════════════════════════════════════════════════════════════
//                    GET ORIGINAL TWEET TEXT
// ═══════════════════════════════════════════════════════════════

async function getOriginalTweetText(page) {
  return await page.evaluate(() => {
    const firstArticle = document.querySelector('article[data-testid="tweet"]');
    if (!firstArticle) return '';
    const textEl = firstArticle.querySelector('[data-testid="tweetText"]');
    return textEl?.innerText || '';
  });
}

// ═══════════════════════════════════════════════════════════════
//                    MAIN
// ═══════════════════════════════════════════════════════════════

async function main() {
  log('═══ X Reply Agent starting ═══');
  log(`Mode: ${CONFIG.dryRun ? 'DRY RUN' : 'LIVE'}`);

  const state = loadState();
  state.lastRun = new Date().toISOString();

  // Connect to browser
  const conn = await connectBrowser();
  if (!conn) {
    log('FATAL: Could not connect to browser');
    process.exit(1);
  }

  let context, page;
  try {
    if (conn.launched) {
      // We launched Chrome — context is directly available
      context = conn.context;
      page = await context.newPage();
    } else {
      // Connected via CDP
      const contexts = conn.browser.contexts();
      context = contexts[0];
      page = await context.newPage();
    }

    // 1. Find latest tweet
    const tweetUrl = await findLatestTweet(page);
    if (!tweetUrl) {
      log('No tweet found. Exiting.');
      return;
    }

    // 2. Scrape replies
    const allReplies = await scrapeReplies(page, tweetUrl);
    if (allReplies.length === 0) {
      log('No replies found. Exiting.');
      return;
    }

    // 3. Get original tweet text (for context)
    const originalText = await getOriginalTweetText(page);

    // 4. Filter
    const candidates = filterReplies(allReplies, state);
    log(`${candidates.length} candidates after filtering`);

    if (candidates.length === 0) {
      log('Nothing new to reply to. Exiting.');
      return;
    }

    // 5. Generate & post replies
    let posted = 0;
    for (const reply of candidates) {
      log(`Processing @${reply.username}: "${reply.text.substring(0, 60)}..."`);

      // Generate reply
      const replyText = await generateReply(originalText, reply);
      if (!replyText) {
        log(`  Skipped (not worth replying)`);
        state.stats.skipped = (state.stats.skipped || 0) + 1;
        // Still mark as processed so we don't retry
        const id = reply.tweetId || `${reply.username}-${reply.text.substring(0, 30)}`;
        state.repliedTo.push(id);
        continue;
      }

      // Post it
      const success = await postReply(page, reply, replyText);
      if (success) {
        posted++;
        state.stats.total = (state.stats.total || 0) + 1;
        const id = reply.tweetId || `${reply.username}-${reply.text.substring(0, 30)}`;
        state.repliedTo.push(id);
      }

      // Brief pause between replies
      if (posted < candidates.length) {
        await page.waitForTimeout(3000);
      }
    }

    log(`═══ Done: ${posted} replies posted, ${candidates.length - posted} skipped ═══`);

  } catch (e) {
    log(`ERROR: ${e.message}`);
    if (CONFIG.debug) console.error(e.stack);
  } finally {
    // Cleanup
    try {
      if (page) await page.close();
      if (conn.launched && conn.context) await conn.context.close();
      else if (conn.browser) await conn.browser.close();
    } catch (_) {}

    saveState(state);
  }
}

main().catch(e => {
  log(`FATAL: ${e.message}`);
  process.exit(1);
});

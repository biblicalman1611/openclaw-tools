#!/usr/bin/env node
// x-outbound-agent.js — Outbound Reply Guy Agent for @Biblicalman
// Monitors X List timeline, finds quality tweets, replies strategically
// Uses Bird CLI + Claude Haiku for cost-effective engagement at scale

const { execSync } = require('child_process');
const https = require('https');
const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════
//                    CONFIGURATION
// ═══════════════════════════════════════════════════════════════

const SCRIPT_DIR = __dirname;
const DATA_DIR = path.join(SCRIPT_DIR, '..', 'data');
const LOG_DIR = path.join(SCRIPT_DIR, '..', 'logs');
const STATE_FILE = path.join(DATA_DIR, 'x-outbound-state.json');
const LOG_FILE = path.join(LOG_DIR, 'x-outbound-agent.log');

const CONFIG = {
  listId: '1768991813094842495',
  username: 'Biblicalman',
  userId: '1759642430649823232',
  
  // Targeting filters
  minLikes: 5,                    // Skip low-engagement tweets
  maxReplies: 20,                 // Avoid buried threads
  maxAgeHours: 6,                 // Freshness matters
  
  // Reply limits
  maxRepliesPerRun: 8,            // Don't spam
  
  // Modes
  dryRun: !process.argv.includes('--live'),
  debug: process.argv.includes('--debug'),
  quiet: process.argv.includes('--quiet'),
};

// ═══════════════════════════════════════════════════════════════
//                    VOICE DNA
// ═══════════════════════════════════════════════════════════════

const VOICE_PROMPT = `You are Biblical Man (@Biblicalman) engaging strategically on X.

This is OUTBOUND reply-guy strategy — you're jumping into someone else's conversation to add value and get visibility.

Your REAL reply voice (match this energy):
- "Amen, brother. Don't neglect it"
- "Appreciate the read, and yes you should."
- "Get in the Bible, that's how God speaks."
- "Thanks for reading"
- "Brother, thank you. Writing this one cost me."
- "That's a great word right there"

RULES:
- AIM FOR 8-15 WORDS. Max 25 words. Brevity is your edge.
- One sentence. Two max.
- Sound like a real dude texting, not a pastor giving a sermon
- Use contractions (don't, that's, it's, won't)
- Use commas. Never em dashes, semicolons, or colons
- "Amen" and "brother" are natural for you
- Add value — deepen, twist, or offer perspective. Don't just "great post"

BANNED (never use):
"great point", "thanks for sharing", "absolutely", "I appreciate",
"in today's world", "let's dive in", "important to note",
"This is the part most people miss", "Sit with that", "Exactly.",
"cuts deep", "holy fire", "calls us back", "truth bomb"

SCRIPTURE:
- DO NOT cite scripture unless the tweet is explicitly about the Bible
- NO "KJV" labels, NO verse references (e.g., "1 John 4:19")
- If scripture fits naturally, paraphrase it conversationally

WHEN TO SKIP (return exactly: SKIP):
- Political hot takes outside faith/family (you're not a political account)
- Low-effort tweets (just emojis, links with no context)
- Tweets asking for engagement bait ("Comment your favorite verse!")
- Anything you can't add genuine value to
- Trolls, rage bait, or divisive culture war nonsense

Your goal: be the guy who says something worth reading. Build genuine connections, not follower counts.

If you can't add value, return exactly: SKIP`;

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
    if (state.repliedTo.length > 1000) state.repliedTo = state.repliedTo.slice(-1000);
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch (e) { log(`State save error: ${e.message}`); }
}

// ═══════════════════════════════════════════════════════════════
//                    BIRD CLI WRAPPER
// ═══════════════════════════════════════════════════════════════

function birdJson(args) {
  try {
    const cmd = `bird ${args} --json --plain`;
    const result = execSync(cmd, {
      encoding: 'utf8',
      timeout: 30000,
      env: { ...process.env, NO_COLOR: '1' },
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return JSON.parse(result.trim());
  } catch (e) {
    log(`Bird JSON error (${args.substring(0, 30)}): ${(e.stderr || e.message).substring(0, 200)}`);
    return null;
  }
}

function bird(args) {
  try {
    const result = execSync(`bird ${args} --plain`, {
      encoding: 'utf8',
      timeout: 30000,
      env: { ...process.env, NO_COLOR: '1' },
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return result.trim();
  } catch (e) {
    log(`Bird error (${args.substring(0, 30)}): ${(e.stderr || e.message).substring(0, 200)}`);
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════
//                    CLAUDE API (Haiku)
// ═══════════════════════════════════════════════════════════════

async function callHaiku(prompt) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) { log('ERROR: No ANTHROPIC_API_KEY'); return null; }

  return new Promise((resolve) => {
    const data = JSON.stringify({
      model: 'claude-3-5-haiku-latest',
      max_tokens: 100,
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
            resolve((result.content && result.content[0] && result.content[0].text || '').trim() || null);
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
//                    LIST TIMELINE FETCHING
// ═══════════════════════════════════════════════════════════════

function getListTimeline() {
  log(`Fetching tweets from list ${CONFIG.listId}...`);
  const tweets = birdJson(`list-timeline ${CONFIG.listId}`);
  if (!tweets) {
    log('Failed to fetch list timeline');
    return [];
  }

  // Filter to original tweets only
  const original = tweets.filter(t => {
    // Skip retweets
    if (t.text && t.text.startsWith('RT ')) return false;
    // Must have author
    if (!t.author) return false;
    // Must have text
    if (!t.text || t.text.length < 10) return false;
    return true;
  });

  log(`Found ${original.length} original tweets (${tweets.length} total)`);
  return original;
}

// ═══════════════════════════════════════════════════════════════
//                    TWEET FILTERING
// ═══════════════════════════════════════════════════════════════

function filterTweets(tweets, state) {
  const cutoff = Date.now() - (CONFIG.maxAgeHours * 60 * 60 * 1000);
  const repliedSet = new Set(state.repliedTo);

  const candidates = tweets.filter(t => {
    // Skip if already replied
    if (repliedSet.has(t.id)) return false;

    // Skip our own tweets
    if (t.author.username.toLowerCase() === CONFIG.username.toLowerCase()) return false;
    if (t.authorId === CONFIG.userId) return false;

    // Skip too old
    if (t.createdAt) {
      const tweetTime = new Date(t.createdAt).getTime();
      if (tweetTime < cutoff) return false;
    }

    // Skip low engagement
    const likes = t.likeCount || 0;
    if (likes < CONFIG.minLikes) return false;

    // Skip high reply count (buried)
    const replies = t.replyCount || 0;
    if (replies > CONFIG.maxReplies) return false;

    // Skip link-only tweets
    if (t.text.match(/^https?:\/\//)) return false;

    return true;
  });

  log(`${candidates.length} candidates after filtering`);
  return candidates.slice(0, CONFIG.maxRepliesPerRun);
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY GENERATION
// ═══════════════════════════════════════════════════════════════

async function generateReply(tweet) {
  const author = tweet.author.username;
  const tweetText = tweet.text.replace(/https?:\/\/\S+/g, '').trim(); // Strip links

  const prompt = `${VOICE_PROMPT}

TWEET FROM @${author}:
"${tweetText}"

Generate your reply (8-25 words). If not worth replying, say SKIP.`;

  const response = await callHaiku(prompt);
  if (!response) return null;

  const cleaned = response.trim();
  if (cleaned === 'SKIP' || cleaned.toUpperCase().includes('SKIP')) return null;

  // Remove quotes if Haiku wrapped it
  let final = cleaned.replace(/^["']|["']$/g, '').trim();
  if (final.length > 280) final = final.substring(0, 277) + '...';
  return final;
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY POSTING
// ═══════════════════════════════════════════════════════════════

function postReply(tweetId, text) {
  if (CONFIG.dryRun) {
    log(`  [DRY RUN] Would reply to ${tweetId}: "${text}"`);
    return true;
  }

  try {
    const escaped = text.replace(/"/g, '\\"');
    const result = bird(`reply ${tweetId} "${escaped}"`);
    if (result !== null) {
      log(`  ✅ Posted reply to ${tweetId}: "${text}"`);
      return true;
    } else {
      log(`  ❌ Bird reply command failed for ${tweetId}`);
      return false;
    }
  } catch (e) {
    log(`  ❌ Post error: ${e.message}`);
    return false;
  }
}

// ═══════════════════════════════════════════════════════════════
//                    MAIN
// ═══════════════════════════════════════════════════════════════

async function main() {
  log('═══ X Outbound Reply Agent starting ═══');
  log(`Mode: ${CONFIG.dryRun ? 'DRY RUN (pass --live to post)' : 'LIVE'}`);

  // Verify Bird auth
  const whoami = bird('whoami');
  if (!whoami || !whoami.includes(CONFIG.username)) {
    log(`FATAL: Bird auth failed. Got: ${whoami}`);
    process.exit(1);
  }
  log(`Authenticated as @${CONFIG.username}`);

  const state = loadState();
  state.lastRun = new Date().toISOString();

  // Get list timeline
  const allTweets = getListTimeline();
  if (allTweets.length === 0) {
    log('No tweets found. Exiting.');
    saveState(state);
    return;
  }

  // Filter to actionable targets
  const candidates = filterTweets(allTweets, state);
  if (candidates.length === 0) {
    log('No candidates to reply to. Exiting.');
    saveState(state);
    return;
  }

  // Process each candidate
  let posted = 0;
  for (const tweet of candidates) {
    const author = tweet.author.username;
    const age = Math.floor((Date.now() - new Date(tweet.createdAt).getTime()) / 3600000);
    const preview = tweet.text.substring(0, 60).replace(/\n/g, ' ');
    log(`Processing @${author} (${age}h ago, ${tweet.likeCount}♥ ${tweet.replyCount}💬): "${preview}..."`);

    const generatedReply = await generateReply(tweet);
    if (!generatedReply) {
      log('  Skipped (SKIP or not worth replying)');
      state.stats.skipped = (state.stats.skipped || 0) + 1;
      state.repliedTo.push(tweet.id);
      continue;
    }

    const success = postReply(tweet.id, generatedReply);
    if (success) {
      posted++;
      state.stats.total = (state.stats.total || 0) + 1;
      state.repliedTo.push(tweet.id);
    }

    // Rate limit between replies
    if (posted < candidates.length) {
      await new Promise(r => setTimeout(r, 3000));
    }
  }

  log(`═══ Done: ${posted} replies ${CONFIG.dryRun ? '(dry run)' : 'posted'}, ${candidates.length - posted} skipped ═══`);
  saveState(state);
}

main().catch(e => { log(`FATAL: ${e.message}`); process.exit(1); });

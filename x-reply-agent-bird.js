#!/usr/bin/env node
// x-reply-agent-bird.js — X Reply Bot for @Biblicalman (Bird CLI edition)
// Uses Bird CLI for Twitter API, Claude Haiku for reply generation
// No Chrome needed. Clean cron execution every 20 minutes.

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
const STATE_FILE = path.join(DATA_DIR, 'x-reply-state.json');
const LOG_FILE = path.join(LOG_DIR, 'x-reply-agent.log');

const CONFIG = {
  username: 'Biblicalman',
  userId: '1759642430649823232',
  maxRepliesPerRun: 3,
  skipOlderThanHours: 24,
  dryRun: process.argv.includes('--dry-run'),
  debug: process.argv.includes('--debug'),
  quiet: process.argv.includes('--quiet'),
  live: process.argv.includes('--live'),
};

// If --live is passed, override dryRun
if (CONFIG.live) CONFIG.dryRun = false;

// ═══════════════════════════════════════════════════════════════
//                    VOICE DNA (reply-specific)
// ═══════════════════════════════════════════════════════════════

const VOICE_PROMPT = `You are Biblical Man (@Biblicalman) replying on X (Twitter).

VOICE:
- Short sentences. 8 words avg. Fragments = power.
- Direct. Zero hedging. No filler.
- Use contractions (don't, that's, it's, won't)
- Use commas, NOT em dashes (—) or semicolons
- "Amen" and "brother" are natural for you
- KJV only for any scripture references.

BANNED PHRASES (never use these):
"great point", "thanks for sharing", "absolutely", "I appreciate",
"in today's world", "let's dive in", "important to note",
"This is the part most people miss", "Sit with that", "Exactly."

REPLY STYLE:
- PRAISE/THANKS → "Appreciate the read" or "Thanks for reading" + brief personal touch
- AGREEMENT → "Amen, brother" + deepen or twist, don't just echo
- PERSONAL SHARE → Use their first name if visible. Brief, warm. "Amen, [Name]. [response]"
- QUESTION → One direct answer, maybe scripture
- CHALLENGE → Stand firm, no defensiveness, binary choice
- EMOTIONAL → Honor it briefly. "Brother, thank you. [connect back]"
- TROLL/SPAM → return exactly: SKIP
- EMOJI-ONLY (just 👍❤️🔥 etc) → return exactly: SKIP
- SIMPLE "Amen" with nothing else → return exactly: SKIP

LENGTH:
- Quick acknowledgment: 3-10 words
- Standard reply: 10-25 words
- Deep response (personal share): 25-50 words

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
    if (state.repliedTo.length > 500) state.repliedTo = state.repliedTo.slice(-500);
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch (e) { log(`State save error: ${e.message}`); }
}

// ═══════════════════════════════════════════════════════════════
//                    BIRD CLI WRAPPER
// ═══════════════════════════════════════════════════════════════

function bird(args) {
  try {
    const cmd = `bird ${args} --plain 2>/dev/null`;
    const result = execSync(cmd, {
      encoding: 'utf8',
      timeout: 30000,
      env: { ...process.env, NO_COLOR: '1' }
    });
    return result.trim();
  } catch (e) {
    log(`Bird error: ${e.message}`);
    return null;
  }
}

function birdJson(args) {
  try {
    const cmd = `bird ${args} --json --plain 2>/dev/null`;
    const result = execSync(cmd, {
      encoding: 'utf8',
      timeout: 30000,
      env: { ...process.env, NO_COLOR: '1' }
    });
    return JSON.parse(result.trim());
  } catch (e) {
    log(`Bird JSON error: ${e.message}`);
    return null;
  }
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
//                    TWEET DISCOVERY (via Bird)
// ═══════════════════════════════════════════════════════════════

function getLatestTweet() {
  log(`Fetching latest tweets from @${CONFIG.username}...`);
  const tweets = birdJson(`user-tweets @${CONFIG.username}`);
  if (!tweets || tweets.length === 0) {
    log('No tweets found');
    return null;
  }

  // Find the most recent non-reply, non-retweet
  for (const tweet of tweets) {
    // Skip retweets
    if (tweet.text && tweet.text.startsWith('RT @')) continue;
    // Skip replies to others (but allow self-threads)
    if (tweet.inReplyToUserId && tweet.inReplyToUserId !== CONFIG.userId) continue;

    log(`Latest tweet [${tweet.id}]: "${(tweet.text || '').substring(0, 80)}..."`);
    return tweet;
  }

  // Fallback to first tweet
  const t = tweets[0];
  log(`Fallback tweet [${t.id}]: "${(t.text || '').substring(0, 80)}..."`);
  return t;
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY FETCHING (via Bird)
// ═══════════════════════════════════════════════════════════════

function getReplies(tweetId) {
  log(`Fetching replies to tweet ${tweetId}...`);
  const replies = birdJson(`replies ${tweetId}`);
  if (!replies) {
    log('Failed to fetch replies');
    return [];
  }

  // Filter out our own replies and non-reply tweets
  const validReplies = replies.filter(r => {
    // Must have user info
    if (!r.user) return false;
    // Must not be from us
    if (r.user.screenName?.toLowerCase() === CONFIG.username.toLowerCase()) return false;
    if (r.user.id === CONFIG.userId) return false;
    // Must have text
    if (!r.text || r.text.length < 2) return false;
    return true;
  });

  log(`Found ${validReplies.length} replies from others (${replies.length} total)`);
  return validReplies;
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY FILTERING
// ═══════════════════════════════════════════════════════════════

function filterReplies(replies, state) {
  const cutoff = Date.now() - (CONFIG.skipOlderThanHours * 60 * 60 * 1000);
  const repliedSet = new Set(state.repliedTo);

  return replies.filter(r => {
    // Skip already replied
    if (repliedSet.has(r.id)) return false;

    // Skip too old
    if (r.createdAt) {
      const replyTime = new Date(r.createdAt).getTime();
      if (replyTime < cutoff) return false;
    }

    return true;
  }).slice(0, CONFIG.maxRepliesPerRun);
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY GENERATION
// ═══════════════════════════════════════════════════════════════

async function generateReply(originalTweetText, reply) {
  const replyUser = reply.user?.screenName || 'unknown';
  const replyName = reply.user?.name || replyUser;
  const replyText = (reply.text || '').replace(/@\w+\s*/g, '').trim(); // Strip @mentions

  const prompt = `${VOICE_PROMPT}

ORIGINAL TWEET (yours):
"${(originalTweetText || '').substring(0, 300)}"

REPLY FROM @${replyUser} (${replyName}):
"${replyText}"

Generate your reply (under 200 chars). If not worth replying, say SKIP.`;

  const response = await callHaiku(prompt);
  if (!response) return null;

  const cleaned = response.trim();
  if (cleaned === 'SKIP' || cleaned.includes('SKIP')) return null;

  // Remove quotes if Haiku wrapped it
  let final = cleaned.replace(/^["']|["']$/g, '').trim();
  if (final.length > 280) final = final.substring(0, 277) + '...';
  return final;
}

// ═══════════════════════════════════════════════════════════════
//                    REPLY POSTING (via Bird)
// ═══════════════════════════════════════════════════════════════

function postReply(replyToId, text) {
  if (CONFIG.dryRun) {
    log(`  [DRY RUN] Would reply to ${replyToId}: "${text}"`);
    return true;
  }

  try {
    // Escape quotes in the reply text for shell
    const escaped = text.replace(/"/g, '\\"').replace(/'/g, "'\\''");
    const result = bird(`reply ${replyToId} "${escaped}"`);
    if (result !== null) {
      log(`  ✅ Posted reply to ${replyToId}: "${text}"`);
      return true;
    } else {
      log(`  ❌ Bird reply command failed for ${replyToId}`);
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
  log('═══ X Reply Agent (Bird) starting ═══');
  log(`Mode: ${CONFIG.dryRun ? 'DRY RUN' : 'LIVE'}`);

  // Verify Bird auth
  const whoami = bird('whoami');
  if (!whoami || !whoami.includes(CONFIG.username)) {
    log(`FATAL: Bird auth failed. Got: ${whoami}`);
    process.exit(1);
  }
  log(`Authenticated as @${CONFIG.username}`);

  const state = loadState();
  state.lastRun = new Date().toISOString();

  // Get latest tweet
  const latestTweet = getLatestTweet();
  if (!latestTweet) {
    log('No tweet found. Exiting.');
    saveState(state);
    return;
  }

  // Get replies
  const allReplies = getReplies(latestTweet.id);
  if (allReplies.length === 0) {
    log('No replies from others. Exiting.');
    saveState(state);
    return;
  }

  // Filter to actionable replies
  const candidates = filterReplies(allReplies, state);
  log(`${candidates.length} candidates after filtering`);

  if (candidates.length === 0) {
    log('Nothing new to reply to. Exiting.');
    saveState(state);
    return;
  }

  // Process each candidate
  let posted = 0;
  for (const reply of candidates) {
    const replyUser = reply.user?.screenName || 'unknown';
    const replyText = (reply.text || '').replace(/@\w+\s*/g, '').trim();
    log(`Processing @${replyUser}: "${replyText.substring(0, 60)}..."`);

    // SAFETY: Never reply to self
    if (replyUser.toLowerCase() === CONFIG.username.toLowerCase()) {
      log('  Skipped (self-reply prevention)');
      state.repliedTo.push(reply.id);
      continue;
    }

    const generatedReply = await generateReply(latestTweet.text, reply);
    if (!generatedReply) {
      log('  Skipped (not worth replying or SKIP)');
      state.stats.skipped = (state.stats.skipped || 0) + 1;
      state.repliedTo.push(reply.id);
      continue;
    }

    const success = postReply(reply.id, generatedReply);
    if (success) {
      posted++;
      state.stats.total = (state.stats.total || 0) + 1;
      state.repliedTo.push(reply.id);
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

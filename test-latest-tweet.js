#!/usr/bin/env node
// Quick test to find the latest tweet

const { chromium } = require('playwright');

async function test() {
  console.log('Testing latest tweet finder...');
  
  try {
    // Try to connect via CDP first
    const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
    const context = browser.contexts()[0];
    const page = await context.newPage();
    
    // Clear cache and force refresh
    await page.context().clearCookies();
    
    const timestamp = Date.now();
    await page.goto(`https://x.com/Biblicalman?t=${timestamp}`, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    
    // Force refresh
    await page.keyboard.down('Meta');
    await page.keyboard.press('r');
    await page.keyboard.up('Meta');
    
    await page.waitForTimeout(6000);
    
    // Get ALL tweets for debugging
    const tweets = await page.evaluate(() => {
      const articles = document.querySelectorAll('article[data-testid="tweet"]');
      const results = [];
      
      for (let i = 0; i < Math.min(5, articles.length); i++) {
        const article = articles[i];
        const links = article.querySelectorAll('a[href*="/status/"]');
        const timeEl = article.querySelector('time');
        const textEl = article.querySelector('[data-testid="tweetText"]');
        
        for (const link of links) {
          const href = link.getAttribute('href');
          if (href && href.includes('/Biblicalman/status/')) {
            results.push({
              position: i,
              url: 'https://x.com' + href,
              time: timeEl?.getAttribute('datetime'),
              text: textEl?.innerText?.substring(0, 100) || '',
              tweetId: href.match(/\/status\/(\d+)/)?.[1]
            });
            break;
          }
        }
      }
      
      return results;
    });
    
    console.log('\nFound tweets:');
    tweets.forEach((tweet, i) => {
      console.log(`\n${i + 1}. Tweet ID: ${tweet.tweetId}`);
      console.log(`   URL: ${tweet.url}`);
      console.log(`   Time: ${tweet.time}`);
      console.log(`   Text: "${tweet.text}..."`);
      
      if (tweet.tweetId === '2017279405752549511') {
        console.log('   ⚠️  THIS IS THE OLD STUCK TWEET!');
      }
    });
    
    const latest = tweets.find(t => t.tweetId !== '2017279405752549511');
    if (latest) {
      console.log('\n✅ LATEST TWEET (ignoring stuck one):');
      console.log(`   ID: ${latest.tweetId}`);
      console.log(`   URL: ${latest.url}`);
      console.log(`   Text: "${latest.text}..."`);
    } else {
      console.log('\n❌ ERROR: Could not find a tweet other than the stuck one!');
    }
    
    await page.close();
    await browser.close();
    
  } catch (error) {
    console.error('Error:', error.message);
    console.log('\nTrying to launch Chrome instead of connecting...');
    
    // Fallback: launch Chrome
    const context = await chromium.launchPersistentContext('../profiles/x-scanner', {
      headless: false,
      channel: 'chrome',
      viewport: { width: 1280, height: 900 },
    });
    
    const page = await context.newPage();
    await page.goto('https://x.com/Biblicalman');
    console.log('Chrome launched. Check the browser window.');
    
    setTimeout(async () => {
      await context.close();
    }, 30000);
  }
}

test();
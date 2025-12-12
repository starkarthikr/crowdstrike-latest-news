#!/usr/bin/env python3
"""
CrowdStrike News & Blog RSS Feed Monitor
Fetches latest updates from multiple CrowdStrike RSS feeds
"""

import feedparser
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# CrowdStrike RSS Feeds
FEEDS = {
    'main_blog': 'https://www.crowdstrike.com/blog/feed/',
    'threat_intel': 'https://www.crowdstrike.com/blog/category/threat-intel-research/feed/',
    'adversary_universe': 'https://www.crowdstrike.com/blog/category/adversary-universe/feed/',
    'cloud_security': 'https://www.crowdstrike.com/blog/category/cloud-security/feed/',
    'endpoint_security': 'https://www.crowdstrike.com/blog/category/endpoint-security/feed/',
    'industry_news': 'https://www.crowdstrike.com/blog/category/industry-news/feed/',
}

OUTPUT_DIR = Path('crowdstrike_updates')
OUTPUT_DIR.mkdir(exist_ok=True)

def fetch_feed(feed_url, feed_name):
    """Fetch and parse RSS feed"""
    try:
        print(f"Fetching {feed_name} from {feed_url}")
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            print(f"Warning: Feed parsing issue for {feed_name}")
            
        return feed
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
        return None

def is_recent(published_date, days=7):
    """Check if article is from last N days"""
    try:
        if hasattr(published_date, 'timetuple'):
            pub_date = datetime(*published_date.timetuple()[:6])
        else:
            return True  # Include if we can't parse date
            
        cutoff = datetime.now() - timedelta(days=days)
        return pub_date >= cutoff
    except:
        return True

def extract_article_summary(link):
    """Extract article summary from webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content')
            
        # Fallback to og:description
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc.get('content')
            
        return None
    except:
        return None

def process_feeds():
    """Process all RSS feeds and generate reports"""
    all_articles = []
    recent_articles = []
    
    for feed_name, feed_url in FEEDS.items():
        feed = fetch_feed(feed_url, feed_name)
        
        if not feed or not hasattr(feed, 'entries'):
            continue
            
        print(f"Found {len(feed.entries)} entries in {feed_name}")
        
        for entry in feed.entries[:10]:  # Limit to 10 most recent per feed
            article = {
                'category': feed_name,
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', ''),
                'published': entry.get('published', 'Unknown'),
                'summary': entry.get('summary', ''),
                'authors': [author.get('name', '') for author in entry.get('authors', [])],
            }
            
            # Check if recent (last 7 days)
            if hasattr(entry, 'published_parsed') and is_recent(entry.published_parsed, days=7):
                recent_articles.append(article)
                
            all_articles.append(article)
    
    return all_articles, recent_articles

def save_json_report(articles, filename):
    """Save articles as JSON"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(articles)} articles to {filepath}")

def generate_markdown_report(recent_articles):
    """Generate Markdown report of recent articles"""
    md_content = f"""# CrowdStrike Latest Updates

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Recent Articles (Last 7 Days)

"""
    
    if not recent_articles:
        md_content += "*No new articles in the last 7 days.*\n"
    else:
        # Group by category
        by_category = {}
        for article in recent_articles:
            cat = article['category'].replace('_', ' ').title()
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(article)
        
        for category, articles in sorted(by_category.items()):
            md_content += f"\n### {category}\n\n"
            for article in articles:
                md_content += f"- **[{article['title']}]({article['link']})**\n"
                md_content += f"  - Published: {article['published']}\n"
                if article['authors']:
                    md_content += f"  - Authors: {', '.join(article['authors'])}\n"
                if article['summary']:
                    # Truncate summary
                    summary = article['summary'][:200] + '...' if len(article['summary']) > 200 else article['summary']
                    md_content += f"  - {summary}\n"
                md_content += "\n"
    
    md_content += f"""
---

## RSS Feeds Monitored

"""
    for feed_name, feed_url in FEEDS.items():
        md_content += f"- **{feed_name.replace('_', ' ').title()}**: [{feed_url}]({feed_url})\n"
    
    md_content += f"""
---

*This report is automatically generated every 6 hours by GitHub Actions.*
*Repository: [CrowdStrike Monitor](https://github.com/starkarthikr/crowdstrike-monitor)*
"""
    
    # Save markdown
    with open('CROWDSTRIKE_UPDATES.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Generated Markdown report with {len(recent_articles)} recent articles")

def main():
    print("=" * 60)
    print("CrowdStrike News Monitor - Starting")
    print("=" * 60)
    
    # Fetch all feeds
    all_articles, recent_articles = process_feeds()
    
    # Save full archive as JSON
    save_json_report(all_articles, 'all_articles.json')
    save_json_report(recent_articles, 'recent_articles.json')
    
    # Generate Markdown report
    generate_markdown_report(recent_articles)
    
    print("=" * 60)
    print(f"Total Articles: {len(all_articles)}")
    print(f"Recent Articles (7 days): {len(recent_articles)}")
    print("=" * 60)

if __name__ == '__main__':
    main()

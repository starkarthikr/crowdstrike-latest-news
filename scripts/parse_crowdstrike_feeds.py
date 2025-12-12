#!/usr/bin/env python3
"""
CrowdStrike News & Blog RSS Feed Monitor
Fetches latest updates from multiple CrowdStrike RSS feeds
Generates AI-style summaries from article content
"""

import feedparser
import json
import re
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

def clean_html_text(html_text):
    """Remove HTML tags and clean text"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[\r\n\t]', ' ', text)
    return text.strip()

def extract_key_sentences(text, max_sentences=2):
    """Extract key sentences from text for summarization"""
    if not text:
        return None
        
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return None
    
    # Take first few sentences as summary
    summary_sentences = sentences[:max_sentences]
    summary = '. '.join(summary_sentences)
    
    # Limit to reasonable length
    if len(summary) > 250:
        summary = summary[:247] + '...'
    elif not summary.endswith('.'):
        summary += '.'
        
    return summary

def generate_ai_summary(title, description, content):
    """
    Generate a concise AI-style summary from article content
    Uses extractive summarization approach
    """
    # Start with RSS description if available
    if description:
        clean_desc = clean_html_text(description)
        summary = extract_key_sentences(clean_desc, max_sentences=2)
        if summary:
            return summary
    
    # Fallback to content extraction
    if content:
        clean_content = clean_html_text(content)
        summary = extract_key_sentences(clean_content, max_sentences=2)
        if summary:
            return summary
    
    # Last resort: use title as basis
    return f"Article about {title.lower()}."

def extract_article_content(link):
    """Extract full article content from webpage for better summarization"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(link, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple methods to extract content
        content = None
        
        # Method 1: Look for article content
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text() for p in paragraphs[:3]])
        
        # Method 2: Meta description
        if not content:
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                content = meta_desc.get('content')
        
        # Method 3: og:description
        if not content:
            og_desc = soup.find('meta', {'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                content = og_desc.get('content')
        
        return content
    except Exception as e:
        print(f"  Warning: Could not extract content from {link}: {e}")
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
            print(f"  Processing: {entry.get('title', 'No Title')[:50]}...")
            
            # Get content for summarization
            description = entry.get('summary', '')
            content = entry.get('content', [{}])[0].get('value', '') if 'content' in entry else ''
            
            # Extract full article content for better summaries (only for recent articles)
            full_content = None
            if hasattr(entry, 'published_parsed') and is_recent(entry.published_parsed, days=7):
                full_content = extract_article_content(entry.get('link', ''))
            
            # Generate AI summary
            ai_summary = generate_ai_summary(
                entry.get('title', ''),
                description or full_content,
                content
            )
            
            article = {
                'category': feed_name,
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', ''),
                'published': entry.get('published', 'Unknown'),
                'summary': description,
                'ai_summary': ai_summary,  # New AI-generated summary
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
    """Generate Markdown report of recent articles with AI summaries"""
    md_content = f"""# 🛡️ CrowdStrike Latest Updates

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 📰 Recent Articles (Last 7 Days)

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
            for idx, article in enumerate(articles, 1):
                md_content += f"#### {idx}. [{article['title']}]({article['link']})\n\n"
                
                # Add metadata
                md_content += f"**Published:** {article['published']}  \n"
                if article['authors']:
                    md_content += f"**Authors:** {', '.join(article['authors'])}  \n"
                
                # Add AI-generated summary
                if article.get('ai_summary'):
                    md_content += f"\n**🤖 Summary:** {article['ai_summary']}\n"
                
                md_content += "\n---\n\n"
    
    md_content += f"""
## 📡 RSS Feeds Monitored

"""
    for feed_name, feed_url in FEEDS.items():
        md_content += f"- **{feed_name.replace('_', ' ').title()}**: [{feed_url}]({feed_url})\n"
    
    md_content += f"""
---

*🤖 This report is automatically generated every 6 hours by GitHub Actions with AI-powered summarization.*  
*Repository: [CrowdStrike Monitor](https://github.com/starkarthikr/crowdstrike-monitor)*
"""
    
    # Save markdown
    with open('CROWDSTRIKE_UPDATES.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Generated Markdown report with {len(recent_articles)} recent articles")

def main():
    print("=" * 60)
    print("CrowdStrike News Monitor - Starting (AI Summaries Enabled)")
    print("=" * 60)
    
    # Fetch all feeds
    all_articles, recent_articles = process_feeds()
    
    # Save full archive as JSON
    save_json_report(all_articles, 'all_articles.json')
    save_json_report(recent_articles, 'recent_articles.json')
    
    # Generate Markdown report with AI summaries
    generate_markdown_report(recent_articles)
    
    print("=" * 60)
    print(f"Total Articles: {len(all_articles)}")
    print(f"Recent Articles (7 days): {len(recent_articles)}")
    print(f"AI Summaries Generated: {sum(1 for a in recent_articles if a.get('ai_summary'))}")
    print("=" * 60)

if __name__ == '__main__':
    main()

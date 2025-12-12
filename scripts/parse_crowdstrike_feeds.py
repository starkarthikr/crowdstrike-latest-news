#!/usr/bin/env python3
"""
CrowdStrike News & Blog RSS Feed Monitor
Fetches latest updates from multiple CrowdStrike RSS feeds
Generates structured analysis: Issue, Solution, Cause, Timeline
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
            return True
            
        cutoff = datetime.now() - timedelta(days=days)
        return pub_date >= cutoff
    except:
        return True

def clean_html_text(html_text):
    """Remove HTML tags and clean text"""
    text = re.sub(r'<[^>]+>', '', html_text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\r\n\t]', ' ', text)
    return text.strip()

def extract_key_sentences(text, max_sentences=2):
    """Extract key sentences from text"""
    if not text:
        return None
        
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return None
    
    summary_sentences = sentences[:max_sentences]
    summary = '. '.join(summary_sentences)
    
    if len(summary) > 250:
        summary = summary[:247] + '...'
    elif not summary.endswith('.'):
        summary += '.'
        
    return summary

def analyze_article_structure(title, content, link):
    """
    Extract structured information: Issue, Solution, Cause, Timeline
    Uses keyword-based extraction and pattern matching
    """
    analysis = {
        'issue': None,
        'solution': None,
        'cause': None,
        'timeline': None
    }
    
    if not content:
        return analysis
    
    content_lower = content.lower()
    
    # Extract ISSUE
    issue_keywords = ['vulnerability', 'threat', 'attack', 'risk', 'flaw', 'exploit', 
                      'breach', 'malware', 'ransomware', 'zero-day', 'cve-', 'adversary',
                      'leakage', 'injection', 'disclosed', 'critical']
    
    for keyword in issue_keywords:
        if keyword in content_lower:
            # Find sentences containing the keyword
            sentences = re.split(r'[.!?]+', content)
            for sent in sentences:
                if keyword in sent.lower() and len(sent.strip()) > 30:
                    analysis['issue'] = sent.strip()[:200]
                    break
            if analysis['issue']:
                break
    
    # Fallback: Use title for issue if it contains security keywords
    if not analysis['issue']:
        for keyword in issue_keywords:
            if keyword in title.lower():
                analysis['issue'] = f"{title}"
                break
    
    # Extract SOLUTION/MITIGATION
    solution_keywords = ['mitigate', 'fix', 'patch', 'update', 'protect', 'defend',
                        'remediate', 'solution', 'recommendation', 'detection',
                        'prevention', 'security', 'safeguard', 'implement']
    
    for keyword in solution_keywords:
        if keyword in content_lower:
            sentences = re.split(r'[.!?]+', content)
            for sent in sentences:
                if keyword in sent.lower() and len(sent.strip()) > 30:
                    analysis['solution'] = sent.strip()[:200]
                    break
            if analysis['solution']:
                break
    
    # Extract CAUSE/ROOT CAUSE
    cause_keywords = ['caused by', 'due to', 'result of', 'stemming from', 'originates',
                     'attributed to', 'exploits', 'leverages', 'abuses', 'misconfiguration']
    
    for keyword in cause_keywords:
        if keyword in content_lower:
            # Find context around the keyword
            idx = content_lower.find(keyword)
            if idx != -1:
                # Extract sentence containing the cause
                start = max(0, content.rfind('.', 0, idx) + 1)
                end = content.find('.', idx)
                if end != -1:
                    analysis['cause'] = content[start:end].strip()[:200]
                    break
    
    # Extract TIMELINE
    # Look for date patterns and temporal keywords
    timeline_patterns = [
        r'(since|from|starting)\s+([A-Z][a-z]+\s+\d{4})',  # "since January 2024"
        r'(in|during)\s+([A-Z][a-z]+\s+\d{4})',  # "in December 2024"
        r'(\d{4})',  # Year alone
        r'(first|initially|recently|ongoing)\s+(detected|observed|discovered|identified)',
    ]
    
    for pattern in timeline_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            # Get surrounding context
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 100)
            context = content[start:end].strip()
            analysis['timeline'] = context[:150]
            break
    
    # Look for "active since" or "observed since" patterns
    if not analysis['timeline']:
        temporal_keywords = ['active since', 'observed since', 'discovered in', 
                           'first seen', 'reported in', 'disclosed on']
        for keyword in temporal_keywords:
            if keyword in content_lower:
                idx = content_lower.find(keyword)
                if idx != -1:
                    end = content.find('.', idx)
                    if end != -1:
                        analysis['timeline'] = content[idx:end].strip()[:150]
                        break
    
    return analysis

def extract_article_content(link):
    """Extract full article content from webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(link, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        content = None
        
        # Extract main article content
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text() for p in paragraphs[:10]])  # Get more content for analysis
        
        # Fallback methods
        if not content:
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                content = meta_desc.get('content')
        
        if not content:
            og_desc = soup.find('meta', {'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                content = og_desc.get('content')
        
        return content
    except Exception as e:
        print(f"  Warning: Could not extract content from {link}: {e}")
        return None

def generate_ai_summary(title, description, content):
    """Generate concise summary"""
    if description:
        clean_desc = clean_html_text(description)
        summary = extract_key_sentences(clean_desc, max_sentences=1)
        if summary:
            return summary
    
    if content:
        clean_content = clean_html_text(content)
        summary = extract_key_sentences(clean_content, max_sentences=1)
        if summary:
            return summary
    
    return f"Article about {title.lower()}."

def process_feeds():
    """Process all RSS feeds and generate reports"""
    all_articles = []
    recent_articles = []
    
    for feed_name, feed_url in FEEDS.items():
        feed = fetch_feed(feed_url, feed_name)
        
        if not feed or not hasattr(feed, 'entries'):
            continue
            
        print(f"Found {len(feed.entries)} entries in {feed_name}")
        
        for entry in feed.entries[:10]:
            print(f"  Processing: {entry.get('title', 'No Title')[:50]}...")
            
            description = entry.get('summary', '')
            content = entry.get('content', [{}])[0].get('value', '') if 'content' in entry else ''
            
            # Extract full article content for analysis
            full_content = None
            structured_analysis = None
            
            if hasattr(entry, 'published_parsed') and is_recent(entry.published_parsed, days=7):
                full_content = extract_article_content(entry.get('link', ''))
                if full_content:
                    structured_analysis = analyze_article_structure(
                        entry.get('title', ''),
                        full_content,
                        entry.get('link', '')
                    )
            
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
                'ai_summary': ai_summary,
                'authors': [author.get('name', '') for author in entry.get('authors', [])],
            }
            
            # Add structured analysis if available
            if structured_analysis:
                article['analysis'] = structured_analysis
            
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
    """Generate Markdown report with structured analysis"""
    md_content = f"""# 🛡️ CrowdStrike Latest Updates

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 📰 Recent Articles (Last 7 Days)

"""
    
    if not recent_articles:
        md_content += "*No new articles in the last 7 days.*\n"
    else:
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
                
                # Metadata
                md_content += f"**📅 Published:** {article['published']}  \n"
                if article['authors']:
                    md_content += f"**✍️ Authors:** {', '.join(article['authors'])}  \n"
                
                # AI Summary
                if article.get('ai_summary'):
                    md_content += f"\n**📝 Summary:** {article['ai_summary']}\n"
                
                # Structured Analysis
                if article.get('analysis'):
                    analysis = article['analysis']
                    md_content += "\n**🔍 Detailed Analysis:**\n\n"
                    
                    if analysis.get('issue'):
                        md_content += f"- **⚠️ Issue:** {analysis['issue']}\n"
                    
                    if analysis.get('cause'):
                        md_content += f"- **🔎 Cause:** {analysis['cause']}\n"
                    
                    if analysis.get('solution'):
                        md_content += f"- **✅ Solution:** {analysis['solution']}\n"
                    
                    if analysis.get('timeline'):
                        md_content += f"- **⏰ Timeline:** {analysis['timeline']}\n"
                
                md_content += "\n---\n\n"
    
    md_content += f"""
## 📡 RSS Feeds Monitored

"""
    for feed_name, feed_url in FEEDS.items():
        md_content += f"- **{feed_name.replace('_', ' ').title()}**: [{feed_url}]({feed_url})\n"
    
    md_content += f"""
---

*🤖 This report is automatically generated every 6 hours with AI-powered analysis.*  
*📊 Includes: Issue identification, Root cause analysis, Solutions, Timeline tracking*  
*Repository: [CrowdStrike Monitor](https://github.com/starkarthikr/crowdstrike-monitor)*
"""
    
    with open('CROWDSTRIKE_UPDATES.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Generated Markdown report with {len(recent_articles)} recent articles")

def main():
    print("=" * 60)
    print("CrowdStrike Monitor - Structured Analysis Mode")
    print("=" * 60)
    
    all_articles, recent_articles = process_feeds()
    
    save_json_report(all_articles, 'all_articles.json')
    save_json_report(recent_articles, 'recent_articles.json')
    
    generate_markdown_report(recent_articles)
    
    analyzed = sum(1 for a in recent_articles if a.get('analysis'))
    
    print("=" * 60)
    print(f"Total Articles: {len(all_articles)}")
    print(f"Recent Articles (7 days): {len(recent_articles)}")
    print(f"Structured Analysis: {analyzed}")
    print("=" * 60)

if __name__ == '__main__':
    main()

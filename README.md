# 🛡️ CrowdStrike News & Updates Monitor

[![CrowdStrike News Monitor](https://github.com/starkarthikr/crowdstrike-monitor/actions/workflows/crowdstrike-monitor.yml/badge.svg)](https://github.com/starkarthikr/crowdstrike-monitor/actions/workflows/crowdstrike-monitor.yml)

Automated monitoring of CrowdStrike news, blogs, threat intelligence, and security updates using GitHub Actions - **No API credentials required!**

## 🚀 Features

- ✅ **Zero API Setup**: Uses public RSS feeds, no authentication needed
- ⏰ **Automated Updates**: Runs every 6 hours via GitHub Actions
- 📊 **Multiple Feed Sources**: Monitors 6 different CrowdStrike RSS feeds
- 📝 **Markdown Reports**: Auto-generated human-readable updates
- 💾 **JSON Archives**: Structured data storage for all articles
- 🔍 **Smart Filtering**: Highlights articles from the last 7 days
- 🤖 **Fully Automated**: Set it and forget it

## 📡 Monitored RSS Feeds

This automation monitors the following CrowdStrike feeds:

1. **Main Blog**: Latest CrowdStrike blog posts
2. **Threat Intelligence**: Research on emerging threats
3. **Adversary Universe**: Threat actor profiles and TTPs
4. **Cloud Security**: Cloud-specific security insights
5. **Endpoint Security**: Endpoint protection updates
6. **Industry News**: General cybersecurity industry news

## 📋 How It Works

### Workflow Overview

```
┌─────────────────┐
│  GitHub Actions │
│  (Every 6 hrs)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Fetch RSS      │
│  Feeds (6)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse & Filter │
│  (Last 7 days)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate:      │
│  - Markdown     │
│  - JSON Reports │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Auto-commit    │
│  to Repository  │
└─────────────────┘
```

### Automated Schedule

- **Runs**: Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
- **Manual Trigger**: Available via GitHub Actions UI
- **Auto-commits**: Updates pushed automatically

## 📁 Repository Structure

```
crowdstrike-monitor/
├── .github/
│   └── workflows/
│       └── crowdstrike-monitor.yml    # GitHub Actions workflow
├── scripts/
│   └── parse_crowdstrike_feeds.py     # Python RSS parser
├── crowdstrike_updates/               # Auto-generated directory
│   ├── all_articles.json              # Full article archive
│   └── recent_articles.json           # Last 7 days articles
├── CROWDSTRIKE_UPDATES.md             # Human-readable report
├── requirements.txt                    # Python dependencies
└── README.md                          # This file
```

## 🔧 Setup Instructions

### Prerequisites

- GitHub account
- Repository with Actions enabled

### Installation

1. **Fork or Clone** this repository

2. **Enable GitHub Actions**:
   - Go to repository **Settings** → **Actions** → **General**
   - Enable "Read and write permissions" for workflows
   - Save changes

3. **Manual First Run** (Optional):
   - Go to **Actions** tab
   - Select "CrowdStrike News Monitor" workflow
   - Click "Run workflow"

4. **Done!** The workflow will now run automatically every 6 hours

## 📊 Viewing Results

### Markdown Report

View the human-readable report:
- **File**: [`CROWDSTRIKE_UPDATES.md`](./CROWDSTRIKE_UPDATES.md)
- **Contains**: Recent articles with titles, links, publish dates, and summaries

### JSON Data

Access structured data:
- **All Articles**: `crowdstrike_updates/all_articles.json`
- **Recent Articles**: `crowdstrike_updates/recent_articles.json`

### GitHub Actions Logs

- Navigate to **Actions** tab
- Click on latest workflow run
- View detailed logs of fetching and processing

## ⚙️ Customization

### Change Update Frequency

Edit `.github/workflows/crowdstrike-monitor.yml`:

```yaml
schedule:
  - cron: '0 */3 * * *'   # Every 3 hours
  # OR
  - cron: '0 8 * * *'     # Daily at 8 AM UTC
  # OR
  - cron: '0 0 * * 0'     # Weekly on Sunday
```

### Modify Lookback Period

Edit `scripts/parse_crowdstrike_feeds.py`:

```python
# Change from 7 days to desired period
if hasattr(entry, 'published_parsed') and is_recent(entry.published_parsed, days=14):
```

### Add More RSS Feeds

Edit the `FEEDS` dictionary in `scripts/parse_crowdstrike_feeds.py`:

```python
FEEDS = {
    'main_blog': 'https://www.crowdstrike.com/blog/feed/',
    'your_custom_feed': 'https://example.com/feed.xml',
    # Add more feeds here
}
```

## 🔔 Notifications (Optional)

### Email Notifications

Add email notification step to workflow:

```yaml
- name: Send Email Notification
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: New CrowdStrike Updates
    body: file://CROWDSTRIKE_UPDATES.md
    to: your-email@example.com
```

### Slack/Discord Webhooks

Add webhook notification to send updates to team channels.

## 🛠️ Technical Details

### Dependencies

- **feedparser**: RSS/Atom feed parsing
- **requests**: HTTP requests for web scraping
- **beautifulsoup4**: HTML parsing for metadata extraction
- **python-dateutil**: Date parsing utilities

### GitHub Actions

- **Runner**: Ubuntu Latest
- **Python Version**: 3.11
- **Permissions**: Contents (write), Issues (write)

## 📈 Use Cases

1. **Security Teams**: Stay updated on latest threats and vulnerabilities
2. **SOC Analysts**: Monitor CrowdStrike advisories and threat intelligence
3. **IT Professionals**: Track endpoint security updates
4. **Researchers**: Archive CrowdStrike publications for reference
5. **DevSecOps**: Integrate security news into CI/CD pipelines

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📜 License

MIT License - Feel free to use and modify as needed.

## ⚠️ Disclaimer

This is an unofficial monitoring tool. CrowdStrike® and Falcon® are registered trademarks of CrowdStrike, Inc. This project is not affiliated with or endorsed by CrowdStrike.

## 🔗 Related Links

- [CrowdStrike Official Website](https://www.crowdstrike.com/)
- [CrowdStrike Blog](https://www.crowdstrike.com/blog/)
- [CrowdStrike GitHub](https://github.com/CrowdStrike)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Made with ❤️ for the Cybersecurity Community**

*Last Updated: December 2025*

# Crypto RSS Agent & Digest System

An automated RSS feed processor that monitors crypto news sources, analyzes articles with AI, and creates hierarchical digest reports stored in a Supabase database.

## 🚀 Features

### RSS Processing
- **Automated RSS Processing**: Monitors multiple crypto news feeds
- **AI-Powered Analysis**: Generates summaries, sentiment analysis, and verdicts using OpenAI
- **Database Storage**: Stores articles and state in Supabase
- **Duplicate Prevention**: Avoids processing the same article twice
- **GitHub Actions**: Automated deployment with scheduled runs
- **Dynamic Feed Management**: Add/remove feeds through database

### Digest System
- **Daily Digests**: AI-generated summaries of daily crypto news
- **Weekly Digests**: Aggregated analysis of weekly developments
- **Monthly Digests**: Comprehensive monthly market analysis
- **Hierarchical Structure**: Each level builds on the previous
- **Sentiment Tracking**: Detailed sentiment breakdowns and trends
- **Trending Topics**: AI-identified trending topics and themes

## 📡 Supported Feeds

- **CoinTelegraph**: https://cointelegraph.com/rss
- **CoinDesk**: https://www.coindesk.com/arc/outboundfeeds/rss/
- **The Defiant**: https://thedefiant.io/feed/

## 🛠️ Setup

### 1. Prerequisites

- Python 3.13+
- Supabase account
- OpenAI API key

### 2. Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Database Setup

Run the SQL schema in your Supabase project:

```sql
-- See supabase_schema.sql for the complete schema
```

### 4. Local Development

```bash
# Install dependencies
uv sync

# Run the agent
uv run python main.py
```

## 🚀 Deployment

### GitHub Actions (Recommended)

1. **Fork this repository**
2. **Add secrets to your GitHub repo**:
   - Go to Settings → Secrets and variables → Actions
   - Add: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`
3. **Enable GitHub Actions** in your repo
4. **The workflow will run every 30 minutes automatically**

### Manual Deployment

```bash
# Install dependencies
uv sync

# Run once
uv run python main.py

# Run continuously (for servers)
uv run python -c "from main import run_polling; run_polling(30)"
```

## 📊 Database Schema

### Tables

#### RSS Processing
- **`crypto_news`**: Stores processed articles
- **`rss_state`**: Tracks last check time for each feed

#### Digest System
- **`daily_digests`**: Daily AI-generated summaries
- **`weekly_digests`**: Weekly aggregated analysis
- **`monthly_digests`**: Monthly comprehensive reports

### Key Fields

#### Articles (`crypto_news`)
- `title`: Article title
- `url`: Article URL (unique)
- `summary`: AI-generated bullet points
- `sentiment`: Positive/Negative/Neutral
- `verdict`: AI-generated forward-looking analysis
- `published_at`: Original publication date
- `created_at`: Processing timestamp

#### Daily Digests (`daily_digests`)
- `digest_date`: Date of the digest
- `summary`: AI-generated daily summary
- `sentiment`: Overall daily sentiment
- `verdict`: Forward-looking analysis
- `article_count`: Number of articles processed
- `sentiment_breakdown`: JSON breakdown of sentiments
- `trending_topics`: JSON array of top 5 trending topics

#### Weekly Digests (`weekly_digests`)
- `week_start_date`: Start of week (Monday)
- `week_end_date`: End of week (Sunday)
- `summary`: AI-generated weekly summary
- `sentiment`: Overall weekly sentiment
- `verdict`: Forward-looking analysis
- `daily_digest_count`: Number of daily digests processed
- `sentiment_breakdown`: JSON breakdown of sentiments
- `trending_topics`: JSON array of top 6 trending topics

#### Monthly Digests (`monthly_digests`)
- `month_year`: Month identifier (e.g., "2024-01")
- `summary`: AI-generated monthly summary
- `sentiment`: Overall monthly sentiment
- `verdict`: Forward-looking analysis
- `weekly_digest_count`: Number of weekly digests processed
- `sentiment_breakdown`: JSON breakdown of sentiments
- `trending_topics`: JSON array of top 8 trending topics

## 🔧 Core Functions

### RSS Agent
The RSS agent automatically:
- **Processes new articles** from configured feeds
- **Skips duplicates** to avoid reprocessing
- **Stores AI analysis** in Supabase database
- **Tracks state** to only process new content

### Digest Agents
The digest system automatically:
- **Daily Agent**: Processes yesterday's articles into daily summaries
- **Weekly Agent**: Aggregates daily digests into weekly analysis
- **Monthly Agent**: Consolidates weekly digests into monthly reports
- **AI Analysis**: Each digest includes sentiment, themes, and forward-looking verdicts
- **Hierarchical Processing**: Each level builds on the previous level's data

## 🚀 Usage

### Running Individual Agents

```bash
# Run RSS agent (processes new articles)
uv run python main.py

# Run daily digest (processes yesterday's articles)
uv run python daily_digest_agent.py

# Run weekly digest (processes last week's daily digests)
uv run python weekly_digest_agent.py

# Run monthly digest (processes last month's weekly digests)
uv run python monthly_digest_agent.py

# Run all digest agents
uv run python digest_orchestrator.py all

# Run specific digest type
uv run python digest_orchestrator.py daily
uv run python digest_orchestrator.py weekly
uv run python digest_orchestrator.py monthly
```

### GitHub Actions Scheduling

The system includes automated scheduling:

- **RSS Agent**: Runs every 2 hours
- **Daily Digest**: Runs daily at 1:00 AM UTC
- **Weekly Digest**: Runs Sundays at 2:00 AM UTC
- **Monthly Digest**: Runs 1st of each month at 3:00 AM UTC

You can also trigger manual runs through GitHub Actions workflow dispatch.

## 📁 Project Structure

```
crypto_rss_agent/
├── main.py                    # RSS agent (processes articles)
├── schemas.py                 # Pydantic models for all data structures
├── daily_digest_agent.py      # Daily digest agent
├── weekly_digest_agent.py     # Weekly digest agent
├── monthly_digest_agent.py    # Monthly digest agent
├── digest_orchestrator.py     # Main orchestrator for all digest agents
├── supabase_schema.sql        # Database schema
├── pyproject.toml             # Python dependencies
├── .github/workflows/
│   ├── rss-agent.yml          # RSS agent scheduling
│   └── digest-scheduler.yml   # Digest agents scheduling
└── README.md                  # This file
```

## 📈 Monitoring

- **GitHub Actions**: Check the Actions tab for run logs
- **Supabase**: Monitor database for new articles
- **Logs**: Console output shows processing status

## 🛡️ Error Handling

- **Duplicate Articles**: Automatically skipped
- **Feed Errors**: Graceful fallback for individual feeds
- **Database Errors**: Retry logic and error logging
- **API Limits**: Respects OpenAI rate limits

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

If you encounter any issues:
1. Check the GitHub Actions logs
2. Verify your environment variables
3. Ensure your Supabase database is properly set up
4. Check the console output for specific error messages

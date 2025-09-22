# Crypto RSS Agent

An automated RSS feed processor that monitors crypto news sources, analyzes articles with AI, and stores them in a Supabase database.

## 🚀 Features

- **Automated RSS Processing**: Monitors multiple crypto news feeds
- **AI-Powered Analysis**: Generates summaries, sentiment analysis, and verdicts using OpenAI
- **Database Storage**: Stores articles and state in Supabase
- **Duplicate Prevention**: Avoids processing the same article twice
- **GitHub Actions**: Automated deployment with scheduled runs
- **Dynamic Feed Management**: Add/remove feeds through database

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

- **`crypto_news`**: Stores processed articles
- **`rss_state`**: Tracks last check time for each feed

### Key Fields

- `title`: Article title
- `url`: Article URL (unique)
- `summary`: AI-generated bullet points
- `sentiment`: Positive/Negative/Neutral
- `verdict`: AI-generated forward-looking analysis
- `published_at`: Original publication date
- `created_at`: Processing timestamp

## 🔧 Core Functions

The RSS agent automatically:
- **Processes new articles** from configured feeds
- **Skips duplicates** to avoid reprocessing
- **Stores AI analysis** in Supabase database
- **Tracks state** to only process new content

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

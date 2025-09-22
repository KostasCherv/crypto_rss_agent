-- Create the crypto_news table
CREATE TABLE IF NOT EXISTS crypto_news (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    feed_url TEXT NOT NULL,
    summary TEXT NOT NULL,
    sentiment TEXT NOT NULL CHECK (sentiment IN ('Positive', 'Negative', 'Neutral')),
    verdict TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create RSS state table for tracking last check times
CREATE TABLE IF NOT EXISTS rss_state (
    id BIGSERIAL PRIMARY KEY,
    feed_url TEXT UNIQUE NOT NULL,
    last_check_timestamp DOUBLE PRECISION NOT NULL,
    last_check_date TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_crypto_news_created_at ON crypto_news(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_crypto_news_sentiment ON crypto_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_crypto_news_feed_url ON crypto_news(feed_url);
CREATE INDEX IF NOT EXISTS idx_rss_state_feed_url ON rss_state(feed_url);

-- Enable Row Level Security (RLS)
ALTER TABLE crypto_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE rss_state ENABLE ROW LEVEL SECURITY;

-- Create policies that allow all operations (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations on crypto_news" ON crypto_news
    FOR ALL USING (true);

CREATE POLICY "Allow all operations on rss_state" ON rss_state
    FOR ALL USING (true);

-- Create daily digests table
CREATE TABLE IF NOT EXISTS daily_digests (
    id BIGSERIAL PRIMARY KEY,
    digest_date DATE NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    sentiment TEXT NOT NULL CHECK (sentiment IN ('Positive', 'Negative', 'Neutral')),
    verdict TEXT NOT NULL,
    article_count INTEGER NOT NULL DEFAULT 0,
    sentiment_breakdown JSONB, -- {"Positive": 5, "Negative": 2, "Neutral": 3}
    trending_topics JSONB, -- ["Bitcoin ETF", "DeFi Regulation", "Ethereum Upgrade"]
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create weekly digests table
CREATE TABLE IF NOT EXISTS weekly_digests (
    id BIGSERIAL PRIMARY KEY,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    summary TEXT NOT NULL,
    sentiment TEXT NOT NULL CHECK (sentiment IN ('Positive', 'Negative', 'Neutral')),
    verdict TEXT NOT NULL,
    daily_digest_count INTEGER NOT NULL DEFAULT 0,
    sentiment_breakdown JSONB,
    trending_topics JSONB, -- ["Bitcoin ETF", "DeFi Regulation", "Ethereum Upgrade"]
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(week_start_date, week_end_date)
);

-- Create monthly digests table
CREATE TABLE IF NOT EXISTS monthly_digests (
    id BIGSERIAL PRIMARY KEY,
    month_year VARCHAR(7) NOT NULL UNIQUE, -- "2024-01"
    summary TEXT NOT NULL,
    sentiment TEXT NOT NULL CHECK (sentiment IN ('Positive', 'Negative', 'Neutral')),
    verdict TEXT NOT NULL,
    weekly_digest_count INTEGER NOT NULL DEFAULT 0,
    sentiment_breakdown JSONB,
    trending_topics JSONB, -- ["Bitcoin ETF", "DeFi Regulation", "Ethereum Upgrade"]
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for digest tables
CREATE INDEX IF NOT EXISTS idx_daily_digests_date ON daily_digests(digest_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_digests_sentiment ON daily_digests(sentiment);
CREATE INDEX IF NOT EXISTS idx_weekly_digests_week ON weekly_digests(week_start_date DESC);
CREATE INDEX IF NOT EXISTS idx_weekly_digests_sentiment ON weekly_digests(sentiment);
CREATE INDEX IF NOT EXISTS idx_monthly_digests_month ON monthly_digests(month_year DESC);
CREATE INDEX IF NOT EXISTS idx_monthly_digests_sentiment ON monthly_digests(sentiment);

-- Enable RLS for digest tables
ALTER TABLE daily_digests ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_digests ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_digests ENABLE ROW LEVEL SECURITY;

-- Create policies for digest tables
CREATE POLICY "Allow all operations on daily_digests" ON daily_digests
    FOR ALL USING (true);

CREATE POLICY "Allow all operations on weekly_digests" ON weekly_digests
    FOR ALL USING (true);

CREATE POLICY "Allow all operations on monthly_digests" ON monthly_digests
    FOR ALL USING (true);

-- Insert initial state for the feeds (optional - can be done programmatically)
INSERT INTO rss_state (feed_url, last_check_timestamp) VALUES 
    ('https://cointelegraph.com/rss', 0),
    ('https://www.coindesk.com/arc/outboundfeeds/rss/', 0),
    ('https://thedefiant.io/feed/', 0)
ON CONFLICT (feed_url) DO NOTHING;

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

-- Insert initial state for the feeds (optional - can be done programmatically)
INSERT INTO rss_state (feed_url, last_check_timestamp) VALUES 
    ('https://cointelegraph.com/rss', 0),
    ('https://www.coindesk.com/arc/outboundfeeds/rss/', 0),
    ('https://thedefiant.io/feed/', 0)
ON CONFLICT (feed_url) DO NOTHING;

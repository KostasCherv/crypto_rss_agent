import os, feedparser, time
from dotenv import load_dotenv
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from supabase import ClientOptions, create_client, Client

# Load .env secrets
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

DEFAULT_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://thedefiant.io/feed/"
]

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=ClientOptions(schema="public"))

# 1. Define structured schema
class NewsSummary(BaseModel):
    summary: list[str] = Field(..., description="2-4 bullet points about the article")
    sentiment: str = Field(..., description="One of: Positive, Negative, Neutral")
    verdict: str = Field(..., description="Forward-looking evaluation, 1–2 sentences")

parser = JsonOutputParser(pydantic_object=NewsSummary)

# 2. Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that processes financial/technology news."),
    ("user", """Articles:
{articles}

Return ONLY valid JSON following this schema:
{format_instructions}""")
]).partial(format_instructions=parser.get_format_instructions())

# 3. Define LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 4. Process article
def process_article(title, summary, url):
    article_text = f"Title: {title}\nSummary: {summary}\nURL: {url}"
    chain = prompt | llm | parser
    return chain.invoke({"articles": article_text})

# 5. Write to Supabase
def write_supabase(item: NewsSummary, title, url, feed_url, published_date=None):
    try:
        # Check if article already exists
        existing = supabase.table("crypto_news").select("id").eq("url", url).execute()
        
        if existing.data:
            print(f"⚠️  Article already exists, skipping: {title}")
            return True
        
        # Format summary as bullet points
        summary_text = "• " + "\n• ".join(item["summary"])
        
        # Use provided published_date or fallback to current time
        published_at = published_date or datetime.now(timezone.utc)
        if isinstance(published_at, str):
            published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        
        article_data = {
            "title": title,
            "url": url,
            "feed_url": feed_url,
            "summary": summary_text,
            "sentiment": item["sentiment"],
            "verdict": item["verdict"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "published_at": published_at.isoformat()
        }
        
        result = supabase.table("crypto_news").insert(article_data).execute()
        
        if result.data:
            print(f"✅ Successfully added article to Supabase: {title}")
            return True
        else:
            print(f"❌ Failed to add article: {title}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing article {title}: {e}")
        return False

# 6. RSS State Management


def load_last_check():
    """Load last check timestamp from Supabase"""
    try:
        result = supabase.table("rss_state").select("*").execute()
        timestamps = {}
        for row in result.data:
            timestamps[row["feed_url"]] = row["last_check_timestamp"]
        return timestamps
    except Exception as e:
        print(f"Error loading state from Supabase: {e}")
        return {}

def save_last_check(timestamps):
    """Save last check timestamp to Supabase"""
    try:
        for feed_url, timestamp in timestamps.items():
            # Check if record exists first
            result = supabase.table("rss_state").select("id").eq("feed_url", feed_url).execute()
            
            if result.data:
                # Update existing record
                supabase.table("rss_state").update({
                    "last_check_timestamp": timestamp,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("feed_url", feed_url).execute()
            else:
                # Insert new record
                supabase.table("rss_state").insert({
                    "feed_url": feed_url,
                    "last_check_timestamp": timestamp,
                    "last_check_date": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).execute()
    except Exception as e:
        print(f"Error saving state to Supabase: {e}")

def initialize_state():
    """Initialize RSS state for default feeds if not exists"""
    try:
        for feed_url in DEFAULT_FEEDS:
            # Check if state exists for this feed
            result = supabase.table("rss_state").select("id").eq("feed_url", feed_url).execute()
            
            if not result.data:
                # Insert initial state
                supabase.table("rss_state").insert({
                    "feed_url": feed_url,
                    "last_check_timestamp": 0,
                    "last_check_date": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).execute()
                print(f"Initialized state for feed: {feed_url}")
            else:
                print(f"Feed already exists: {feed_url}")
    except Exception as e:
        print(f"Error initializing state: {e}")

def get_published_date(e):
    """Get published date from RSS entry"""
    if hasattr(e, 'published_parsed') and e.published_parsed:
        return datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
    elif hasattr(e, 'published') and e.published:
        return datetime.fromisoformat(e.published.replace('Z', '+00:00'))
    return None

def run_once():
    """Run once and process only new articles"""
    timestamps = load_last_check()
    new_articles_count = 0
    
    for feed in DEFAULT_FEEDS:
        print(f"Checking feed: {feed}")
        d = feedparser.parse(feed)
        last_check = timestamps.get(feed, 0)
        
        for e in d.entries:
            # Extract published date from RSS entry
            published_date = get_published_date(e)
            
            # Convert published time to timestamp for comparison
            pub_time = time.mktime(e.published_parsed) if hasattr(e, 'published_parsed') else 0
            
            # Only process if newer than last check
            if pub_time > last_check:
                print(f"Processing new article: {e.title} (Published: {published_date})")
                parsed = process_article(e.title, e.summary, e.link)
                if write_supabase(parsed, e.title, e.link, feed, published_date):
                    new_articles_count += 1
                
                # Update last check time
                timestamps[feed] = max(timestamps.get(feed, 0), pub_time)
    
    save_last_check(timestamps)
    print(f"Processed {new_articles_count} new articles")
    return new_articles_count



def main():
    """Main function to run the RSS agent"""
    print("🚀 Crypto RSS Agent Starting...")
    print("=" * 50)
    
    # Initialize RSS state in Supabase
    print("📡 Initializing RSS state...")
    initialize_state()
    
    # Process new articles
    print("🔍 Checking for new articles...")
    new_count = run_once()
    
    if new_count > 0:
        print(f"✅ Successfully processed {new_count} new articles!")
    else:
        print("ℹ️  No new articles found.")
    
    print("=" * 50)
    print("🏁 RSS Agent completed successfully!")

if __name__ == "__main__":
    main()
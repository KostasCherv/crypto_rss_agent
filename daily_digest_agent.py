import os
from datetime import datetime, timezone, date, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from supabase import ClientOptions, create_client, Client
from schemas import DailyDigestSummary, DailyDigestData
from collections import Counter
import json

# Load .env secrets
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=ClientOptions(schema="public"))

# Define parser for daily digest
parser = JsonOutputParser(pydantic_object=DailyDigestSummary)

# Define prompt for daily digest
daily_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert crypto market analyst. Create a comprehensive daily digest of crypto news."),
    ("user", """Based on the following crypto news articles from today, create a daily digest:

Articles:
{articles}

Please analyze the overall sentiment, identify key themes, and provide a forward-looking verdict for tomorrow.

Return ONLY valid JSON following this schema:
{format_instructions}""")
]).partial(format_instructions=parser.get_format_instructions())

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def get_articles_for_date(target_date: date):
    """Get all articles published on a specific date"""
    try:
        start_datetime = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_datetime = start_datetime + timedelta(days=1)
        
        result = supabase.table("crypto_news").select("*").gte("published_at", start_datetime.isoformat()).lt("published_at", end_datetime.isoformat()).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching articles for {target_date}: {e}")
        return []

def analyze_articles(articles):
    """Analyze articles and create daily digest using AI"""
    if not articles:
        return None
    
    # Prepare articles text for AI analysis
    articles_text = ""
    for article in articles:
        articles_text += f"Title: {article['title']}\nSummary: {article['summary']}\nSentiment: {article['sentiment']}\n\n"
    
    # Create chain and get AI analysis
    chain = daily_prompt | llm | parser
    result = chain.invoke({"articles": articles_text})
    
    return result

def calculate_sentiment_breakdown(articles):
    """Calculate sentiment breakdown from articles"""
    sentiments = [article['sentiment'] for article in articles]
    return dict(Counter(sentiments))


def create_daily_digest(target_date: date = None):
    """Create daily digest for a specific date (defaults to yesterday)"""
    if target_date is None:
        target_date = date.today() - timedelta(days=1)
    
    print(f"📅 Creating daily digest for {target_date}")
    
    # Check if digest already exists
    existing = supabase.table("daily_digests").select("id").eq("digest_date", target_date.isoformat()).execute()
    if existing.data:
        print(f"⚠️  Daily digest for {target_date} already exists, skipping")
        return False
    
    # Get articles for the date
    articles = get_articles_for_date(target_date)
    if not articles:
        print(f"ℹ️  No articles found for {target_date}")
        return False
    
    print(f"📰 Found {len(articles)} articles for {target_date}")
    
    # Analyze articles with AI
    ai_analysis = analyze_articles(articles)
    if not ai_analysis:
        print(f"❌ Failed to analyze articles for {target_date}")
        return False
    
    # Calculate metrics
    sentiment_breakdown = calculate_sentiment_breakdown(articles)
    
    # Prepare digest data
    digest_data = DailyDigestData(
        digest_date=target_date,
        summary="• " + "\n• ".join(ai_analysis["summary"]),
        sentiment=ai_analysis["sentiment"],
        verdict=ai_analysis["verdict"],
        article_count=len(articles),
        sentiment_breakdown=sentiment_breakdown,
        trending_topics=ai_analysis["trending_topics"]
    )
    
    # Save to database
    try:
        result = supabase.table("daily_digests").insert({
            "digest_date": digest_data.digest_date.isoformat(),
            "summary": digest_data.summary,
            "sentiment": digest_data.sentiment,
            "verdict": digest_data.verdict,
            "article_count": digest_data.article_count,
            "sentiment_breakdown": json.dumps(digest_data.sentiment_breakdown),
            "trending_topics": json.dumps(digest_data.trending_topics),
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        if result.data:
            print(f"✅ Successfully created daily digest for {target_date}")
            print(f"   📊 Articles: {digest_data.article_count}")
            print(f"   😊 Sentiment: {digest_data.sentiment}")
            print(f"   🔥 Trending: {', '.join(digest_data.trending_topics[:3])}")
            return True
        else:
            print(f"❌ Failed to save daily digest for {target_date}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving daily digest for {target_date}: {e}")
        return False

def main():
    """Main function to run the daily digest agent"""
    print("🌅 Daily Digest Agent Starting...")
    print("=" * 50)
    
    # Create digest for yesterday
    success = create_daily_digest()
    
    if success:
        print("✅ Daily digest created successfully!")
    else:
        print("ℹ️  No daily digest created (may already exist or no articles found)")
    
    print("=" * 50)
    print("🏁 Daily Digest Agent completed!")

if __name__ == "__main__":
    main()

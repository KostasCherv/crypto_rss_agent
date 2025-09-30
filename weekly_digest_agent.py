import os
from datetime import datetime, timezone, date, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from supabase import ClientOptions, create_client, Client
from schemas import WeeklyDigestSummary, WeeklyDigestData
from collections import Counter
import json

# Load .env secrets
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=ClientOptions(schema="public"))

# Define parser for weekly digest
parser = JsonOutputParser(pydantic_object=WeeklyDigestSummary)

# Define prompt for weekly digest
weekly_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert crypto market analyst. Create a comprehensive weekly digest of crypto developments."),
    ("user", """Based on the following daily digests from the past week, create a weekly summary:

Daily Digests:
{daily_digests}

Please analyze the overall sentiment, identify key themes and trends, and provide a forward-looking verdict for the next week.

Return ONLY valid JSON following this schema:
{format_instructions}""")
]).partial(format_instructions=parser.get_format_instructions())

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def get_week_start_date(target_date: date = None):
    """Get the start of the week (Monday) for a given date"""
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()
    
    # Get Monday of the current week
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    return week_start

def get_daily_digests_for_week(week_start: date):
    """Get all daily digests for a specific week"""
    try:
        week_end = week_start + timedelta(days=6)
        
        result = supabase.table("daily_digests").select("*").gte("digest_date", week_start.isoformat()).lte("digest_date", week_end.isoformat()).order("digest_date").execute()
        return result.data
    except Exception as e:
        print(f"Error fetching daily digests for week {week_start}: {e}")
        return []

def analyze_daily_digests(daily_digests):
    """Analyze daily digests and create weekly digest using AI"""
    if not daily_digests:
        return None
    
    # Prepare daily digests text for AI analysis
    digests_text = ""
    for digest in daily_digests:
        digests_text += f"Date: {digest['digest_date']}\nSummary: {digest['summary']}\nSentiment: {digest['sentiment']}\nVerdict: {digest['verdict']}\n\n"
    
    # Create chain and get AI analysis
    chain = weekly_prompt | llm | parser
    result = chain.invoke({"daily_digests": digests_text})
    
    return result

def calculate_weekly_sentiment_breakdown(daily_digests):
    """Calculate sentiment breakdown from daily digests"""
    sentiments = [digest['sentiment'] for digest in daily_digests]
    return dict(Counter(sentiments))


def create_weekly_digest(target_date: date = None):
    """Create weekly digest for a specific week (defaults to the week that just finished)"""
    if target_date is None:
        # Always find the Monday of the current week, then go back 7 days to get the previous week
        today = datetime.now(timezone.utc).date()
        this_week_monday = today - timedelta(days=today.weekday())
        previous_week_monday = this_week_monday - timedelta(days=7)
        target_date = previous_week_monday
    
    week_start = get_week_start_date(target_date)
    week_end = week_start + timedelta(days=6)
    
    print(f"📅 Creating weekly digest for {week_start} to {week_end}")
    print(f"🔍 Target date used: {target_date} (UTC today is {datetime.now(timezone.utc).date()})")
    
    # Check if digest already exists
    existing = supabase.table("weekly_digests").select("id").eq("week_start_date", week_start.isoformat()).eq("week_end_date", week_end.isoformat()).execute()
    if existing.data:
        print(f"⚠️  Weekly digest for week {week_start} to {week_end} already exists, skipping")
        return False
    
    # Get daily digests for the week
    daily_digests = get_daily_digests_for_week(week_start)
    if not daily_digests:
        print(f"ℹ️  No daily digests found for week {week_start} to {week_end}")
        return False
    
    print(f"📰 Found {len(daily_digests)} daily digests for the week")
    
    # Analyze daily digests with AI
    ai_analysis = analyze_daily_digests(daily_digests)
    if not ai_analysis:
        print(f"❌ Failed to analyze daily digests for week {week_start}")
        return False
    
    # Calculate metrics
    sentiment_breakdown = calculate_weekly_sentiment_breakdown(daily_digests)
    
    # Prepare digest data
    digest_data = WeeklyDigestData(
        week_start_date=week_start,
        week_end_date=week_end,
        summary="• " + "\n• ".join(ai_analysis["summary"]),
        sentiment=ai_analysis["sentiment"],
        verdict=ai_analysis["verdict"],
        daily_digest_count=len(daily_digests),
        sentiment_breakdown=sentiment_breakdown,
        trending_topics=ai_analysis["trending_topics"]
    )
    
    # Save to database
    try:
        result = supabase.table("weekly_digests").insert({
            "week_start_date": digest_data.week_start_date.isoformat(),
            "week_end_date": digest_data.week_end_date.isoformat(),
            "summary": digest_data.summary,
            "sentiment": digest_data.sentiment,
            "verdict": digest_data.verdict,
            "daily_digest_count": digest_data.daily_digest_count,
            "sentiment_breakdown": json.dumps(digest_data.sentiment_breakdown),
            "trending_topics": json.dumps(digest_data.trending_topics),
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        if result.data:
            print(f"✅ Successfully created weekly digest for {week_start} to {week_end}")
            print(f"   📊 Daily Digests: {digest_data.daily_digest_count}")
            print(f"   😊 Sentiment: {digest_data.sentiment}")
            print(f"   🔥 Trending: {', '.join(digest_data.trending_topics[:3])}")
            return True
        else:
            print(f"❌ Failed to save weekly digest for week {week_start}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving weekly digest for week {week_start}: {e}")
        return False

def main():
    """Main function to run the weekly digest agent"""
    print("📊 Weekly Digest Agent Starting...")
    print("=" * 50)
    
    # Create digest for last week
    success = create_weekly_digest()
    
    if success:
        print("✅ Weekly digest created successfully!")
    else:
        print("ℹ️  No weekly digest created (may already exist or no daily digests found)")
    
    print("=" * 50)
    print("🏁 Weekly Digest Agent completed!")

if __name__ == "__main__":
    main()

import os
from datetime import datetime, timezone, date, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from supabase import ClientOptions, create_client, Client
from schemas import MonthlyDigestSummary, MonthlyDigestData
from collections import Counter
import json

# Load .env secrets
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=ClientOptions(schema="public"))

# Define parser for monthly digest
parser = JsonOutputParser(pydantic_object=MonthlyDigestSummary)

# Define prompt for monthly digest
monthly_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert crypto market analyst. Create a comprehensive monthly digest of crypto market developments and trends."),
    ("user", """Based on the following weekly digests from the past month, create a monthly summary:

Weekly Digests:
{weekly_digests}

Please analyze the overall sentiment, identify major themes and trends, and provide a forward-looking verdict for the next month.

Return ONLY valid JSON following this schema:
{format_instructions}""")
]).partial(format_instructions=parser.get_format_instructions())

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def get_month_year(target_date: date = None):
    """Get month-year string for a given date"""
    if target_date is None:
        target_date = date.today()
    
    return target_date.strftime("%Y-%m")

def get_weekly_digests_for_month(month_year: str):
    """Get all weekly digests for a specific month"""
    try:
        # Parse month_year to get start and end of month
        year, month = map(int, month_year.split('-'))
        month_start = date(year, month, 1)
        
        # Get last day of month
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        result = supabase.table("weekly_digests").select("*").gte("week_start_date", month_start.isoformat()).lte("week_end_date", month_end.isoformat()).order("week_start_date").execute()
        return result.data
    except Exception as e:
        print(f"Error fetching weekly digests for month {month_year}: {e}")
        return []

def analyze_weekly_digests(weekly_digests):
    """Analyze weekly digests and create monthly digest using AI"""
    if not weekly_digests:
        return None
    
    # Prepare weekly digests text for AI analysis
    digests_text = ""
    for digest in weekly_digests:
        digests_text += f"Week: {digest['week_start_date']} to {digest['week_end_date']}\nSummary: {digest['summary']}\nSentiment: {digest['sentiment']}\nVerdict: {digest['verdict']}\n\n"
    
    # Create chain and get AI analysis
    chain = monthly_prompt | llm | parser
    result = chain.invoke({"weekly_digests": digests_text})
    
    return result

def calculate_monthly_sentiment_breakdown(weekly_digests):
    """Calculate sentiment breakdown from weekly digests"""
    sentiments = [digest['sentiment'] for digest in weekly_digests]
    return dict(Counter(sentiments))


def create_monthly_digest(target_date: date = None):
    """Create monthly digest for a specific month (defaults to last month)"""
    if target_date is None:
        # Get first day of current month, then go back one month
        today = date.today()
        if today.month == 1:
            target_date = date(today.year - 1, 12, 1)
        else:
            target_date = date(today.year, today.month - 1, 1)
    
    month_year = get_month_year(target_date)
    
    print(f"📅 Creating monthly digest for {month_year}")
    
    # Check if digest already exists
    existing = supabase.table("monthly_digests").select("id").eq("month_year", month_year).execute()
    if existing.data:
        print(f"⚠️  Monthly digest for {month_year} already exists, skipping")
        return False
    
    # Get weekly digests for the month
    weekly_digests = get_weekly_digests_for_month(month_year)
    if not weekly_digests:
        print(f"ℹ️  No weekly digests found for month {month_year}")
        return False
    
    print(f"📰 Found {len(weekly_digests)} weekly digests for the month")
    
    # Analyze weekly digests with AI
    ai_analysis = analyze_weekly_digests(weekly_digests)
    if not ai_analysis:
        print(f"❌ Failed to analyze weekly digests for month {month_year}")
        return False
    
    # Calculate metrics
    sentiment_breakdown = calculate_monthly_sentiment_breakdown(weekly_digests)
    
    # Prepare digest data
    digest_data = MonthlyDigestData(
        month_year=month_year,
        summary="• " + "\n• ".join(ai_analysis["summary"]),
        sentiment=ai_analysis["sentiment"],
        verdict=ai_analysis["verdict"],
        weekly_digest_count=len(weekly_digests),
        sentiment_breakdown=sentiment_breakdown,
        trending_topics=ai_analysis["trending_topics"]
    )
    
    # Save to database
    try:
        result = supabase.table("monthly_digests").insert({
            "month_year": digest_data.month_year,
            "summary": digest_data.summary,
            "sentiment": digest_data.sentiment,
            "verdict": digest_data.verdict,
            "weekly_digest_count": digest_data.weekly_digest_count,
            "sentiment_breakdown": json.dumps(digest_data.sentiment_breakdown),
            "trending_topics": json.dumps(digest_data.trending_topics),
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        if result.data:
            print(f"✅ Successfully created monthly digest for {month_year}")
            print(f"   📊 Weekly Digests: {digest_data.weekly_digest_count}")
            print(f"   😊 Sentiment: {digest_data.sentiment}")
            print(f"   🔥 Trending: {', '.join(digest_data.trending_topics[:4])}")
            return True
        else:
            print(f"❌ Failed to save monthly digest for {month_year}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving monthly digest for {month_year}: {e}")
        return False

def main():
    """Main function to run the monthly digest agent"""
    print("📈 Monthly Digest Agent Starting...")
    print("=" * 50)
    
    # Create digest for last month
    success = create_monthly_digest()
    
    if success:
        print("✅ Monthly digest created successfully!")
    else:
        print("ℹ️  No monthly digest created (may already exist or no weekly digests found)")
    
    print("=" * 50)
    print("🏁 Monthly Digest Agent completed!")

if __name__ == "__main__":
    main()

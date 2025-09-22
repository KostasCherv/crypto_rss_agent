from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date

class NewsSummary(BaseModel):
    summary: List[str] = Field(..., description="2-4 bullet points about the article")
    sentiment: str = Field(..., description="One of: Positive, Negative, Neutral")
    verdict: str = Field(..., description="Forward-looking evaluation, 1–2 sentences")

class DailyDigestSummary(BaseModel):
    summary: List[str] = Field(..., description="3-5 bullet points summarizing the day's crypto news")
    sentiment: str = Field(..., description="Overall sentiment: Positive, Negative, or Neutral")
    verdict: str = Field(..., description="Forward-looking analysis for the next day, 2-3 sentences")
    trending_topics: List[str] = Field(..., description="Top 5 trending topics and themes from the day's news")

class WeeklyDigestSummary(BaseModel):
    summary: List[str] = Field(..., description="4-6 bullet points summarizing the week's crypto developments")
    sentiment: str = Field(..., description="Overall sentiment: Positive, Negative, or Neutral")
    verdict: str = Field(..., description="Forward-looking analysis for the next week, 3-4 sentences")
    trending_topics: List[str] = Field(..., description="Top 6 trending topics and themes from the week's news")

class MonthlyDigestSummary(BaseModel):
    summary: List[str] = Field(..., description="5-8 bullet points summarizing the month's major crypto developments")
    sentiment: str = Field(..., description="Overall sentiment: Positive, Negative, or Neutral")
    verdict: str = Field(..., description="Forward-looking analysis for the next month, 4-5 sentences")
    trending_topics: List[str] = Field(..., description="Top 8 trending topics and themes from the month's news")

class DailyDigestData(BaseModel):
    digest_date: date
    summary: str
    sentiment: str
    verdict: str
    article_count: int
    sentiment_breakdown: Dict[str, int]
    trending_topics: List[str]

class WeeklyDigestData(BaseModel):
    week_start_date: date
    week_end_date: date
    summary: str
    sentiment: str
    verdict: str
    daily_digest_count: int
    sentiment_breakdown: Dict[str, int]
    trending_topics: List[str]

class MonthlyDigestData(BaseModel):
    month_year: str
    summary: str
    sentiment: str
    verdict: str
    weekly_digest_count: int
    sentiment_breakdown: Dict[str, int]
    trending_topics: List[str]

from typing import List
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    """Represents a news article with relevance scoring."""
    title: str
    url: str
    summary: str
    relevance_score: float = Field(ge=0.0, le=1.0)

class Config(BaseModel):
    """Application configuration."""
    perplexity_api_key: str
    email_from: str
    email_to: List[str]
    topics: List[str] 
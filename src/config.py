import os
from typing import List
from dotenv import load_dotenv
from .types import Config

# Load environment variables
load_dotenv()

def get_config() -> Config:
    """Load and validate configuration from environment variables."""
    return Config(
        perplexity_api_key=os.getenv('PERPLEXITY_API_KEY', ''),
        email_from=os.getenv('EMAIL_FROM', ''),
        email_to=os.getenv('EMAIL_TO', '').split(','),
        topics=[
            'enterprise AI',
            'open ai',
            'chatgpt',
            'generative ai',
            'perplexity',
            'agi',
            'claude',
            'agentic ai',
        ]
    ) 
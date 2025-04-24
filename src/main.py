import asyncio
import logging
from logging.handlers import RotatingFileHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
from typing import List
import os
from pathlib import Path

from .types import NewsItem
from .config import get_config

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    handlers=[
        RotatingFileHandler(log_dir / 'newsletter.log', maxBytes=1e6, backupCount=5),
        logging.StreamHandler()  # Also log to console
    ],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def get_news_for_topic(session: aiohttp.ClientSession, topic: str) -> List[NewsItem]:
    """Fetch and analyze news for a specific topic using Perplexity AI."""
    try:
        config = get_config()
        logger.info(f"Fetching news for topic: {topic}")
        
        async with session.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {config.perplexity_api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'sonar',
                'messages': [{
                    'role': 'user',
                    'content': f'Find the latest news about {topic} in digital transformation and enterprise technology. '
                              f'For each news item, provide the actual headline (without any numbering or "Title:" prefix), URL, '
                              f'brief summary, and relevance score (0-1). Return in this exact format:\n'
                              f'Headline | URL | Summary | 0.9'
                }],
                'max_tokens': 1024,
                'temperature': 0.2,
                'search_recency_filter': 'week',
                'web_search_options': {
                    'search_context_size': 'high'
                }
            }
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"API error for {topic}. Status: {response.status}, Response: {error_text}")
                return []
                
            data = await response.json()
            logger.debug(f"Raw API response for {topic}: {data}")
            
            if 'error' in data:
                logger.error(f"API returned error for {topic}: {data['error']}")
                return []
            
            # Handle different response formats
            content = None
            if 'choices' in data and len(data['choices']) > 0:
                if 'message' in data['choices'][0]:
                    content = data['choices'][0]['message'].get('content', '')
                else:
                    content = data['choices'][0].get('text', '')
            
            if not content:
                logger.error(f"No content in response for {topic}. Response structure: {data.keys()}")
                return []
            
            # Parse response and convert to NewsItems
            items = []
            for line in content.split('\n'):
                if not line.strip() or line.startswith('#') or line.startswith('*'):
                    continue
                    
                try:
                    # Remove any markdown formatting and clean up the title
                    line = line.replace('**', '').replace('[', '').replace(']', '')
                    if '|' not in line:
                        continue
                        
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 4:  # We might have more parts due to URLs with |
                        # Clean up the title by removing any numbering or "Title:" prefix
                        title = parts[0]
                        # Remove common prefixes and numbering patterns
                        title = title.strip()
                        title = title.lstrip('0123456789.- ')
                        title = title.removeprefix('Title:').strip()
                        
                        url = parts[1]
                        summary = parts[2]
                        # Extract the score - look for a number between 0 and 1
                        score_text = parts[-1]  # Take the last part
                        import re
                        score_match = re.search(r'0\.\d+', score_text)
                        if score_match:
                            score = float(score_match.group())
                            items.append(NewsItem(
                                title=title,
                                url=url,
                                summary=summary,
                                relevance_score=score
                            ))
                except Exception as parse_error:
                    logger.error(f"Error parsing line for {topic}: {line}. Error: {str(parse_error)}")
                    continue
            
            if not items:
                logger.warning(f"No news items found for {topic}")
            else:
                logger.info(f"Found {len(items)} news items for {topic}")
            
            return items
            
    except Exception as e:
        logger.error(f"Error fetching news for {topic}: {str(e)}")
        return []

def send_newsletter(news_items: List[NewsItem]) -> None:
    """Send newsletter via email."""
    try:
        config = get_config()
        msg = MIMEMultipart()
        msg['From'] = config.email_from
        msg['To'] = ', '.join(config.email_to)
        msg['Subject'] = "Actualización de Noticias en IA y Transformación Digital"

        # Create HTML content with Hanova branding
        html_content = """<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
    <div style="background-color: #1E3C72; color: white; padding: 30px; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">Actualización de Noticias en IA y Transformación Digital</h1>
        <p style="margin: 10px 0 0 0;">Información relevante seleccionada por Hanova Consulting</p>
    </div>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <p style="color: #666; margin-bottom: 20px;">Hola Alén, espero estés bien. Aquí te comparto las noticias más relevantes sobre IA y transformación digital de esta semana:</p>
        {}
    </div>
    <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666;">
        <p style="margin: 5px 0;">Hanova Consulting - Tu consultora en transformación digital</p>
        <p style="margin: 5px 0;">Este boletín es curado y enviado por el servicio de noticias impulsado por IA de Hanova Consulting.</p>
        <p style="margin: 5px 0;">Para cancelar la suscripción o gestionar preferencias, contáctanos en {}</p>
    </div>
</body>
</html>""".format(
            ''.join(
                f"""<div style="margin-bottom: 30px; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
                    <h2 style="color: #1E3C72; margin-top: 0; font-size: 20px;">{idx + 1}. {item.title.split('.', 1)[-1].strip()}</h2>
                    <p style="margin: 10px 0;">{item.summary}</p>
                    <a href="{item.url}" style="display: inline-block; background-color: #FF6B35; color: white; text-decoration: none; padding: 8px 15px; border-radius: 3px; font-size: 14px;">Leer Más →</a>
                </div>""" 
                for idx, item in enumerate(news_items)
            ),
            config.email_from
        )

        msg.attach(MIMEText(html_content, 'html'))

        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(config.email_from, os.getenv('EMAIL_PASSWORD'))
            server.send_message(msg)

        logger.info("Newsletter sent successfully")
    except Exception as e:
        logger.error(f"Error sending newsletter: {str(e)}")
        raise

async def main():
    """Main execution function."""
    try:
        config = get_config()
        
        # Collect news for all topics
        async with aiohttp.ClientSession() as session:
            tasks = [get_news_for_topic(session, topic) for topic in config.topics]
            results = await asyncio.gather(*tasks)
            
        # Flatten results and remove duplicates
        all_news = []
        seen_urls = set()
        for topic_news in results:
            for item in topic_news:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    all_news.append(item)
        
        # Sort by relevance score and take top 10
        all_news.sort(key=lambda x: x.relevance_score, reverse=True)
        top_news = all_news[:10]
        
        # Send newsletter if we have news items
        if top_news:
            logger.info(f"Sending newsletter with {len(top_news)} most relevant news items")
            send_newsletter(top_news)
        else:
            logger.warning("No relevant news found")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 
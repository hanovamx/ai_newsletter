import asyncio
import logging
from datetime import datetime
import sys
from src.main import main
from src.config import get_config

# Configure logging to console for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def test_configuration():
    """Test if configuration is properly set up."""
    try:
        config = get_config()
        logger.info("Testing configuration...")
        
        # Check required environment variables
        missing_vars = []
        if not config.perplexity_api_key:
            missing_vars.append("PERPLEXITY_API_KEY")
        if not config.email_from:
            missing_vars.append("EMAIL_FROM")
        if not config.email_to:
            missing_vars.append("EMAIL_TO")
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please check your .env file")
            return False
        
        logger.info("✓ Configuration loaded successfully")
        logger.info(f"Topics to monitor: {', '.join(config.topics)}")
        logger.info(f"Email will be sent to: {', '.join(config.email_to)}")
        return True
        
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        return False

async def run_local_test():
    """Run a local test of the newsletter system."""
    logger.info("Starting local newsletter test...")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test configuration first
    if not await test_configuration():
        return
    
    try:
        logger.info("Running main newsletter function...")
        await main()
        logger.info("Newsletter test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during newsletter generation: {str(e)}")
        logger.error("Please check the error message above and verify your configuration")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Newsletter System Local Test")
    print("="*50 + "\n")
    
    try:
        asyncio.run(run_local_test())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    
    print("\n" + "="*50 + "\n") 
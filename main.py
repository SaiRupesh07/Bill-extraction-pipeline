import uvicorn
import logging
import os
from config.settings import settings

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Validate settings (only if not using mock)
        if not settings.use_mock:
            settings.validate()
            logger.info("Using Azure Form Recognizer for extraction")
        else:
            logger.info("Using mock extractor for testing")
        
        logger.info("Starting Bill Extraction API Server...")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"Confidence threshold: {settings.CONFIDENCE_THRESHOLD}")
        
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.DEBUG,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
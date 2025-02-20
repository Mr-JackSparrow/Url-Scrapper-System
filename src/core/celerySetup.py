import logging
import httpx
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, TooManyRedirects, SSLError, ConnectionError
from sqlalchemy.orm import Session
from celery import Celery, group
from ssl import CERT_NONE

from src.logging_config import setup_logging
from src.repositories.scrapedDataRepository import ScrapedDataRepository
from src.repositories.userRepository import UserRepository
from src.models.scrapedDataModel import ScrapedData
from src.core.config import getRedisDbSettings
from src.dependencies import getDb

setup_logging()
log = logging.getLogger(__name__)

settings = getRedisDbSettings()

celeryApp = Celery(
    'scrapper-service',
    broker=settings.REDIS_DB_URL,
    backend=settings.REDIS_DB_URL
)

celeryApp.conf.update(
    broker_use_ssl={'ssl_cert_reqs': CERT_NONE},
    redis_backend_use_ssl={'ssl_cert_reqs': CERT_NONE},
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Constants
REQUEST_TIMEOUT = 2  # Timeout for HTTP requests in seconds
MAX_WORKERS = 200  # Number of concurrent workers for scraping
BATCH_SIZE = 50  # Number of records to insert in a single batch

@celeryApp.task(name="scrapper-service.core.celerySetup.scrapMetaData", bind=True)
def scrapMetaData(self, urlList: list, emailId: str):
    """
    Scrapes metadata from a list of URLs concurrently and saves the results to the database in bulk.
    
    Args:
        urlList (list): List of URLs to scrape.
        emailId (str): Email ID of the user initiating the scrape.
    
    Returns:
        list: List of scraped data or error messages.
    """
    log.info(f"Starting scrapMetaData task for emailId: {emailId} with {len(urlList)} URLs")
    db = next(getDb())
    repo = ScrapedDataRepository(db)
    userRepo = UserRepository(db)

    # Get user ID from email
    userId = userRepo.getUserIdByEmailId(emailId)
    if not userId:
        raise ValueError(f"User with email {emailId} not found")

    # Create a group of tasks for concurrent execution
    job = group(scrape_url.s(url, userId, self.request.id) for url in urlList)
    result = job.apply_async()

    # Wait for the group to complete and collect results
    results = result.get(disable_sync_subtasks=False)

    # Save all results to the database in bulk
    if results:
        for i in range(0, len(results), BATCH_SIZE):
            batch_data = [ScrapedData.from_dict(data) for data in results[i:i + BATCH_SIZE]]
            repo.create_scraped_data_batch(batch_data)

    log.info(f"Completed scrapMetaData task for emailId: {emailId}")
    return results

@celeryApp.task(name="scrapper-service.core.celerySetup.scrape_url", bind=True)
async def scrape_url(self, url: str, userId: int, temp_token: str):
    """
    Scrapes metadata from a single URL.
    
    Args:
        url (str): URL to scrape.
        userId (int): ID of the user initiating the scrape.
        temp_token (str): Temporary token for tracking the scrape job.
    
    Returns:
        dict: Scraped data or error details.
    """
    try:
        log.info(f"Scraping URL: {url}")
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text.strip() if soup.find('title') else None
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'].strip() if description else None
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords['content'].strip() if keywords else None

        # Prepare scraped data
        data = {
            "user_id": userId,
            "temp_token": temp_token,
            "url": url,
            "title": title,
            "description": description,
            "keywords": keywords,
            "status": "success",
        }

        return data

    except (Timeout, TooManyRedirects, SSLError, ConnectionError, RequestException) as e:
        # Handle known HTTP/network errors
        error_message = f"{type(e).__name__} occurred while scraping URL: {url}. Error: {str(e)}"
        log.warning(error_message)
        return {
            "user_id": userId,
            "temp_token": temp_token,
            "url": url,
            "status": "error",
            "error_message": error_message,
        }

    except Exception as e:
        # Handle unexpected errors
        error_message = f"Unexpected error occurred for URL: {url}. Error: {str(e)}"
        log.error(error_message)
        return {
            "user_id": userId,
            "temp_token": temp_token,
            "url": url,
            "status": "error",
            "error_message": error_message,
        }

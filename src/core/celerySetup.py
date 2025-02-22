import logging
import asyncio
import aiohttp
from celery import Celery
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from fastapi import Depends
from ssl import CERT_NONE
from sqlalchemy.exc import SQLAlchemyError
from src.logging_config import setup_logging
from src.repositories.scrapedDataRepository import ScrapedDataRepository
from src.repositories.userRepository import UserRepository
from src.models.scrapedDataModel import ScrapedData
from src.core.config import getRedisDbSettings
from src.dependencies import getDb
from requests.exceptions import TooManyRedirects, SSLError, ConnectionError

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
    task_acks_late=True,  
    broker_connection_retry_on_startup=True, 
    worker_concurrency=5
)


@celeryApp.task(name="scrapper-service.core.celerySetup.scrapMetaData", bind=True, max_retries=3, default_retry_delay=5)
def scrapMetaData(self, urlList: list, emailId: str):
    return asyncio.run(_scrapMetaData(urlList, emailId, self.request.id))

async def _scrapMetaData(urlList: list, emailId: str, temp_token: str):
    results = []
    db = next(getDb())
    repo = ScrapedDataRepository(db)
    userRepo = UserRepository(db)

    userId = userRepo.getUserIdByEmailId(emailId)
    batch_data = []

    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_metadata(session, url, userId, temp_token) for url in urlList]
        scraped_results = await asyncio.gather(*tasks)

        for data in scraped_results:
            if data:
                batch_data.append(ScrapedData.from_dict(data))
                results.append(data)

    if batch_data:
        try:
            repo.create_scraped_data_batch(batch_data)
            db.commit()
        except SQLAlchemyError as e:
            log.error(f"Error from celery setup : {str(e)}")
            db.rollback()
        finally:
            db.close()

    return results

async def _fetch_metadata(session, url, userId, temp_token):
    try:
        async with session.get(url, timeout=20) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            title = soup.find('title').text.strip() if soup.find('title') else None
            description = soup.find('meta', attrs={'name': 'description'})
            description = description['content'].strip() if description else None
            keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = keywords['content'].strip() if keywords else None

            return {
                "user_id": userId,
                "temp_token": temp_token,
                "url": url,
                "title": title,
                "description": description,
                "keywords": keywords,
                "status": "success",
            }

    except asyncio.TimeoutError:
        log.warning(f"Warning from celery setup : Timeout: {url}")
        return _error_response(userId, temp_token, url, "Timeout occurred")

    except TooManyRedirects:
        log.warning(f"Warning from celery setup : Too many redirects: {url}")
        return _error_response(userId, temp_token, url, "Too many redirects")

    except SSLError:
        log.warning(f"Warning from celery setup : SSL error: {url}")
        return _error_response(userId, temp_token, url, "SSL Error")

    except ConnectionError:
        log.warning(f"Warning from celery setup : Connection error: {url}")
        return _error_response(userId, temp_token, url, "Connection Error")

    except Exception as e:
        log.error(f"Warning from celery setup : Unexpected error for {url}: {str(e)}")
        return _error_response(userId, temp_token, url, f"Unexpected error: {str(e)}")

def _error_response(userId, temp_token, url, error_message):
    return {
        "user_id": userId,
        "temp_token": temp_token,
        "url": url,
        "title": None,
        "description": None,
        "keywords": None,
        "status": "error",
        "error_message": error_message,
    }
from celery import Celery
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from src.repositories.scrapedDataRepository import ScrapedDataRepository
from src.repositories.userRepository import UserRepository
from src.models.scrapedDataModel import ScrapedData
from sqlalchemy.orm import Session
from fastapi import Depends
from src.core.config import getRedisDbSettings
from src.dependencies import getDb
from ssl import CERT_NONE

settings = getRedisDbSettings()

celeryApp = Celery(
    'scrapper-service',
    broker=settings.REDIS_DB_URL,
    backend=settings.REDIS_DB_URL
)

celeryApp.conf.update(
    broker_use_ssl={
        'ssl_cert_reqs': CERT_NONE,  
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': CERT_NONE,  
    },
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celeryApp.task(name="scrapper-service.core.celerySetup.scrapMetaData", bind=True)
def scrapMetaData(self, urlList: list, emailId : str):
    import asyncio

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_scrapMetaData(urlList, emailId))

async def _scrapMetaData(urlList: list, emaiId : str):
    results = []
    db = next(getDb())
    repo = ScrapedDataRepository(db)
    userRepo = UserRepository(db)

    print(f">>>>>>>>>>>>>>>>>>>>>>>>>this is email {emaiId}>>>>>>>>>>>>>>>>>>>>>")
    userId = userRepo.getUserIdByEmailId(emaiId)

    batch_data = []  
    batch_size = 50 

    for url in urlList:
        try:
            print(f"Scraping URL: {url}")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soap = BeautifulSoup(response.text, 'html.parser')

            title = soap.find('title').text.strip() if soap.find('title') else None
            description = soap.find('meta', attrs={'name': 'description'})
            description = description['content'].strip() if description else None
            keywords = soap.find('meta', attrs={'name': 'keywords'})
            keywords = keywords['content'].strip() if keywords else None

            data = {
                "user_id":userId,
                "url": url,
                "title": title,
                "description": description,
                "keywords": keywords,
                "status": "success",
            }

            scraped_data = ScrapedData.from_dict(data)
            batch_data.append(scraped_data)

            results.append({
                "user_id":userId,
                "email_id":emaiId,
                'url': url,
                'title': title,
                'description': description,
                'keywords': keywords,
                'status': 'success',
            })

            if len(batch_data) >= batch_size:
                repo.create_scraped_data_batch(batch_data)
                batch_data = []

        except RequestException as e:
            error_data = ScrapedData.from_dict({
                "user_id":userId,
                "url": url,
                "status": "error",
                "error_message": str(e),
            })
            batch_data.append(error_data)

            results.append({
                "user_id":userId,
                'url': url,
                'title': None,
                'description': None,
                'keywords': None,
                'status': 'error',
                'error_message': str(e),
            })

            if len(batch_data) >= batch_size:
                repo.create_scraped_data_batch(batch_data)
                batch_data = []

        except Exception as e:
            error_data = ScrapedData.from_dict({
                "user_id":userId,
                "url": url,
                "status": "error",
                "error_message": str(e),
            })
            batch_data.append(error_data)

            results.append({
                "user_id":userId,
                'url': url,
                'title': None,
                'description': None,
                'keywords': None,
                'status': 'error',
                'error_message': str(e),
            })

            if len(batch_data) >= batch_size:
                repo.create_scraped_data_batch(batch_data)
                batch_data = []

    if batch_data:
        repo.create_scraped_data_batch(batch_data)

    return results
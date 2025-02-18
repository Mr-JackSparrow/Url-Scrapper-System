from celery import Celery
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from src.repositories.scrapedDataRepository import ScrapedDataRepository
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
def scrapMetaData(self, urlList: list):
    import asyncio

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_scrapMetaData(urlList))

async def _scrapMetaData(urlList: list):
    results = []
    db = next(getDb())
    repo = ScrapedDataRepository(db)

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
                "url": url,
                "title": title,
                "description": description,
                "keywords": keywords,
                "status": "success", 
            }

            scraped_data = ScrapedData.from_dict(data)
            repo.create_scraped_data(scraped_data)

            results.append({
                'url': url,
                'title': title,
                'description': description,
                'keywords': keywords,
                'status': 'success',
            })
        except RequestException as e:

            error_data = ScrapedData.from_dict({
                "url": url,
                "status": "error",
                "error_message": str(e),
            })
            repo.create_scraped_data(error_data)

            results.append({
                'url': url,
                'title': None,
                'description': None,
                'keywords': None,
                'status': 'error',
                'error_message': str(e),
            })
        except Exception as e:
        
            error_data = ScrapedData.from_dict({
                "url": url,
                "status": "error",
                "error_message": str(e),
            })
            repo.create_scraped_data(error_data)

            results.append({
                'url': url,
                'title': None,
                'description': None,
                'keywords': None,
                'status': 'error',
                'error_message': str(e),
            })
    return results
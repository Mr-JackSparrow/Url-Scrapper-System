from celery import Celery
import requests
from bs4 import BeautifulSoup

celeryApp = Celery(
    'scrapper-service',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

@celeryApp.task(name="scrapper-service.core.celerySetup.scrapMetaData", bind=True)
def scrapMetaData(self, urlList : list):
    try:
        
        for url in urlList:
            print("Scraping URL: ", url)
            response = requests.get(url, timeout=5)
            soap = BeautifulSoup(response.text, 'html.parser')
            print("Title: ", soap.find('title').text)

    except Exception as e:
        pass

celeryApp.conf.result_expires = 3600
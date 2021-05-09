from fastapi import FastAPI
from news.service.crawler import CrawlerService

crawler_app = FastAPI()
crawler_service = CrawlerService()


@crawler_app.post('/crawler')
async def run_crawler():
    crawler_service.run_crawler()

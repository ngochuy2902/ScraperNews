from fastapi import FastAPI, BackgroundTasks
from starlette.responses import JSONResponse

from news.service.crawler import CrawlerService

crawler_app = FastAPI()
crawler_service = CrawlerService()


@crawler_app.post('/crawler')
async def run_crawler():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(crawler_service.run_crawler)
    response = JSONResponse(status_code=200, content="Crawler is running", background=background_tasks)
    return response

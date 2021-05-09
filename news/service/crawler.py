from datetime import datetime

import requests

from news.launcher import run_all_spider
from news.settings import RANKING_API_URL


class CrawlerService:

    @staticmethod
    def run_crawler():
        run_all_spider()
        print('Crawl complete')
        created_time = str(datetime.now().isoformat())
        data = {"created_time": created_time}
        requests.post(url=RANKING_API_URL, json=data)

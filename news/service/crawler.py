from datetime import datetime
from multiprocessing.context import Process

import requests

from news.launcher import run_all_spider
from news.settings import RANKING_API_URL


class CrawlerService:

    @staticmethod
    def run_crawler():
        try:
            process = Process(target=run_all_spider)
            process.start()
            process.join()
            process.terminate()
            print('Crawl complete')
            created_time = str(datetime.now().isoformat())
            data = {"created_time": created_time}
            # requests.post(url=RANKING_API_URL, json=data)
        except(Exception,) as ex:
            print(f'Error run spider: {ex}')

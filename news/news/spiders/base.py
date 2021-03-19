from scrapy import Spider


class BaseSpider(Spider):
    name = 'base-spider'
    id_spider = None

    def start_requests(self):
        raise NotImplementedError

    def parse(self, response, **kwargs):
        raise NotImplementedError

import uuid

import scrapy
from scrapy.http.response import Response

from .base import BaseSpider, parse_datetime


class VietnamnetSpider(BaseSpider):
    name = 'vietnamnet'

    def start_requests(self):
        urls_dict = {
            "https://vietnamnet.vn/vn/thoi-su/chinh-tri/": "chinh-tri",
            "https://vietnamnet.vn/vn/thoi-su/": "xa-hoi",
            "https://vietnamnet.vn/vn/giao-duc/": "giao-duc",
            "https://vietnamnet.vn/vn/suc-khoe/": "y-te",
            "https://vietnamnet.vn/vn/cong-nghe/": "cong-nghe",
            "https://vietnamnet.vn/vn/the-thao/": "the-thao",
            "https://vietnamnet.vn/vn/giai-tri/": "giai-tri"
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        urls = response.css('.Top-Cate').re(r'\/vn\/[^"]*?\d{6}.html') + response.css('.list-content').re(
            r'\/vn\/[^"]*?\d{6}.html')
        urls = list(set(urls))
        for url in urls:
            yield scrapy.Request(url="https://vietnamnet.vn" + url, callback=self.parse_content_article,
                                 meta=response.meta)

    def parse_content_article(self, response: Response):
        title = response.css('h1::text').get()
        content = " ".join(response.css('div.ArticleDetail p::text').getall())
        if title is None or content is None:
            yield {}
        else:
            article = {
                'uuid_url': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
                'url': response.url,
                'domain': self.name,
                'title': title.strip(),
                'category_url': response.meta['category_url'],
                'category': response.meta['category'],
                'time': parse_datetime(response.css('.ArticleDate::text').get()),
                'content': content.strip()
            }
            yield article

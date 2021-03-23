import uuid

import scrapy
from scrapy.http.response import Response

from .base import BaseSpider, parse_datetime


class VnexpressSpider(BaseSpider):
    name = 'vnexpress'

    def start_requests(self):
        urls_dict = {
            "https://vnexpress.net/thoi-su/chinh-tri": "chinh-tri",
            "https://vnexpress.net/doi-song": "xa-hoi",
            "https://vnexpress.net/giao-duc": "giao-duc",
            "https://vnexpress.net/khoa-hoc/tin-tuc": "khoa-hoc",
            "https://vnexpress.net/suc-khoe/tin-tuc": "y-te",
            "https://vnexpress.net/the-thao": "the-thao",
            "https://vnexpress.net/giai-tri": "giai-tri"
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        urls = response.css('html').re(r'https:\/\/vnexpress.*.html')
        urls = list(set(urls))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_content_article, meta=response.meta)

    def parse_content_article(self, response: Response):
        content = " ".join(response.css('p::text').getall())
        title = response.css('h1.title-detail::text')
        if title is None:
            yield {}
        else:
            article = {
                'uuid_url': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
                'url': response.url,
                'domain': self.name,
                'title': title.get(),
                'category_url': response.meta['category_url'],
                'category': response.meta['category'],
                'time': parse_datetime(response.css('.date::text').get()),
                'content': content.strip()
            }
            yield article

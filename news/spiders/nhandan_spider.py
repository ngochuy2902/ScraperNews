import uuid

import scrapy
from scrapy.http.response import Response

from .base import BaseSpider, parse_datetime, check_valid_text
from ..data.mongo import MongoDB


class NhanDanSpider(BaseSpider):
    name = 'nhandan'
    mongo = MongoDB()

    def start_requests(self):
        urls_dict = {
            "https://nhandan.com.vn/chinhtri": "chinh-tri",
            "https://nhandan.com.vn/xahoi": "xa-hoi",
            "https://nhandan.com.vn/vanhoa": "van-hoa",
            "https://nhandan.com.vn/giaoduc": "giao-duc",
            "https://nhandan.com.vn/khoahoc-congnghe": "khoa-hoc",
            "https://nhandan.com.vn/y-te": "y-te",
            "https://nhandan.com.vn/thethao": "the-thao",
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        urls = response.css('.boxlist-list').re(r'(\/[^"]*-\d{6}\/)')
        urls = list(set(urls))
        for url in urls:
            if self.mongo.get_articles_by_url(url) is None:
                url = "https://nhandan.com.vn" + url
                meta = response.meta
                meta['url'] = url
                yield scrapy.Request(url=url, callback=self.parse_content_article,
                                     meta=meta)

    def parse_content_article(self, response: Response):
        title = response.css('h1::text').get()
        content = " ".join(response.css('.box-content-detail p::text').getall())
        if check_valid_text(title) is False or check_valid_text(content) is False:
            yield {}
        else:
            article = {
                'uuid_url': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
                'url': response.meta['url'],
                'domain': self.name,
                'title': title.strip(),
                'category_url': response.meta['category_url'],
                'category': response.meta['category'],
                'time': parse_datetime(response.css('div.box-date::text').get()),
                'content': content.strip()
            }
            yield article

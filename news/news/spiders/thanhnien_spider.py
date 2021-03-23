import uuid

import scrapy
from scrapy.http.response import Response
from w3lib.html import remove_tags, remove_tags_with_content

from .base import BaseSpider, parse_datetime


class ThanhNienSpider(BaseSpider):
    name = 'thanhnien'

    def start_requests(self):
        urls_dict = {
            "https://thanhnien.vn/thoi-su/chinh-tri/": "chinh-tri",
            "https://thanhnien.vn/doi-song/": "xa-hoi",
            "https://thanhnien.vn/van-hoa/": "van-hoa",
            "https://thanhnien.vn/giao-duc/": "giao-duc",
            "https://thanhnien.vn/suc-khoe/": "y-te",
            "https://thanhnien.vn/cong-nghe/": "cong-nghe",
            "https://thanhnien.vn/the-thao/": "the-thao",
            "https://thanhnien.vn/giai-tri/": "giai-tri"
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        urls = response.css('.feature').re(r'\/.*\/.*\d{7}.html') + response.css('.relative').re(r'\/.*\/.*\d+.html')
        urls = list(set(urls))
        for url in urls:
            yield scrapy.Request(url="https://thanhnien.vn" + url, callback=self.parse_content_article,
                                 meta=response.meta)

    def parse_content_article(self, response: Response):
        title = response.css('h1.details__headline::text').get()
        if title is None:
            title = response.css('h2.details__headline::text').get()
        if title is None:
            yield {}
        else:
            raw_content = response.xpath('//div[@id="abody"]').extract()[0]
            content = remove_tags(remove_tags_with_content(raw_content, ('script',)))
            article = {
                'uuid_url': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
                'url': response.url,
                'domain': self.name,
                'title': title.strip(),
                'category_url': response.meta['category_url'],
                'category': response.meta['category'],
                'time': parse_datetime(response.css('ti::text').get()),
                'content': content.strip()
            }
            yield article

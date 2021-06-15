import uuid

import scrapy
from scrapy.http.response import Response
from w3lib.html import remove_tags, remove_tags_with_content

from .base import BaseSpider, parse_datetime, check_valid_text
from ..data.mongo import MongoDB


class ThanhNienSpider(BaseSpider):
    name = 'thanhnien'
    mongo = MongoDB()

    def start_requests(self):
        urls_dict = {
            "https://thanhnien.vn/thoi-su/chinh-tri/": "chinh-tri",
            "https://thanhnien.vn/doi-song/": "xa-hoi",
            "https://thanhnien.vn/van-hoa/": "van-hoa",
            "https://thanhnien.vn/tai-chinh-kinh-doanh/": "kinh-te",
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
        urls = response.css('.feature').re(r'\/[^".]*\/[^".]*\d{7}.html') + response.css('.relative').re(
            r'\/[^".]*\/[^".]*\d{7}.html')
        urls = list(set(urls))
        for url in urls:
            if self.mongo.get_articles_by_url(url) is None:
                url = "https://thanhnien.vn" + url
                meta = response.meta
                meta['url'] = url
                yield scrapy.Request(url=url, callback=self.parse_content_article,
                                     meta=meta)

    def parse_content_article(self, response: Response):
        title = response.css('h1.details__headline::text').get()
        content = None
        if bool(response.xpath('//div[@id="abody"]').extract()):
            raw_content = response.xpath('//div[@id="abody"]').extract()[0]
            content = remove_tags(remove_tags_with_content(raw_content, ('script', 'table')))
        if not bool(title):
            title = response.css('h2.details__headline::text').get()
        if check_valid_text(title) is False or check_valid_text(content) is False:
            yield {}
        else:
            article = {
                'uuid': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
                'url': response.meta['url'],
                'domain': self.name,
                'title': title.strip(),
                'category_url': response.meta['category_url'],
                'category': response.meta['category'],
                'time': parse_datetime(response.css('time::text').get()),
                'content': content.strip()
            }
            yield article

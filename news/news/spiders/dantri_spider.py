import re
import uuid
import datetime
import scrapy
from scrapy.http.response import Response
from .base import BaseSpider


class DanTriSpider(BaseSpider):
    name = 'dantri'

    def start_requests(self):
        urls_dict = {
            "https://dantri.com.vn/xa-hoi/chinh-tri.htm": "chinh-tri",
            "https://dantri.com.vn/xa-hoi.htm": "xa-hoi",
            "https://dantri.com.vn/van-hoa.htm": "van-hoa",
            "https://dantri.com.vn/giao-duc-huong-nghiep.htm": "giao-duc",
            "https://dantri.com.vn/suc-khoe.htm": "y-te",
            "https://dantri.com.vn/suc-manh-so.htm": "cong-nghe",
            "https://dantri.com.vn/the-thao.htm": "the-thao",
            "https://dantri.com.vn/giai-tri.htm": "giai-tri"
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        urls = response.css('html').re(r'\/\w*-.*\/.*\d{17}.htm')
        urls = list(set(urls))
        for url in urls:
            yield scrapy.Request(url="https://dantri.com.vn" + url, callback=self.parse_content_article, meta=response.meta)

    def parse_content_article(self, response: Response):
        content = " ".join(response.css('div.dt-news__content p::text').getall())
        article = {
            'uuid_url': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
            'url': response.url,
            'domain': self.name,
            'title': response.css('h1.dt-news__title::text').get().strip(),
            'category_url': response.meta['category_url'],
            'category': response.meta['category'],
            'time': self.parse_datetime(response.css('.dt-news__time::text').get()),
            'content': content
        }
        yield article

    def parse_datetime(self, datetime_str):
        try:
            date_pattern = re.compile(r"\d{1,2}\/\d{1,2}\/\d{4}")
            time_pattern = re.compile(r"\d{1,2}:\d{1,2}")

            date_str = re.findall(date_pattern, datetime_str)
            if len(date_str) == 1:
                date_str = date_str[0]
            else:
                raise Exception(f"Cannot parser date from {datetime_str}")

            time_str = re.findall(time_pattern, datetime_str)
            if len(time_str) == 1:
                time_str = time_str[0]
            else:
                raise Exception(f"Cannot parser time from {datetime_str}")
        except(Exception,) as exc:
            return datetime.datetime.now()

        datetime_str = date_str + " " + time_str
        return datetime.datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')

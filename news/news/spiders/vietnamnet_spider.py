import re
import uuid
import datetime
import scrapy
from scrapy.http.response import Response


class VietnamnetSpider(scrapy.Spider):
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
        urls = response.css('.Top-Cate').re(r'\/vn\/[^"]*?\d+.html') + response.css('.list-content').re(r'\/vn\/[^"]*?\d+.html')
        urls = list(set(urls))
        for url in urls:
            yield scrapy.Request(url="https://vietnamnet.vn" + url, callback=self.parse_content_article, meta=response.meta)

    def parse_content_article(self, response: Response):
        content = " ".join(response.css('div.ArticleDetail p::text').getall())
        article = {
            'uuid_url': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
            'url': response.url,
            'domain': self.name,
            'title': response.css('h1::text').get().strip(),
            'category_url': response.meta['category_url'],
            'category': response.meta['category'],
            'time': self.parse_datetime(response.css('.time-::text').get()),
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

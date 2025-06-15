import scrapy
import sys
import re
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor


class EmailSpider(scrapy.Spider):
    name = 'email_spider'
    start_urls = [str(sys.argv[1])]
    allowed_domains = [urlparse(str(sys.argv[1])).netloc]
    emails_found = set()
    link_extractor = LinkExtractor()

    def parse(self, response):
        email_pattern = r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'
        self.emails_found.update(re.findall(
            email_pattern, response.text, re.IGNORECASE))
        links = self.link_extractor.extract_links(response)
        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse)

    def close(spider, reason):
        output_data = {'emails': list(spider.emails_found)}
        with open('emails.json', 'w') as f:
            import json
            json.dump(output_data, f, indent=4)


if __name__ == "__main__":
    process = CrawlerProcess(
        {'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'})
    process.crawl(EmailSpider)
    process.start()

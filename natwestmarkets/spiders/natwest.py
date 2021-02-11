import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from natwestmarkets.items import Article


class NatwestSpider(scrapy.Spider):
    name = 'natwest'
    start_urls = ['https://ci.natwest.com/insights/articles']

    def parse(self, response):
        articles = response.xpath('//a[@class="n-col n-small-12 n-medium-4 card"]')
        for article in articles:
            link = article.xpath('./@href').get()
            category = article.xpath('.//span[@class="title-label"]/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(category=category))

        next_page = response.xpath('//a[@class="pagination__link pagination__link--next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, category):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="hero__title"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="hero__description"]/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d %B %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="col small-12 xlarge-9 article-content '
                                 'article-content--article editor"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        author = ",".join(response.xpath('//h3[@class="article-aside__author-title"]/text()').getall())

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)
        item.add_value('category', category)

        return item.load_item()

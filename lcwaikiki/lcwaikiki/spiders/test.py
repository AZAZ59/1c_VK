import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings


class TestSpider(scrapy.Spider):
    name = 'test'
    base_url = 'https://www.lcwaikiki.com'
    allowed_domains = ['www.lcwaikiki.com']
#    start_urls = ['https://www.lcwaikiki.com/tr-TR/TR/etiket/bebek-sloganli-tulumlar/']
    start_urls = [
        'https://www.lcwaikiki.com/tr-TR/TR/ajax/Tag/TagPageData?CountryCode=TR&Tag=bebek-sloganli-tulumlar&PageIndex=1']

    def parse(self, response):

        resp_json = response.json()
        all_items_links = [self.base_url + x['ModelUrl'] for x in resp_json['CatalogList']['Items']]
        yield from response.follow_all(all_items_links, callback=self.parse_item)
        next_url = resp_json['CatalogList']['LoadMoreUrl']
        print(next_url)
        if next_url != '#':
            next_url = next_url[next_url.index('\'') + 1:next_url.rindex(',') - 1]
            yield response.follow(self.base_url + next_url)
        pass

    def parse_item(self, response):
        product_code = response.css('div.product-code::text')[0].get().strip()
        product_code = product_code[product_code.index(':') + 2:]

        sizes = response.css('meta[name=Size]').attrib['content'].split(',')
        if len(sizes) > 1:
            try:
                sizes = sorted(sizes, key=lambda x: int(x[:x.index('-')]))
            except:
                raise CloseSpider('ERROR' + sizes)
        colors = response.css('.color-box').css('div::attr(title)').getall()
        yield {
            'img1'         : response.css('#OptionImage0').attrib['src'],
            'img2'         : response.css('#OptionImage1').attrib['src'],
            'all_images'   : ', '.join(response.css('.product-images-desktop img::attr(src)').getall()),
            'product-code' : product_code,
            'product-title': response.css('.product-title::text').get().strip(),
            'sizes'        : sizes,
            'price'        : response.css('.single-price::text').get(),
            'colors'       : colors,
        }
        pass


if __name__ == '__main__':
    process = CrawlerProcess(settings=get_project_settings())

    process.crawl(TestSpider, )
    process.start()  # the script will block here until the crawling is finished

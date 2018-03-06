# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.http.request import Request
from scrapy.selector import Selector
from electronic.items import ElectronicItem
from electronic.customfunction import cleansplit, listbalancer, cleanqty
from scrapy.utils.project import get_project_settings

class TmeSpider(Spider):
    name = "tme"
    allowed_domains = ["www.tme.eu"]
    start_urls = ['http://www.tme.eu/']

    def __init__(self, query='', *args, **kwargs):
        """ Initial instances attributes will be used on class defined here.

        query argument need to be passed in order search keyword to passed on the web result

        Args:
            param1: query

        Returns:
            self.start_urls
            self.query
            self.debug
            self.spider_name

        TODO:
             Incapsula: unblock spider IP from incapsula on distributor firewall to remove necessity of incapsula hack
        """
        super(TmeSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://www.tme.eu/']
        p_setting = get_project_settings()
        self.query = query
        self.debug = p_setting.get("APP_DEBUG")
        self.spider_name = "Tme"

    def start_requests(self):
        """ Start requests

        Initial requests that need to be made (search url queries)

        Args:

        Returns:
            response
        """
        yield Request('http://www.tme.eu/en/katalog/?s_field=accuracy&search=%s' % self.query, callback=self.parse_search)

    def parse_search(self, response):
        """ Parse_search

        Initial parsing after search request made. then check the response whether it single result or pagination result.

        Args:
            response

        Returns:
            response
        """
        s = Selector(response)
        top_cat_urls = s.xpath('//div[@class="category_groups"]//ul/li/a/@href').extract()
        download_table = s.xpath('//div[@id="productsCategoryName"]/h1/text()').extract_first()
        if self.debug: print "Single category status: %s" % (download_table)
        single_result = s.xpath('//div[@class="bota-headline"]//text()').extract_first()
        if self.debug: print "Single item status: %s" % ((single_result))
        #print top_cat_urls
        if top_cat_urls:
            for url in top_cat_urls:
                print response.urljoin(url)#"Following {0}".format(url)
                yield Request(response.urljoin(url), callback=self.parse_search_result, dont_filter=True)
        elif download_table:
            yield Request(response.url, callback=self.parse_search_result, dont_filter=True)
        elif single_result:
            yield Request(response.url, callback=self.single_result, dont_filter=True)

    def single_result(self, response):
        """ single result parser

        Parser that will be used if response result detected as single item page

        Args:
            response

        Returns:
            item
        """
        item = ElectronicItem()

        part_number = cleansplit(Selector(text=response.body)
                                            .xpath('//td[@id="reportPartNumber"]//text()').extract_first())
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                            .xpath('//h1[@itemprop="model"]//text()').extract_first())
        manufacturer_name = cleansplit(Selector(text=response.body)
                                            .xpath('//h2[@class="lnkMfct"]//span//a//span//text()').extract_first())
        description = cleansplit(Selector(text=response.body)
                                            .xpath('//td[@itemprop="description"]//text()').extract_first())
        quantity_available = cleansplit(Selector(text=response.body)
                                            .xpath('//td[@id="quantityAvailable"]//span[@id="dkQty"]//text()').extract_first())
        image_url = cleansplit(Selector(text=response.body)
                                            .xpath('//a[@class="bota-image-large"]//img//@src').extract_first())

        item['manufacturer'] = manufacturer_name
        item['manufacturer_part_number'] = manufacturer_part_number
        item['supplier'] = self.spider_name
        item['supplier_part_number'] = part_number
        item['description'] = description
        item['product_url'] = response.url
        item['image_url'] = "{0}{1}".format("http:", image_url)
        item['stock_qty'] = cleanqty(quantity_available)
        yield item

    def parse_search_result(self, response):
        """ Parse Search Result

        Parser that will be used if response result detected as search result page.

        Args:
            response

        Returns:
            item
        """
        item = ElectronicItem()

        part_number = cleansplit(Selector(text=response.body)
                                            #.xpath('//td[contains(@class, "tr-dkPartNumber")]//a//text()'))
                                            .css("a.symbol.product-symbol::text"))
        #print key_part_number
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                            #.xpath('//td[contains(@class, "tr-mfgPartNumber")]//a//span//text()'))
                                            .css(".manufacturer>a:nth-of-type(2)>b::text"))
        #print manufacturer_part_number
        manufacturer_name = cleansplit(Selector(text=response.body)
                                            #.xpath('//td[contains(@class, "tr-vendor")]//span//a//span//text()'))
                                            .css(".manufacturer>a:nth-of-type(1)>b::text"))
        description = cleansplit(Selector(text=response.body)
                                            #.xpath('//td[contains(@class, "tr-description")]//text()'))
                                            .css(".product>div>span::text"))
        # javascript execution needed, scrapy doesnt handle it
        quantity_available = [] #cleansplit(Selector(text=response.body)
                                            #.xpath('//td[contains(@class, "tr-qtyAvailable ptable-param")]//span//text()'))
                                            #.xpath('//tbody[1]/tr/td[5]/div[1]/b[2]'))
                                            #.css("td.stany>div>b:nth-of-type(2)::text"))
        print quantity_available
        image_url = cleansplit(Selector(text=response.body)
                                            #.xpath('//img[contains(@class, "pszoomer")]')
                                            #.xpath('@src'))
                                            .css(".product_image>a>img::attr(src)"))
        '''
        This is variable handler when no content in selected xpath. so this algorithm will keep list balanced.
        and alyways will process zip iteration. and return scaped item. see customfunction.py for listbalancer method'''
        if not quantity_available: quantity_available = listbalancer(part_number)
        if not image_url: image_url = listbalancer(image_url)
        if not description: description = listbalancer(description)

        for i, j, k, l, m, n in zip(part_number, manufacturer_part_number, manufacturer_name,
                                    description, quantity_available, image_url):
            item['manufacturer'] = k
            item['manufacturer_part_number'] = j
            item['supplier'] = self.spider_name
            item['supplier_part_number'] = i
            item['description'] = l
            item['image_url'] = n
            item['product_url'] = response.url
            item['stock_qty'] = cleanqty(m.replace(u'\xa0', u''))
            yield item
        next_url = response.css('form>div.nawigator>a:last-of-type::attr(href)').extract_first()
        if self.debug: print "Next URL -> %s" % (response.urljoin(next_url))
        if next_url and "javascript:void(0);" not in next_url:
            "Following Next Page {0}".format(response.urljoin(next_url))
            yield Request(response.urljoin(next_url), callback=self.parse_search_result, dont_filter=True)

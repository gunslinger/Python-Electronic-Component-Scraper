# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.http.request import Request
from scrapy.selector import Selector
from electronic.items import ElectronicItem
from electronic.customfunction import cleansplit, listbalancer, cleanqty
from scrapy.utils.project import get_project_settings

class DigikeySpider(Spider):
    name = "digikey"
    allowed_domains = ["digikey.com"]
    start_urls = ['https://www.digikey.com/products/en']

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
        super(DigikeySpider, self).__init__(*args, **kwargs)
        p_setting = get_project_settings()
        self.start_urls = ['https://www.digikey.com']
        self.query = query
        self.debug = p_setting.get("APP_DEBUG")
        self.spider_name = "Digikey"

    def start_requests(self):
        """ Start requests

        Initial requests that need to be made (search url queries)

        Args:

        Returns:
            response
        """
        yield Request('https://www.digikey.com/products/en?keywords=%s' % self.query, callback=self.parse_search)

    def parse_search(self, response):
        """ Parse_search

        Initial parsing after search request made. then check the response whether it single result or pagination result.

        Args:
            response

        Returns:
            response
        """
        s = Selector(response)
        top_cat_urls = s.xpath('//a[@class="catfilterlink"]/@href').extract()
        download_table = s.xpath('//form[@class="download-table"]/input/@value').extract_first()
        if self.debug: print "Single category status: %s" % (download_table)
        single_result = s.xpath('//div[@class="bota-headline"]//text()').extract_first()
        if self.debug: print "Single item status: %s" % ((single_result))
        if top_cat_urls:
            for url in top_cat_urls:
                print "Following {0}".format(url)
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
                                            .xpath('//meta[@itemprop="productID"]/@content').extract_first())
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
        item['supplier_part_number'] = part_number.replace("sku:",""    )
        item['description'] = description
        item['stock_qty'] = cleanqty(quantity_available)
        item['product_url'] = response.url
        item['image_url'] = "{0}{1}".format("http:", image_url)
        yield item


    def parse_search_result(self, response):
        item = ElectronicItem()

        key_part_number = cleansplit(Selector(text=response.body)
                                            .xpath('//td[@id="reportPartNumber"]//text()'))
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                            .xpath('//td[contains(@class, "tr-mfgPartNumber")]//a//span//text()'))
        manufacturer_name = cleansplit(Selector(text=response.body)
                                            .xpath('//td[contains(@class, "tr-vendor")]//span//a//span//text()'))
        description = cleansplit(Selector(text=response.body)
                                            .xpath('//td[contains(@class, "tr-description")]//text()'))
        quantity_available = cleansplit(Selector(text=response.body)
                                            .xpath('//td[contains(@class, "tr-qtyAvailable ptable-param")]//span//text()'))
        image_url = cleansplit(Selector(text=response.body).xpath('//img[contains(@class, "pszoomer")]')
                                            .xpath('@src'))
        for i, j, k, l, m, n in zip(key_part_number, manufacturer_part_number, manufacturer_name,
                                    description, quantity_available, image_url):
            item['manufacturer'] = k
            item['manufacturer_part_number'] = j
            item['supplier'] = self.spider_name
            item['supplier_part_number'] = i
            item['description'] = l
            item['image_url'] = "{0}{1}".format("http:", n)
            item['product_url'] = response.url
            item['stock_qty'] = cleanqty(m)
            yield item
        next_url = response.xpath('//a[@class="Next"]/@href').extract_first()
        if self.debug: print "Next URL -> %s" % (next_url)
        if next_url:
            "Following Next Page {0}".format(response.urljoin(next_url))
            yield Request(response.urljoin(next_url), callback=self.parse_search_result, dont_filter=True)
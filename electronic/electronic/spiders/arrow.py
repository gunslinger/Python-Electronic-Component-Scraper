# -*- coding: utf-8 -*-

from scrapy import Spider, Request, settings
from scrapy.http.request import Request
from scrapy.selector import Selector
from electronic.items import ElectronicItem
from electronic.customfunction import cleansplit, listbalancer, cleanqty
from scrapy.utils.project import get_project_settings

class ArrowSpider(Spider):
    name = "arrow"
    allowed_domains = ["www.arrow.com"]
    start_urls = ['https://www.arrow.com/']

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
        super(ArrowSpider, self).__init__(*args, **kwargs)
        p_setting = get_project_settings()
        self.start_urls = ['https://www.arrow.com']
        self.query = query
        self.debug = p_setting.get("APP_DEBUG")
        self.spider_name = "Arrow"

    def start_requests(self):
        """ Start requests

        Initial requests that need to be made (search url queries)

        Args:

        Returns:
            response
        """
        yield Request('https://www.arrow.com/en/products/search?q=%s' % self.query, callback=self.parse_search)

    def parse_search(self, response):
        """ Parse_search

        Initial parsing after search request made. then check the response whether it single result or pagination result.

        Args:
            response

        Returns:
            response
        """
        s = Selector(response)
        item_result_search_list = s.xpath('//a[@class="SearchResults-productLink"]/@href').extract()
        single_result = s.xpath('//h2[@class="PartSpecifications-heading"]//text()').extract_first()
        if self.debug: print "Single item status: %s" % ((single_result))
        if item_result_search_list:
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
                                            .xpath('//h1[@class="Product-Summary-Name"]//text()').extract_first())
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                            .xpath('//meta[@itemprop="mpn"]//@content').extract_first())
        manufacturer_name = cleansplit(Selector(text=response.body)
                                            .xpath('//p[@itemprop="brand"]//a//text()').extract_first())
        description = cleansplit(Selector(text=response.body)
                                            .xpath('//p[@itemprop="description"]//text()').extract_first())
        quantity_available = cleansplit(Selector(text=response.body)
                                            .xpath("//li[contains(@class,'BuyingOptions-option')]//@data-quantity").extract_first())
        image_url = cleansplit(Selector(text=response.body)
                                            .xpath('//img[@class="Product-Summary-Image"]//@src').extract_first())

        item['manufacturer'] = manufacturer_name
        item['manufacturer_part_number'] = manufacturer_part_number
        item['supplier'] = self.spider_name
        item['supplier_part_number'] = part_number
        item['description'] = description
        item['stock_qty'] = cleanqty(quantity_available)
        item['product_url'] = response.url

        # if image url is not found in item page
        if image_url:
            item['image_url'] = "{0}{1}".format("http:", image_url)
        else:
            item['image_url'] = image_url
        yield item


    def parse_search_result(self, response):
        """ Parse Search Result

        Parser that will be used if response result detected as search result page

        Args:
            response

        Returns:
            item
        """
        item = ElectronicItem()

        part_number = cleansplit(Selector(text=response.body)
                                            .xpath("//span[@class='SearchResults-productName']/span//text()"))
        # manufacturer part number always same with part number in arrow.com
        manufacturer_part_number = part_number
        manufacturer_name = cleansplit(Selector(text=response.body)
                                            .xpath("//a[@class='SearchResults-productManufacturer']//text()"))
        description = cleansplit(Selector(text=response.body)
                                            .xpath("//td[@class='SearchResults-column SearchResults-column--description']"
                                                   "//span//text()"))
        quantity_available = cleansplit(Selector(text=response.body)
                                            .xpath("//span[@class='SearchResults-stock']//span//following-sibling::text()"))
        image_url = cleansplit(Selector(text=response.body).xpath("//img[contains(@class, 'SearchResults-image')]")
                                            .xpath('@src'))

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
            item['image_url'] = "{0}{1}".format("http:",n)
            item['product_url'] = response.url
            item['stock_qty'] = cleanqty(m)

            yield item
        next_url = response.xpath('//link[@rel="next"]/@href').extract_first()
        if self.debug: print "Next URL -> %s" % (next_url)
        if next_url:
            "Following Next Page {0}".format(response.urljoin(next_url))
            yield Request(response.urljoin(next_url), callback=self.parse_search_result, dont_filter=True)

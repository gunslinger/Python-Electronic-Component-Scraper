# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.http.request import Request
from scrapy.selector import Selector
from electronic.items import ElectronicItem
from electronic.customfunction import cleansplit, listbalancer, cleanqty
from scrapy.utils.project import get_project_settings

class FutureelectronicsSpider(Spider):
    name = "futureelectronics"
    allowed_domains = ["futureelectronics.com"]
    start_urls = ['http://futureelectronics.com/']

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
        super(FutureelectronicsSpider, self).__init__(*args, **kwargs)
        p_setting = get_project_settings()
        self.query = query
        self.debug = p_setting.get("APP_DEBUG")
        self.spider_name = "FutureElectronics"

    def start_requests(self):
        """ Start requests

        Initial requests that need to be made (search url queries)

        Args:

        Returns:
            response
        """
        yield Request('http://www.futureelectronics.com/en/Search.aspx'
                      '?dsNav=Ntk:ManufacturerPartNumberUpshiftedSearch'
                      '%%7c*%s*%%7c1%%7c,Ny:True,Nea:True' % self.query, callback=self.parse_search)

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
        search_found = s.xpath("//h3[@class='results']//text()").extract_first()
        single_result = s.xpath('//h2[@class="PartSpecifications-heading"]//text()').extract_first()
        if self.debug: print "Search found status: %s" % (search_found)
        if self.debug: print "Single item status: %s" % ((single_result))
        if search_found:
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
        items = []

        part_number = cleansplit(Selector(text=response.body)
                                                .xpath('//p[@class="ref"]//b//following-sibling::text()[not(preceding-sibling::br) and not(self::br)]').extract_first())
        manufacturer_part_number = part_number
        manufacturer_name = cleansplit(Selector(text=response.body)
                                            .xpath('///div[@id="product-desc"]/h2//text()').extract_first())
        description = cleansplit(Selector(text=response.body)
                                            .xpath('//div[@id="product-desc"]/p[@class="desc"]//text()').extract_first())
        '''Quantity stock available always 29,050,000 for yes.'''
        quantity_available = cleansplit(Selector(text=response.body)
                                        .xpath("//td[@class='qty']//text()").extract_first())
                                            #.xpath('//ul[@class="BuyingOptions-labeledValues BuyingOptions-labeledValues--right"]'
                                            #       '//li[1]//strong//text()').extract_first())
        image_url = cleansplit(Selector(text=response.body)
                                            .xpath('/img[@id="previewedMEDImage"]/@src').extract_first())

        item['manufacturer'] = manufacturer_name
        item['manufacturer_part_number'] = manufacturer_part_number
        item['supplier'] = self.spider_name
        item['supplier_part_number'] = part_number
        item['description'] = description
        item['stock_qty'] = cleanqty(quantity_available)
        item['product_url'] = response.url
        item['image_url'] = image_url
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
                                            .xpath("//p[@class='mfr-results']//a//text()"))
        # manufacturer part number always same with part number in futureelectronics.com
        manufacturer_part_number = part_number
        manufacturer_name = cleansplit(Selector(text=response.body)
                                            .xpath("//div[@class='desc']//h5//text()"))
        description = cleansplit(Selector(text=response.body)
                                            .xpath("//p[@class='mfr-results']//a//text()"))
        quantity_available = cleansplit(Selector(text=response.body)
                                            .xpath("//span[@class='prices-in-stock-value']//text()"))
        image_url = cleansplit(Selector(text=response.body).xpath("//img[@class='productThumbnail']")
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
            item['image_url'] = n
            item['product_url'] = response.url
            item['stock_qty'] = m.replace(u'\xa0', u'')
            yield item
        next_url = response.xpath('//a[@id="ctl00_PlaceHolderMain_results_pagingFooter_ctl08_HyperLink6"]//@href').extract_first()
        if self.debug: print "Next URL -> %s" % (next_url)
        if next_url:
            "Following Next Page {0}".format(response.urljoin(next_url))
            yield Request(response.urljoin(next_url), callback=self.parse_search_result, dont_filter=True)
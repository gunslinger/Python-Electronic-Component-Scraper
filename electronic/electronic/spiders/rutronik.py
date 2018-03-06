# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.http.request import Request
from scrapy.selector import Selector
from electronic.items import ElectronicItem
from electronic.customfunction import cleansplit, listbalancer, cleanqty
from scrapy.utils.project import get_project_settings

class RutronikSpider(Spider):
    name = "rutronik"
    allowed_domains = ["rutronik24.com"]
    start_urls = ['https://www.rutronik24.com/']

    def __init__(self, query='', *args, **kwargs):
        '''
        Query test :
        * vn2 or VN20.6/09472-> Multiple item on search result

        :param query:
        :param args:
        :param kwargs:
        '''
        super(RutronikSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.rutronik24.com/']
        p_setting = get_project_settings()
        self.query = query
        self.debug = p_setting.get("APP_DEBUG")
        self.spider_name = "Rutronik"

    def start_requests(self):
        '''
        First initial request
        :return response:
        '''
        yield Request('https://www.rutronik24.com/search-result/qs:%s' % self.query, callback=self.parse_search)


    def parse_search(self, response):

        #print response.xpath('//html//text()').extract()
        s = Selector(response)
        item_result_search_list = s.xpath('//a[@class="SearchResults-productLink"]/@href').extract()
        search_found = s.xpath("//label[@for='new_orderby']//text()").extract_first()
        single_result = s.css(".tableheadFirstCol::text").extract_first()
        if self.debug: print "Search found status: %s" % (search_found)
        if self.debug: print "Single item status: %s" % (single_result)
        if search_found:
            yield Request(response.url, callback=self.parse_search_result, dont_filter=True)
        elif single_result:
            yield Request(response.url, callback=self.single_result, dont_filter=True)


    def single_result(self, response):
        '''
        Single result Parser

        :param response:
        :return:
        '''
        item = ElectronicItem()

        part_number = cleansplit(Selector(text=response.body)
                                    .css('td#ttiPartNumber strong::text').extract_first())
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                    .css('td#manufacturerPartNumber strong::text').extract_first())
        manufacturer_name = cleansplit(Selector(text=response.body)
                                    .css('td#manufacturer::text').extract_first())
        description = cleansplit(Selector(text=response.body)
                                    .css('td#partDescription::text').extract_first())
        '''Quantity stock available always 29,050,000 for yes.'''
        quantity_available = cleansplit(Selector(text=response.body)
                                    .xpath("//td[@class='val']//text()").extract_first())
        image_url = cleansplit(Selector(text=response.body)
                                    .xpath("/span[@class='photo-holder']/img/@src").extract_first())

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
                                #.css("li.ttipartnumber a ::text/li[@class='ttipartnumber']/a/text()"))
                                 #.css("li.ttipartnumber a::text"))
                                .xpath("//meta[@itemprop='sku']/@content"))
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                .xpath("//meta[@itemprop='mpn']/@content"))
                                 #.css("li.mfrpartnumber a::text"))
        manufacturer_name = cleansplit(Selector(text=response.body)
                                .xpath("//td[@class='oc_row']/div/img/@title"))
                                 #.css("li.manufacturer::text"))
        description = cleansplit(Selector(text=response.body)
                                .xpath("//span[@itemprop='description']/text()"))
                                #.css("td.description::text"))
        quantity_available = cleansplit(Selector(text=response.body)
                                .xpath("//table[1]/tbody[1]/tr/td[5]//text()"))
                                #.css("td.availability::text"))
        image_url = cleansplit(Selector(text=response.body)
                               .xpath("//table[1]/tbody[1]/tr/td[2]/img[1]/@src"))

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
        #next_url = response.xpath(
        #    '//a[@id="ctl00_PlaceHolderMain_results_pagingFooter_ctl08_HyperLink6"]//@href').extract_first()
        next_url = response.xpath("//nav[1]/ul[1]/li[4]/a[1]/@href").extract_first()
        if self.debug: print "Next URL -> %s" % (next_url)
        if next_url:
            "Following Next Page {0}".format(response.urljoin(next_url))
            yield Request(response.urljoin(next_url), callback=self.parse_search_result, dont_filter=True)
            # items.append(dict(item))
            # return items

# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.http.request import Request
from scrapy.selector import Selector
from electronic.items import ElectronicItem
from electronic.customfunction import cleansplit, listbalancer, cleanqty
from scrapy.utils.project import get_project_settings

class MouserSpider(Spider):
    name = "mouser"
    allowed_domains = ["www.mouser.com"]
    start_urls = ['http://www.mouser.com']

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
        super(MouserSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://www.mouser.com']
        p_setting = get_project_settings()
        self.query = query
        self.debug = p_setting.get("APP_DEBUG")
        self.pn = 1 # start number for pagination
        self.spider_name = "Mouser"

    def start_requests(self):
        """ Start requests

        Initial requests that need to be made (search url queries)

        Args:

        Returns:
            response
        """
        yield Request('http://www.mouser.com/All-Manufacturers/_/N-0?Keyword=%s&FS=True' % self.query, callback=self.parse_search)

    def parse_search(self, response):
        """ Parse_search

        Initial parsing after search request made. then check the response whether it single result or pagination result.

        Args:
            response

        Returns:
            response
        """
        #print response.xpath('//html//text()').extract()
        s = Selector(response)
        item_result_search_list = s.xpath('//a[@class="SearchResults-productLink"]/@href').extract()
        # search_found = s.css("h2.searchResults::text").extract_first()
        search_found = s.xpath("//a[@id='ctl00_ContentMain_lnkCategory']/h1/text()").extract_first()
        # single_result = s.css('span[itemprop="http://schema.org/manufacturer"]::text').extract_first()
        single_result = s.xpath("//div[@id='divMouserPartNum']/text()").extract_first()
        if self.debug: print "Search found status: %s" % (search_found)
        if self.debug: print "Single item status: %s" % (single_result)
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

        part_number = cleansplit(Selector(text=response.body)
                                 #.css('a.primarySearchLink::text').extract_first())
                                 .xpath("//div[@id='divMouserPartNum']/text()").extract_first())
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                #.css('dd[itemprop="mpn"]::text').extract_first())
                                .xpath("//div[@id='divManufacturerPartNum']/h1/text()").extract_first())
        manufacturer_name = cleansplit(Selector(text=response.body)
                                #.css('a.secondarySearchLink::text').extract_first())
                                .xpath("//a[@id='ctl00_ContentMain_hlnk10']/text()").extract_first())
        description = cleansplit(Selector(text=response.body)
                                 #.css('div[itemprop="http://schema.org/description"]::text').extract_first())
                                .xpath("//div[@id='divDes']/text()").extract_first())
        quantity_available = cleansplit(Selector(text=response.body)
                                .xpath("//div[@class='av-row'][1]/div[@class='av-col2']/text()").extract_first().split(" ")[0])
        image_url = cleansplit(Selector(text=response.body)
                               .xpath("//img[@id='ctl00_ContentMain_img1']/@src").extract_first().replace("../../../",self.start_urls[0]+"/"))
                               #.css("img[id='productMainImage']::attr(src)").extract_first())

        item['manufacturer'] = manufacturer_name
        item['manufacturer_part_number'] = manufacturer_part_number
        item['supplier'] = self.spider_name
        item['supplier_part_number'] = part_number
        item['description'] = description
        item['stock_qty'] = cleanqty(quantity_available)
        item['product_url'] = response.url
        item['image_url'] = image_url
        # items = dict((item['part_number'], item['manufacturer_part_number'], item['manufacturer_name'],
        #         item['description'], item['stock_qty'], item['image_url']))
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
                                 #.css("table.SearchResultsTable > tbody > tr > td:nth-child(3) > div > a"))
                                 #.xpath("//table[@class='SearchResultsTable']/tbody/tr/td[3]/div/a/text()"))
                                 #.xpath("//table[@id='ctl00_ContentMain_SearchResultsGrid_grid']/tbody/tr/td[3]/div/a/text()"))
                                 .xpath("//a[@title='Click to view additional information on this product.']//text()"))
        #print part_number
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                 .xpath("//div[@class='mfrDiv']/a/text()"))
                                #.xpath("//table/tbody/tr/td[4]/div/a/text()"))
                                #.css("tbody tr td:nth-of-type(4)"))
        #print manufacturer_part_number
        manufacturer_name = cleansplit(Selector(text=response.body)
                                #.xpath("//table[@class='SearchResultsTable']/tbody/tr/td[5]/a/text()"))
                                .xpath("//a[contains(@id, 'lnkSupplier')]/text()"))
                                #.css("table#ctl00_ContentMain_SearchResultsGrid_grid > tbody > tr > td:nth-child(5) > a::text"))
        #print manufacturer_name
        description = cleansplit(Selector(text=response.body)
                                 .xpath("//a[contains(@id, 'lnkSupplier')]/../following-sibling::td/text()"))
                                 #.css("table#ctl00_ContentMain_SearchResultsGrid_grid tbody tr td:nth-child(6)"))
        #print len(description)
        quantity_available = cleansplit(Selector(text=response.body)
                                 .xpath("//span[contains(@id,'lnkAvailability')]/text()"))
                                 #       "/text()[1]"))
                                # .css("span.inStockBold::text"))
        print quantity_available
        image_url = cleansplit(Selector(text=response.body).xpath("//tr[@class='SearchResultsRowOdd']/td/a/img/@src"))

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
            item['image_url'] = "{0}{1}".format(self.start_urls[0],n)
            item['product_url'] = response.url
            item['stock_qty'] = cleanqty(m.replace('In Stock', ''))
            yield item
        next_url = response.xpath("//a[@id='ctl00_ContentMain_PagerTop_lnkNext']/@href").extract_first()
        if self.debug: print "Next URL -> %s" % (next_url)
        if next_url:
            self.pn += 1
            "Following Next Page {0}".format(response.urljoin(next_url))
            yield Request(response.urljoin(next_url), callback=self.parse_search_result, dont_filter=True)


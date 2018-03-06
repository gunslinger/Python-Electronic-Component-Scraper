# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.http.request import Request
from scrapy.selector import Selector
from electronic.items import ElectronicItem
from electronic.customfunction import cleansplit, listbalancer, cleanqty
from scrapy.utils.project import get_project_settings

class RscomponentsSpider(Spider):
    name = "rscomponents"
    allowed_domains = ["uk.rs-online.com"]
    start_urls = ['http://uk.rs-online.com/web/']

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
        super(RscomponentsSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://uk.rs-online.com/web/']
        p_setting = get_project_settings()
        self.query = query
        self.debug = p_setting.get("APP_DEBUG")
        self.pn = 1 # start number for pagination, need to defined in program because we are not dealing with javascript
        self.spider_name = "RsComponents"

    def start_requests(self):
        """ Start requests

        Initial requests that need to be made (search url queries)

        Args:

        Returns:
            response
        """
        yield Request('http://uk.rs-online.com/web/c/?sra=oss&r=t&searchTerm=%s&pn=1&rpp=2' % self.query, callback=self.parse_search)

    def parse_search(self, response):
        """ Parse_search

        Initial parsing after search request made. then check the response whether it single result or pagination result.

        Args:
            response

        Returns:
            response
        """
        # print response.xpath('//html//text()').extract()
        s = Selector(response)
        item_result_search_list = s.xpath('//a[@class="SearchResults-productLink"]/@href').extract()
        search_found = s.css("h2.searchResults::text").extract_first()
        # single_result = s.css('span[itemprop="http://schema.org/manufacturer"]::text').extract_first()
        single_result = s.xpath("//div[@class='advLineLevelContainer']/div[2]/div[@class='heading']/text()").extract_first()
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
                                 .xpath("//ul[@class='keyDetailsLL']/li[1]/span[@class='keyValue bold']/text()"))
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                #.css('dd[itemprop="mpn"]::text').extract_first())
                                .xpath("//ul[@class='keyDetailsLL']/li[3]/span[@class='keyValue bold']/span/text()"))
        manufacturer_name = cleansplit(Selector(text=response.body)
                                #.css('a.secondarySearchLink::text').extract_first())
                                .xpath("//ul[@class='keyDetailsLL']/li[2]/span[@class='keyValue']/a/span/text()"))
        description = cleansplit(Selector(text=response.body)
                                 #.css('div[itemprop="http://schema.org/description"]::text').extract_first())
                                .xpath("//div[@class='rangeOverview'][1]/p[1]/text()"))
        ''' There is no direct quantity available on rscomponents.'''
        quantity_available = cleansplit(Selector(text=response.body)
                                .xpath("//span[@class='availability']//text()").extract_first())
        image_url = cleansplit(Selector(text=response.body)
                               .xpath("//img[@id='mainImage']/@src").extract_first())
                               #.css("img[id='productMainImage']::attr(src)").extract_first())

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
        items = []

        part_number = cleansplit(Selector(text=response.body)
                                 # .css("li.ttipartnumber a ::text/li[@class='ttipartnumber']/a/text()"))
                                .xpath("//div[@class='partColContent']/ul[@class='viewDescList']/li[1]/a[@class='primarySearchLink']/text()"))
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                .xpath("//ul[@class='viewDescList']/li[3]/span[@class='defaultSearchText']/text()"))
                                #.css("td.productImage.mftrPart a::text"))
        manufacturer_name = cleansplit(Selector(text=response.body)
                                .xpath("//ul[@class='viewDescList']/li[2]/a[@class='secondarySearchLink']/text()"))
                                # .css("td.description a p:first-of-type::text"))
        description = cleansplit(Selector(text=response.body)
                                 .xpath("//div[@class='srDescDiv']/a[@class='primarySearchLink'][1]/text()"))
                                 #.css("td.description a p:nth-of-type(2)::text"))
        quantity_available = cleansplit(Selector(text=response.body)
                                 # .xpath("/td[@class='availability']/text()"))
                                 .css("span.inStockBold::text")) # quantity is not found in rscomponents
        image_url = cleansplit(Selector(text=response.body).xpath("//div[@class='viewsImage']/a/img/@src"))

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
            item['stock_qty'] = cleanqty(m.replace(u'\xa0', u''))
            yield item

        next_url = response.xpath("//a[@class='rightLink nextLink approverMessageTitle']/@href").extract_first()
        if self.debug: print "Next URL -> %s" % (next_url)
        if next_url:
            self.pn += 1
            "Following Next Page {0}".format(response.urljoin(next_url))
            yield Request('http://uk.rs-online.com/web/c/?sra=oss&r=t&searchTerm=%s&pn=%s&rpp=2' % (self.query, self.pn),
                          callback=self.parse_search_result, dont_filter=True)

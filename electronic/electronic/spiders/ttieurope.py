# -*- coding: utf-8 -*-

from scrapy import Spider, Request
from scrapy.http.request import Request
from scrapy.selector import Selector
from electronic.items import ElectronicItem
from electronic.customfunction import cleansplit, listbalancer, cleanqty
from scrapy.utils.project import get_project_settings
'''
Keyword to test :
CL05B104KO5NNND -> single item
5NNND -> multiple item

scrapy cracker was added in case we need to crack the firewall. but Sometime we got blocked by incapsula web firewall.
here it is example result :
 u'Why do I have to enter this image?', u'\r\n\t
t\t\t\t\tSome people use automated programs to browse the web and search for inventory.
By entering the code you see in the image, you help us prevent automated programs from using the TTI website.
'''

class TtieuropeSpider(Spider):
    name = "ttieurope"
    allowed_domains = ["ttieurope.com"]
    start_urls = ['http://www.ttieurope.com/page/home']

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
        super(TtieuropeSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://www.ttieurope.com/page/home']
        p_setting = get_project_settings()
        self.query = query
        self.debug = p_setting.get("APP_DEBUG")
        self.spider_name = "TtiEurope"

    def start_requests(self):
        """ Start requests

        Initial requests that need to be made (search url queries)

        Args:

        Returns:
            response
        """
        yield Request('http://www.ttieurope.com/page/search_results.html?searchTerms=%s'
                      '&searchType=s&systemsCatalog=&autoComplete=false' % self.query, callback=self.parse_search)


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
        search_found = s.css(".pageheader::text").extract_first()
        #search_found = s.xpath("/html/body[@id='search_results']/div[@id='pageContent']/div[@id='content-wrapper']/div[@id='content-box']/form[@id='SearchAgainForm']/div[1]/div[1]/span[@class='pageheader']/text()").extract_first()
        single_result = s.css(".tableheadFirstCol::text").extract_first()
        if self.debug: print "Search found status: %s" % (search_found)
        if self.debug: print "Single item status: %s" % (single_result)
        # If we haven't get blocked we continue
        if "Please Enter Image Text" not in search_found:
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
        item['product_url'] = response.url
        item['image_url'] = image_url
        item['stock_qty'] = cleanqty(quantity_available)
        yield item


    def parse_search_result(self, response):
        '''
        Search Result Page Parser. self callback if there is pagination automatically.

        :param response:
        :return:
        '''
        item = ElectronicItem()
        items = []

        part_number = cleansplit(Selector(text=response.body)
                                #.css("li.ttipartnumber a ::text/li[@class='ttipartnumber']/a/text()"))
                                 .css("li.ttipartnumber a::text"))
        manufacturer_part_number = cleansplit(Selector(text=response.body)
                                #.xpath("/li[@class='mfrpartnumber']/a/text()"))
                                 .css("li.mfrpartnumber a::text"))
        manufacturer_name = cleansplit(Selector(text=response.body)
                                #.xpath("/li[@class='manufacturer']/text()"))
                                 .css("li.manufacturer::text"))
        description = cleansplit(Selector(text=response.body)
                                #.xpath("/td[@class='description']/text()"))
                                .css("td.description::text"))
        quantity_available = cleansplit(Selector(text=response.body)
                                #.xpath("/td[@class='availability']/text()"))
                                .css("td.availability::text"))
        image_url = cleansplit(Selector(text=response.body).xpath("//img[@class='large-photo']")
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
            item['stock_qty'] = cleanqty(m.replace(u'\xa0', u''))
            yield item

        next_url = response.xpath("/html/body[@id='search_results']"
                                  "/div[@id='pageContent']/div[@id='content-wrapper']"
                                  "/div[@id='content-box']/form[@id='SearchAgainForm']"
                                  "/div[2]/div[@id='search-results']/div[@class='action-row']"
                                  "/div[@class='pagination']/strong/a[@class='current']"
                                  "/following-sibling::a/@href").extract_first()
        if self.debug: print "Next URL -> %s" % (next_url)
        if next_url:
            "Following Next Page {0}".format(response.urljoin(next_url))
            yield Request(response.urljoin(next_url), callback=self.parse_search_result, dont_filter=True)
            # items.append(dict(item))
            # return items

# -*- coding: utf-8 -*-

""" Item is structured container (model) for scraped data

Scrapy spiders return the extracted data as Python dicts. While convenient and
familiar, Python dicts lack structure: it is easy to make a typo in a field name
or return inconsistent data, especially in a larger project with many spiders.

To define common output data format Scrapy provides the Item class.
Item objects are simple containers used to collect the scraped data.
They provide a dictionary-like API with a convenient syntax for declaring
their available fields.

For more information check out the scrapy documentation:
http://doc.scrapy.org/en/latest/topics/items.html

Returns:
    Ordered Scrapy Item

"""

from scrapy import Item, Field
from collections import OrderedDict

class OrderedItem(Item):
    def __init__(self, *args, **kwargs):
        self._values = OrderedDict()
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in six.iteritems(dict(*args, **kwargs)):
                self[k] = v

class ElectronicItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # Manufacturer and supplier details
    manufacturer_part_number = Field()
    manufacturer = Field()
    supplier_part_number = Field()
    supplier = Field()

    # Item details
    description = Field()
    image_url = Field()
    product_url = Field()
    datasheet_url = Field()
    country_of_origin = Field()
    customs_tariff_no = Field()

    # Stock and price information
    stock_qty = Field()
    moq = Field()

    def keys(self):
        return ['manufacturer_part_number', 'manufacturer', 'supplier_part_number', 'supplier',
                'description', 'image_url', 'product_url', 'datasheet_url', 'country_of_origin',
                'customs_tariff_no', 'stock_qty', 'moq']

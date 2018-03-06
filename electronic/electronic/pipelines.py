# -*- coding: utf-8 -*-

""" Item pipeline for cleansing, validating or checking results

After an item has been scraped by a spider, it is sent to the Item Pipeline which processes it through several 
components that are executed sequentially.

Each item pipeline component (sometimes referred as just “Item Pipeline”) is a Python class that implements a 
simple method. They receive an item and perform an action over it, also deciding if the item should continue 
through the pipeline or be dropped and no longer processed.

See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""

class ElectronicPipeline(object):
    def process_item(self, item, spider):
        return item

# -*- coding: utf-8 -*-

from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from electronic.settings import *
import logging
from scrapy.utils.log import configure_logging
from os import remove, path, mkdir
import sys
import optparse
import json

parser = optparse.OptionParser()
parser.add_option('-k', '--keyword', dest='query', help='Keyword to search')

(options, args) = parser.parse_args()

if options.query is None:
	print ("Keyword is needed.")
	sys.exit(1)


settings = get_project_settings()
output_data_dir = settings.get("OUTPUT_DATA_DIR")
settings.set('FEED_URI', output_data_dir+'result.jsonl', priority='cmdline')
settings.set('FEED_FORMAT', 'jsonlines', priority='cmdline')

file_path = output_data_dir + "result.jsonl"
output = output_data_dir + "data.json"

if not path.exists(output_data_dir):
    mkdir(output_data_dir)

configure_logging(install_root_handler=False)
logging.basicConfig(
    filename=output_data_dir+'/log.txt',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)


process = CrawlerProcess(settings)

for spider_name in process.spider_loader.list():
	if settings.get(spider_name.upper()):
		print ("Running spider %s" % spider_name)
		process.crawl(spider_name,query=options.query)
	else:
		print("Spider %s disabled on settings" % spider_name)

process.start()

# Data processing
try:
	remove(file_path)
except OSError:
	pass

try:
	contents = open(file_path, "r").read()
	#data = [json.loads(str(item)) for item in contents.strip().split('\n')]
	data = []
	for item in contents.strip().split('\n'):
		try:
			data.append(json.loads(str(item)))
		# sometime we get not good value on some item. so this one will make robust
		except ValueError:
			pass
	final_json = json.dumps(data)

	try:
		remove(output)
	except OSError:
		pass

	with open(output, 'w+') as outfile:
		json.dump(data, outfile)
except OSError:
	print "No item result from scrapy spider found."
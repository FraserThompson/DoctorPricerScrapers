import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re

regex = re.compile(r'[\n\r\t]')

fees_dict = {}
root = 'https://ebpha.org.nz/'

def scrape(name):
	scraper = scrapers.Scraper(name)

	listSouped = scrapers.openAndSoup(root + '?page_id=784')
	
	practice_rows = listSouped.find('div', {'class': 'et_pb_section_2'}).find_all('div', {'class': 'et_pb_column_1_3'})

	for row in practice_rows:

		name = row.find('h4', {'class': 'et_pb_module_header'})
		url = row.find('a', {'class':'et_pb_button'}).get('href')

		scraper.newPractice(name, url, "Eastern Bay PHO", "")

		scraper.practice = scraper.practice | scrapers.scrapeHealthpoint(url)

		scraper.finishPractice()

	return scraper.finish()
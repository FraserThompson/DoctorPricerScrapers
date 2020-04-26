
import sys, codecs, os, re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	practiceListUrlSouped = scrapers.openAndSoup('http://www.korowai.co.nz/contact_us')
	practiceRoot = practiceListUrlSouped.find('div', {'class': 'page-content'})
	practiceNames = practiceRoot.find_all('h3')

	for row in practiceNames:
		scraper.newPractice(row.get_text(strip=True), "http://www.korowai.co.nz/", "Te Korowai", "")

		# These prices come from http://www.korowai.co.nz/services/fees and are the same for all practices
		scraper.practice['prices'] = [
			{
				'age': 0,
				'price': 0
			},
			{
				'age': 18,
				'price': 18
			},
			{
				'age': 65,
				'price': 12
			}
		]

		scraper.finishPractice()

	return scraper.finish()
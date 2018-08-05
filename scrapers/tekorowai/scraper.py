
import sys, codecs, os, re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	feesList = scrapers.openAndSoup('http://www.korowai.co.nz/services/fees').find('table', {'class': 'fees'}).find_all('tr')
	prices = []
	for row in feesList[2:6]:
		cells = row.find_all('td')
		prices.append({'age': scrapers.getFirstNumber(cells[0].get_text(strip=True).replace("Under 18s", "6")), 'price': float(cells[1].get_text(strip=True).replace("Free", "0").replace("$", ""))})

	practiceListUrlSouped = scrapers.openAndSoup('http://www.korowai.co.nz/contact_us')
	practiceRoot = practiceListUrlSouped.find('div', {'class': 'page-content'})
	practiceNames = practiceRoot.find_all('h3')

	for row in practiceNames:
		scraper.newPractice(row.get_text(strip=True), "http://www.korowai.co.nz/", "Te Korowai", "")
		scraper.practice['prices'] = prices

		# they changed their website and got rid of useful info so we'll just use what we got for now I guess

		scraper.finishPractice()

	return scraper.finish()
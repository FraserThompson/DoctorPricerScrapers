import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers
import re

#stupid shit because the windows console can't print stuff properly
sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')

def scrape(name):
	scraper = scrapers.Scraper(name)

	root = 'http://www.rcpho.org.nz/?page_id=16'
	listUrlSouped = scrapers.openAndSoup(root)
	providers_rows = listUrlSouped.find('table', {'id': 'tablepress-1'}).find('tbody').find_all('tr')

	for row in providers_rows:
		cells = row.find_all('td')

		scraper.newPractice(cells[0].get_text(strip='true'), cells[0].find('a').get('href').replace('pracitces', 'practices'), "Rural Canterbury PHO", "")

		practiceSouped = scraper.openAndSoup()
		try:
			infoTable = practiceSouped.find_all('table')[5].find('tbody').find_all('tr')
			scraper.practice['address'] = ', '.join([infoTable[0].get_text(strip='true').replace('\t', ' '), infoTable[1].get_text(strip='true').replace('\t', ' ')])
			for tr in infoTable:
				if 'Phone: ' in tr.get_text(strip='true'):
					scraper.practice['phone'] = tr.get_text(strip='true').split(': ')[1]
		except IndexError:
			scraper.addError("Cannot find contact details.")
			continue


		scraper.practice['prices'] = [
				{
				'age': 0,
				'price': float(cells[1].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 13,
				'price': float(cells[2].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 18,
				'price': float(cells[3].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 25,
				'price': float(cells[4].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 45,
				'price': float(cells[5].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 65,
				'price': float(cells[6].get_text(strip=True).replace("$", "")),
				}
			]

		scraper.practice['new_prices'] = [
				{'from_age': 0, 'to_age': 13, 'price': float(cells[1].get_text(strip=True).replace("$", ""))},
				{'from_age': 13, 'to_age': 18, 'price': float(cells[2].get_text(strip=True).replace("$", ""))},
				{'from_age': 18, 'to_age': 25, 'price': float(cells[3].get_text(strip=True).replace("$", ""))},
				{'from_age': 25, 'to_age': 45, 'price': float(cells[4].get_text(strip=True).replace("$", ""))},
				{'from_age': 45, 'to_age': 65, 'price': float(cells[5].get_text(strip=True).replace("$", ""))},
				{'from_age': 65, 'to_age': 150, 'price': float(cells[6].get_text(strip=True).replace("$", ""))}
			]
		
		scraper.postPractice()

	scraper.finish()
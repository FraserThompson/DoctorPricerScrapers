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
	
	practice_rows = listSouped.find_all('div', {'class': 'et_pb_column_1_3'})

	for row in practice_rows:
		url = row.find('a', {'class':'et_pb_button'}).get('href')
		practiceSouped = scrapers.openAndSoup(url)

		name = practiceSouped.find('div', {'id': 'heading'}).find('h1').get_text(strip=True)

		scraper.newPractice(name, url, "Eastern Bay PHO", "")

		scraper.practice['address'] = practiceSouped.find('div', {'class': 'service-location'}).get_text(strip=True)
		scraper.practice['phone'] = practiceSouped.find('ul', {'class', 'contact-list'}).find('p').get_text(strip=True)
		
		coords = practiceSouped.find('div', {'class', 'map'}).get('data-position').split(", ")
		scraper.setLatLng(coords)

		enrolling = practiceSouped.find('div', {'id': 'section-books'}).find('h4').get_text(strip=True) == "Yes"
		if not enrolling:
			scraper.notEnrolling()

		fees_table = practiceSouped.find('div', {'id': 'section-fees'}).find('table').find_all('tr')

		scraper.practice['prices'] = []

		for row in fees_table:
			price = {
				'age': scrapers.getFirstNumber(row.find('th').get_text(strip=True)),
				'price':  scrapers.getFirstNumber(row.find('td').get_text(strip=True)),
			}

			scraper.practice['prices'].append(price)

		scraper.finishPractice()

	return scraper.finish()
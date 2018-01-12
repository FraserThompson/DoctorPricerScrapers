import sys, codecs, os
import json, io
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re

def scrape(name):
	scraper = scrapers.Scraper(name)
	practice_table = scrapers.openAndSoup('http://www.wrpho.org.nz/practices').find('div', {'class': 'view-enrolling'}).find('tbody').find_all('tr')

	for row in practice_table:
		cells = row.find_all('td')

		name = cells[0].get_text(strip=True)
		url = 'http://www.wrpho.org.nz' + cells[0].find('a').attrs['href']

		scraper.newPractice(name, url, "Whanganui Regional PHO", "")

		practice_page = scrapers.openAndSoup(url)

		scraper.practice['address'] = practice_page.find('div', {'class': 'field-name-field-street-address'}).find('div', {'class': 'field-items'}).get_text(strip=True)
		scraper.practice['phone'] = practice_page.find('div', {'class': 'field-name-field-phone'}).find('div', {'class': 'field-items'}).get_text(strip=True)

		fees_table = practice_page.find('div', {'class': 'field-name-field-consult-fees'}).find_all('td')

		for cell in fees_table:
			split = list(cell.stripped_strings)

			age = scrapers.getFirstNumber(split[0])
			price = scrapers.getFirstNumber(split[1])

			scraper.practice['prices'].append({'age': age, 'price': price})

		scraper.finishPractice()

	return scraper.finish()
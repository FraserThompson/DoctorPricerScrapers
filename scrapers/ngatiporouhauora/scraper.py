import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re

def scrape(name):
	scraper = scrapers.Scraper(name)
	url = 'http://www.nph.org.nz/our-clinics/'
	listUrlSouped = scrapers.openAndSoup(url)

	prac_rows = listUrlSouped.find('div', {'class', 'grid_4'}).find_all('a', href=True)

	for row in prac_rows:
		name = row.get_text(strip=True)
		url = 'http://www.nph.org.nz' + row['href']

		scraper.newPractice(name, url, 'Ngati Porou Hauora', "")

		scraper.practice['prices'] = []
		prac_page = scrapers.openAndSoup(url)
		contact_box = prac_page.find_all('div', {'class', 'grid_4'})[1].find_all('p')

		if name == "Puhi Kaiti Community Health Centre":
			contact = contact_box[1].get_text().split('Ph: ')
			scraper.practice['address'] = contact[0]
			scraper.practice['phone'] = contact[1]
		elif name == "Ruatoria Community Health Centre":
			contact = contact_box[0].get_text().split('PH: ')
			scraper.practice['address'] = contact[0]
			scraper.practice['phone'] = contact[1]
		else:
			address_p = contact_box[0].contents
			scraper.practice['address'] = ""
			for thing in address_p:
				if isinstance(thing, str):
					scraper.practice['address'] += thing + " "
			scraper.practice['phone'] = re.split('Ph: |PH: |Phone', contact_box[1].get_text(strip=True))[1]
		
		scraper.finishPractice()

	return scraper.finish()
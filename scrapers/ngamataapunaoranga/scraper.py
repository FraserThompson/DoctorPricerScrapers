import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

url = 'http://nmo.org.nz/our-services/gp-clinics'

def scrape(name):
	scraper = scrapers.Scraper(name)
	listUrlSouped = scrapers.openAndSoup(url)

	prices = [
	            {
	                "age": 0,
	                "price": 0.0
	            },
	            {
	                "age": 13,
	                "price": 12.0
	            },
	            {
	                "age": 18,
	                "price": 18.0
	            }
	        ]

	prac_rows = listUrlSouped.find_all('div', {'class', 'row'})[1:]
	for row in prac_rows:
		lines = row.find('p').get_text().splitlines()

		scraper.newPractice(row.find('h1').get_text(strip=True), "http://nmo.org.nz/our-services/gp-clinics", "Nga Mataapuna Oranga", "")
		scraper.practice['address'] = lines[3].replace('\t', '')

		# This one has an error on the page
		if (scraper.practice['name'] == "Pirirākau Hauora"):
			scraper.practice['address'] = scraper.practice['address'].replace(", 8.30am - 11.30am, Wed", "")

		scraper.practice['phone'] = lines[5].replace('\t', '')
		scraper.practice['prices'] = prices

		scraper.finishPractice()

	return scraper.finish()
import sys, codecs, os
import json
import re
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

prices_south_gi = [
	{
	'age': 0,
	'price': 0,
	},
	{
	'age': 18,
	'price': 10,
	}
]

prices_dan = [
	{
	'age': 0,
	'price': 0,
	},
	{
	'age': 18,
	'price': 15,
	},
	{
	'age': 65,
	'price': 10,
	}
]

prices_exception = ['Dannemora', 'Sandringham', 'Sylvia Park']

def scrape(name):
	scraper = scrapers.Scraper(name)
	url = 'http://www.ethc.co.nz/121/all-clinics'

	listUrlSouped = scrapers.openAndSoup(url)
	rows = listUrlSouped.findAll('div', {'class': ['addressbox', 'addressboxalt']})

	for row in rows:
		name =  row.find('h2').get_text() if "ETHC" in row.find('h2').get_text() else "ETHC " + row.find('h2').get_text()
		print(name)
		scraper.newPractice(name, url, "East Tamaki Healthcare", "")

		scraper.practice['address'] = row.find('img')['src'].split('center=')[1].split('&')[0]
		scraper.practice['phone'] = row.find('h3').get_text().split(': ')[1].split('Fax: ')[0]

		if (scraper.practice['name'] in prices_exception):
			scraper.practice['prices'] = prices_dan
		else:
			scraper.practice['prices'] = prices_south_gi

		scraper.finishPractice()

	return scraper.finish()
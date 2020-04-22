import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re

def scrape(name):
	scraper = scrapers.Scraper(name)

	root = 'https://waitaha.health.nz/find-a-gp/'
	listUrlSouped = scrapers.openAndSoup(root)
	providers_rows = listUrlSouped.findAll('div', {'class': 'gp-inner'})

	for row in providers_rows:
		name = row.find('div', {'class': 'gp-name'}).getText(strip=True)
		url = row.find('div', {'class': 'more'}).find('a').get('href')

		scraper.newPractice(name, url, "Waitaha Primary Health", "")

		scraper.practice['address'] = row.find('div', {'class': 'gp-address'}).getText(strip=True)
		scraper.practice['phone'] = row.find('div', {'class': 'gp-phone'}).getText(strip=True).split("Phone:")[1]

		practiceSouped = scraper.openAndSoup()
		feeTable = practiceSouped.findAll('div', {'class': 'pricing-row'})
	
		prices = []
		for feeRow in feeTable:
			td = feeRow.findAll('div', {'class': 'pricing-col'})
			ageCol = td[0].getText(strip=True)
			priceCol = td[1].getText(strip=True)

			if "CSC" in ageCol:
				continue

			prices.append({'age': scrapers.getFirstNumber(ageCol), 'price': scrapers.getFirstNumber(priceCol)})

		scraper.practice['prices'] = prices
		scraper.finishPractice()

	return scraper.finish()
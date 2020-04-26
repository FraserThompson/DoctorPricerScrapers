import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re
import requests

def scrape(name):
	scraper = scrapers.Scraper(name)

	fees_dict = {}
	root = 'https://www.wboppho.org.nz'
	feesUrl = root + '/fees-and-subsidies/'

	# These guys have this weird little API so that's cool
	fees = requests.post(feesUrl, {'get_fees': True}).json()
	prices = {}

	# Assemble fees dict for use when scraping practice details
	for row in fees:
		name = row['title']

		# Some of them are straight broked
		if not row['ages_14_17']:
			continue

		fees = [
			{
				'age': 0,
				'price': 0
			},
			{
				'age': 14,
				'price': float(row['ages_14_17'])
			},
			{
				'age': 18,
				'price': float(row['ages_18_24'])
			},
			{
				'age': 25,
				'price': float(row['ages_25_44'])
			},
			{
				'age': 45,
				'price': float(row['ages_45_64'])
			},
			{
				'age': 65,
				'price': float(row['ages_64up'])
			},
		]

		fees_dict[scrapers.normalize(name)] = fees

	pracsURLSouped = scrapers.openAndSoup(root + '/medical-centres/')
	pracs_rows = pracsURLSouped.find('div', {'class': 'medicalCentres'}).find('table').find('tbody').findAll('tr')

	# Scrape practices
	for row in pracs_rows:
		cells = row.find_all('td')

		name = cells[0].get_text(strip=True)

		try:
			url = cells[0].find('a').get('href')
		except AttributeError:
			url = root

		scraper.newPractice(name, url, "Western Bay of Plenty PHO", "")

		if cells[3].find('img').get('alt') == "NOT ACCEPTING PATIENTS":
			scraper.notEnrolling()

		try:
			prices = fees_dict[scrapers.normalize(name)]
		except:
			scraper.addWarning('Could not get fees.')
			prices = []

		scraper.practice['address'] = cells[1].get_text(strip=True)
		scraper.practice['phone'] = cells[2].get_text(strip=True)
		scraper.practice['prices'] = prices

		scraper.finishPractice()

	return scraper.finish()
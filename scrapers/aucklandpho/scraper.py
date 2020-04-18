from bs4 import BeautifulSoup, Comment
import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	rootURL = 'https://aucklandpho.co.nz'

	# build a dict with practice info keyed to practice name
	listUrlSouped = scrapers.openAndSoup(rootURL + '/practices/')
	practiceEls = listUrlSouped.find('div', {'class': 'practices-fees-items'}).find_all('p')

	practiceInfo = {}
	for el in practiceEls:
		
		linkEl = el.find('a')
		if not linkEl:
			break

		name = linkEl.get_text(strip=True)
		practiceInfo[name] = {}
		practiceInfo[name]['name'] = name
		practiceInfo[name]['url'] = linkEl.get('href') if rootURL in linkEl.get('href') else rootURL + linkEl.get('href')
		practiceInfo[name]['address'] = el.get_text(strip=True).split("Address:")[1]
		practiceUrlSouped = scrapers.openAndSoup(practiceInfo[name]['url'])

		try:
			practiceInfo[name]['phone'] = practiceUrlSouped.find('h4', {'class': 'vc_custom_heading'}).get_text(strip=True).split("phone")[1]
		except IndexError:
			practiceInfo[name]['phone'] = None

	print("Done. Iterating fee rows...")

	feeEls = listUrlSouped.find('table').find_all('tr')[3:]

	for row in feeEls:
		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)

		try:
			info = practiceInfo[name]
		except KeyError:
			scraper.addError("Could not find details.")
			continue

		scraper.newPractice(name, info['url'], "Auckland PHO", "")

		scraper.practice['address'] = info['address']
		scraper.practice['phone'] = info['phone']

		scraper.practice['prices'] =  [
				{
				'age': 0,
				'price': float(cells[1].get_text(strip=True).replace(" ", "").replace("$", ""))
				},
				{
				'age': 14,
				'price': float(cells[4].get_text(strip=True).replace(" ", "").replace("$", ""))
				},
				{
				'age': 18,
				'price': float(cells[5].get_text(strip=True).replace(" ", "").replace("$", ""))
				},
				{
				'age': 25,
				'price': float(cells[6].get_text(strip=True).replace(" ", "").replace("$", ""))
				},
				{
				'age': 45,
				'price': float(cells[7].get_text(strip=True).replace(" ", "").replace("$", ""))
				},
				{
				'age': 65,
				'price': float(cells[8].get_text(strip=True).replace(" ", "").replace("$", ""))
				}
			]

		scraper.finishPractice()

	return scraper.finish()
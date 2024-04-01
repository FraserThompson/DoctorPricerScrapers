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
	listUrlSouped = scrapers.seleniumAndSoup(rootURL + '/practices-fees/')
	practiceEls = listUrlSouped.find_all('div', {'data-testid': 'mesh-container-content'})

	practiceInfo = {}
	
	regex = re.compile('tel:')
	
	for el in practiceEls:

		nameEl = el.find('h6')

		if not nameEl:
			continue

		linkEl = nameEl.find('a')

		name = nameEl.get_text(strip=True)
		practiceInfo[name] = {}
		practiceInfo[name]['name'] = name
		practiceInfo[name]['url'] = linkEl.get('href') if linkEl else rootURL
		practiceInfo[name]['address'] = el.find('div', {'data-testid': 'richTextElement'}).get_text(strip=True)

		phoneEl = el.find('a', {'href': regex})

		if phoneEl:
			practiceInfo[name]['phone'] = phoneEl.get_text(strip=True)

	print("Done. Iterating fee rows...")

	feesiFrameSouped = scrapers.seleniumAndSoup(rootURL + '/practices-fees/', 'iframe')
	feeEls = feesiFrameSouped.find('tbody').find_all('tr')

	for row in feeEls:
		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)

		# Two cases where the name differs between tables
		if "Symonds Street Medical Centre" in name:
			name = "Symonds Street Medical Centre"
		
		if name == "Tend":
			name = "Tend Health"

		scraper.newPractice(name, "https://www.aucklandpho.co.nz/practices-fees/", "Auckland PHO", "")
		
		try:
			info = practiceInfo[name]
		except KeyError:
			scraper.addError("Could not find details.")
			continue

		scraper.practice = scraper.practice | info

		if len(scraper.practice['prices']) == 0:

			# If even regular prices arent applicable then clearly its a weird one, just skip it
			if "N/A" in cells[4].get_text(strip=True):
				continue
		
			scraper.practice['prices'] =  [
					{
					'age': 0,
					'price': 0
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

			if "N/A" not in cells[1].get_text(strip=True):
				scraper.practice['prices_csc'] =  [
						{
						'age': 0,
						'price': 0
						},
						{
						'age': 14,
						'price': float(cells[2].get_text(strip=True).replace(" ", "").replace("$", ""))
						},
						{
						'age': 18,
						'price': float(cells[3].get_text(strip=True).replace(" ", "").replace("$", ""))
						}
					]

		scraper.finishPractice()

	return scraper.finish()
import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '\\..\\')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('https://www.mahitahihauora.co.nz/practices')
	rows = listUrlSouped.find('table').find_all('tr')

	for row in rows[1:]:
		skip = 0
		cells = row.findAll('td')

		scraper.newPractice(cells[0].get_text(strip=True), cells[0].find('a').get('href'), 'Mahitahi Hauora', "")

		enrolling = cells[1].get_text(strip=True)
		if enrolling != "Yes":
			scraper.notEnrolling()

		scraper.practice['phone'] = cells[2].get_text(strip=True)
		scraper.practice['address'] = cells[3].get_text(strip=True)

		# These bozos tried to cram multiple age groups into one field so this is set manually
		if scraper.practice['name'] == "Bush Road Medical Centre":

			scraper.practice['prices'] = [
				{
				'age': 0,
				'price': 0,
				},
				{
				'age': 14,
				'price': 28,
				},
				{
				'age': 18,
				'price': 40,
				},
				{
				'age': 25,
				'price': 43.50
				},
				{
				'age': 65,
				'price': 39.50,
				},
			]
		else:
			scraper.practice['prices'] = [
				{
				'age': 0,
				'price': 0,
				},
				{
				'age': 14,
				'price': scrapers.getFirstNumber(cells[5].get_text(strip=True)),
				},
				{
				'age': 18,
				'price': scrapers.getFirstNumber(cells[6].get_text(strip=True)),
				},
				{
				'age': 65,
				'price': scrapers.getFirstNumber(cells[7].get_text(strip=True)),
				},
			]

			# Also set manually because this is what it always is
			if ("CSC" in cells[5].get_text(strip=True)):
				scraper.practice['prices_csc'] = [
					{
					'age': 0,
					'price': 0,
					},
					{
					'age': 14,
					'price': scrapers.getFirstNumber(cells[5].get_text(strip=True).split("CSC")[1]),
					},
					{
					'age': 18,
					'price': scrapers.getFirstNumber(cells[6].get_text(strip=True).split("CSC")[1]),
					}
				]
		
		scraper.finishPractice()

	return scraper.finish()
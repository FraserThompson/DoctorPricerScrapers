import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('http://www.marlboroughpho.org.nz/general-practices-fees/')
	rows = listUrlSouped.find('table', {'class': 'omsc-custom-table omsc-style-1'}).find_all('tr')
	deets = listUrlSouped.find_all('h6')

	phone_numbers = {}
	ages = []

	for deet in deets[1:]:
		pairs = list(deet.stripped_strings)
		phone_numbers[pairs[0]] = pairs[1]

	for index, row in enumerate(rows):

		if index == 0:
			cells = row.find_all('th')
		else:
			cells = row.find_all('td')

		name = cells[0].get_text(strip=True).replace('#', '')

		# Get ages
		if index == 0:

			for cell in cells[1:]:

				age = scrapers.getFirstNumber(cell.get_text(strip=True))

				if age != 1000:
					ages.append(age)
			
			continue

		scraper.newPractice(name, "http://www.marlboroughpho.org.nz/general-practices-fees/", "Malborough PHO", "")

		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index + 1].get_text(strip=True):
				price = scrapers.getFirstNumber(cells[index + 1].get_text(strip=True))

			scraper.practice['prices'].append({'age': age, 'price': price })

		scraper.practice['phone'] = phone_numbers[name]

		scraper.finishPractice()

	return scraper.finish()
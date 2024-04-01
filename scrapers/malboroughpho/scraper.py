import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('http://www.marlboroughpho.org.nz/general-practices-fees/')
	tables = listUrlSouped.find_all('table', {'class': 'omsc-custom-table omsc-style-1'})

	practice_cells = tables[0].find_all('td')

	practice_details = {}

	# Get practice details from box at top
	for cell in practice_cells:
		lines = cell.get_text(strip=True, separator='\n').splitlines()
		name = lines[0].strip().lower()
		practice_details[name] = {
			'address': lines[1].strip(),
			'phone': lines[2].strip()
		}

	# The second table on the page is CSC prices
	csc_prices = {}
	csc_rows = tables[2].find_all('tr')
	ages = []

	for index, row in enumerate(csc_rows):

		if index == 0:
			cells = row.find_all('th')
		else:
			cells = row.find_all('td')

		# Get ages
		if index == 0:

			for cell in cells[1:]:

				age = scrapers.getFirstNumber(cell.get_text(strip=True))

				if age != 1000:
					ages.append(age)
			
			continue

		name = cells[0].get_text(strip=True).replace('#', '').strip().lower()
		csc_prices[name] = []

		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index + 1].get_text(strip=True):
				price = scrapers.getFirstNumber(cells[index + 1].get_text(strip=True))

			csc_prices[name].append({'age': age, 'price': price })


	# Get the normal prices and finish the practice
	fee_rows = tables[1].find_all('tr')
	ages = []

	for index, row in enumerate(fee_rows):

		if index == 0:
			cells = row.find_all('th')
		else:
			cells = row.find_all('td')

		# Get ages
		if index == 0:

			for cell in cells[1:]:

				age = scrapers.getFirstNumber(cell.get_text(strip=True))

				if age != 1000:
					ages.append(age)
			
			continue

		name = cells[0].get_text(strip=True).replace('#', '')
		scraper.newPractice(name, "https://www.marlboroughpho.org.nz/general-practices-fees/", "Malborough PHO", "")

		# Get details
		try:
			practice = practice_details[name.strip().lower()]
			scraper.practice = scraper.practice | practice
		except KeyError:
			scraper.addWarning("Couldn't get details, will use existing")

		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index + 1].get_text(strip=True):
				price = scrapers.getFirstNumber(cells[index + 1].get_text(strip=True))

			scraper.practice['prices'].append({'age': age, 'price': price })

		try:
			scraper.practice['prices_csc'] = csc_prices[name.strip().lower()]
		except KeyError:
			scraper.addWarning("No CSC prices.")

		scraper.finishPractice()

	return scraper.finish()
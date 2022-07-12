import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('http://www.marlboroughpho.org.nz/general-practices-fees/')
	fee_rows = listUrlSouped.find('table', {'class': 'omsc-custom-table omsc-style-1'}).find_all('tr')
	names = listUrlSouped.find_all('h6')
	names.pop(len(names) - 2) #second to last one has no image, so we remove it from the names list
	images = listUrlSouped.select('img.size-cta-thumbnail.alignleft')

	practice_details = {}

	for i, image in enumerate(images):
		link = image.find_parent('a')
		pairs = list(names[i].stripped_strings)
		name = pairs[0].lower()
		
		if not link:
			continue

		link = link.get('href')

		if "healthpoint" not in link:
			continue

		healthpoint_details = scrapers.scrapeHealthpoint(link)
		practice_details[name] = healthpoint_details

	ages = []

	for index, row in enumerate(fee_rows):

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

		scraper.newPractice(name, "https://www.marlboroughpho.org.nz/general-practices-fees/", "Malborough PHO", "")

		# Get details
		try:
			practice = practice_details[name.lower()]
			scraper.practice = scraper.practice | practice
		except KeyError:
			scraper.addWarning("Couldn't get details, will use existing")

		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index + 1].get_text(strip=True):
				price = scrapers.getFirstNumber(cells[index + 1].get_text(strip=True))

			scraper.practice['prices'].append({'age': age, 'price': price })

		scraper.finishPractice()

	return scraper.finish()
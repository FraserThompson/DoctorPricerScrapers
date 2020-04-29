import sys, codecs, os, re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

# Get the list of practices for Hawkes Bay
# First URL for getting fees
def scrape(name):
	scraper = scrapers.Scraper(name)
	rootUrl = 'http://www.ourhealthhb.nz'

	feesUrlSouped = scrapers.openAndSoup(rootUrl + '/your-health/gp-fees-for-enrolled-patients/')
	fees_table = feesUrlSouped.find('table').find_all('tr')

	ages = []
	wairoa = False

	allPrices = {}

	for index, row in enumerate(fees_table):

		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)

		if name == "WAIROA":
			wairoa = True
			continue

		# Get ages
		if index == 0 or wairoa:

			if wairoa:
				ages = []
				cells = cells [0:4]
				wairoa = False

			ages.append(0)

			for cell in cells[2:]:
				age = scrapers.getFirstNumber(cell.get_text(strip=True))

				if cell.get_text(strip=True) == "Adult":
					age = 18

				if age != 1000:
					ages.append(age)
			
			continue

		if len(cells) <= 3 or not name:
			continue

		prices = []
		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index + 1].get_text(strip=True):
				price = float(cells[index + 1].get_text(strip=True).replace('Free', '$0').replace("$", ""))

			prices.append({'age': age, 'price': price })
		
		allPrices[scrapers.normalize(name)] = prices

	listUrlSouped = scrapers.openAndSoup('http://www.ourhealthhb.nz/your-health/find-a-family-doctor-or-gp/')
	practiceList = listUrlSouped.find('div', {'class': 'rightbar'}).findAll('a')

	for practice in practiceList[1:-2]:
		name = practice.getText(strip=True)
		url = rootUrl + practice.get('href')
		scraper.newPractice(name, url , "Health Hawke's Bay", "")

		if practice.get('class') == 'red':
			scraper.notEnrolling()

		practice_info = scrapers.openAndSoup(url)

		content = practice_info.find('div', {'class': 'col-md-6 main-content print-center-children'})

		scraper.practice['phone'] = scrapers.better_strip(content.find('h3').stripped_strings).split("Phone ")[1].split("Fax ")[0]
		scraper.practice['address'] = scrapers.better_strip(content.find_all('p')[0].stripped_strings)
		foundPrices = scrapers.partial_match(scrapers.normalize(name), allPrices)

		if foundPrices == None:
			scraper.addError('No prices found in fee table (could be name mismatch)')
		else:
			scraper.practice['prices'] = foundPrices

		scraper.finishPractice()

	return scraper.finish()
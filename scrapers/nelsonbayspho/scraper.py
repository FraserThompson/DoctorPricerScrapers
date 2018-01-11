import sys, codecs, os
import json, urllib
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	# Access the URLs
	listUrlSouped = scrapers.openAndSoup('http://nbph.org.nz/gp-fees-table')
	rows = listUrlSouped.find('table', {'id': 'gp-fees-comparison'}).find_all('tr')

	ages = []

	for index, row in enumerate(rows):

		if index == 0:
			cells = row.find_all('th')
		else:
			cells = row.find_all('td')

		if len(cells) <= 1:
			continue

		# Get ages
		if index == 0:

			for cell in cells[2:]:

				age = scrapers.getFirstNumber(cell.get_text(strip=True).replace('13>', '0'))

				if age != 1000:
					ages.append(age)
			
			continue

		name = cells[0].get_text(strip=True)
		url = cells[0].find('a').attrs['href']

		scraper.newPractice(name, url, "Nelson Bays PHO", "")

		if cells[1].get_text(strip=True) == "No new":
			scraper.notEnrolling()

		# Go into the practice to get the details
		practiceUrlSouped = scrapers.openAndSoup(url)
		deets = practiceUrlSouped.find("meta",  { "name": "description"}).attrs["content"].splitlines()
		scraper.practice['address'] = deets[0]
		scraper.practice['phone'] = deets[1]

		# Delve into the map script to get the latlngs
		map_deets = json.loads(urllib.parse.unquote(practiceUrlSouped.find("div", {"class": "map-block"}).attrs["data-block-json"]))
		scraper.practice['lat'] = map_deets['location']['mapLat']
		scraper.practice['lng'] = map_deets['location']['mapLng']

		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index + 2].get_text(strip=True):
				price = scrapers.getFirstNumber(cells[index + 2].get_text(strip=True))

			scraper.practice['prices'].append({'age': age, 'price': price })

		scraper.finishPractice()

	return scraper.finish()
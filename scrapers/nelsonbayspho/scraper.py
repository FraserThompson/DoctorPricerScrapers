import sys, codecs, os
import json, urllib
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	# Access the URLs
	listUrlSouped = scrapers.openAndSoup('http://nbph.org.nz/services/gp-fees-table')
	tables = listUrlSouped.find_all('table', {'id': 'gp-fees-comparison'})

	heading = tables[0].find('thead').find_all('th')
	rows = tables[0].find('tbody').find_all('tr')
	rows_csc = tables[1].find('tbody').find_all('tr')

	ages = []
	for cell in heading[2:]:
		age = scrapers.getFirstNumber(cell.get_text(strip=True).replace('14<', '0'))
		ages.append(age)

	prices_csc = {}

	for row in rows_csc:
		cells = row.find_all('td')

		if (len(cells) == 0):
			continue

		name = cells[0].get_text(strip=True)

		prices_csc[name] = []

		for i, age in enumerate(ages):
			price_csc = {
				'age': age,
				'price': scrapers.getFirstNumber(cells[i + 2].get_text(strip=True))
			}
			prices_csc[name].append(price_csc)
		

	for row in rows:
		cells = row.find_all('td')

		if (len(cells) == 0):
			continue

		name = cells[0].get_text(strip=True)
		url = cells[0].find('a').attrs['href']

		scraper.newPractice(name, url, "Nelson Bays PHO", "")

		if "No" in cells[1].get_text(strip=True):
			scraper.notEnrolling()

		scraper.practice['prices'] = []
		for i, age in enumerate(ages):
			price = {
				'age': age,
				'price': scrapers.getFirstNumber(cells[i + 2].get_text(strip=True))
			}
			scraper.practice['prices'].append(price)
		
		if prices_csc[name]:
			scraper.practice['prices_csc'] = prices_csc[name]

		# Go into the practice to get the details
		try:
			practiceUrlSouped = scrapers.openAndSoup(url)
		except:
			scraper.addWarning('Website URL is a 404 for some reason so couldnt get any details, skipping')
			continue

		deets = practiceUrlSouped.find("meta",  { "name": "description"}).attrs["content"].splitlines()
		scraper.practice['address'] = deets[0]
		scraper.practice['phone'] = deets[1].replace("Phone: ", "")

		# Delve into the map script to get the latlngs
		map_deets = json.loads(urllib.parse.unquote(practiceUrlSouped.find("div", {"class": "map-block"}).attrs["data-block-json"]))
		scraper.practice['lat'] = map_deets['location']['mapLat']
		scraper.practice['lng'] = map_deets['location']['mapLng']

		scraper.finishPractice()

	return scraper.finish()
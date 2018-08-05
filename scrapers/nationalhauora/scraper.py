import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	list_url = "https://www.nhc.maori.nz/clinic-network"
	listUrlSouped = scrapers.openAndSoup(list_url)

	maps = listUrlSouped.find_all('div', {'class': 'map-block'})
	fees = listUrlSouped.find_all('div', {'class': 'sqs-block html-block sqs-block-html sqs-col-4 span-4 float float-left'})

	for fee in fees:
		text = fee.get_text(strip=True)

		if ":" not in text or "$" not in text:
			continue

		map = fee.find_previous_sibling()
		name = map.find_previous_sibling().get_text(strip=True)

		json_string = map.get('data-block-json')
		json_data = json.loads(json_string)

		scraper.newPractice(name, "https://www.nhc.maori.nz/clinic-network", "National Hauora Coalition", "")

		scraper.practice['address'] = json_data['location']['addressLine1'] + ", " + json_data['location']['addressLine2']
		scraper.practice['lat'] = json_data['location']['mapLat']
		scraper.practice['lng'] = json_data['location']['mapLng']

		lines = text.split(':')

		prices = []
		price_wip = {'age': 0, 'price': 0}

		for line in lines[1:]:

			line = line.replace('\xa0', '')

			if "Ages" in line:
				split_line = line.split("Ages")
			elif "Age" in line:
				split_line = line.split("Age")
			else:
				price_wip['price'] = scrapers.getFirstNumber(line)
				prices.append(price_wip)
				break
		
			price_wip['price'] = scrapers.getFirstNumber(split_line[0])
			prices.append(price_wip)
			price_wip = {'age': scrapers.getFirstNumber(split_line[1]), 'price': 0}

		scraper.practice['prices'] = prices

		scraper.finishPractice()
	
	return scraper.finish()
import sys, codecs, os
import json, io
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

# We found this API URL by looking at their public code in map.js and figured out how to get it to return the list used by the map
url = 'https://www.haurakipho.org.nz/GoogleMapSetBlock/GetMapData'

def scrape(name):
	scraper = scrapers.Scraper(name)

	data = requests.post(url, json={"blockid": "308432"})
	json_data = data.json()

	for practice in json_data['Points']:

		if not practice['PageUrl']:
			continue

		scraper.newPractice(practice['Name'], "http://www.haurakipho.org.nz" + practice['PageUrl'] , "Hauraki PHO", "")

		scraper.practice['lat'] = practice['Lat']
		scraper.practice['lng'] = practice['Lng']
		scraper.practice['address'] = practice['Address']
		scraper.practice['phone'] = practice['PhoneNumber']

		practice_page = scraper.openAndSoup()
		fees_table = practice_page.find('table', {'class': 'pricelist'})

		if not fees_table:
			scraper.addError("No fees table.")
			continue

		fees_rows = fees_table.find_all('tr')

		for fees_row in fees_rows[1:]:
			fees_cells = fees_row.find_all('td')
			
			age = scrapers.getFirstNumber(fees_cells[0].get_text(strip=True).replace("Under 13", "0").replace("All enrolled patients", "0"))
			price = scrapers.getFirstNumber(fees_cells[1].get_text(strip=True).replace('Koha', '$0').replace('(CSC)', '$15').replace('Free', '$0').replace('FREE', '$0').replace("NA", "999"))

			scraper.practice['prices'].append({'age': age, 'price': price })

		scraper.finishPractice()

	return scraper.finish()

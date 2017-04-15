import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

details_dict = {}

# Access the URLs
def scrape(name):
	scraper = scrapers.Scraper(name)

	root_url = 'http://www.midlandshn.health.nz/patient-fees/'
	extensions = ['lakes/', 'tairawhiti/', 'taranaki/', 'waikato/']

	with open('./' + name + '/legacy_data.json', 'r') as inFile:
		prac_dict = json.load(inFile)

	for extension in extensions:
		listUrlSouped = scrapers.openAndSoup(root_url + extension)
		tables = listUrlSouped.find_all('table')
		for table in tables:
			rows = table.find_all('tr')[1:]
			for row in rows:
				cells = row.find_all('td')

				scraper.newPractice(cells[0].get_text(strip=True), "https://www.midlandshn.health.nz", 'Midlands Health Network', "")

				try:
					p45 = float(cells[5].get_text(strip=True).replace("$", ""))
					p65 = float(cells[6].get_text(strip=True).replace("$", ""))
				except IndexError:
					p45 = 999
					p65 = 999
				try:
					scraper.practice['prices'] = [
						{
						'age': 0,
						'price': float(cells[1].get_text(strip=True).replace("$", "")),
						},
						{
						'age': 13,
						'price': float(cells[2].get_text(strip=True).replace("$", "")),
						},
						{
						'age': 18,
						'price': float(cells[3].get_text(strip=True).replace("$", "")),
						},
						{
						'age': 25,
						'price': float(cells[4].get_text(strip=True).replace("$", "").replace('4300', '43.00')),
						},
						{
						'age': 45,
						'price': p45,
						},
						{
						'age': 65,
						'price': p65,
						}
					]
				except (ValueError, IndexError):
					scraper.addError("Couldn't get prices because of a weird format.")
					continue

				for thing in prac_dict:
					if (thing['name'] == scraper.practice['name']):
						scraper.practice['address'] = thing['address']
						scraper.practice['url'] = thing['url']
						scraper.practice['phone'] = thing['phone']
						scraper.practice['lat'] = thing['coordinates'][0]
						scraper.practice['lng'] = thing['coordinates'][1]

				if 'address' not in scraper.practice:
					scraper.addError("Couldn't get info.")
					continue

				scraper.postPractice()
	scraper.finish()
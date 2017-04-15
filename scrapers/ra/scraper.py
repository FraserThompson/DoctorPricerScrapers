import sys, codecs, os
import json, io
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	url = 'http://www.raphs.org.nz/community/fees/'
	listUrlSouped = scrapers.openAndSoup(url)

	prac_url = 'http://www.raphs.org.nz/community/general-practice-details/'
	pracUrlSouped = scrapers.openAndSoup(prac_url)

	prices_dict = {}

	#### Prices
	fee_rows = listUrlSouped.find('table').find_all('tr')

	for i in range(0, len(fee_rows), 2):
		if i == 0:
			continue
		cells = fee_rows[i].find_all('td')
		name = re.sub(r'\(\bVLCA\b\)| \bService\b| \bServices\b| \bCentre\b', '', cells[0].get_text(strip=True))

		prices = [
			{
			'age': 0,
			'price': 0,
			},
			{
			'age': 6,
			'price': float(cells[2].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 13,
			'price': float(cells[3].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 18,
			'price': float(cells[4].get_text(strip=True).replace("$", "")),
			}
		]

		if cells[5].get_text(strip=True):
			prices.append({
				'age': 25,
				'price': float(cells[5].get_text(strip=True).replace("$", ""))
			})

		prices.append({
			'age': 65,
			'price': float(cells[6].get_text(strip=True).replace("$", ""))
		})

		prices_dict[scrapers.normalize(name)] = prices;

	#### Practices
	prac_rows = pracUrlSouped.find_all('div', {'class': 'contacts'})
	for row in prac_rows:
		more_info = row.find_all('div', {'class': 'span3'})

		scraper.newPractice(row.find('h3').get_text(strip=True), 'http://www.raphs.org.nz/community/general-practice-details/', 'Rotorua Area PHO', "")

		if len(more_info) > 4:
			scraper.practice['url'] = more_info[3].get_text(strip=True)

		scraper.practice['phone'] = more_info[1].get_text(strip=True)
		scraper.practice['address'] = more_info[2].get_text(strip=True)

		try:
			scraper.practice['prices'] = prices_dict[scrapers.normalize(re.sub(r' \bService\b| \bServices\b| \bCentre\b', '', scraper.practice['name']))]
			print(scraper.practice['prices'])
		except KeyError:
			scraper.addWarning("Could not find prices.")
			scraper.practice['prices'] = []
		
		coord = scraper.geolocate()
		if (coord):
			scraper.addError("Cannot geolocate address: " + scraper.practice['address'])
			continue

		scraper.postPractice()

	scraper.finish()
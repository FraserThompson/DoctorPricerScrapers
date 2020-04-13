import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re

regex = re.compile(r'[\n\r\t]')

fees_dict = {}
root = 'http://www.ebpha.org.nz/'

def scrape(name):
	scraper = scrapers.Scraper(name)

	feesUrlSouped = scrapers.openAndSoup(root + '?page_id=110')
	fees_rows = feesUrlSouped.find('table').find('tbody').find_all('tr')[1:]

	for row in fees_rows:
		cells = row.find_all('td')
		name = cells[0].get_text(strip='true').lower()
		if name == '':
			break

		prices = [
				{
				'age': 0,
				'price': float(cells[1].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 14,
				'price': float(cells[2].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 18,
				'price': float(cells[3].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 25,
				'price': float(cells[4].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 45,
				'price': float(cells[5].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 65,
				'price': float(cells[6].get_text(strip=True).replace("$", "").replace("Koha", "0")),
				}
			]

		fees_dict[scrapers.normalize(name)] = prices

	pracs_rows = feesUrlSouped.find('div', {'class': 'et_pb_section_3'}).find_all('div', {'class': 'et_pb_row'})

	for row in pracs_rows:

		url = "https://ebpha.org.nz/"
		website_button = row.find('a', {'class': 'et_pb_promo_button'})
		if website_button:
			url = website_button.get('href')

		name = row.find('h2').get_text(strip=True)
		scraper.newPractice(name, url, "Eastern Bay PHO", "")

		gmaps_url = row.find('div', {'class': 'et_pb_image'}).find('a').get('href')

		scraper.practice['address'] = gmaps_url.split("/")[4].replace("+" , " ")

		coords = gmaps_url.split("!3d")[1].split("!4d")
		scraper.practice['lat'] = coords[0]
		scraper.practice['lng'] = coords[1]

		main_text = row.find('div', {'class': 'et_pb_promo_description'}).get_text(strip=True)
		scraper.practice['phone'] = main_text.split('P.')[1].split('F.')[0]

		try:
			fees = scrapers.partial_match(scrapers.normalize(name.lower()), fees_dict)
		except:
			scraper.addWarning('Could not get fees.')

		if not fees:
			scraper.addWarning('Could not get fees.')

		scraper.practice['prices'] = fees
		scraper.finishPractice()

	return scraper.finish()
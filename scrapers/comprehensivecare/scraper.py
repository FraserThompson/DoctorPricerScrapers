import sys, codecs, os
import json
import re
from bs4 import BeautifulSoup
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

details_dict = {}
coords_list = []
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

api_url = "https://comprehensivecare.co.nz/find-a-practice/?num=20&sort=post_title&_ajax_=%23drts-platform-render-62b7deb4a6a35-1%20.drts-view-entities-container&_=1656217277811&_page="

def scrape(name):
	scraper = scrapers.Scraper(name)

	i = 1
	pages = 3

	while i <= pages:
		# Get info to build a dict
		r = requests.get(api_url + str(i), verify=False)
		info_json = r.json()
		markers = info_json['markers']
		i = i + 1

		for marker in markers:

			soup = BeautifulSoup(marker['content'])
			name = soup.find('div', {'class': 'drts-bs-card-title'}).get_text(strip=True)
			url = soup.find('div', {'class': 'drts-bs-card-title'}).find('a').get('href')

			scraper.newPractice(name, url, "Comprehensive Care", "")
			scraper.setLatLng([marker['lat'], marker['lng']])

			scraper.practice['address'] = soup.find('address', {'class': 'drts-map-marker-address'}).get_text(strip=True)

			deeper = scrapers.openAndSoup(url)

			price_table = deeper.find('table', {'class': 'my-table'}).find('tbody').find_all('tr')

			scraper.practice['prices'] = []
			scraper.practice['prices_csc'] = []

			for row in price_table:
				cols = row.find_all('td')

				price = {
					'age': scrapers.getFirstNumber(cols[0].get_text(strip=True)),
					'price': scrapers.getFirstNumber(cols[2].get_text(strip=True)),
				}

				price_csc = {
					'age': scrapers.getFirstNumber(cols[0].get_text(strip=True)),
					'price': scrapers.getFirstNumber(cols[1].get_text(strip=True)),
				}

				scraper.practice['prices'].append(price)
				scraper.practice['prices_csc'].append(price_csc)

			scraper.finishPractice()

	return scraper.finish()
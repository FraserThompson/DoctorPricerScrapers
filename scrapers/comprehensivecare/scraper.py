import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

details_dict = {}
coords_list = []
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('http://www.comprehensivecare.co.nz/category/region/waitemata-pho/')
	rows = listUrlSouped.find_all('article', {'class': 'post type-post status-publish format-standard hentry category-post-formats has_thumbnail post-teaser'})

	print("Done. Iterating rows...")
	for row in rows:
		coord = [0,0]
		scraper.newPractice(row.find('a').get_text(strip=True), row.find('header').find('a').get('href'), "Comprehensive Care", "")
		# address = row.find('div').find('span', {'class': 'address1'}).get_text()
		scraper.practice['phone'] = row.find('div').find('span', {'class': 'address2'}).get_text()

		# Go deeper
		pracUrlSouped = scraper.openAndSoup()
		fees_list = pracUrlSouped.find_all('div', {'class': 'wpb_wrapper'})[2].get_text().splitlines()
		address_el = pracUrlSouped.find_all('div', {'class': 'wpb_wrapper'})[0].get_text().splitlines()[4:6]
		scraper.practice['address'] = ', '.join(address_el).replace('\t', '')

		# Try find the coordinates of the address for Google Maps to display
		coord = scraper.geolocate()
		if coord:
			scraper.addError("Couldn't geocode address: " + scraper.practice['address'])
			continue

		prices = []
		count = 0
		for fee in fees_list:
			if fee.strip() == '':
				continue
			count += 1
			if (count <= 1):
				continue

			print(fee)
			fee = re.split('yrs|years', fee)
			try:
				prices.append({
					'age': scrapers.getFirstNumber(fee[0]) if count != 2 else 0,
					'price': scrapers.getFirstNumber(fee[1].replace("Free", "0"))
				})
			except IndexError:
				print("================================WTF====================")
				scraper.addWarning("Couldn't get all the prices?")

		scraper.practice['prices'] = prices
		scraper.finishPractice()
	return scraper.finish()
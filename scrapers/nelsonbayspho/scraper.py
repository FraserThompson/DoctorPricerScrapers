import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	# Access the URLs
	listUrlSouped = scrapers.openAndSoup('http://www.nbph.org.nz/programmes-and-services/general-practice/')
	rows = listUrlSouped.find_all('table')[2].find_all('tr')[2:]
	print("Done. Iterating rows...")

	for row in rows:
		cells = row.find_all('td')
		if (len(cells) != 4):
			continue

		try:
			name = cells[1].find('a').get_text(strip=True)
		except AttributeError: 
			continue

		url = cells[1].find('a').get('href')

		scraper.newPractice(name, url, 'Nelson Bays PHO', "")

		isnt_enrolling = cells[0].find('img')
		if (isnt_enrolling):
			scraper.notEnrolling()

		scraper.practice['address'] = cells[2].get_text(strip=True)
		scraper.practice['phone'] = cells[3].get_text(strip=True)

		prac_website_souped = scrapers.openAndSoup(url)
		fees_table_rows = prac_website_souped.find_all('tr')
		scraper.practice['prices'] = [
			{
			'age': 0,
			'price': float(fees_table_rows[1].find_all('td')[1].get_text(strip=True).replace("No Charge", "0").replace("$", "")),
			},
			{
			'age': 13,
			'price': float(fees_table_rows[2].find_all('td')[1].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 18,
			'price': float(fees_table_rows[3].find_all('td')[1].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 25,
			'price': float(fees_table_rows[4].find_all('td')[1].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 45,
			'price': float(fees_table_rows[5].find_all('td')[1].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 65,
			'price': float(fees_table_rows[6].find_all('td')[1].get_text(strip=True).replace("$", "")),
			}
		]

		try:
			coord = prac_website_souped.find_all('script')[15].get_text().split('"position":[')[1].split('"]}', 1)[0].replace('"', '').split(',')
			coord[0] = float(coord[0])
			coord[1] = float(coord[1])
			scraper.setLatLng(coord)
		except IndexError:
			print("no coords")

		scraper.finishPractice()

	return scraper.finish()
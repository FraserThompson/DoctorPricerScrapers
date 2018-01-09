import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

regions = ['Auckland-Central', 'Auckland-South', 'auckland-east', 'Auckland-West', 'Tairawhiti', 'midlands-region']

def scrape(name):
	scraper = scrapers.Scraper(name)

	with open('./scrapers/' + name + '/legacy_data.json', 'r') as inFile:
		prac_dict = json.load(inFile)

	# Access the URLs
	for region in regions:
		url = 'http://www.nhc.maori.nz/index.php?page=' + region
		listUrlSouped = scrapers.openAndSoup(url)
		rows = listUrlSouped.find_all('div', {'class': 'news_post'})
		print("Done. Iterating rows...")

		for row in rows:
			coord = [0,0]
			name = row.find('h4').get_text(strip=True)
			left_panel = row.find('div', {'class': 'c_left'})
			right_panel = row.find('div', {'class': 'c_right'})
			pho_name = left_panel.find('p').get_text(strip=True).split(':')[1]

			if right_panel.find('a'):
				website = right_panel.find('a').get('href')
			else:
				for thing in prac_dict:
					if (thing['name'] == name):
						website = thing['url']

			if not website:
				scraper.addWarning("Couldn't find website.")
				website = url

			scraper.newPractice(name, website, pho_name, "")

			if 'is taking new patients' not in right_panel.find_all('p')[2].get_text():
				scraper.notEnrolling()

			scraper.practice['address'] = right_panel.find_all('p')[1].get_text(strip=True)
			scraper.practice['phone'] = right_panel.find_all('p')[0].get_text().splitlines()[1].split(':')[1].strip()

			fees_table = left_panel.find('table', {'class': 'tbl fees'}).find_all('tr')
			scraper.practice['prices'] = []
			count = 0
			for tr in fees_table:
				cells = tr.find_all('td')
				count += 1
				try:
					scraper.practice['prices'].append({
						'age': scrapers.getFirstNumber(cells[0].get_text()) if count != 1 else 0,
						'price': scrapers.getFirstNumber(cells[1].get_text())
					})
				except IndexError:
					print("================================WTF====================")
					scraper.addWarning("Couldn't get all the prices?")

			scraper.finishPractice()
	
	return scraper.finish()
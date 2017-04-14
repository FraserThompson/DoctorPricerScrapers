import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

practices_list = []
error_list = []
warning_list = []
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
regions = ['Auckland-Central', 'Auckland-South', 'auckland-east', 'Auckland-West', 'Tairawhiti', 'midlands-region']

def scrape():
	with open(current_dir + '\legacy_data.json', 'r') as inFile:
		prac_dict = json.load(inFile)

	# Access the URLs
	for region in regions:
		listUrlSouped = scrapers.openAndSoup('http://www.nhc.maori.nz/index.php?page=' + region)
		rows = listUrlSouped.find_all('div', {'class': 'news_post'})
		print("Done. Iterating rows...")

		for row in rows:
			coord = [0,0]
			name = row.find('h4').get_text(strip=True)
			left_panel = row.find('div', {'class': 'c_left'})
			right_panel = row.find('div', {'class': 'c_right'})
			pho_name = left_panel.find('p').get_text(strip=True).split(':')[1]

			if 'is taking new patients' not in right_panel.find_all('p')[2].get_text():
				error_list.append(name + ': Is not taking patients')
				continue

			if right_panel.find('a'):
				website = right_panel.find('a').get('href')
			else:
				for thing in prac_dict:
					if (thing['name'] == name):
						website = thing['url']

			if not website:
				warning_list.append(name + ": Couldn't find website.")

			address = right_panel.find_all('p')[1].get_text(strip=True)
			phone = right_panel.find_all('p')[0].get_text().splitlines()[1].split(':')[1].strip()

			# Try find the coordinates of the address for Google Maps to display
			coord = scrapers.geolocate(address)
			if coord[0] == 0:
				error_list.append(website + ": Couldn't geocode address: " + address)
				continue

			fees_table = left_panel.find('table', {'class': 'tbl fees'}).find_all('tr')
			prices = []
			count = 0
			for tr in fees_table:
				cells = tr.find_all('td')
				count += 1
				try:
					prices.append({
						'age': scrapers.getFirstNumber(cells[0].get_text()) if count != 1 else 0,
						'price': scrapers.getFirstNumber(cells[1].get_text())
					})
				except IndexError:
					print("================================WTF====================")
					warning_list.append("WARNING " + website + ": Couldn't get all the prices?")

			practice = {
				'name': name,
				'url': website,
				'address': address,
				'phone': phone,
				'pho': pho_name,
				'restriction': '',
				'lat': coord[0],
				'lng': coord[1],
				'prices': prices
				}
			scrapers.postToDatabase(practice, warning_list);
			practices_list.append(practice)

	with open(current_dir + '//data.json', 'w') as outFile:
		json.dump(practices_list, outFile, ensure_ascii=False, sort_keys=True, indent=4)

	scrapers.dealWithFailure(error_list, warning_list, current_dir)
import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '\\..\\')
from scrapers import common as scrapers

def scrape():
	# Get the list of practices for Wellington
	listUrlSouped = scrapers.openAndSoup('http://www.tttpho.co.nz/gp-clinics/our-fees')
	rows = listUrlSouped.find('table', {'class': 'fees'}).find_all('tr')
	prac_details = listUrlSouped.find_all('ul')[3].find_all('li')
	prac_url_dict = {}

	practices_list = []
	error_list = []
	warning_list = []
	current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

	with open(current_dir + '\legacy_data.json', 'r') as inFile:
		prac_dict = json.load(inFile)

	for prac in prac_details[2:]:
		name = prac.find('span').get_text()
		if name == "Bayview Medical Centre - Paihia":
			name = "Bayview Medical Centre"
		if name == "Commercial Street Surgery - Kawakawa":
			name = "Commercial Street Surgery"
		if name == "Kawakawa Medical Centre":
			name = "Hauora Whanui Kawakawa Medical Centre"
		if name == "Top Health Kaitaia":
			name = "Top Health"
		if name == "Te Kohanga Whakaora - Kaitaia":
			name = "Te Kohanga Whakaora"
		url = prac.find('a').get('href')
		prac_url_dict[name.lower()] = url

	print("Iterating table...")
	for row in rows[1:]:
		skip = 0
		cells = row.findAll('td')
		coord = (0, 0)
		name = cells[0].get_text()

		try:
			practiceURL = prac_url_dict[name.lower()]
		except KeyError:
			for thing in prac_dict:
				if (thing['name'] == name):
					address = thing['address']
					practiceURL = thing['url']
					phone = thing['phone']
					coord = thing['coordinates']

			# practiceURL = scrapers.getHealthpagesURLFromSearch(name)
			# if not practiceURL:
			# 	error_list.append(name + ": Couldn't find healthpages URL.")
			# 	continue
			# address = scrapers.scrapeHealthpagesAddress(scrapers.openAndSoup(practiceURL))
			# coord = scrapers.geolocate(address)
			skip = 1

		if not skip:
			print("Found: " + practiceURL)

			practiceContent = scrapers.openAndSoup(practiceURL).find('section', {'class': 'content'})
			info = practiceContent.find_all('p')
			phone = info[1].get_text().replace("Tel ", "")

			if not practiceContent.find('iframe'):
				for index, thing in enumerate(info):
					if thing.get_text(strip=True).lower() == "find us:":
						address = ", ".join([info[index + 1].get_text(strip=True), info[index + 2].get_text(strip=True)])
						coord = scrapers.geolocate(address)
			else:
				print('found iframe')
				maps_url = practiceContent.find('iframe').get('src')
				address = maps_url.split('q=')[1].split('&')[0].replace('+', ' ')
				coord = maps_url.split('ll=')[1].split('&')[0].split(',')

		if (coord[0] == 0):
			error_list.append(name + ": Cannot geolocate address: " + address)
			continue

		prices = [
				{
				'age': 0,
				'price': float(cells[2].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 13,
				'price': float(cells[3].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 18,
				'price': float(cells[4].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 25,
				'price': float(cells[5].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 65,
				'price': float(cells[6].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 80,
				'price': float(cells[7].get_text(strip=True).replace("$", "")),
				},
			]

		# Make the dictionary object
		practice = {
			'name': name,
			'url': practiceURL,
			'address': address,
			'phone': phone,
			'restriction': '',
			'pho': 'Te Tai Tokerau',
			'lat': coord[0],
			'lng': coord[1],
			'prices': prices
		}
		
		scrapers.postToDatabase(practice, warning_list);
		practices_list.append(practice)
			
	with open(current_dir + '\\data.json', 'w') as outFile:
		json.dump(practices_list, outFile, ensure_ascii=False, sort_keys=True, indent=4)

	scrapers.dealWithFailure(error_list, warning_list, current_dir)
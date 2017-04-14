import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers
import re

#stupid shit because the windows console can't print stuff properly
# sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
# sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')

current_dir = './nph/'

def scrape():
	url = 'http://www.nph.org.nz/our-clinics/'
	listUrlSouped = scrapers.openAndSoup(url)

	practices_list = []
	error_list = []
	warning_list = []

	prac_rows = listUrlSouped.find('div', {'class', 'grid_4'}).find_all('a', href=True)
	for row in prac_rows:
		prices = []
		name = row.get_text(strip=True)
		url = 'http://www.nph.org.nz' + row['href']
		prac_page = scrapers.openAndSoup(url)
		contact_box = prac_page.find_all('div', {'class', 'grid_4'})[1].find_all('p')

		if name == "Puhi Kaiti Medical Centre":
			prices = [
	            {
	                "age": 0,
	                "price": 0.0
	            },
	            {
	                "age": 14,
	                "price": 5.0
	            },
	            {
	                "age": 18,
	                "price": 12.0
	            }
			]

			contact = contact_box[1].get_text().split('Ph: ')
			address = contact[0]
			phone = contact[1]
		elif name == "Ruatoria Community Health Centre":
			contact = contact_box[0].get_text().split('PH: ')
			address = contact[0]
			phone = contact[1]
		else:
			address_p = contact_box[0].contents
			address = ""
			for thing in address_p:
				if isinstance(thing, str):
					address += thing + " "
			phone = re.split('Ph: |PH: |Phone', contact_box[1].get_text(strip=True))[1]
		
		coord = scrapers.geolocate(address)

		if (coord[0] == 0):
			error_list.append(name + ": Cannot geolocate address: " + address)
			continue



		# Make the dictionary object
		practice = {
			'name': name,
			'url': url,
			'address': address,
			'phone': phone,
			'restriction': '',
			'pho': 'Ngati Porou Hauora',
			'lat': coord[0],
			'lng': coord[1],
			'prices': prices
		}
		
		scrapers.postToDatabase(practice, warning_list);
		practices_list.append(practice)

	with io.open(current_dir + 'data.json', 'w', encoding='utf8') as outFile:
		json.dump(practices_list, outFile, ensure_ascii=False, sort_keys=True, indent=4)

	scrapers.dealWithFailure(error_list, warning_list, current_dir)
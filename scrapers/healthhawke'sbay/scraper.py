import sys, codecs, os, re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

# Get the list of practices for Hawkes Bay
# First URL for getting fees
def scrape(name):
	scraper = scrapers.Scraper(name)
	listUrlSouped = scrapers.openAndSoup('http://www.ourhealthhb.nz/health-services/family-doctor-gp-fees-for-enrolled-patients/')
	fees_table = listUrlSouped.find('table').find_all('tr')

	ages = []
	wairoa = False

	for index, row in enumerate(fees_table):

		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)

		if name == "WAIROA":
			wairoa = True
			continue

		# Get ages
		if index == 0 or wairoa:

			if wairoa:
				cells = cells [0:4]
				wairoa = False

			ages.append(0)

			for cell in cells[2:]:
				age = scrapers.getFirstNumber(cell.get_text(strip=True))

				if cell.get_text(strip=True) == "Adult":
					age = 18

				if age != 1000:
					ages.append(age)
			
			continue

		if len(cells) <= 3 or not name:
			continue

		url_name = name

		# These practices have URLs which differ from their names (from here http://www.ourhealthhb.nz/health-services/find-a-family-doctor-or-gp/?Locations%5B0%5D=24&Locations%5B1%5D=0&action_doFindService=Go#Form_Form)
		if name == "Tuki Tuki Medical Ltd":
			url_name = "tukituki-medical"

		if name == "The Havelock North Health Centre":
			url_name = "dr-wakefields-practice"

		if name == "Gascoigne Medical Centre":
			url_name = "gascoigne-medical-services"
		
		if name == "Mahora Medical Centre":
			url_name = "mahora-medical-trust"

		if name == "Hawke’s Bay Wellness Centre":
			url_name = "hb-wellness-centre"

		if name == "Totara Health – Flaxmere":
			url_name = "totara-health-limited-flaxmere"

		if name == "Totara Health – Nelson Street":
			url_name = "totara-health-hastings"

		# These guys work at Maraenui Medical Centre which is already a thing
		if name == "Dr Paul Hendy" or name == "Dr Robert Harris":
			continue

		url = 'http://www.ourhealthhb.nz/health-services/find-a-family-doctor-or-gp/' + url_name.lower().replace(' ', '-').replace(',', '').replace('&', 'and').replace('(', '').replace(')', '')
		scraper.newPractice(name, url, "Health Hawke's Bay", "")

		scraper.practice['prices'] = []

		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index + 1].get_text(strip=True):
				price = float(cells[index + 1].get_text(strip=True).replace('Free', '$0').replace("$", ""))

			scraper.practice['prices'].append({'age': age, 'price': price })

		# Delve deep to find the info
		practice_info = scrapers.openAndSoup(url)

		content = practice_info.find('div', {'class': 'col-md-6 main-content print-center-children'})

		scraper.practice['phone'] = scrapers.better_strip(content.find('h3').stripped_strings).split("Phone ")[1].split("Fax ")[0]
		scraper.practice['address'] = scrapers.better_strip(content.find_all('p')[0].stripped_strings)
		enrolling = content.find('img')

		if enrolling and enrolling.attrs['src'] == 'assets/Uploads/_resampled/ResizedImageWzE0MCwxNDBd/TLred.jpg':
			scraper.notEnrolling()

		scraper.finishPractice()

	return scraper.finish()
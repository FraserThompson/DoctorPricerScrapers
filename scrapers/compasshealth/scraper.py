import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	things = [
		{
		'listUrl': 'http://www.compasshealth.org.nz/PracticesandFees/WellingtonPractices/PracticeFees.aspx',
		'infoUrl': 'http://www.compasshealth.org.nz/PracticesandFees/WellingtonPractices.aspx',
		'addressEl': "dnn_ctr484_Map_AddressLabel",
		'phoneEl': "dnn_ctr484_Map_PhoneLabel"},
		{
		'listUrl': 'http://www.compasshealth.org.nz/PracticesandFees/WairarapaPractices/PracticeFees.aspx',
		'infoUrl': 'http://www.compasshealth.org.nz/PracticesandFees/WairarapaPractices.aspx',
		'addressEl': "dnn_ctr499_Map_AddressLabel",
		'phoneEl': "dnn_ctr499_Map_PhoneLabel"}
	]

	scraper = scrapers.Scraper(name)
	for thing in things:
		listUrlSouped = scrapers.openAndSoup(thing['listUrl'])
		infoURLSouped = scrapers.openAndSoup(thing['infoUrl'])
		rows = listUrlSouped.find('table', {'class': 'FeesTable'}).find_all('tr')
		info_table = infoURLSouped.find('table', {'class': 'PracticeTable'})
		info_list = [[cell.get_text(strip=True) or cell.find('img').get('alt') == "No" for cell in row("td")] for row in info_table("tr")[1:]]
		info_dict = {}
		for item in info_list:
			info_dict[item[0]] = item[1:]

		print("Iterating table...")
		for row in rows:
			cells = row.findAll('td')
			if len(cells) > 0:
				deep = 0
				coord = (0.000, 0.000)
				scraper.newPractice(cells[0].find('a').get_text(), cells[0].find('a').get('href'), "Compass Health", "")

				try:
					if info_dict[scraper.practice['name']][0]:
						scraper.notEnrolling()
				except KeyError:
					print("couldn't find in dict: " + scraper.practice['name'])
					deep = 1

				try:
					practiceUrlSouped = scraper.openAndSoup()
				except:
					continue

				if deep:
					addressElement = practiceUrlSouped.find('span', {"id": thing['addressEl']})
					phoneElement = practiceUrlSouped.find('span', {"id": thing['phoneEl']})
					if addressElement is None:
						scraper.addError("No address.")
						continue
					else:
						scraper.practice['address'] = addressElement.get_text(strip=True)
						scraper.practice['phone'] = addressElement.get_text(strip=True) if phoneElement else "None supplied"
				else:
					scraper.practice['phone'] = info_dict[scraper.practice['name']][1]
					scraper.practice['address'] = info_dict[scraper.practice['name']][2]

				#### GOING IN REALLY DEEP ####
				scriptElement = practiceUrlSouped.find('body').findAll('script', {"type":"text/javascript"})
				first = scriptElement[2].text.split("LatLng(", 1)
				if (len(first) > 1):
					coord = first[1].split(");", 1)[0].split(", ");
					coord[0] = float(coord[0])
					coord[1] = float(coord[1])
				else:
					coord = scrapers.geolocate(scraper.practice['address'])

				if coord[0] == 0 or coord[1] == 0:
					scraper.addError("Bad coords." + str(coord[0]) + ", " + str(coord[1]))
					continue

				scraper.practice['prices'] = [
						{
						'age': 0,
						'price': float(cells[1].get_text(strip=True).replace("$", "")),
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
						},
						{
						'age': 25,
						'price': float(cells[5].get_text(strip=True).replace("$", "")),
						},
						{
						'age': 45,
						'price': float(cells[6].get_text(strip=True).replace("$", "")),
						},
						{
						'age': 65,
						'price': float(cells[7].get_text(strip=True).replace("$", "")),
						},
				]

				scraper.setLatLng(coord)
				scraper.finishPractice()

	return scraper.finish()
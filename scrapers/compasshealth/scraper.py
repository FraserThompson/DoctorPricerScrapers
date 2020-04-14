import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	things = [
		{
		'feesUrl': 'https://www.compasshealth.org.nz/PracticesandFees/WellingtonPractices/PracticeFees.aspx',
		'infoUrl': 'https://www.compasshealth.org.nz/PracticesandFees/WellingtonPractices.aspx',
		'addressEl': "dnn_ctr484_Map_AddressLabel",
		'phoneEl': "dnn_ctr484_Map_PhoneLabel"},
		{
		'feesUrl': 'https://www.compasshealth.org.nz/PracticesandFees/WairarapaPractices/PracticeFees.aspx',
		'infoUrl': 'https://www.compasshealth.org.nz/PracticesandFees/WairarapaPractices.aspx',
		'addressEl': "dnn_ctr499_Map_AddressLabel",
		'phoneEl': "dnn_ctr499_Map_PhoneLabel"}
	]

	scraper = scrapers.Scraper(name)
	for thing in things:
		feesUrlSouped = scrapers.openAndSoup(thing['feesUrl'])
		infoURLSouped = scrapers.openAndSoup(thing['infoUrl'])

		rows = feesUrlSouped.find('table').find_all('tr')[1:]

		info_table = infoURLSouped.find('table')
		info_list = [[cell.get_text(strip=True) for cell in row("td")] for row in info_table("tr")[1:]]
		info_dict = {}
		for item in info_list:
			info_dict[item[0]] = item[1:]

		print("Iterating table...")
		for row in rows:
			cells = row.findAll('td')
			if len(cells) > 0:
				deep = 0
				scraper.newPractice(cells[0].get_text(), "https://compasshealth.org.nz/Practices-and-Fees/Wellington-Practices", "Compass Health", "")

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

				#### Getting coordinates from the google maps script
				scriptElement = practiceUrlSouped.find('body').findAll('script', {"type":"text/javascript"})

				first = scriptElement[2].text.split("LatLng(", 1)

				if (len(first) > 1):
					coord = first[1].split(");", 1)[0].split(", ")

					try:
						coord[0] = float(coord[0])
						coord[1] = float(coord[1])
						scraper.setLatLng(coord)
					except ValueError:
						print("No coords, will geolocate.")

				scraper.practice['prices'] = [
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
						'price': float(cells[6].get_text(strip=True).replace("$", "")),
						},
				]

				scraper.finishPractice()

	return scraper.finish()
import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re

def scrape(name):
	scraper = scrapers.Scraper(name)

	fees_list = scrapers.openAndSoup('https://www.scdhb.health.nz/info-for-you/gps/fees').find('table').find_all('tr')

	# Pulled this from the initMap() function at https://www.scdhb.health.nz/info-for-you/gps
	listOfGps = [["Aoraki Medical Centre", -44.401439, 171.251624, "Dr Mike Devlin, Dr Jenny McGechie, Dr John Fanning, Dr Maria del mar Requena Duran, Dr Tahir Ayub", "Unit 1 45 Heaton Street, Timaru 7910", "03 684 7533", "03 684 6932", "Visit GP site", "http://southlinkgp.co.nz/aoraki-medical-centre/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Better Health (Timaru) Ltd", -44.394942, 171.247751, "Dr Anneke Pribis, Dr Jayne Ward, Dr Liang Wei Ong", "12 Elizabeth Street, Timaru 7910", "03 688 3003", "03 688 3010", "Visit GP site", "http://www.timaruhealth.co.nz/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Shrimpton's Practice", -44.391003, 171.231849, "Dr Grant Shrimpton", "2A Preston Street, Timaru 7940", "03 684 9502", "03 684 9508", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Diana Scott's Practice", -44.093737, 171.245079, "Dr Diana Scott, Sharon Hansen (NP)", "84 Talbot Street, Geraldine 7930", "03 693 9909", "03 693 9901", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Griffiths' Practice", -44.404968, 171.242635, "Dr Ron Griffiths", "46A Harper Street, Timaru 7910", "03 684 5154", "03 684 5151", "Visit GP site", "http://www.woodstreet.co.nz/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Helliwell's Practice", -44.395919, 171.248043, "Dr Rob Helliwell, Dr Brad Satchwell", "4A Dee Street, Timaru 7910", "03 687 2680", "03 688 8254", "Visit GP site", "http://deesthealth.co.nz/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Hepburn's Practice", -44.395919, 171.248043, "Dr Rob Hepburn, Dr Brad Satchwell", "4A Dee Street, Timaru 7910", "03 687 2680", "03 688 8254", "Visit GP site", "http://deesthealth.co.nz/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Morris Ltd", -44.395919, 171.248043, "Dr Tony Morris, Dr Brad Satchwell", "4A Dee Street, Timaru 7910", "03 687 2680", "03 688 8254", "Visit GP site", "http://deesthealth.co.nz/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr O'Connell's Practice", -44.395609, 171.247772, "Dr Barbara O'Connell", "5 Dee Street, Timaru 7910", "03 688 6009", "03 688 9898", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr van den Bergh's Practice", -44.391003, 171.231849, "Dr Anton van den Bergh", "2A Preston Street, Timaru 7910", "03 684 9988", "03 684 9223", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Walker's Family Practice", -44.404968, 171.242635, "Dr Margaret Walker", "46A Harper St, Timaru 7910", "03 684 5154", "03 684 5151", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Werkmeister's Practice", -44.390129, 171.223381, "Dr Nellie Werkmeister", "161 Wai-iti Road, Timaru 7910", "03 688 9965", "03 688 9965", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Fairlie Medical Centre", -44.095073, 170.822612, "Dr Lewis Arundell, Dr Paula Hyde, Dr Mark Holland", "10B Ayr Street, Fairlie 7925", "03 685 8211", "03 685 8215", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Four Peak Health", -44.093096, 171.242564, "Dr Kevin Moginie, Dr Mike Crawford, Dr Carlien Bolder", "16 Cox Street, Geraldine 7930", "03 693 8880", "03 693 9919", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["High Country Health Ltd", -44.261122, 170.098121, "Dr Beth Blumenstein, Dr Albertine Offringa", "15 Mackenzie Drive, Twizel 7901", "03 435 0777", "03 435 0789", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Highfield Medical Centre", -44.39331, 171.223356, "Dr Richard Price", "245 Otipua Road, Timaru 7910", "03 688 4505", "03 684 9835", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Oak House Medical Centre", -44.737848, 171.042053, "Dr Steven Fish, Dr Crispin Langston, Dr Mike Carey", "161 Queen Street, Waimate 7924", "03 689 7676", "03 689 7897", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Parkside Medical Centre", -44.401439, 171.251624, "Dr Mary McSherry, Dr Nicola Hayman, Dr Jeremy Buchanan", "45 Heaton St, Timaru 7940", "03 688 9095", "03 688 4062", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Pleasant Point Health Centre", -44.26083, 171.13163, "Tania Kemp (NP), Dr Chloe Dearlove", "59-73 Main Road, Pleasant Point 7903", "03 614 7002", "03 614 7633", "Visit GP site", "http://point-health.nz/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Temuka Family Practice", -44.241557, 171.277346, "Dr Brian Moore, Dr Katy Burton", "178 King Street, Temuka 7920", "03 615 9920", "03 615 6630", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Dr Vara's Practice", -44.244233, 171.277637, "Dr Ram Vara, Dr Kerry Neilson, Sharon Hansen (NP)", "104 King Street, Temuka 7920", "03 615 8284", "03 615 8280", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Timaru Health Ltd", -44.395915, 171.247936, "Dr Paul Keys, Dr Bruce Small, Dr Lik Loh, Dr Cathy Edge", "6a Dee Street, Timaru 7910", "03 688 6267", "03 688 6266", "Visit GP site", "", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Waimate Medical Centre", -44.73415, 171.045673, "Dr Sarah Creegan, Dr David Shin", "1 Glasgow St, Waimate 7924", "03 689 8016", "03 689 8014", "Visit GP site", "http://www.waimatemedical.nz/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Wood Street Surgery", -44.242017, 171.277975, "Dr Kirsty Russell, Dr Dagmar Crosby, Dr Maria Lasher", "7 Wood Street, Temuka 7920", "03 615 7677", "03 615 8196", "Visit GP site", "http://www.woodstreet.co.nz/", "http://scdhb.health.nz/info-for-you/gps/fees", "https://www.scdhb.health.nz/__data/assets/image/0005/89177/health-medical.png", "GP"],["Roberts Pharmacy", -44.404637, 171.242593, "", "Corner of Hassall and Harper Streets", "03 688 9156", "03 684 9148", "Visit Website", "http://www.robertspharmacy.co.nz/", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Marchwiel Pharmacy", -44.378888, 171.229423, "", "255 Selwyn St, Marchwiel, Timaru", "03 688 8044", "", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Unichem Highfield Mall", -44.390167, 171.226479, "", "145 Wai-Iti Rd, Highfield, Timaru", "03 684 5792", "03 684 5486", "Visit Website", "http://www.unichem.co.nz", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Ashbury Pharmacy", -44.383426, 171.236893, "", "Northtown Mall, Timaru, 7910", "03 688 9736", "03 684 5016", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Dee Street Chemist", -44.395646, 171.247774, "", "5 Dee Street, Timaru, 7910", "03 688 0317", "03 684 4132", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Geraldine Pharmacy", -44.091144, 171.243672, "", "24 Talbot Street, Geraldine", "03 693 8601", "03 693 9450", "Visit website", "http://www.geraldinepharmacy.co.nz", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Mackenzie Pharmacy", -44.257037, 170.098135, "", "6-7 Market Place, Twizel, 7901", "03 435 0883", "03 435 0892", "Visit website", "http://www.mackenziepharmacy.co.nz", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Moyle's Pharmacy", -44.395869, 171.247841, "", "6 Dee Street, Timaru, 7910", "03 688 4628", "03 684 5335", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Roberts Pharmacy", -44.401454, 171.251608, "", "45 Heaton Street, Timaru, 7910", "03 688 9152", "", "Visit website", "http://www.robertspharmacy.co.nz", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Temuka Pharmacy", -44.245006, 171.277578, "", "81 King Street, Temuka", "03 615 75299", "03 615 8920", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Unichem Timaru Pharmacy", -44.394437, 171.251124, "", "278 Stafford Street, Timaru, 7910", "03 688 8069", "03 688 8068", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Waimate Pharmacy", -44.732716, 171.047708, "", "58 Queen Street, Waimate, 7924", "03 689 8247", "03 689 8248", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Fairlie Pharmacy Depot", -44.098574, 170.828865, "", "Main Road,", "03 685 8164", "", "Visit GP site", "", "", "https://www.scdhb.health.nz/__data/assets/image/0007/89683/pharmacyicon.png", "Pharmacy"],["Medlab Dee St", -44.395895064815015, 171.24799232493387, "", "4 Dee Street, Timaru", "(03) 688 6206", "", "View Website", "http://www.sclabs.co.nz/index.php/collection-centres/timaru", "", "https://www.scdhb.health.nz/__data/assets/image/0005/94055/labicon.png", "Medlab"],["Medlab Timaru Hospital", -44.408273288023544, 171.25610064268358, "", "Level 2, Timaru Hospital, Queen Street, Timaru", "(03) 687 2253", "", "View Website", "http://www.sclabs.co.nz/index.php/collection-centres/timaru", "", "https://www.scdhb.health.nz/__data/assets/image/0005/94055/labicon.png", "Medlab"],["Medlab Temuka", -44.2442328, 171.27763670000002, "", "104 King Street, Temuka", "(03) 615 6579", "", "View Website", "http://www.sclabs.co.nz/index.php/collection-centres/timaru", "", "https://www.scdhb.health.nz/__data/assets/image/0005/94055/labicon.png", "Medlab"]]

	ages = []
	practice_prices = {}

	for index, row in enumerate(fees_list):

		cells = row.find_all('td')
		header_cells = row.find_all('th')

		# Get ages
		if index == 0:

			for header_cell in header_cells[1:]:

				age = scrapers.getFirstNumber(header_cell.get_text(strip=True).replace("Under 13", "0"))

				if age != 1000:
					ages.append(age)

			continue

		name = header_cells[0].get_text(strip=True)

		if name == "Dr Hepburns's Practice": name = "Dr Hepburn's Practice" #someone did a woopsie
		if name == "Pleasant Point Health Care": name = "Pleasant Point Health Centre"
		if name == "Timaru Primary Care": name = "Timaru Health Ltd"

		# Assign fees to prices
		prices = []
		for index, age in enumerate(ages):

			price_cell = cells[index].get_text(strip=True)

			if price_cell:
				price = scrapers.getFirstNumber(price_cell)

			prices.append({'age': age, 'price': price })

		practice_prices[name] = prices
	
	for practice in listOfGps:

		type = practice[11]

		if type != "GP":
			continue

		name = practice[0]
		lat = practice[1]
		lng = practice[2]
		address = practice[4]
		phone = practice[5]
		url = practice[7]


		scraper.newPractice(name, url, "SCDHB")

		scraper.practice['address'] = address
		scraper.practice['phone'] = phone
		scraper.practice['lat'] = lat
		scraper.practice['lng'] = lng
		scraper.practice['prices'] = practice_prices[name]

		scraper.finishPractice()

	return scraper.finish()
import csv, json
import os, sys, codecs
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)
	current_dir = "./procare/"
	with open(current_dir + 'legacy_data.json', 'r') as inFile:
		prac_dict = json.load(inFile)
		for practice in prac_dict:
			scraper.newPractice(practice['name'], practice['url'], practice['pho'], "")
			scraper.practice['address'] = practice['address']
			scraper.practice['phone'] = practice['phone']
			scraper.practice['prices'] = practice['prices']
			scraper.setLatLng(practice['coordinates'])

			scraper.postPractice()

	scraper.finish()

# def scrape(name):
# 	scraper = scrapers.Scraper(name)
# 	current_dir = "./procare/"

# 	details_dict = {}
# 	count = 0
# 	with open(current_dir + 'legacy_data.json', 'r') as inFile:
# 		prac_dict = json.load(inFile)

# 	print("Started scraping.")
# 	with open(current_dir + 'practices 2013.csv', 'r') as prac_file:
# 		prac_reader = csv.reader(prac_file)
# 		for row in prac_reader:
# 			address = row[1] + ", " + row[2] if row[2] != '' and row[2] != 'CBD' and row[2] != 'Royal Oak' else row[1]
# 			details_dict[scrapers.normalize(row[0])] = [address, row[4], [0,0]]

# 	with open(current_dir + 'fees.csv', 'r') as fees_file:
# 		fees_reader = csv.reader(fees_file)
# 		for fees_row in fees_reader:
# 			if (len(error_list) > 60):
# 				print("too many fails")
# 				scrapers.dealWithFailure(error_list, warning_list, current_dir)
# 				sys.exit()
# 			name = fees_row[0]
# 			student = scrapers.checkForStudent(name)
# 			fees = fees_row[1:]
# 			for thing in prac_dict:
# 				if (thing['name'] == name):
# 					address = thing['address']
# 					url = thing['url']
# 					phone = thing['phone']
# 					coord = thing['coordinates']

# 			# details = scrapers.partial_match(scrapers.normalize(name), details_dict)
# 			# urls = []
# 			# url = ''
# 			# errorcode = scrapers.getURLFromSearch(name, urls)

# 			# if errorcode == 0:
# 			# 	url = urls[0] or urls[1]

# 			# if len(details) != 3: #If we couldn't  find details in the PDF
# 			# 	if errorcode or len(urls) == 0:
# 			# 		print("errorcode triggered: no url and also no details from pdf")
# 			# 		error_list.append(name + ": No URL or details." )
# 			# 		continue

# 			# 	details = scrapers.scrapeDetails(urls)
# 			# 	if details == 1:
# 			# 		print("scrapeDetails is 1: couldn't get any details for urls:" + urls[0])
# 			# 		error_list.append(name + ": Could not scrape details from URL." )
# 			# 		continue
# 			# 	if details[0] == '':
# 			# 		error_list.append(name + ": Could not scrape address." )
# 			# 		continue
# 			# 	if details[2] == '' or details[2][0] == 0:
# 			# 		error_list.append(name + ": Could not scrape coords." )
# 			# 		continue

# 			# 	url = details[3]

# 			# elif details[2][0] == 0 or details[2][0] == "":
# 			# 	details[2] = scrapers.geolocate(details[0] + ", Auckland")
# 			# 	if details[2][0] == 0:
# 			# 		address_components = details[0].split(' ')
# 			# 		details[2] = scrapers.geolocate(address_components[len(address_components) - 1] + ", Auckland")
# 			# 		if details[2][0] == 0:
# 			# 			error_list.append(name + ": Couldn't geocode: " + address)
# 			# 			continue
# 			prices =  [
# 				{
# 				'age': 0,
# 				'price': float(fees[0]),
# 				},
# 				{
# 				'age': 6,
# 				'price': float(fees[1]),
# 				},
# 				{
# 				'age': 18,
# 				'price': float(fees[2]),
# 				},
# 				{
# 				'age': 25,
# 				'price': float(fees[3]),
# 				},
# 				{
# 				'age': 45,
# 				'price': float(fees[4]),
# 				},
# 				{
# 				'age': 65,
# 				'price': float(fees[5]),
# 				},
# 			] 
# 			scraper.newPractice(name, url, "Procare Networks", "")
# 			scraper.practice['phone'] = phone
# 			scraper.setLatLng(coord)
# 			scraper.practice['prices'] = prices
# 			count += 1

# 			scraper.postPractice()

# 	scraper.finish()
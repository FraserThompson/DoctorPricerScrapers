import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

# Searches a multidimensional array for all instances of a chosen value
# then returns the parents parent for all of them
def searchForValue(target, searchValue, parent=[], result=[]):
	if isinstance(target, list):
		for x in target:
			if x == searchValue:
				result.append(parent)
			if isinstance(x, list):
				for y in x:
					if y == searchValue:
						result.append(parent)
					searchForValue(y, searchValue, target, result)
	return result

# Ok this one is kind of black magic... 
# Their info is inside Google Maps embeds, Google stores it in unstructured arrays, so we can get it...
# But it's kind of unreliable. This is a best effort sort of deal.
def scrape(name):
	scraper = scrapers.Scraper(name)

	list_url = "https://www.nhc.maori.nz/providers/information-for-general-practices/our-practices/"
	listUrlSouped = scrapers.openAndSoup(list_url)

	regex = re.compile('/maps')
	mapElements = listUrlSouped.find_all('iframe', {'src': regex})

	for map in mapElements:
		
		map_link = map.get('src')
		mapSouped = scrapers.openAndSoup(map_link)
		script_text = mapSouped.find('script').string
		json_text = script_text.split('_pageData = "')[1].rsplit('"', 1)[0].replace(r'\"', '"').replace(r'\\"', '\'')
		json_blob = json.loads(json_text)
		practices = searchForValue(json_blob, "name")
		
		for practice_info_blob in practices:
			practice = practice_info_blob[5]

			name = practice[0][1][0].replace("\\n", "")

			if scraper.doWeHaveItAlready(name):
				continue

			try:
				info = practice[1][1][0].split("\\n")
			except:
				continue

			if "ADDRESS" in info[0]:
				address_start = 1
			elif "COMMUNITY CLINICS" in info[0]:
				address_start = 3
			else:
				address_start = 0

			sections = ["CONTACT", "Contact", "OPENING HOURS", "FEES"]
			address = ""

			for thing in info[address_start:]:
				if thing not in sections:
					address = address + " " + thing
				else:
					break

			url = None
			phone = None
			prices_array = None
			for i, thing in enumerate(info):
				if "P:" in thing:
					phone = thing.split(": ")[1]
				if "W:" in thing:
					url = thing.split(": ")[1]
				if "FEES" in thing:
					prices_array = info[(i + 1):]

			scraper.newPractice(name, url or list_url, "National Hauora Coalition", "")

			try:
				scraper.setLatLng(practice_info_blob[1][0][0])
			except:
				# All good, just dont bother
				pass
			
			scraper.practice['address'] = address
			scraper.practice['phone'] = phone
			scraper.practice['place_id'] = info[-1][1] if len(info[-1]) else None

			scraper.practice['prices'] = []

			ages_done = []
			ages_done_csc = []

			if prices_array:
				csc = False
				for price_line in prices_array:
					if "Duration" in price_line:
						continue

					# Some of them do this ['-- With CSC', 'Under 13: Free', 'Ages 13-17: $12.00', 'Ages 18-64: $19.50', 'Age 65+: $19.50', '-- Without CSC', 'Under 13: Free'...
					if "with csc" in price_line.lower():
						csc = True
						continue

					if "without csc" in price_line.lower():
						csc = False
						continue

					# Most of them do this 'Under 13: Free'
					split = price_line.split(":")

					# Some of them do this 'Under 6 years $0'
					if len(split) == 1:
						split = price_line.split("$")

					# Some of them do this 'Under 6 years FREE'
					if len(split) == 1:
						split = price_line.split("years")

					try:
						age = scrapers.getFirstNumber(split[0])

						if age == 1000:
							continue

						price = scrapers.getFirstNumber(split[1])

						if age not in ages_done:
							price = {
								'age': age,
								'price':  price
							}

							if not csc:
								ages_done.append(age)
								scraper.practice['prices'].append(price)
							else:
								
								if not scraper.practice.get('prices_csc'):
									scraper.practice['prices_csc'] = [] 

								ages_done_csc.append(age)
								scraper.practice['prices_csc'].append(price)
					except IndexError:
						# We've probably hit the next section, get out
						break

				scraper.finishPractice()
	
	return scraper.finish()
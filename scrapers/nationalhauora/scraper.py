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

def scrape(name):
	scraper = scrapers.Scraper(name)

	list_url = "https://www.nhc.maori.nz/clinic-network"
	listUrlSouped = scrapers.openAndSoup(list_url)

	mapElements = listUrlSouped.find_all('iframe', {'class': 'no-lazyload'})

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

			try:
				info = practice[1][1][0].split("\\n")
			except TypeError:
				continue

			address_start = 0 if info[0] != "ADDRESS" else 1
			sections = ["CONTACT", "Contact", "OPENING HOURS", "FEES"]
			address = ""
			for thing in info[address_start:]:
				if thing not in sections:
					address = address + thing
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
			except IndexError:
				# All good, just dont bother
				pass
			
			scraper.practice['address'] = address
			scraper.practice['phone'] = phone
			scraper.practice['place_id'] = info[-1][1] if len(info[-1]) else None

			scraper.practice['prices'] = []

			ages_done = []

			if prices_array:
				for price_line in prices_array:

					if "Duration" in price_line:
						continue

					split = price_line.split(": ")

					try:
						age = scrapers.getFirstNumber(split[0])
						price = scrapers.getFirstNumber(split[1])

						ages_done.append(age)

						if age not in ages_done:
							price = {
								'age': age,
								'price':  price
							}

							scraper.practice['prices'].append(price)
					except IndexError:
						# We've probably hit the next section, get out
						break

				scraper.finishPractice()
	
	return scraper.finish()
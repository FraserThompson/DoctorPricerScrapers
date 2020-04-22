import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	list_url = "https://www.nhc.maori.nz/clinic-network"
	listUrlSouped = scrapers.openAndSoup(list_url)

	practiceElements = listUrlSouped.findAll('div', {'class': 'et_pb_toggle_content'})

	for practiceEl in practiceElements:

		try:
			name = practiceEl.find('span', style=re.compile(r'#8dc63f*')).getText(strip=True)
			print(name)
			scraper.newPractice(name, "https://www.nhc.maori.nz/clinic-network", "National Hauora Coalition", "")

			try: 
				enrolling = practiceEl.find(text="Taking new patients? ").findNext("strong").getText(strip=True) == "Yes"
			except AttributeError:
				enrolling = not practiceEl.find(text="Taking new patients? No")

			if not enrolling:
				scraper.notEnrolling()

			peas = practiceEl.findAll(["p"])
			scraper.practice['phone'] = peas[1].getText(strip=True).split("P:")[1].split("F:")[0]
			scraper.practice['address'] = peas[2].getText(strip=True)

			pricesMaybe = scrapers.better_strip(peas[0].stripped_strings)
			pricesArray = pricesMaybe.split(",")

			prices = []
			properThing = enumerate(pricesArray[1:len(pricesArray) - 1])

			for idx, thing in properThing:
				split = thing.split(":")
				split = [x for x in split if x != '']
				if len(split) > 1:
					age = scrapers.getFirstNumber(split[0])
					price = scrapers.getFirstNumber(split[1])
				else:
					age = scrapers.getFirstNumber(thing)
					price = scrapers.getFirstNumber(pricesArray[idx + 2])
					next(properThing, None)
				# don't add price for an age which is already there
				if len([x for x in prices if x['age'] == age]) == 0:
					prices.append({'age': age, 'price': price})

			scraper.practice['prices'] = prices
			scraper.finishPractice()
		except:
			scraper.addError("Weird format")
			continue
	
	return scraper.finish()
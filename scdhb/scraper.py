import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers
import re

#stupid shit because the windows console can't print stuff properly
# sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
# sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')

def scrape(name):
	scraper = scrapers.Scraper(name)

	areas = ['fairlie', 'geraldine', 'pleasant-point', 'temuka', 'twizel', 'waimate']
	for area in areas:
		url = "http://www.scdhb.health.nz/a-healthy-community/primary-care/finding-a-gp/" + area + ".html"
		areaUrlSouped = scrapers.openAndSoup(url)

		prac_rows = areaUrlSouped.find_all('table', {'cellpadding': '6'})
		fees_rows = areaUrlSouped.find_all('table', {'bgcolor': ['#fff8dc', 'cornsilk']})
		i = 0

		# get practices
		for prac in prac_rows:
			rows = prac.find_all('tr')

			scraper.newPractice(rows[0].find('h4').get_text(strip=True), url, "SCDHB", "")

			try:
				more_info = rows[1].find('td').find_all('span')
				scraper.practice['address'] = more_info[0].get_text(strip=True).split(":")[1]
				scraper.practice['phone'] = more_info[1].get_text(strip=True).split(":")[1]
			except IndexError:
				more_info = rows[0].find_all('td')[2].find_all('span')
				scraper.practice['address'] = more_info[0].get_text(strip=True).split(":")[1]
				scraper.practice['phone'] = more_info[1].get_text(strip=True).split(":")[1]

			try:
				fees = fees_rows[i].find_all('tr')
			except IndexError:
				print("Not enough numbers for the fee thing")
				continue

			i = i + 1
			# assemble fees
			scraper.practice['prices'] = []
			for thing in fees:
				cells = thing.find_all('td')

				if (len(cells) < 2):
					continue

				if cells[0].get_text(strip=True).strip() == "":
					continue

				age = scrapers.getFirstNumber(cells[0].get_text(strip=True))
				price = scrapers.getFirstNumber(cells[1].get_text(strip=True).replace("No charge", "0").replace("No Charge", "0"))

				if age == -1 or price == -1:
					continue

				scraper.practice['prices'].append({
						"age": age,
						"price": price
					})

			scraper.postPractice()

	scraper.finish()
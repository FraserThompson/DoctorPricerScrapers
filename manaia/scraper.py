import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '\\..\\')
import scrapers

#stupid shit because the windows console can't print stuff properly
# sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
# sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('http://www.manaiapho.co.nz/PracticeInformation')
	rows = listUrlSouped.find('table').find_all('tr')

	for row in rows[1:len(rows) - 1]:
		skip = 0
		cells = row.findAll('td')
		coord = (0, 0)

		scraper.newPractice(cells[0].get_text(strip=True), cells[0].find('a').get('href'), 'Manaia Health PHO', "")

		enrolling = cells[1].find('img').get('src')
		if enrolling == "http://www.manaiapho.co.nz/sites/default/files/u5/misc/cross2.png":
			scraper.notEnrolling()
			continue

		scraper.practice['phone'] = cells[2].get_text(strip=True)
		scraper.practice['address'] = cells[3].get_text(strip=True)
		coord = scraper.geolocate()

		if coord:
			scraper.addError("Cannot geolocate address: " + scraper.practice['address'])
			continue

		scraper.practice['prices'] = [
				{
				'age': 0,
				'price': 0,
				},
				{
				'age': 13,
				'price': float(cells[5].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 18,
				'price': float(cells[6].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 65,
				'price': float(cells[7].get_text(strip=True).replace("$", "")),
				},
			]
		
		scraper.postPractice()

	scraper.finish()
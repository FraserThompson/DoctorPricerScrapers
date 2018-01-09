import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '\\..\\')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('http://www.manaiapho.co.nz/Practice_Information')
	rows = listUrlSouped.find('table').find_all('tr')

	for row in rows[1:len(rows) - 1]:
		skip = 0
		cells = row.findAll('td')
		coord = (0, 0)

		scraper.newPractice(cells[0].get_text(strip=True), cells[0].find('a').get('href'), 'Manaia Health PHO', "")

		enrolling = cells[1].find('img').get('src')
		if enrolling == "http://www.manaiapho.co.nz/sites/default/files/u5/misc/cross2.png":
			scraper.notEnrolling()

		scraper.practice['phone'] = cells[2].get_text(strip=True)
		scraper.practice['address'] = cells[3].get_text(strip=True)

		if scraper.practice['name'] == "Bush Road Medical Centre":

			custom_prices = cells[6].get_text().replace("$", "").split(" ")
			print(custom_prices)

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
				'age': scrapers.getFirstNumber(custom_prices[1]),
				'price': float(custom_prices[0]),
				},
				{
				'age': scrapers.getFirstNumber(custom_prices[3]),
				'price': float(custom_prices[2])
				},
				{
				'age': 65,
				'price': float(cells[7].get_text(strip=True).replace("$", "")),
				},
			]
		else:
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
		
		scraper.finishPractice()

	return scraper.finish()
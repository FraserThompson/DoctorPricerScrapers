import sys, codecs, os
import json
import re
import requests
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)
	url = 'http://www.wellsouth.org.nz/'
	coord = [0.00, 0.00]

	for i in range(1, 8):
		print("================" + str(i) + "===============")
		listUrlSouped = scrapers.openAndSoup(url + 'info.php?rid=' + str(i))
		rows = listUrlSouped.find('div', {'class': 'content'}).find_all('table')[1].find_all('tr')

		for row in rows:
			scraper.newPractice(row.find("a").text, url + row.find("a").get("href"), "Southern PHO", "")

			#### GO DEEPER #####
			practiceUrlSouped = scraper.openAndSoup()
			practice_rows = practiceUrlSouped.find('div', {'class': 'contentws'}).find('table').find_all('tr')
			practice_info_cells = practice_rows[0].find_all('td')

			#### GOING IN REALLY DEEP ####
			try:
				scriptElement = practiceUrlSouped.findAll('script', {"type":"text/javascript"})
				first = scriptElement[3].text.split("LatLng(", 1)
				if (len(first) > 1):
					coord = first[1].split("),", 1)[0].split(", ")
					coord[0] = float(coord[0])
					coord[1] = float(coord[1])
			except IndexError:
				scraper.addError("No coordinates.")
				coord = coord

			try:
				address = practice_info_cells[1].find_all('p')[0].text.split("Location")[1].replace("\n", "").strip()
			except IndexError:
				scraper.addWarning("No address.")
				address = "None supplied"
			try:
				phone = practice_info_cells[1].find_all('p')[1].text.split("Phone: ")[1].strip()
			except IndexError:
				scraper.addWarning("No phone number.")
				phone = "None supplied"

			price_rows = practice_info_cells[2].find('table').find_all('tr')
			first_price = price_rows[0].find_all('td')[1].get_text(strip=True).replace(" ", "")

			# Try get all the prices regardless of formatting lol
			prices = []

			if scraper.practice['name'] == "Number 10 Youth One Stop Shop":
				prices = [
				{
					'age': 0,
					'price': 999
				},
				{
					'age': 10,
					'price': 0
				},
				{
					'age': 25,
					'price': 999
				}]
			elif (first_price == ""):
				scraper.addWarning("No price list.")
			else:
				prices.append({
					'age': 0,
					'price': 0
				})
				try:
					for i in range(1, 7):
						cells = price_rows[i].find_all('td')
						print("working on : " + str(cells))
						if 'and' not in cells[1].get_text(strip=True) and ',' not in cells[1].get_text(strip=True):
							prices.append({
								'age': scrapers.getFirstNumber(cells[0].get_text(strip=True)),
								'price': scrapers.getFirstNumber(cells[1].get_text(strip=True))
							})
						else:
							price_search = re.split('and|,', cells[1].get_text(strip=True))
							for price_bracket in price_search:
								price_bracket = price_bracket.split()
								print("Brackets: " + str(price_bracket))
								try:
									prices.append({
										'age': scrapers.getFirstNumber(price_bracket[0]),
										'price': scrapers.getFirstNumber(price_bracket[len(price_bracket)-1])
									})
								except IndexError: 
									scraper.addWarning("Weird price list.")
				except IndexError:
					scraper.addWarning("Weird price list.")	

			if not prices:
				scraper.addWarning("Weird price list.")	

			scraper.practice['address'] = address
			scraper.practice['phone'] = phone
			scraper.setLatLng(coord)
			scraper.practice['prices'] = prices

			scraper.finishPractice()

	return return scraper.finish()
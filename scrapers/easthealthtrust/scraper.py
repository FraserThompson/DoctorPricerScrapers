import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

# Get the list of practices for Wellington
def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('https://www.easthealth.co.nz/practices')
	rows = listUrlSouped.find_all('a', {'class': 'style-jgd359yclink'})

	print("Iterating table...")
	for row in rows:

		name = row.get_text(strip=True).replace(" >", "")
		scraper.newPractice(name, row.get('href'), "East Health Trust", "")

		######## GOING IN DEEP #######
		practiceUrlSouped = scraper.openAndSoup()
		could_be_anything = practiceUrlSouped.find_all('div', {'data-packed': 'true'})

		for thing in could_be_anything:
			text = thing.get_text(strip=True)

			if "fees current" in text:
				continue

			if "Phone" in text:
				scraper.practice['phone']= text.split("Phone")[1]
				continue
			
			if "Address" in text:
				scraper.practice['address'] = text.split("Physical Address")[1]
				continue

			if "$" in text:
				fees = text.split("$")
				continue

		#### Fees ####
		scraper.practice['prices'] =  [
			{
			'age': 0,
			'price': float(fees[0].replace('FREE', '0')),
			},
			{
			'age': 13,
			'price': float(fees[1]),
			},
			{
			'age': 18,
			'price': float(fees[2]),
			},
			{
			'age': 25,
			'price': float(fees[3]),
			},
			{
			'age': 45,
			'price': float(fees[4]),
			},
			{
			'age': 65,
			'price': float(fees[5]),
			},
		] 

		scraper.finishPractice()
	return scraper.finish()
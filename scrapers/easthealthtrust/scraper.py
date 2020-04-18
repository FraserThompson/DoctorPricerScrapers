import sys, codecs, os, re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

# Get the list of practices for Wellington
def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('https://www.easthealth.co.nz/clinics')
	rows = listUrlSouped.find_all('div', {'class': 'style-jgd359yc'})

	print("Iterating table...")
	for row in rows:
		linkEl = row.find('a')
		name = linkEl.get_text(strip=True).replace(" >", "")
		scraper.newPractice(name, linkEl.get('href'), "East Health Trust", "")

		practiceUrlSouped = scraper.openAndSoup().find('main')

		addressText = practiceUrlSouped.find(text="Physical Address").findParent('div', {'class': 'txtNew'}).getText(strip=True)
		scraper.practice['address'] = addressText.split("Physical Address")[1]

		phoneText = practiceUrlSouped.find(text="Phone").findParent('div', {'class': 'txtNew'}).getText(strip=True)
		scraper.practice['phone'] = phoneText.split("Phone")[1]

		try:
			feesTextEl = practiceUrlSouped.find(text=re.compile("^Fees")).findParent('div', {'class': 'txtNew'})
		except AttributeError:
			scraper.addError("Couldn't find fees.")
			continue

		ages = feesTextEl.findNext('div').findAll('p')
		prices = feesTextEl.findNext('div').findNext('div').findAll('p')

		scraper.practice['prices'] = []

		for idx, age in enumerate(ages):
			fee = {
				'age': scrapers.getFirstNumber(age.get_text(strip=True)),
				'price': float(scrapers.getFirstNumber(prices[idx].get_text(strip=True).replace('FREE', '0')))
			}
			scraper.practice['prices'].append(fee)

		scraper.finishPractice()
	return scraper.finish()
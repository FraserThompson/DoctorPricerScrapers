import sys, codecs, os, re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

# Get the list of practices for Wellington
def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('https://www.easthealth.co.nz/clinics')
	buttons = listUrlSouped.find_all('a', {'class': 'StylableButton2545352419__link'})

	for button in buttons:
		url = button.get('href')
		practiceSouped = scrapers.openAndSoup(url)

		bits = practiceSouped.find_all('div', {'class': '_1Q9if'})
		other_bits = practiceSouped.find_all('div', {'class': '_2Hij5'})

		name = bits[0].get_text(strip=True)

		scraper.newPractice(name, url, "East Health Trust", "")	

		scraper.practice['address'] = bits[1].get_text(strip=True).split("Physical Address")[1]
		scraper.practice['phone'] = bits[2].get_text(strip=True).split("Phone")[1]

		ages = bits[7].find_all('p')
		prices = ' '.join(re.split('\\xa0|\\n', other_bits[1].get_text())).split()

		# this one is weird
		if "Juliet" in name:
			ages_new = []
			prices_new = []

			for something in ages:
				split = something.get_text(strip=True).rsplit(' ', 1)
				ages_new.append(split[0])
				prices_new.append(split[1])

			ages = ages_new
			prices = prices_new

		if len(prices) != len(ages):
			thing = bits[8].find_all('p')
			prices = list(map(lambda a : a.get_text(strip=True), thing))
		
		if len(prices) != len(ages):
			scraper.addError('Could not get prices, instead got: ' + str(prices))
			continue

		scraper.practice['prices'] = []
		scraper.practice['prices_csc'] =  [
			{
			'age': 0,
			'price': 0,
			},
			{
			'age': 14,
			'price': 13,
			},
			{
			'age': 18,
			'price': 19.50,
			}
		]

		for i, age in enumerate(ages):
			price = {
				'age': scrapers.getFirstNumber(age if isinstance(age, str) else age.get_text(strip=True)),
				'price': scrapers.getFirstNumber(prices[i])
			}

			scraper.practice['prices'].append(price)

		scraper.finishPractice()

	return scraper.finish()
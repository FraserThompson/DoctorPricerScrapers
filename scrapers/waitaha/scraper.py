from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	fees_url = "https://waitaha.health.nz/your-health/fees/"
	fees_table = scrapers.openAndSoup(fees_url).find('table', {'id': 'tablepress-1'})

	ages = scrapers.parseAgeHeader(fees_table.find('thead').find_all('th'))

	practice_rows = fees_table.find('tbody').find_all('tr')

	practice_fees = {}
	for row in practice_rows:
		cells = row.find_all('td')

		name = cells[0].get_text(strip=True)

		prices = []
		for i, cell in enumerate(cells[1:]):
			price = {
				"age": ages[i],
				"price": scrapers.getFirstNumber(cell.get_text(strip=True))
			}
			prices.append(price)

		practice_fees[name] = prices

	practice_url = "https://waitaha.health.nz/find-a-gp/"
	practices = scrapers.openAndSoup(practice_url).find_all('div', {'class': 'gp-inner'})

	for practice in practices:
		name = practice.find('div', {'class': 'gp-name'}).get_text(strip=True)
		url = practice.find('a', {'class', 'button-multi'}).get('href')

		scraper.newPractice(name, url, "Waitaha PHO")

		scraper.practice['address'] = practice.find('div', {'class', 'gp-address'}).get_text(strip=True)
		scraper.practice['phone'] = practice.find('div', {'class', 'gp-phone'}).find("a").get_text(strip=True)
		scraper.practice['prices'] = practice_fees[name]

		scraper.finishPractice()

	return scraper.finish()
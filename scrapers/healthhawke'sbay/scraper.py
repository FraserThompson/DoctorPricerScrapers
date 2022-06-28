import sys, codecs, os, re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

# Get the list of practices for Hawkes Bay
# First URL for getting fees
def scrape(name):
	scraper = scrapers.Scraper(name)
	rootUrl = 'http://www.ourhealthhb.nz'

	feesUrlSouped = scrapers.openAndSoup(rootUrl + '/your-health/gp-fees-for-enrolled-patients/')
	fees_table = feesUrlSouped.find('table').find('tbody').find_all('tr')
	fees_header = feesUrlSouped.find('table').find('thead').find('tr').find_all('td')

	ages = []

	for header_cell in fees_header[1:]:
		text = header_cell.get_text(strip=True)
		if (text != "CSC"):
			age = scrapers.getFirstNumber(header_cell.get_text(strip=True))
			ages.append(age)

	allPrices = {}

	for row in fees_table:

		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)

		# These cells are different, lets just do them manually lol
		if "Wairoa" in name:
			prices = [
				{
					"age": 0,
					"price": 0,
				},
				{
					"age": 14,
					"price": 0,
				},
				{
					"age": 18,
					"price": 19.50,
				}
			]
			name = "Queen Street Practice"
			allPrices[scrapers.normalize(name)] = prices
			continue

		prices = []
		prices_csc = []

		csc_price = cells.pop() # last cell is always CSC price
		prices_csc.append({
			"age": 0,
			"price": scrapers.getFirstNumber(csc_price.get_text(strip=True))
		})

		for i, cell in enumerate(cells[1:]):
			text = cell.get_text(strip=True)
			prices.append({
				"age": ages[i],
				"price": scrapers.getFirstNumber(text)
			})
		
		allPrices[scrapers.normalize(name)] = prices

	listUrlSouped = scrapers.openAndSoup('http://www.ourhealthhb.nz/your-health/find-a-family-doctor-or-gp/')
	practiceList = listUrlSouped.find('div', {'class': 'rightbar'}).findAll('a')

	for practice in practiceList[1:-2]:
		name = practice.getText(strip=True)
		href = practice.get('href')
		url = href if "http" in href else rootUrl + href
		scraper.newPractice(name, url , "Health Hawke's Bay", "")

		maybe_span = practice.find('span')
		maybe_strong = practice.find('strong')
		notenrolling = maybe_span.get('class') == 'red' if maybe_span else maybe_strong.get('class') == 'red'
		if notenrolling:
			scraper.notEnrolling()

		practice_info = scrapers.openAndSoup(url)

		content = practice_info.find('div', {'class': 'col-md-6 main-content print-center-children'})

		scraper.practice['phone'] = scrapers.better_strip(content.find('h3').stripped_strings).split("Phone ")[1].split("Fax ")[0]
		scraper.practice['address'] = scrapers.better_strip(content.find_all('p')[0].stripped_strings)
		foundPrices = scrapers.partial_match(scrapers.normalize(name), allPrices)

		if foundPrices == None:
			scraper.addError('No prices found in fee table (could be name mismatch)')
		else:
			scraper.practice['prices'] = foundPrices

		scraper.finishPractice()

	return scraper.finish()
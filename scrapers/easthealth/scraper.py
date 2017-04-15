import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

# Get the list of practices for Wellington
def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('http://www.easthealth.co.nz/about/locate/')
	rows = listUrlSouped.find('ul', {'class': 'cggm_sidebar_list'}).find_all('li')

	print("Iterating table...")
	for row in rows:
		prices = []
		coord = (0.000, 0.000)
		scraper.newPractice(row.find('a').get_text(), row.find('a').get('href'), "Eastern Bay PHO", "")

		######## GOING IN DEEP #######
		practiceUrlSouped = scraper.openAndSoup()
		scraper.practice['address'] = practiceUrlSouped.find('section', {"id": "content"}).find('p').get_text().split(':')[1].strip()
		scraper.practice['phone'] = practiceUrlSouped.find('div', {"id": "phone"}).get_text().split('PHONE')[1]

		#### GOING IN REALLY DEEP ####
		scriptElement = practiceUrlSouped.find('body').find_all('script')
		first = scriptElement[3].text.split("LatLng(", 1)
		if (len(first) > 1):
			coord = first[1].split(")", 1)[0].split(",");
			coord[0] = float(coord[0])
			coord[1] = float(coord[1])

		if coord[0] == 0 or coord[1] == 0:
			scraper.addError("Bad coords." + str(coord[0]) + ", " + str(coord[1]))
			continue

		scraper.practice['lat'] = coord[0]
		scraper.practice['lng'] = coord[1]

		#### Fees ####
		try:
			fees_rows = practiceUrlSouped.find('table').find_all('tr')
			scraper.practice['prices'] =  [
				{
				'age': 0,
				'price': float(fees_rows[0].find_all('td')[1].get_text(strip=True).replace("$", "").replace('Free', '0')),
				},
				{
				'age': 13,
				'price': float(fees_rows[1].find_all('td')[1].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 18,
				'price': float(fees_rows[2].find_all('td')[1].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 25,
				'price': float(fees_rows[3].find_all('td')[1].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 45,
				'price': float(fees_rows[4].find_all('td')[1].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 65,
				'price': float(fees_rows[5].find_all('td')[1].get_text(strip=True).replace("$", "")),
				},
			] 
		except AttributeError:
			print("no fees")
			scraper.practice['prices'] = []
			scraper.addWarning("No prices.")

		scraper.postPractice()
	scraper.finish()
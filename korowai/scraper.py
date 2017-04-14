
import sys, codecs, os, re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

#stupid shit because the windows console can't print stuff properly
sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')

def scrape(name):
	scraper = scrapers.Scraper(name)

	feesList = scrapers.openAndSoup('http://www.korowai.co.nz/services/fees').find('table', {'class': 'fees'}).find_all('tr')
	prices = []
	for row in feesList[2:6]:
		cells = row.find_all('td')
		prices.append({'age': scrapers.getFirstNumber(cells[0].get_text(strip=True)), 'price': float(cells[1].get_text(strip=True).replace("Free", "0").replace("$", ""))})

	practiceListUrlSouped = scrapers.openAndSoup('http://www.korowai.co.nz/contact_us')
	practiceRoot = practiceListUrlSouped.find('div', {'class': 'contact-info'})
	practiceNames = practiceRoot.find_all('h2')
	practiceDeets = practiceRoot.find_all('div')
	i = 0

	for row in practiceNames:
		scraper.newPractice(row.get_text(strip=True), "http://www.korowai.co.nz/", "Te Korowai", "")
		scraper.practice['lat'] = float(row['data-latitude'])
		scraper.practice['lng'] = float(row['data-longitude'])

		details = practiceDeets[i].find_all('p')
		scraper.practice['address'] = re.sub(' +', ' ', details[0].get_text().replace('\n', ', ').replace('\xa0', ' ')).strip(', ')

		scraper.practice['phone'] = details[1].get_text(strip=True)
		i = i + 1

		scraper.practice['prices'] = prices

		scraper.postPractice()

	scraper.finish()
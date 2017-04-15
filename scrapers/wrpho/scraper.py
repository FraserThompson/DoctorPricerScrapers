import sys, codecs, os
import json, io
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers
import re

def scrape():
	url = 'http://www.wrpho.org.nz/resources.html#fee_schedule'
	listUrlSouped = scrapers.openAndSoup(url)

	practices_list = []
	error_list = []
	warning_list = []
	current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
	tables = listUrlSouped.find_all('table')
	fees_table = tables[2].find_all('tr')
	vlca_table = tables[3].find_all('tr')

	# Standard practices
	for row in fees_table[1:]:
		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)
		practice = scrapers.getDetailsFromSearch(name)
		if practice == 0:
			error_list.append(name + ": No details.")
			continue

		if name == "Dr Moore":
			prices = [
				{
					'age': 0,
					'price': 0
				},
				{
					'age': 6,
					'price': 25.00
				},
				{
					'age': 13,
					'price': scrapers.getFirstNumber(cells[2].get_text(strip=True))
				},
				{
					'age': 25,
					'price': scrapers.getFirstNumber(cells[4].get_text(strip=True))
				},
				{
					'age': 45,
					'price': scrapers.getFirstNumber(cells[5].get_text(strip=True))
				},
				{
					'age': 65,
					'price': scrapers.getFirstNumber(cells[6].get_text(strip=True))
				}
			]
		else:	
			prices = [
				{
					'age': 0,
					'price': 0
				},
				{
					'age': 13,
					'price': scrapers.getFirstNumber(cells[2].get_text(strip=True))
				},
				{
					'age': 25,
					'price': scrapers.getFirstNumber(cells[4].get_text(strip=True))
				},
				{
					'age': 45,
					'price': scrapers.getFirstNumber(cells[5].get_text(strip=True))
				},
				{
					'age': 65,
					'price': scrapers.getFirstNumber(cells[6].get_text(strip=True))
				}
			]
		
		if len(prices) == 0:
			warning_list.append(name + ": No prices.")

		# Make the dictionary object
		practice['name'] = name
		practice['restriction'] = ''
		practice['pho'] = 'Whanganui Regional PHO'
		practice['prices'] = prices
		
		scrapers.postToDatabase(practice, warning_list);
		practices_list.append(practice)

	#VLCA practices LOL IM COPYPASTING CODE
	for row in vlca_table[1:]:
		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)
		practice = scrapers.getDetailsFromSearch(name)
		if practice == 0:
			error_list.append(name + ": No details.")
			continue

		if name == "Te Oranganui Medical Centres":
			prices = [
				{
					'age': 0,
					'price': 0
				},
				{
					'age': 13,
					'price': scrapers.getFirstNumber(cells[2].get_text(strip=True))
				},
				{
					'age': 18,
					'price': 17.00
				},
				{
					'age': 65,
					'price': 12.00
				}
			]
		else:
			prices = [
				{
					'age': 0,
					'price': 0
				},
				{
					'age': 13,
					'price': scrapers.getFirstNumber(cells[2].get_text(strip=True))
				},
				{
					'age': 18,
					'price': scrapers.getFirstNumber(cells[3].get_text(strip=True))
				}
			]

		if len(prices) == 0:
			warning_list.append(name + ": No prices.")

		# Make the dictionary object
		practice['name'] = name
		practice['restriction'] = ''
		practice['pho'] = 'Whanganui Regional PHO (VLCA)'
		practice['prices'] = prices
		
		scrapers.postToDatabase(practice, warning_list);
		practices_list.append(practice)

	with io.open(current_dir + '\\data.json', 'w', encoding='utf8') as outFile:
		json.dump(practices_list, outFile, ensure_ascii=False, sort_keys=True, indent=4)

	scrapers.dealWithFailure(error_list, warning_list, current_dir)
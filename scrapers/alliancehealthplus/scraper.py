import sys, codecs, os
import json
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	root = 'http://www.alliancehealth.org.nz'
	listUrlSouped = scrapers.openAndSoup(root + '/find-a-gp')

	print(listUrlSouped)

	clinics = listUrlSouped.find('a', {'class': 'g-transparent-a'})

	for clinic in clinics:
		coord = [0,0]
		prices_list = []

		# Info
		scraper.newPractice(clinic.get_text(), clinic.get('href'), "Alliance Health Plus", "")

		infoUrlSouped = scrapers.openAndSoup(clinic.get('href'))

		scraper.practice['address'] = infoUrlSouped.find('div', {'[style]': 'left: 779px; width: 304px; position: absolute; top: 148px;'})
		scraper.practice['phone'] = infoUrlSouped.find('div', {'[style]': 'left: 779px; width: 164px; position: absolute; top: 431px;'}).split(':')[1].split('Fax')[0]


		# # Fees
		# try:
		# 	if (clinic_data.get_text() != 'Bader Drive Healthcare Manurewa'):
		# 		info_lines2 = pracURLSouped.find('div', {'class' : 'info'}).find('ul').find_all('li')
		# 	else: 
		# 		info_lines2 = pracURLSouped.find('div', {'class' : 'info'}).find_all('ul')[1].find_all('li')

		# 	count = 0

		# 	print(clinic_data.get_text() + ": ")
		# 	for line in info_lines2:
		# 		fees = line.get_text(strip=True).split(':')
		# 		print(fees)
		# 		if len(fees) == 2:
		# 			# Dealing with the left hand side
		# 			if (count == 0):
		# 				fees[0] = 0
		# 			else:
		# 				fees[0] = fees[0].replace('-', ' ').replace('+', '')
		# 				strip_numbers = [int(s) for s in fees[0].split() if s.isdigit()]
		# 				if len(strip_numbers) > 0:
		# 					fees[0] = strip_numbers[0]

		# 			# Dealing with the right hand side
		# 			fees[1] = fees[1].replace('\xa0', '').replace('&nbsp;', '').replace(' ', '')
		# 			if fees[1] == 'Free' or fees[1] == 'FREE':
		# 				fees[1] = 0;
		# 			elif "Extended" in fees[1]:
		# 				continue
		# 			else:
		# 				fees[1] = fees[1].split('(')[0]

		# 			if (isinstance(fees[1], int) is not True):
		# 				fees[1] = float(fees[1].replace("$", ""))

		# 			prices_list.append({"age" : fees[0], "price": fees[1]})
		# 			count += 1

		# except AttributeError:
		# 	scraper.addError("Couldn't get fees.")

		# scraper.practice['prices'] = prices_list
		# scraper.setLatLng(coord)
		# scraper.finishPractice()

	return scraper.finish()
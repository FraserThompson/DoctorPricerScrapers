import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	root = 'http://www.alliancehealth.org.nz'
	listUrlSouped = scrapers.openAndSoup(root + '/clinics')

	clinics = listUrlSouped.find('div', {'id': 'clinics-left'}).find('ul').find_all('li')
	for clinic in clinics:
		coord = [0,0]
		prices_list = []

		# Coord and website
		clinic_data = clinic.find('a')
		scraper.newPractice(clinic_data.get_text(), root + clinic_data.get('href'), "Alliance Health Plus", "")
		coord[0] = float(clinic_data.get('data-lat'))
		coord[1] = float(clinic_data.get('data-lng'))

		# Information
		pracURLSouped = scraper.openAndSoup()
		takingPatients = pracURLSouped.find('div', {'class': 'box-rgt text'}).find('p').get_text()
		if "is taking new patients" not in takingPatients:
			scraper.notEnrolling()
			continue
		info_lines1 = pracURLSouped.find('div', {'class': 'box-lft text'}).find('p').get_text().splitlines()
		scraper.practice['address'] = ' '.join(info_lines1[0:2])
		scraper.practice['phone'] = ' '.join(info_lines1[2].split()[1:])

		# Fees
		try:
			if (clinic_data.get_text() != 'Bader Drive Healthcare Manurewa'):
				info_lines2 = pracURLSouped.find('div', {'class' : 'info'}).find('ul').find_all('li')
			else: 
				info_lines2 = pracURLSouped.find('div', {'class' : 'info'}).find_all('ul')[1].find_all('li')

			count = 0

			print(clinic_data.get_text() + ": ")
			for line in info_lines2:
				fees = line.get_text(strip=True).split(':')
				print(fees)
				if len(fees) == 2:
					# Dealing with the left hand side
					if (count == 0):
						fees[0] = 0
					else:
						fees[0] = fees[0].replace('-', ' ').replace('+', '')
						strip_numbers = [int(s) for s in fees[0].split() if s.isdigit()]
						if len(strip_numbers) > 0:
							fees[0] = strip_numbers[0]

					# Dealing with the right hand side
					fees[1] = fees[1].replace('\xa0', '').replace('&nbsp;', '').replace(' ', '')
					if fees[1] == 'Free' or fees[1] == 'FREE':
						fees[1] = 0;
					elif "Extended" in fees[1]:
						continue
					else:
						fees[1] = fees[1].split('(')[0]

					if (isinstance(fees[1], int) is not True):
						fees[1] = float(fees[1].replace("$", ""))

					prices_list.append({"age" : fees[0], "price": fees[1]})
					count += 1

		except AttributeError:
			scraper.addError("Couldn't get fees.")

		scraper.practice['prices'] = prices_list
		scraper.practice['lat'] = coord[0]
		scraper.practice['lng'] = coord[1]
		scraper.postPractice()
	scraper.finish()
import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

url = 'http://www.haurakipho.org.nz/medical-centres/our-medical-centres'
fees_url = 'http://www.haurakipho.org.nz/medical-centres/hpho-practice-fees'

#
#
# THESE GUYS SCREENSHOTTED THEIR FEES TABLE SO I CANT SCRAPE IT WTF

def scrape():
	# listUrlSouped = scrapers.openAndSoup(url)
	# feesUrlSouped = scrapers.openAndSoup(fees_url)

	# fees_rows = feesUrlSouped.find('table', {'style': 'border: currentColor; border-collapse: collapse;'}).find_all('tr')[1:]
	# fees_dict = {}
	# practices_list = []
	# error_list = []
	# warning_list = []
	# current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

	# for row in fees_rows:
	# 	cells = row.find_all('td')
	# 	name = cells[1].get_text(strip=True)
	# 	if name == '0.00' or name == '-':
	# 		name = cells[0].get_text(strip=True)
	# 	try:
	# 		prices = [
	# 					{
	# 					'age': 0,
	# 					'price': 0,
	# 					},
	# 					{
	# 					'age': 6,
	# 					'price': float(cells[2].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
	# 					},
	# 					{
	# 					'age': 18,
	# 					'price': float(cells[3].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
	# 					},
	# 					{
	# 					'age': 25,
	# 					'price': float(cells[4].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
	# 					},
	# 					{
	# 					'age': 45,
	# 					'price': float(cells[5].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
	# 					},
	# 					{
	# 					'age': 65,
	# 					'price': float(cells[6].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
	# 					},
	# 				]
	# 		fees_dict[scrapers.normalize(name)] = prices
	# 	except (ValueError, IndexError):
	# 		warning_list.append(name + ": Could not get fees.")

	# for i in range(0, 25):
	# 	address = ''
	# 	phone = ''
	# 	practice = listUrlSouped.find('div', {'class': 'items-row cols-1 row-'+str(i)}).find('div', {'class': 'item column-1'});
	# 	name = practice.find('h2').get_text(strip='true');
	# 	lines = practice.find_all('p');

	# 	try:
	# 		prices = scrapers.partial_match(scrapers.normalize(name), fees_dict)
	# 	except:
	# 		warning_list.append(name + ': Could not get fees because of an exception.')

	# 	if len(prices) == 0:
	# 		prices = scrapers.partial_match(scrapers.normalize('hamilton ' + name.replace('centre', 'centres')), fees_dict)
	# 		if len(prices) == 0:
	# 			warning_list.append(name + ': Could not find fees in dict.')


	# 	if '-' in lines[0].get_text():
	# 		address = ', '.join(lines[0].strings).split('-')[1].strip()

	# 	for line in lines:
	# 		if 'Location:' in line.get_text(strip='true'):
	# 			address = ', '.join(line.strings).split('Location:')[1].replace(',,', ',').strip()
	# 		if 'Contact details:' in line.get_text(strip='true'):
	# 			phone = line.get_text(strip='true').split('Contact details:')[1].split('     ')[0].strip()
	# 		if 'Contact Details:' in line.get_text(strip='true'):
	# 			phone = line.get_text(strip='true').split('Contact Details:')[1].split('     ')[0].strip()
	# 		if 'Contact:' in line.get_text(strip='true'):
	# 			phone = line.get_text(strip='true').split('Contact:')[1].split('     ')[0].strip()

	# 	if address == '':
	# 		error_list.append(name + ": Cannot find address.")
	# 		continue
	# 	if phone == '':
	# 		warning_list.append(name + ": Cannot find phone.")

	# 	if ' - ' in phone:
	# 		phone = phone.split(' - ')[1]

	# 	coord = scrapers.geolocate(address)
	# 	if (coord[0] == 0):
	# 		error_list.append(name + ": Cannot geolocate address: " + address)
	# 		continue

	# 	# Make the dictionary object
	# 	practice = {
	# 		'name': name,
	# 		'url': url,
	# 		'address': address,
	# 		'phone': phone,
	# 		'restriction': '',
	# 		'pho': 'Hauraki PHO',
	# 		'lat': coord[0],
	# 		'lng': coord[1],
	# 		'prices': prices
	# 	}
		
	# 	scrapers.postToDatabase(practice, warning_list);
	# 	practices_list.append(practice)

	# with io.open(current_dir + '//data.json', 'w', encoding='utf8') as outFile:
	# 	json.dump(practices_list, outFile, ensure_ascii=False, sort_keys=True, indent=4)

	# scrapers.dealWithFailure(error_list, warning_list, current_dir)
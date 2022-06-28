from scrapers import common as scrapers
current_dir = './scrapers/nga_mataapuna_oranga/'

def scrape(name):
	with open(current_dir + 'data.json', 'r') as inFile:
		return scrapers.localScrape(inFile, name)
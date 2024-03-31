import requests
from scrapers import common as scrapers

current_dir = './scrapers/compasshealth/'

fee_url = 'https://tuora.org.nz/api/public/tuora-portal/practice-fees/filter?pageSize=10&showOnPracticeList=true&page=1&dhb='
info_url = 'https://tuora.org.nz/api/public/tuora-portal/practices/filter?page=1&pageSize=100&showOnPracticeList=true&dhb='

def scrape(name):

    scraper = scrapers.Scraper(name)

    # compass splits their lists into two sub-dhb type jams
    dhbs = [2, 3]

    for dhb in dhbs:
        # Get info to build a dict
        r = requests.get(info_url + str(dhb), verify=False)
        info_json = r.json()
        practice_info = info_json['content']
        practice_dict = {}

        for info in practice_info:
            name = info['name']
            practice_dict[name] = {
                'address': info['address'],
                'phone': info['phone'],
                'active': info['acceptingNewPatients'],
                'url': info['webSite']
            }

        # Get fees to add the practices
        r = requests.get(fee_url + str(dhb), verify=False)
        fees_json = r.json()
        practice_fees = fees_json['content']

        for fee in practice_fees:
            name = fee['practice']
            csc = fee['cscHolder']

            try:
                info = practice_dict[name]
            except KeyError:
                scraper.addError("Practice exists in Fees but not in info. Skipping.")
                continue

            scraper.newPractice(name, info['url'], "Compass Health", "")
            scraper.practice['phone'] = info['phone']
            scraper.practice['address'] = info['address']

            if not info['active']:
                scraper.notEnrolling()

            if csc:
                scraper.practice['prices_csc'] = [
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
                    },
                ]

            scraper.practice['prices'] = [
                {
                'age': 0,
                'price': fee['groupUnder14'],
                },
                {
                'age': 14,
                'price': fee['group14To17'],
                },
                {
                'age': 18,
                'price': fee['group18To24'],
                },
                {
                'age': 25,
                'price': fee['group25To44'],
                },
                {
                'age': 45,
                'price': fee['group45To65'],
                },
                {
                'age': 65,
                'price': fee['groupOver65'],
                },
            ]

            scraper.finishPractice()

    return scraper.finish()
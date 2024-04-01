import requests
from scrapers import common as scrapers

current_dir = './scrapers/compasshealth/'

fee_url = 'https://tuora.org.nz/api/tuora-profile/practice-fees/filter?page=1&pageSize=100&showOnPracticeList=true&dhb='
info_url = 'https://tuora.org.nz/api/tuora-profile/practice-fees/practices-except-after-care'

def scrape(name):

    scraper = scrapers.Scraper(name)

    # Get info to build a dict
    r = requests.get(info_url, verify=False)
    practice_info = r.json()
    practice_dict = {}

    for info in practice_info:
        name = info['name']
        practice_dict[name] = info

    # fees requests are per DHB
    dhbs = [2, 3, 9]

    # Get fees to add the practices
    for dhb in dhbs:

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

            scraper.newPractice(name, info['webSite'], "Compass Health", "")
            scraper.setLatLng([info['coordinates']['lat'], info['coordinates']['lng']])
            scraper.practice['phone'] = info['phone']
            scraper.practice['address'] = info['address']

            if not info['acceptingNewPatients']:
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
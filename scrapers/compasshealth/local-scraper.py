from scrapers import common as scrapers
import sys
import codecs
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')

current_dir = './scrapers/compasshealth/'


def scrape(name):
    things = [
        {
            'feesUrl': 'https://www.compasshealth.org.nz/PracticesandFees/WellingtonPractices/PracticeFees.aspx',
            'infoUrl': 'https://www.compasshealth.org.nz/PracticesandFees/WellingtonPractices.aspx',
            'addressEl': "dnn_ctr484_Map_AddressLabel",
            'phoneEl': "dnn_ctr484_Map_PhoneLabel"},
        {
            'feesUrl': 'https://www.compasshealth.org.nz/PracticesandFees/WairarapaPractices/PracticeFees.aspx',
            'infoUrl': 'https://www.compasshealth.org.nz/PracticesandFees/WairarapaPractices.aspx',
            'addressEl': "dnn_ctr499_Map_AddressLabel",
            'phoneEl': "dnn_ctr499_Map_PhoneLabel"}
    ]

    mainUrl = "https://compasshealth.org.nz/Practices-and-Fees"

    scraper = scrapers.Scraper(name)

    for thing in things:
        feesUrlSouped = scrapers.openAndSoup(thing['feesUrl'])
        infoURLSouped = scrapers.openAndSoup(thing['infoUrl'])

        fees_rows = feesUrlSouped.find('table').find_all('tr')[1:]

        info_table = infoURLSouped.find('table')
        info_list = [[cell.get_text(strip=True) for cell in row("td")]
                     for row in info_table("tr")[1:]]
        info_dict = {}
        for item in info_list:
            info_dict[item[0]] = item[1:]

        print("Iterating table...")
        for row in fees_rows:

            cells = row.findAll('td')

            if len(cells) > 0:
                scraper.newPractice(cells[0].get_text(
                ), "https://compasshealth.org.nz/", "Compass Health", "")

                practice_info = scrapers.partial_match(scraper.practice['name'], info_dict)

                if not practice_info:
                    scraper.addError(
                        "Couldn't find in info dict. Key mismatch?")
                    continue

                if not practice_info[0]:
                    scraper.notEnrolling()

                scraper.practice['phone'] = practice_info[1]
                scraper.practice['address'] = practice_info[2]

                scraper.practice['prices'] = [
                    {
                        'age': 0,
                        'price': float(cells[1].get_text(strip=True).replace("$", "")),
                    },
                    {
                        'age': 14,
                        'price': float(cells[2].get_text(strip=True).replace("$", "")),
                    },
                    {
                        'age': 18,
                        'price': float(cells[3].get_text(strip=True).replace("$", "")),
                    },
                    {
                        'age': 25,
                        'price': float(cells[4].get_text(strip=True).replace("$", "")),
                    },
                    {
                        'age': 45,
                        'price': float(cells[5].get_text(strip=True).replace("$", "")),
                    },
                    {
                        'age': 65,
                        'price': float(cells[6].get_text(strip=True).replace("$", "")),
                    },
                ]

                scraper.finishPractice()

    result = scraper.finish()

    with open(current_dir + 'data.json', 'w') as outfile:
        json.dump(result, outfile)

    return result

import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
    scraper = scrapers.Scraper(name)

    homepage = 'https://www.thedoctors.co.nz/'
    soup = scrapers.openAndSoup(homepage)

    practices = soup.find('li', {'class': 'has-dropdown first'}).find_all('a')

    for practice in practices:
        url = practice.get('href')
        name = practice.get_text(strip=True).replace("*", "").strip()

        if "https://www.thedoctors.co.nz" not in url:
            continue

        scraper.newPractice(name, url, 'The Doctors')

        practiceDetails = scrapers.openAndSoup(url)

        address_area = practiceDetails.find('p', {'class': 'map'})

        # This will fail if the linked page is weird (looking at you whakatipu)
        try:
            scraper.practice['phone'] = practiceDetails.find('p', {'class': 'phone tel'}).get_text(strip=True)
        except AttributeError:
            continue
    
        scraper.practice['address'] = scrapers.better_strip(address_area.stripped_strings)

        # Extract coordinates from gmaps URL, or move on
        coords = None
        try:
            coords = address_area.find('a').get('href').split('@')[1].split(",")[0:2]
        except IndexError:
            pass
        try:
            coords = address_area.find('a').get('href').split('ll=')[1].split("&")[0].split(",")
        except IndexError:
            pass

        if coords is not None:
            scraper.setLatLng(coords)

        # This might contain info on whether it's enrolling or not
        potentially_useful = practiceDetails.find('div', {'id': 'dnn_ContentCenter'}).find_all('h3')
        for thing in potentially_useful:
            text = thing.get_text(strip=True)
            if ("enrolment" in text or "enrolling" in text or "enrolments" in text) and ("not" in text or "limited" in text or "closed"):
                scraper.notEnrolling()
                break

        # There are sometimes many tables, but the first in the second accordion is usually it
        # but it's sometimes the 0th if there's only one accordion, so we'll try both.

        accordions = practiceDetails.find_all('div', {'class': 'DNNModuleContent ModLiveAccordionC'})

        if not accordions:
            scraper.addWarning("No prices")
            scraper.finishPractice()
            continue

        table = accordions[1].find('table') if len(accordions) > 1 else accordions[0].find('table')

        if not table:
            scraper.addWarning("No prices")
            scraper.finishPractice()
            continue
            
        entire_table = table.get_text(strip=True).lower()

        # one of them was like WE DON'T KNOW YET LMAo so we'll skip them
        if "tbc" in entire_table:
            continue

        # Determine if one of the columns has CSC prices
        csc_index = None
        header = table.find_all('th')
        for i, thing in enumerate(header):
            text = thing.get_text(strip=True).lower()
            if "csc" in text and "no" not in text:
                csc_index = i
                break

        rows = table.find('tbody').find_all('tr')

        ages = []
        csc_ages = []
        for row in rows:

            cells = row.find_all('td')

            if not cells:
                scraper.addWarning('A price row was empty, skipping it.')
                continue

            age_text = cells[0].get_text(strip=True)

            age = scrapers.getFirstNumber(age_text)
            price_text = cells[1].get_text(strip=True)
            price = scrapers.getFirstNumber(price_text if price_text else cells[2].get_text(strip=True))

            # Some of them put the header in tbody so they fail and we can skip
            if age == 1000 or price == 1000:
                continue

            if csc_index is not None or "csc" in age_text.lower() and age not in csc_ages:
                price_csc = {
                    'age': age,
                    'price': scrapers.getFirstNumber(cells[csc_index or 1].get_text(strip=True))
                }

                csc_ages.append(age)
                scraper.practice['prices_csc'].append(price_csc)

                continue

            if age not in ages:
        
                price = {
                    'age': age,
                    'price': price
                }

                ages.append(age)
                scraper.practice['prices'].append(price)

        scraper.finishPractice()

    return scraper.finish()
from __future__ import absolute_import, unicode_literals
import json

from celery import shared_task
from django_celery_results.models import TaskResult

from dp_server import models
from scrapers import run # someday we'll seperate these scrapers from the server

from collections import defaultdict

from django.db.models import Q
from django.contrib.gis.geos import Point
from django.db.models import Avg, Max, Min
from django.forms.models import model_to_dict

######################################
# Calls the scraper for a module
# Params: name of module to scrape
#
@shared_task
def scrape(module):

    task_result = TaskResult(task_id=scrape.request.id)
    task_result.meta = "Scraping"
    task_result.save()

    pho = models.Pho.objects.get(module=module)
    pho.current_task_id = scrape.request.id
    pho.save()

    response = run.one(module)

    pho.last_scrape = response['data']
    pho.current_task_id = None
    pho.save()

    # If we're dealing with a special manual import
    if module == "_manual" or module == "_legacy":

        sorted_by_pho = defaultdict(list)

        # Make sure the PHO objects exist
        for value in response['data']['scraped']:

            sorted_by_pho[value["practice"]["pho"]].append(value)

            try:
                pho = models.Pho.objects.get(name=value["practice"]["pho"])
            except models.Pho.DoesNotExist:
                print('making new pho:' + value["practice"]["pho"])
                pho = models.Pho(name=value["practice"]["pho"], module=value["practice"]["pho"].lower().replace(" ", ""))
                pho.save()

        # Add our scraped objects to the PHO's last_scrape
        for key, value in sorted_by_pho.items():
            pho_obj = models.Pho.objects.get(name=key)
            pho_obj.last_scrape = {"name": key, "scraped": value, "errors": [], "warnings": []}
            pho_obj.save()

    return response

######################################
# Submits data to a PHO
# Params: module to submit for, data to submit (optional, will use last scrape if omitted)
@shared_task
def submit(module, data):

    task_result = TaskResult(task_id=submit.request.id)
    task_result.meta = "Submitting"
    task_result.save()

    # Get the PHO
    pho = models.Pho.objects.get(module=module)

    # Have we been supplied JSON to submit?
    if not data:
        data = pho.last_scrape

    changes = {}

    # Add the practices
    for result in data['scraped']:

        practice = result['practice']

        practice_pho, created = models.Pho.objects.get_or_create(name=practice['pho'], defaults={'scraper_source': practice.get('scraper_source', 'Web')})

        print("Making or updating practice: " + practice['name'])

        # Make the practice
        new_practice = models.Practice.objects.update_or_create( 
            name=practice['name'], 
            defaults={
                'address': practice['address'],
                'pho_link': practice_pho,
                'phone': practice['phone'],
                'url': practice['url'],
                'location': Point( float(practice['lng']), float(practice['lat']) ),
                'restriction': practice['restriction'],
                'active': practice.get('active', True),
                'place_id': practice['place_id'] if 'place_id' in practice and practice['place_id'] is not None else ''
            }
        )

        if practice.get('prices'):

            price_changes = process_prices(practice, pho, new_practice, False)

            if len(price_changes):
                
                if practice['name'] not in changes:
                    changes[practice['name']] = {}

                changes[practice['name']]["non-csc"] = price_changes

        if practice.get('prices_csc'):

            csc_price_changes = process_prices(practice, pho, new_practice, True)

            if len(csc_price_changes):
                
                if practice['name'] not in changes:
                    changes[practice['name']] = {}

                changes[practice['name']]["csc"] = csc_price_changes


    # Update the PHO
    pho.number_of_practices = len(data['scraped'])
    pho.save()

    average_prices = get_pho_averages(pho)
    pho.average_prices = average_prices
    pho.save()

    # Add a log item
    log = models.Logs(source=pho, scraped=data['scraped'], errors=data['errors'], warnings=data['warnings'], changes=changes)
    log.save()

    return model_to_dict(log)

# Helper: Processes prices
def process_prices(practice, pho, new_practice, cscPrices=False):
    old_prices = models.Prices.objects.filter(practice__name=practice['name'], csc=cscPrices)
    changes = {}

    prices_key = 'prices' if not cscPrices else 'prices_csc'

    # If the age buckets have changed we must remain calm and act appropriately
    if old_prices.count() != len(practice[prices_key]):

        # Get all the ages we want
        ages = []
        for price in practice[prices_key]:
            ages.append(int(price['age']))

        # Delete prices which don't fit the age brackets we have or which are duplicates
        for price in old_prices:

            if models.Prices.objects.filter(practice__name=practice['name'], from_age=price.from_age, csc=cscPrices).count() > 1:
                price.delete()
            elif price.from_age not in ages:
                price.delete()

    # Submit prices
    for i, price in enumerate(practice[prices_key]):

        rounded_price = round(float(price['price']), 2)

        from_age = int(price['age'])
        if i < len(practice[prices_key]) - 1:
            to_age = int(practice[prices_key][i+1]['age']) - 1
        else:
            to_age = 150

        print('Submitting price for: ' + practice['name'])

        old_price = models.Prices.objects.filter(practice__name=practice['name'], from_age=from_age, csc=cscPrices).first()

        # If there's already a price for that age group then we should update that one so we get history
        if old_price:

            rounded_old_price = round(float(old_price.price), 2)
            # If there's a change
            if rounded_old_price != rounded_price:

                # add it to the changes object
                changes[str(old_price.from_age)] = [str(rounded_old_price), str(rounded_price)]

                # change the thing in the database
                old_price.pho = pho
                old_price.price = rounded_price
                old_price.save()
        
        # Otherwise we should make a new price
        else:

            new_prices = models.Prices.objects.create(
                practice = new_practice[0],
                from_age = from_age,
                to_age = to_age,
                pho = pho,
                price = rounded_price,
                csc = cscPrices,
            )

        # We should delete any prices matching the age with a different price (~Q is how you do do not equal in django)
        bad_old_price = models.Prices.objects.filter(~Q(price=rounded_price), practice__name=practice['name'], from_age=from_age, csc=cscPrices)
        bad_old_price.delete()

    return changes

# Helper: Updates the averages prices for a PHO
# Params: pho name
def get_pho_averages(pho):

    average_prices = [
        {'age': '0', 'average': '0', 'min': '0', 'max': '0'},
        {'age': '6', 'average': '0', 'min': '0', 'max': '0'},
        {'age': '14', 'average': '0', 'min': '0', 'max': '0'},
        {'age': '18', 'average': '0', 'min': '0', 'max': '0'},
        {'age': '25', 'average': '0', 'min': '0', 'max': '0'},
        {'age': '45', 'average': '0', 'min': '0', 'max': '0'},
        {'age': '65', 'average': '0', 'min': '0', 'max': '0'}
    ]

    # Update the average
    for price in average_prices:
        stats = get_pho_average(pho.id, price['age'])
        price['average'] = "{:.2f}".format(stats['price__avg'])
        price['min'] = "{:.2f}".format(stats['price__min'])
        price['max'] = "{:.2f}".format(stats['price__max'])
    return average_prices

# Helper: Gets the average price for a particular age over a PHO.
# Params: pho name, age
def get_pho_average(pho, age):
    result = models.Prices.objects.filter(pho__id=pho, to_age__gte=age, from_age__lte=age, price__lt=999, csc=False).aggregate(Avg('price'), Max('price'), Min('price'), Max('from_age'))
    return result
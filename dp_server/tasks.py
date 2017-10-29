from __future__ import absolute_import, unicode_literals
import json

from celery import shared_task
from dp_server import models
from collections import defaultdict
from scrapers import run # someday we'll seperate these scrapers from the server
from django_celery_results.models import TaskResult

@shared_task
def scrape(module):

    task_result = TaskResult(task_id=scrape.request.id)
    task_result.save()

    response = run.one(module)

    # If we're dealing with a normal import
    if module != "_manual":

        pho = models.Pho.objects.get(module=module)
        pho.last_scrape = response['data']
        pho.save()

    # If we're dealing with a special manual import
    else:

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
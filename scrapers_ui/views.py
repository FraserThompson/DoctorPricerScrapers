from django.http import HttpResponse
from django.shortcuts import render
from scrapers import run
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D

from django.contrib.auth.models import User, Group
from rest_framework import viewsets

from scrapers_ui import serializers
from scrapers_ui import models

import logging, json

logger = logging.getLogger(__name__)

######################################################
# Django REST Framework views
######################################################
class PhoViewSet(viewsets.ModelViewSet):
    queryset = models.Pho.objects.all()
    serializer_class = serializers.PhoSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

class PricesViewSet(viewsets.ModelViewSet):
    queryset = models.Prices.objects.all()
    serializer_class = serializers.PricesSerializer

class PracticeViewSet(viewsets.ModelViewSet):
    queryset = models.Practice.objects.all()
    serializer_class = serializers.PracticeSerializer

    def get_queryset(self):
        queryset = models.Practice.objects.all()

        name = self.request.query_params.get('name', None)
        lat = self.request.query_params.get('lat', None)
        lng = self.request.query_params.get('lng', None)
        age = self.request.query_params.get('age', None)
        pho = self.request.query_params.get('pho', None)
        distance = self.request.query_params.get('distance', '2')

        # Specific practice
        if name is not None:
            queryset = queryset.filter(name=name)

        # All pho's practices
        if pho is not None:
            queryset = queryset.filter(pho=pho)

        # Location lookup
        if lat is not None and lng is not None and age is not None and distance is not None:
            pnt = 'POINT('+str(lng)+' '+str(lat)+')'
            # get prices here too somehow
            queryset = queryset.filter(location__distance_lte=(pnt, D(km=distance)))

        return queryset

class LogsViewSet(viewsets.ModelViewSet):
    queryset = models.Logs.objects.all()
    serializer_class = serializers.LogsSerializer

    def get_queryset(self):
        queryset = models.Logs.objects.all()
        source = self.request.query_params.get('source', None)

        if source is not None:
            queryset = queryset.filter(source__module=source)

        return queryset


######################################################
# Renders the index page
######################################################
def index(request):
    context = {}
    return render(request, 'home/index.html', context)

######################################################
# Runs a scraper
######################################################
@csrf_exempt
def scrape(request):
    if request.method == "POST":

        return_code = 200
        data = request.body.decode('utf-8')
        json_body = json.loads(data)

        response = run.one(json_body['module'])

        if not response['error']:
            submit(response['data'], json_body['module'])
        else:
            return_code = 400

        return HttpResponse(json.dumps(response), content_type="application/json", status=return_code)

######################################################
# Helper: Submits scraped data to the database.
######################################################
def submit(data, module):

    average_prices = [
        {'age': 0, 'price': 0},
        {'age': 6, 'price': 0},
        {'age': 13, 'price': 0},
        {'age': 18, 'price': 0},
        {'age': 25, 'price': 0}, 
        {'age': 45, 'price': 0},
        {'age': 65, 'price': 0}
    ]

    changes = []

    # Get the PHO
    pho = models.Pho.objects.get(module=module)

    # Add the practices
    for practice in data['scraped']:

        new_practice = models.Practice.objects.update_or_create( 
            name=practice['name'], 
            address=practice['address'],
            pho=practice['pho'],
            phone=practice['phone'],
            url=practice['url'],
            location=GEOSGeometry('POINT('+str(practice['lng'])+' '+str(practice['lat'])+')'),
            restriction=practice['restriction'],
            place_id=practice['place_id']
        )

        for i, price in enumerate(practice['prices']):

            from_age = price['age']

            if i < len(practice['prices']) - 1:
                to_age = practice['prices'][i+1]['age'] - 1
            else:
                to_age = 150

            new_prices = models.Prices.objects.update_or_create(
                practice = new_practice[0],
                pho = pho,
                from_age = from_age,
                to_age = to_age,
                price = price['price']
            )

    # Update the average
    for price in average_prices:
        price['price'] = get_pho_average(pho.id, price['age'])

    # Update the PHO
    pho.number_of_practices = len(data['scraped']) 
    pho.average_prices = average_prices
    pho.save()

    # Add a log item
    log = models.Logs(source=pho, scraped=data['scraped'], errors=data['errors'], warnings=data['warnings'], changes=changes)
    log.save()

######################################################
# Helper: Gets the average price
# for a particular age over a PHO.
######################################################
def get_pho_average(pho, age):
    result = models.Prices.objects.filter(pho__id=pho, to_age__gte=age, from_age__lte=age).aggregate(Avg('price'))
    return result['price__avg']
import re
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

from dp_server.celery import app

from dp_server import tasks

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from django.contrib.auth.models import User, Group
from django.db.models import Avg, Max, Min, Q, Count

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from dp_server import serializers
from dp_server import models

import logging
import json

from django_celery_results.models import TaskResult

logger = logging.getLogger(__name__)

###########################################################
# Django REST Framework views
###########################################################

###########################################################
# Returns regions, with optional data for each region
# Params:
#         name: will return a specific region
#         practices: if specified will return all practices in that region
###########################################################


class RegionViewSet(viewsets.ModelViewSet):
    queryset = models.Region.objects.all().order_by('name')
    serializer_class = serializers.RegionSerializer

    @method_decorator(cache_page(60*60*24))  # 1 day
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = models.Region.objects.all()

        name = self.request.query_params.get('name', None)
        practices = self.request.query_params.get('practices', None)

        if name is not None:
            queryset = queryset.filter(name=name)

            if practices is not None:
                self.serializer_class = serializers.RegionWithPracticesSerializer

                for region in queryset:
                    for practice in region.practices:
                        practice.all_prices = practice.all_prices(
                            True, csc=False)

        return queryset

###########################################################
# Returns PHOs
###########################################################


class PhoViewSet(viewsets.ModelViewSet):
    queryset = models.Pho.objects.all().order_by('name')
    serializer_class = serializers.PhoSerializer

###########################################################
# Returns prices
###########################################################


class PricesViewSet(viewsets.ModelViewSet):
    queryset = models.Prices.objects.all()
    serializer_class = serializers.PricesSerializer

    def get_queryset(self):
        queryset = models.Prices.objects.all()

        name = self.request.query_params.get('name', None)

        if name is not None:
            queryset = queryset.filter(practice__name=name)

        return queryset

###########################################################
# Returns some practices
# Params:
#         name will return a specific practice
#         pho will return all practices from a pho
#         lat=x,lng=x will return practices within 60,000km of that coordinate.
#         distance=x will override the default 60,000km distance setting.
#         if age is specified it will also calculate prices.
#         all_prices=true will return the price set for each practice (expensive)
#         sort: Only supported with lat/lng. Will sort it into buckets for frontend.
###########################################################


class PracticeViewSet(viewsets.ModelViewSet):
    queryset = models.Practice.objects.all()
    serializer_class = serializers.PracticeSerializer

    def get_queryset(self):
        queryset = models.Practice.objects.all()

        name = self.request.query_params.get('name', None)
        lat = self.request.query_params.get('lat', None)
        lng = self.request.query_params.get('lng', None)
        age = self.request.query_params.get('age', None)
        csc = self.request.query_params.get('csc', False)
        pho = self.request.query_params.get('pho', None)
        all_prices = self.request.query_params.get('all_prices', None)
        distance = self.request.query_params.get('distance', '60000')
        sort = self.request.query_params.get('sort', False)

        queryset = queryset.filter(disabled=False)

        # Specific practice
        if name is not None:
            queryset = queryset.filter(name=name)

        # All pho's practices
        if pho is not None:
            queryset = queryset.filter(pho_link__name=pho)

        # Location lookup
        if lat is not None and lng is not None:
            pnt = Point(x=float(lng), y=float(lat), srid=4326)
            queryset = queryset.filter(location__distance_lte=(pnt, D(m=distance))).annotate(
                distance=Distance('location', pnt)).order_by('distance')

        # Prices
        if age is not None:
            for practice in queryset:
                practice.price = practice.price(age=age, csc=csc)
        elif all_prices:
            for practice in queryset:
                practice.all_prices = practice.all_prices(True, csc)

        # Sorting into radius buckets
        if lat is not None and lng is not None and sort is not False:
            queryset = sortPractices(queryset)
            self.serializer_class = serializers.SortedPracticeSerializer

        return queryset

###########################################################
# Returns submission logs
# Params:
#         source: will return logs from a particular module
###########################################################


class LogsViewSet(viewsets.ModelViewSet):
    queryset = models.Logs.objects.all()
    serializer_class = serializers.LogsSerializer

    def get_queryset(self):
        queryset = models.Logs.objects.all()
        source = self.request.query_params.get('source', None)

        if source is not None:
            queryset = queryset.filter(source__module=source).order_by('-id')

        return queryset

# Helper method for the practices view


def sortPractices(practices):

    supportedRadius = [2000, 5000, 10000, 30000, 60000]

    # The radius buckets
    sortedPractices = list(map(lambda a: {'name': str(
        int(a / 1000)) + "km", 'distance': a, 'practices': []}, supportedRadius))

    bucket_index = 0

    for practice in practices:

        if practice.distance.m > sortedPractices[bucket_index]['distance']:
            bucket_index += 1

        bucket = sortedPractices[bucket_index]
        bucket['practices'].append(practice)

    return sortedPractices

###########################################################
# Normal views
###########################################################

###########################################################
# Returns the history of price changes for overall averages
###########################################################
@csrf_exempt
@api_view(['GET'])
@cache_page(60 * 60 * 24 * 1)  # 1 day caching
def price_history(request):

    response = {}

    queryset = models.Prices.history.filter(
        Q(csc=False) | Q(csc=None)).order_by('history_date').values()

    averages = {}

    for thing in queryset:

        date_string = thing['history_date'].strftime("%Y")
        age = thing['from_age']

        if date_string not in averages:
            averages[date_string] = {}

        if age not in averages[date_string]:
            averages[date_string][age] = {'count': 0, 'price': 0}

        averages[date_string][age]['count'] += 1
        averages[date_string][age]['price'] += float(thing['price'])

    for key, average in averages.items():
        for key, value in average.items():
            value['price'] = value['price'] / value['count']

    response = json.dumps(averages)

    return HttpResponse(response, content_type="application/json")

###########################################################
# Returns the history of price changes for a particular practice or PHO
###########################################################
@csrf_exempt
@api_view(['GET'])
@cache_page(60 * 60 * 24 * 1)  # 1 day caching
def model_price_history(request, type=None):

    name = request.GET.get('name', None)

    averages = {}

    match type:
        case "pho":
            queryset = models.Pho.history.filter(module=name).order_by(
                'history_date').values('average_prices', 'history_date')

            for thing in queryset:
                date_string = thing['history_date'].strftime("%Y")

                if date_string not in averages:
                    averages[date_string] = {}

                for thing in thing['average_prices']:

                    age = thing['age'] if thing['age'] != 13 else 14

                    if age not in averages[date_string]:
                        averages[date_string][age] = {'price': 0}

                    averages[date_string][age]['price'] = thing['average']

    return JsonResponse(averages, status=200, safe=False)

###########################################################
# Gets averages for a pho
###########################################################
@csrf_exempt
@api_view(['GET'])
@cache_page(60 * 60 * 24 * 1)  # 1 day caching
def model_averages(request, type=None):

    ages = [0, 6, 14, 18, 25, 45, 65]
    response = []
    name = request.GET.get('name', None)

    for age in ages:

        match type:
            case "pho":
                queryset = models.Prices.objects.filter(
                    pho__name=name, to_age__gte=age, from_age__lte=age, price__lt=999, csc=False)

        queryset = queryset.aggregate(Avg('price'), Max(
            'price'), Min('price'), Max('from_age'))
        response.append(queryset)

    return JsonResponse(response, status=200, safe=False)


###########################################################
#################### ADMIN VIEWS ##########################
###########################################################

###########################################################
# Runs a scraper
# Expects a 'module' param specifying what to run
###########################################################
@csrf_exempt
@api_view(['POST'])
def scrape(request):

    if not request.user.is_authenticated:
        return HttpResponseBadRequest("You're not cool enough to do that.")

    data = request.body.decode('utf-8')
    json_body = json.loads(data)

    pho = models.Pho.objects.get(module=json_body['module'])

    if pho.current_task_id:
        return HttpResponseBadRequest("We're already scraping: " + pho.current_task_id)

    task = tasks.scrape.delay(json_body['module'])

    return JsonResponse({'task_id': task.task_id}, status=200)

###########################################################
# Submits to database
# Expects a 'module' param, optional 'data' param or it will submit last_scrape for the PHO
###########################################################
@csrf_exempt
@api_view(['POST'])
def submit(request):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest("You're not cool enough to do that.")

    data = request.body.decode('utf-8')
    json_body = json.loads(data)

    task = tasks.submit.delay(
        json_body['module'], json_body['data'] if 'data' in json_body else None)

    return JsonResponse({'task_id': task.task_id}, status=200)


###########################################################
# GETs the status of a task or DELETES one
# Expects 'task_id' param, to DELETE it also needs 'module'
###########################################################
@csrf_exempt
@api_view(['GET', 'DELETE'])
def task_status(request):

    data = request.query_params

    if request.method == 'GET':
        try:
            task_result = TaskResult.objects.get(task_id=data['task_id'])
        except TaskResult.DoesNotExist:
            return HttpResponseBadRequest('Task object does not exist.')

        if (task_result.status != "FAILURE"):
            return JsonResponse(task_result.as_dict(), status=200, safe=False)
        else:
            return JsonResponse(task_result.as_dict(), status=400, safe=False)

    elif request.method == 'DELETE':

        if not request.user.is_authenticated:
            return HttpResponseBadRequest("You're not cool enough to do that.")

        app.control.terminate(data['task_id'])

        pho = models.Pho.objects.get(module=data['module'])
        pho.current_task_id = None
        pho.save()

        return HttpResponse('Killed it')

###########################################################
# Helper function for the clean() method. Does the actual deletion.
###########################################################


def clean_delete(matches, dry_run=True):

    disabled = []

    # Because this was when the field got populated for the first time
    never_updated_string = "2022-07-09T22:46:51.445203+00:00"

    for delete in matches:
        # If the newest one has never been updated then let's just go by ID
        if delete[0]['updated_at'].isoformat() == never_updated_string:
            delete.sort(key=lambda a: a['id'], reverse=True)

        for disable in delete[1:]:
            disabled.append(disable['id'])
            if not dry_run:
                models.Practice.objects.filter(
                    id=disable['id']).update(disabled=True)

    return disabled

###########################################################
# Does a search for points on top of each other and deletes the oldest
###########################################################
@csrf_exempt
@api_view(['GET'])
def clean(request):

    if not request.user.is_authenticated:
        return HttpResponseBadRequest("You're not cool enough to do that.")

    dry_run = request.query_params.get('dry')
    name_search = request.query_params.get('names')
    location_search = request.query_params.get('location')
    smart_search = request.query_params.get('smart')
    dumb_search = request.query_params.get('dumb')
    price_search = request.query_params.get('price_search')

    # These places are allowed to be on top of each other because they are
    whitelist = ["Otahuhu Whitecross", "Otahuhu Local Doctors"]

    # Probably a cool way to do this with db queries but whatever
    all_queryset = models.Practice.objects.filter(disabled=False).values()

    # We sort matches into buckets based on confidence...
    # very_confident: Practices which are located within 5m of each other physically. These are automatically deleted.
    # quite_confident. Practices which have similar names, similar addresses, and are within 100m of each other physically. These are automatically deleted.
    # less_confident: Practices with similar names and addresses, but more than 100m apart. These are NOT automatically deleted.
    # disabled: A list of the IDs of practices which were disabled.
    matches = {'very_confident': [], 'quite_confident': [],
               'less_confident': [], 'disabled': []}

    if name_search:
        # # Find practices with identical names but weird newline stuff
        for practice in all_queryset:
            escaped_name = practice['name'].replace(
                "(", "\(").replace(")", "\)")
            name_identical = models.Practice.objects.filter(disabled=False, name__iregex=r'^[\s]*%s[\s]*$' % (
                escaped_name)).values('id', 'name', 'address', 'updated_at').order_by('-updated_at')

            if len(name_identical) > 1:
                very_confident = []

                for thing in name_identical:
                    match_obj = {
                        'id': thing['id'],
                        'name': thing['name'],
                        'address': thing['address'],
                        'updated_at': thing['updated_at']
                    }

                    very_confident.append(match_obj)

                matches['very_confident'].append(very_confident)

        # Delete the older ones
        matches['disabled'] += clean_delete(matches['very_confident'], dry_run)

        # Get again so we don't disable ones we just disabled
        all_queryset = models.Practice.objects.filter(disabled=False).values()

    if location_search:
        # Find practices on top of each other
        for practice in all_queryset:

            physically_close = models.Practice.objects.filter(disabled=False, location__distance_lte=(
                practice['location'], D(m=10))).values('id', 'name', 'address', 'updated_at').order_by('-updated_at')

            if len(physically_close) > 1:
                physical_duplicates = []
                for thing in physically_close:
                    if thing['name'] not in whitelist:
                        physical_duplicates.append(
                            {
                                'id': thing['id'],
                                'name': thing['name'],
                                'address': thing['address'],
                                'updated_at': thing['updated_at']
                            }
                        )
                if len(physical_duplicates):
                    matches['very_confident'].append(physical_duplicates)

        # Delete the very confident ones
        matches['disabled'] += clean_delete(matches['very_confident'], dry_run)

        # Get again so we don't disable ones we just disabled
        all_queryset = models.Practice.objects.filter(disabled=False).values()

    if smart_search:
        # Find practices which have similar names, similar addresses, and similar locations
        for practice in all_queryset:

            fuzzy_name = practice['name'].rsplit(
                sep=" ", maxsplit=2)[0].lower()
            address_split = practice['address'].split(" ")
            fuzzy_address = " ".join(address_split[0:2]).lower()

            # Address starts with something more generic, move to the next piece
            if "po box" in fuzzy_address or "level" in fuzzy_address or "unit" in fuzzy_address or "shop" in fuzzy_address or "gate" in fuzzy_address:
                fuzzy_address = " ".join(address_split[2:5]).lower()

            name_close = models.Practice.objects.filter(Q(disabled=False) & Q(name__icontains=fuzzy_name) & Q(address__icontains=fuzzy_address)).annotate(
                distance=Distance('location', practice['location'])).values('id', 'name', 'address', 'updated_at', 'distance').order_by('-updated_at')

            if len(name_close) > 1:
                quite_confident = []
                less_confident = []

                for thing in name_close:
                    if thing['name'] not in whitelist:
                        match_obj = {
                            'id': thing['id'],
                            'name': thing['name'],
                            'address': thing['address'],
                            'distance': str(thing['distance']),
                            'updated_at': thing['updated_at'],
                            'search_params': [fuzzy_name, fuzzy_address],
                        }

                        if thing['distance'].m < 200:
                            quite_confident.append(match_obj)
                        else:
                            if len(less_confident) == 0:
                                less_confident.append(
                                    {'id': practice['id'], 'name': practice['name'], 'address': practice['address'], 'updated_at': practice['updated_at']})
                            less_confident.append(match_obj)

                if len(less_confident) > 1:
                    matches['less_confident'].append(less_confident)

                if len(quite_confident) > 1:
                    matches['quite_confident'].append(quite_confident)

        # Delete the quite confident ones
        matches['disabled'] += clean_delete(
            matches['quite_confident'], dry_run)

        # Get again so we don't disable ones we just disabled
        all_queryset = models.Practice.objects.filter(disabled=False).values()

    if dumb_search:
        # Find practices with just similar names
        for practice in all_queryset:
            name_close = models.Practice.objects.filter(disabled=False, name__icontains=practice['name']).annotate(
                distance=Distance('location', practice['location'])).values('id', 'name', 'address', 'updated_at', 'distance').order_by('-updated_at')

            if len(name_close) > 1:
                less_confident = []

                for thing in name_close:
                    match_obj = {
                        'id': thing['id'],
                        'name': thing['name'],
                        'address': thing['address'],
                        'distance': str(thing['distance']),
                        'updated_at': thing['updated_at'],
                        'search_params': [practice['name']],
                    }

                    less_confident.append(match_obj)

                matches['less_confident'].append(less_confident)

    # Find practices where the <14 price is greater than 0
    if price_search:
        sus_prices = models.Prices.objects.filter(
            to_age__lte=14,
            from_age=0,
            price__gt=0,
            practice__disabled=False
        ).values('id', 'practice__name')

        very_confident = []

        for thing in sus_prices:
            very_confident.append({
                'id': thing['id'],
                'name': thing['practice__name'],
            })
        
        matches['very_confident'].append(very_confident)

    return JsonResponse(matches, status=200, safe=False)

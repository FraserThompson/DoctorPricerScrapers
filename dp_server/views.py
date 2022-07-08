from datetime import date
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

from dp_server.celery import app

from dp_server import tasks

from scrapers import run

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from django.contrib.auth.models import User, Group
from django.db.models import Avg, Max, Min, Q

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from dp_server import serializers
from django.core import serializers as core_serializers
from dp_server import models

import logging
import json
from django.db.models.base import ObjectDoesNotExist

from collections import defaultdict

from django_celery_results.models import TaskResult

logger = logging.getLogger(__name__)

######################################################
# Django REST Framework views
######################################################


class PhoViewSet(viewsets.ModelViewSet):
    queryset = models.Pho.objects.all().order_by('name')
    serializer_class = serializers.PhoSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class PricesViewSet(viewsets.ModelViewSet):
    queryset = models.Prices.objects.all()
    serializer_class = serializers.PricesSerializer

    def get_queryset(self):
        queryset = models.Prices.objects.all()

        name = self.request.query_params.get('name', None)

        if name is not None:
            queryset = queryset.filter(practice__name=name)

        return queryset


####################################################
# Returns some practices
# Params:
#         name will return a specific practice
#         pho will return all practices from a pho
#         lat=x,lng=x will return practices within 60,000km of that coordinate.
#         distance=x will override the default 60,000km distance setting.
#         if age is specified it will also calculate prices.
#         all_prices=true will return the price set for each practice (expensive)
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

        return queryset


class LogsViewSet(viewsets.ModelViewSet):
    queryset = models.Logs.objects.all()
    serializer_class = serializers.LogsSerializer

    def get_queryset(self):
        queryset = models.Logs.objects.all()
        source = self.request.query_params.get('source', None)

        if source is not None:
            queryset = queryset.filter(source__module=source).order_by('-id')

        return queryset

######################################################
# Normal views
######################################################

####################################################
# Returns the history of price changes for overall averages
@csrf_exempt
@api_view(['GET'])
#@cache_page(60 * 60 * 24 * 14) # 2 week caching because this rarely changes
def price_history(request):

    response = {}

    queryset = models.Prices.history.filter(Q(csc=False) | Q(csc=None)).order_by('history_date').values()

    averages = {}

    for thing in queryset:

        date_string = thing['history_date'].strftime("%Y-%m")
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

####################################################
# Returns the history of price changes for a particular practice or PHO
@csrf_exempt
@api_view(['GET'])
#@cache_page(60 * 60 * 24 * 14) # 2 week caching because this rarely changes
def model_price_history(request, type=None):

    name = request.GET.get('name', None)

    averages = {}

    match type:
        case "pho":
            queryset = models.Pho.history.filter(module=name).order_by('history_date').values('average_prices', 'history_date')

            for thing in queryset:
                date_string = thing['history_date'].strftime("%Y-%m")

                if date_string not in averages:
                    averages[date_string] = {}

                for thing in thing['average_prices']:

                    age = thing['age'] if thing['age'] != 13 else 14

                    if age not in averages[date_string]:
                        averages[date_string][age] = {'price': 0}

                    averages[date_string][age]['price'] = thing['average']

    return JsonResponse(averages, status=200, safe=False)

####################################################
# Gets averages for a pho
@csrf_exempt
@api_view(['GET'])
#@cache_page(60 * 60 * 24 * 14)
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

####################################################
# Gets averages for all practices
@csrf_exempt
@api_view(['GET'])
#@cache_page(60 * 60 * 24 * 14)
def averages(request):

    ages = [0, 6, 14, 18, 25, 45, 65]
    response = []

    for age in ages:
        queryset = models.Prices.objects.filter(
            to_age__gte=age, from_age__lte=age, price__lt=999, csc=False)

        queryset = queryset.aggregate(Avg('price'), Max(
            'price'), Min('price'), Max('from_age'))
        response.append(queryset)

    return JsonResponse(response, status=200, safe=False)


####################################################
# Runs a scraper
# Expects a 'module' param specifying what to run
@csrf_exempt
@api_view(['POST'])
def scrape(request):

    if request.user.is_authenticated:

        data = request.body.decode('utf-8')
        json_body = json.loads(data)

        pho = models.Pho.objects.get(module=json_body['module'])

        if pho.current_task_id:
            return HttpResponseBadRequest("We're already scraping: " + pho.current_task_id)

        task = tasks.scrape.delay(json_body['module'])

        return JsonResponse({'task_id': task.task_id}, status=200)

    else:
        return HttpResponseBadRequest("You're not cool enough to do that.")

####################################################
# Submits to database
# Expects a 'module' param, optional 'data' param or it will submit last_scrape for the PHO
@csrf_exempt
@api_view(['POST'])
def submit(request):
    if request.user.is_authenticated:

        data = request.body.decode('utf-8')
        json_body = json.loads(data)

        task = tasks.submit.delay(
            json_body['module'], json_body['data'] if 'data' in json_body else None)

        return JsonResponse({'task_id': task.task_id}, status=200)

    else:
        return HttpResponseBadRequest("You're not cool enough to do that.")


####################################################
# GETs the status of a task or DELETES one
# Expects 'task_id' param, to DELETE it also needs 'module'
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
        if request.user.is_authenticated:

            app.control.terminate(data['task_id'])

            pho = models.Pho.objects.get(module=data['module'])
            pho.current_task_id = None
            pho.save()

            return HttpResponse('Killed it')

    return HttpResponseBadRequest("You're not cool enough to do that.")

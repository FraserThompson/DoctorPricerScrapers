from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from dp_server.celery import app

from dp_server import tasks

from scrapers import run # someday we'll seperate these scrapers from the server

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from django.contrib.auth.models import User, Group

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from dp_server import serializers
from django.core import serializers as core_serializers
from dp_server import models

import logging, json
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
# Params: Lat (latitude), lng (longitude) will return practices within 60km or distance if that's specified
#         name will return a specific practice
#         pho will return all practices from a pho
#         if age is specified it will also calculate prices.
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
        distance = self.request.query_params.get('distance', '60000')

        # Specific practice
        if name is not None:
            queryset = queryset.filter(name=name)

        # All pho's practices
        if pho is not None:
            queryset = queryset.filter(pho=pho)

        # Location lookup
        if lat is not None and lng is not None:
            pnt = Point(float(lng), float(lat))
            queryset = queryset.filter(location__dwithin=(pnt, distance)).annotate(distance=Distance('location', pnt)).order_by('distance')

        # Prices
        if age is not None:
            for practice in queryset:
                practice.price = practice.price(age=age)
            
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

# Returns the history of price changes for a particular practice OR averages for a PHO.
def price_history(request):

    practice = request.GET.get('practice', None)
    pho = request.GET.get('pho', None)
    response = {}

    if practice is not None:
        queryset = models.Prices.history.filter(practice__name=practice).order_by('-history_date')
        response = core_serializers.serialize('json', list(queryset), fields=('price','from_age','to_age', 'history_date', 'history_id'))
    elif pho is not None:
        queryset = models.Pho.history.filter(name=pho).order_by('-history_date')
        response = core_serializers.serialize('json', list(queryset), fields=('average_prices', 'history_date', 'history_id'))

    return HttpResponse(response, content_type="application/json")

####################################################
# Runs a scraper
# Expects a 'module' param specifying what to run
@csrf_exempt
@api_view(['POST'])
def scrape(request):

    if request.user.is_authenticated():

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
    if request.user.is_authenticated():

        data = request.body.decode('utf-8')
        json_body = json.loads(data)

        task = tasks.submit.delay(json_body['module'], json_body['data'] if 'data' in json_body else None)

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
        if request.user.is_authenticated():

            app.control.terminate(data['task_id'])

            pho = models.Pho.objects.get(module=data['module'])
            pho.current_task_id = None
            pho.save()

            return HttpResponse('Killed it')
    
    return HttpResponseBadRequest("You're not cool enough to do that.")

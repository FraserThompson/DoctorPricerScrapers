from django.http import HttpResponse
from django.shortcuts import render
from scrapers import run
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User, Group
from rest_framework import viewsets

from scrapers_ui import serializers
from scrapers_ui import models

import logging, json

# Get an instance of a logger
logger = logging.getLogger(__name__)

class PhoViewSet(viewsets.ModelViewSet):
    queryset = models.Pho.objects.all()
    serializer_class = serializers.PhoSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

class PracticeViewSet(viewsets.ModelViewSet):
    queryset = models.Practice.objects.all()
    serializer_class = serializers.PracticeSerializer

    def get_queryset(self):
        queryset = models.Practice.objects.all()
        name = self.request.query_params.get('name', None)

        if scraper is not None:
            queryset = queryset.filter(source__module=scraper)

        return queryset

class LogsViewSet(viewsets.ModelViewSet):
    queryset = models.Logs.objects.all()
    serializer_class = serializers.LogsSerializer

    def get_queryset(self):
        queryset = models.Logs.objects.all()
        scraper = self.request.query_params.get('scraper', None)

        if scraper is not None:
            queryset = queryset.filter(source__module=scraper)

        return queryset

def index(request):
    context = {}
    return render(request, 'home/index.html', context)


@csrf_exempt
def start(request):
    if request.method == "POST":

        return_code = 200
        data = request.body.decode('utf-8')
        json_body = json.loads(data)

        response = run.one(json_body['module'])

        if response['error']:
            return_code = 400
        else:

            pho = models.Pho.objects.get(module=json_body['module'])
            pho.number_of_practices = len(response['data']['scraped']) 
            pho.save()

            log = models.Logs(source_id=pho, scraped=response['data']['scraped'], errors=response['data']['errors'], warnings=response['data']['warnings'])
            log.save()

        return HttpResponse(json.dumps(response), content_type="application/json", status=return_code)
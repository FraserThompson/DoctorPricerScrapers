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
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Pho.objects.all()
    serializer_class = serializers.PhoSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

class LogsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = models.Logs.objects.all()
    serializer_class = serializers.LogsSerializer


def index(request):
    context = {}
    return render(request, 'home/index.html', context)

@csrf_exempt
def start(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        json_body = json.loads(data)
        response = run.one(json_body['module'])
        return HttpResponse(json.dumps(response), content_type="application/json")
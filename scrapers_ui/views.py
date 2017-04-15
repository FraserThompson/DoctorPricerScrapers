from django.http import HttpResponse
from django.shortcuts import render
from scrapers import run
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    context = {}
    return render(request, 'home/index.html', context)

def start(request):
    name = request.GET.get('name', '')
    run.one(name)

    return HttpResponse(json.dumps({'name': name}), content_type="application/json")
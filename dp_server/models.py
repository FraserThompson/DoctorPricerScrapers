import json
from django.db import models
from django.core import serializers
from django.db.models import Avg, Max, Min, Q, Count
from django.db.models import JSONField
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from django.conf import settings
from django.utils.functional import cached_property
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Region(models.Model):
    name = models.CharField(unique=True, max_length=30, db_index=True)
    geo = models.PolygonField(srid=4326, geography=True, verbose_name="bounding box", null=True, blank=True)

    @property
    def geojson(self):
        return self.geo.geojson

    @cached_property
    def phos(self):
        practices = self.practices
        phos = []
        for practice in practices:
            if practice.pho_link.id not in phos:
                phos.append(practice.pho_link.id)
        return phos

    @cached_property
    def practices(self):
        return Practice.objects.filter(disabled=False, location__intersects=self.geo)

    @cached_property
    def price_history(self):
        queryset = Prices.history.filter(Q(csc=False) | Q(csc=None), practice__in=self.practices).order_by('history_date').values()
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

        return json.dumps(averages)

    @cached_property
    def averages(self):
        ages = [0, 6, 14, 18, 25, 45, 65]
        response = []

        practices = self.practices

        for age in ages:
            queryset = Prices.objects.filter(practice__in=practices, to_age__gte=age, from_age__lte=age, price__lt=999, csc=False)
            queryset = queryset.aggregate(Avg('price'), Max('price'), Min('price'), Max('from_age'))
            response.append(queryset)
        
        return response

    @cached_property
    def number_of_practices(self):
        return self.practices.count()

    @cached_property
    def number_enrolling(self):
        return Practice.objects.filter(disabled=False, active=True, location__intersects=self.geo).count()

    @cached_property
    def number_notenrolling(self):
        return Practice.objects.filter(disabled=False, active=False, location__intersects=self.geo).count()

    def __str__(self):
        return str(self.name)

class Pho(models.Model):
    name = models.CharField(unique=True, max_length=30, db_index=True)
    module = models.CharField(max_length=30, null=True, blank=True)
    website = models.TextField(blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, blank=True, null=True)
    last_run = models.DateTimeField(auto_now=True)
    current_task_id = models.TextField(blank=True, null=True, default=None)
    average_prices = JSONField(blank=True, null=True, default=dict)
    last_scrape = JSONField(blank=True, null=True, default=list)
    scraper_source = models.TextField(blank=True, null=True)
    history = HistoricalRecords()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def number_of_practices(self):
        return Practice.objects.filter(pho_link=self, disabled=False).count()

    @property
    def number_enrolling(self):
        return Practice.objects.filter(pho_link=self, disabled=False, active=True).count()

    @property
    def number_notenrolling(self):
        return Practice.objects.filter(pho_link=self, disabled=False, active=False).count()
        
    def __str__(self):
        return str(self.name)

class Logs(models.Model):
    source = models.ForeignKey(Pho, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    changes = JSONField(default=dict)
    scraped = JSONField(default=dict)
    errors = JSONField(default=dict)
    warnings = JSONField(default=dict)

    @property
    def module(self):
        return self.source.module

    def __str__(self):
        return str(self.scraped)

class Practice(models.Model):
    name = models.TextField(unique=True, db_index=True)
    address = models.TextField()
    pho_link = models.ForeignKey(Pho, on_delete=models.CASCADE, blank=True, null=True)
    phone = models.TextField(blank=True)
    url = models.TextField()
    location = models.PointField(srid=4326, geography=True, db_index=True)
    restriction = models.TextField(default='', blank=True, null=True)
    place_id = models.TextField(default='', blank=True)
    active = models.BooleanField(default=True)
    disabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def pho(self):
        return str(self.pho_link.name) if self.pho_link else 'None'

    @property
    def lat(self):
        return self.location.y

    @property
    def lng(self):
        return self.location.x

    def __getPrice(self, age=0, csc=False):
        prices = self.prices_set.filter(to_age__gte=age, from_age__lte=age, csc=csc).first()
        if prices:
            return prices.price
        else:
            return None

    def price(self, age=0, csc=False):
        price = None

        # If there's no age we're outta here
        if not age:
            return 1000
        
        price = self.__getPrice(age, csc)

        # If there was no CSC price, try get a normal price
        if csc and price is None:
            price = self.__getPrice(age, False)

        return price if price is not None else 1000

    def distance(self):
        return -1

    def all_prices(self, do=False, csc=False):

        return_obj = []

        if do:
            raw_prices =  serializers.serialize('python', self.prices_set.filter(csc=csc).order_by('from_age'), fields=('price','from_age'))

            if raw_prices:
                return_obj = [d['fields'] for d in raw_prices]
        
        return return_obj

    def __str__(self):
        return str(self.name)

class Prices(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    from_age = models.IntegerField()
    to_age = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    csc = models.BooleanField(default=False, blank=True, null=True)
    history = HistoricalRecords()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def disabled(self):
        return self.practice.disabled

    @property
    def pho(self):
        return self.practice.pho_link.name

    def __str__(self):
        return str(self.practice.name)
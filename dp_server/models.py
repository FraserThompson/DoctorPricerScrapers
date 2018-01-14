from django.db import models
from django.core import serializers
from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Pho(models.Model):
    name = models.CharField(unique=True, max_length=30)
    module = models.CharField(max_length=30, null=True, blank=True)
    website = models.TextField(blank=True, null=True)
    region = models.TextField(blank=True)
    last_run = models.DateTimeField(auto_now=True)
    current_task_id = models.TextField(blank=True, null=True, default=None)
    number_of_practices = models.IntegerField(default=0)
    average_prices = JSONField(default={"0":0})
    last_scrape = JSONField(blank=True, default=[])
    history = HistoricalRecords()

    def __str__(self):
        return str(self.name)

class Logs(models.Model):
    source = models.ForeignKey(Pho, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    changes = JSONField(default={})
    scraped = JSONField(default={})
    errors = JSONField(default={})
    warnings = JSONField(default={})

    def module(self):
        return self.source.module

    def __str__(self):
        return str(self.scraped)

class Practice(models.Model):
    name = models.TextField(unique=True)
    address = models.TextField()
    pho_link = models.ForeignKey(Pho, on_delete=models.CASCADE, blank=True, null=True)
    phone = models.TextField(blank=True)
    url = models.TextField()
    location = models.PointField(srid=4326, geography=True)
    restriction = models.TextField(default='')
    place_id = models.TextField(default='', blank=True)
    active = models.BooleanField(default=True)

    def pho(self):
        return str(self.pho_link.name) if self.pho_link else 'None'

    def lat(self):
        return self.location.y

    def lng(self):
        return self.location.x

    def price(self, age=0):
        return_obj = 1000

        if age:
            prices = self.prices_set.filter(to_age__gte=age, from_age__lte=age).first()

            if prices:
                return_obj = prices.price

        return return_obj

    def distance(self):
        return -1

    def all_prices(self, do=False):

        return_obj = []

        if do:
            raw_prices =  serializers.serialize('python', self.prices_set.all().order_by('from_age'), fields=('price','from_age'))

            if raw_prices:
                return_obj = [d['fields'] for d in raw_prices]
        
        return return_obj

    def __str__(self):
        return str(self.name)

class Prices(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    pho = models.ForeignKey(Pho, on_delete=models.CASCADE)
    from_age = models.IntegerField()
    to_age = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.practice.name)
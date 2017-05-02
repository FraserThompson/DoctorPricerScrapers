from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords

class Pho(models.Model):
    name = models.CharField(unique=True, max_length=30)
    module = models.CharField(unique=True,max_length=30)
    region = models.TextField(blank=True)
    last_run = models.DateTimeField(auto_now=True)
    number_of_practices = models.IntegerField(default=0)
    average_prices = JSONField(default={"0":0})
    last_scrape = JSONField(default=[])
    history = HistoricalRecords()

    def __str__(self):
        return self.name

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
        return self.scraped

class Practice(models.Model):
    name = models.TextField(unique=True)
    address = models.TextField()
    pho = models.TextField()
    phone = models.TextField(blank=True)
    url = models.TextField()
    location = models.PointField(srid=4326)
    restriction = models.TextField(default='')
    place_id = models.TextField(default='', blank=True)

    def lat(self):
        return self.location.y

    def lng(self):
        return self.location.x

    def price(self, age=0):
        if age:
            return self.prices_set.filter(to_age__gte=age, from_age__lte=age).first().price
        else:
            return -1

    def __str__(self):
        return self.name

class Prices(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    pho = models.ForeignKey(Pho, on_delete=models.CASCADE)
    from_age = models.IntegerField()
    to_age = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.practice.name)
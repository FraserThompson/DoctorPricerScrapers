from django.db import models
from django.contrib.postgres.fields import JSONField

class Pho(models.Model):
    name = models.CharField(max_length=30)
    module = models.CharField(max_length=30, primary_key=True)
    last_run = models.DateTimeField(auto_now=True)
    number_of_practices = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Logs(models.Model):
    source = models.ForeignKey(Pho, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    scraped = models.TextField()
    errors = models.TextField()
    warnings = models.TextField()

    def __str__(self):
        return self.scraped

class Practice(models.Model):
    name = models.TextField()
    address = models.TextField()
    pho = models.TextField()
    phone = models.TextField()
    url = models.TextField()
    prices = JSONField()
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    restriction = models.TextField()
    place_id = models.TextField()

    def __str__(self):
        return self.name
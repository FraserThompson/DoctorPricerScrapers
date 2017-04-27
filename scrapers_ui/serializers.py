from scrapers_ui import models
from django.contrib.auth.models import User, Group
from rest_framework import serializers

class PhoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Pho
        fields = ('name', 'module', 'last_run', 'number_of_practices', 'average_prices')

class LogsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Logs
        fields = ('module', 'date', 'changes', 'scraped', 'errors', 'warnings', 'id')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')

class PricesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Prices
        fields = ('practice', 'pho', 'from_age', 'to_age', 'price')

class PracticeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Practice
        fields = ('name', 'address', 'pho', 'phone', 'url', 'lat', 'lng', 'restriction', 'place_id', 'price')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('__all__')
from scrapers_ui import models
from django.contrib.auth.models import User, Group
from rest_framework import serializers

class PhoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Pho
        fields = ('id', 'name', 'module', 'last_run', 'number_of_practices', 'average_prices')

class LogsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Logs
        fields = ('id', 'source', 'scraped', 'date', 'warnings', 'errors', 'changes')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class PricesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Prices
        fields = ('id', 'practice', 'pho', 'from_age', 'to_age', 'price')

class PracticeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Practice
        fields = ('id', 'name', 'address', 'pho', 'phone', 'url', 'location', 'restriction', 'place_id', 'price')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
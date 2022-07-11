from dp_server import models
from django.contrib.auth.models import User, Group
from rest_framework import serializers

class PhoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Pho
        fields = ('name', 'module', 'last_run', 'last_scrape', 'current_task_id', 'number_of_practices', 'average_prices', 'website')

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

class DistanceField(serializers.Field):

    def to_representation(self, obj):
        if obj != -1:
            return obj.m
        else:
            return obj

class PracticeSerializer(serializers.HyperlinkedModelSerializer):
    distance = DistanceField()

    class Meta:
        model = models.Practice
        fields = ('name', 'address', 'pho', 'phone', 'url', 'lat', 'lng', 'restriction', 'place_id', 'price', 'distance', 'all_prices', 'active', 'created_at', 'updated_at')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('__all__')
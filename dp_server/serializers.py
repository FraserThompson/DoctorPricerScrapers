from dp_server import models
from django.contrib.auth.models import User, Group
from rest_framework import serializers

class PhoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Pho
        fields = (
            'id',
            'name',
            'module',
            'last_run',
            'last_scrape',
            'current_task_id',
            'region',
            'number_of_practices',
            'number_enrolling',
            'number_notenrolling',
            'average_prices',
            'website'
        )

class LogsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Logs
        fields = ('module', 'date', 'changes', 'scraped', 'errors', 'warnings', 'id')

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
        fields = (
            'id',
            'name',
            'address',
            'pho',
            'phone',
            'url',
            'lat',
            'lng',
            'restriction',
            'place_id',
            'price',
            'distance',
            'all_prices',
            'active',
            'created_at',
            'updated_at'
        )

class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Region
        fields = (
            'id',
            'name',
            'number_of_practices',
            'number_enrolling',
            'number_notenrolling',
            'averages',
            'price_history',
            'geojson'
        )

class RegionWithPracticesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Region
        fields = (
            'id',
            'name',
            'number_of_practices',
            'number_enrolling',
            'number_notenrolling',
            'averages',
            'price_history',
            'practices',
            'phos',
            'geojson'
        )

    practices = PracticeSerializer(many=True, read_only=True)

class SortedPracticeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)
    distance = serializers.IntegerField()
    practices = PracticeSerializer(many=True, read_only=True)
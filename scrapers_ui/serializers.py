from scrapers_ui import models
from django.contrib.auth.models import User, Group
from rest_framework import serializers

class PhoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Pho
        fields = ('name', 'module', 'last_run', 'number_of_practices')

class LogsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Logs
        fields = ('source', 'scraped', 'date', 'warnings', 'errors')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class PracticeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Practice
        fields = ('name', 'address', 'pho', 'phone', 'url', 'prices', 'lat', 'lng', 'restriction', 'place_id')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
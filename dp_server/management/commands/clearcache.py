from django.core.management.base import BaseCommand, CommandError
from dp_server import models
from django.core.cache import cache

class Command(BaseCommand):
    def handle(self, *args, **options):
        del models.Region.price_history
        del models.Region.averages
        del models.Region.number_of_practices
        del models.Region.number_enrolling
        del models.Region.number_notenrolling
        del models.Region.practices
        del models.Region.phos
        del models.Pho.number_of_practices
        del models.Pho.number_enrolling
        del models.Pho.number_notenrolling
        cache.clear()
        print("Cleared caches.")
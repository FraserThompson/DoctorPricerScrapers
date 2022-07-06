from django.contrib import admin
from dp_server import models

admin.site.register(models.Logs)

@admin.register(models.Practice)
class PracticeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address')

@admin.register(models.Pho)
class PhoAdmin(admin.ModelAdmin):
    search_fields = ('name', 'module')

@admin.register(models.Prices)
class PricesAdmin(admin.ModelAdmin):
    search_fields = ('practice__name')

@admin.register(models.Region)
class PricesAdmin(admin.ModelAdmin):
    search_fields = ('name')
from django.contrib import admin
from dp_server import models

admin.site.register(models.Practice)
admin.site.register(models.Prices)
admin.site.register(models.Logs)
admin.site.register(models.Pho)

class PracticeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address')

class PhoAdmin(admin.ModelAdmin):
    search_fields = ('name', 'region', 'module', )
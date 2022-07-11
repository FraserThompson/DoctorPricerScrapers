from django.contrib import admin
from dp_server import models

admin.site.register(models.Logs)

@admin.register(models.Practice)
class PracticeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address', 'pho_link__name')
    list_display = ('name', 'pho_link', 'updated_at', 'disabled')
    list_filter = ('disabled', 'active', 'pho_link__name')

@admin.register(models.Pho)
class PhoAdmin(admin.ModelAdmin):
    search_fields = ('name', 'module',)
    list_display = ('name', 'module',)

@admin.register(models.Prices)
class PricesAdmin(admin.ModelAdmin):
    search_fields = ('practice__name', 'pho__name')
    list_display = ('practice', 'pho', 'from_age', 'to_age', 'price', 'csc')
    history_list_display = ('price',)
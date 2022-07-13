from django.contrib import admin
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos import Point
from dp_server import models
from django import forms

admin.site.register(models.Logs)

class LatLongWidget(forms.MultiWidget):
    """
    A Widget that splits Point input into latitude/longitude text inputs.
    """

    def __init__(self, attrs=None, date_format=None, time_format=None):
        widgets = (forms.TextInput(attrs=attrs),
                   forms.TextInput(attrs=attrs))
        super(LatLongWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return tuple(value.coords)
        return (None, None)

    def value_from_datadict(self, data, files, name):
        mylat = data[name + '_0']
        mylong = data[name + '_1']

        try:
            point = Point(float(mylat), float(mylong))
        except ValueError:
            return ''

        return point

@admin.action(description='Disable selected practices')
def disable_practices(modeladmin, request, queryset):
    queryset.update(disabled=True)

@admin.action(description='Enable selected practices')
def enable_practices(modeladmin, request, queryset):
    queryset.update(disabled=False)

@admin.register(models.Practice)
class PracticeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address')
    list_display = ('name', 'pho_link', 'updated_at', 'disabled')
    list_filter = ('disabled', 'active', 'pho_link__name')
    actions = [disable_practices, enable_practices]
    formfield_overrides = {
        geomodels.PointField: {'widget': LatLongWidget},
    }

@admin.register(models.Pho)
class PhoAdmin(admin.ModelAdmin):
    search_fields = ('name', 'module',)
    list_display = ('name', 'module',)

@admin.register(models.Prices)
class PricesAdmin(admin.ModelAdmin):
    search_fields = ('practice__name',)
    list_display = ('practice', 'pho', 'from_age', 'to_age', 'price', 'csc', 'disabled')
    list_filter = ('practice__disabled', 'practice__pho_link',)
    history_list_display = ('price')

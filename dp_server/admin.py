from django.contrib import admin
from django.contrib.gis.db import models as geomodels
from dp_server import models
from leaflet.forms.widgets import LeafletWidget

admin.site.register(models.Logs)

# The widget should bring this stuff in itself... But it doesn't, so we do it manually
leaflet_js = (
    '/assets/leaflet/leaflet.js', 
    '/assets/leaflet/draw/leaflet.draw.js',
    '/assets/leaflet/leaflet.extras.js',
    '/assets/leaflet/leaflet.forms.js'
    )

leaflet_css = {'all': ('/assets/leaflet/leaflet.css', '/assets/leaflet/draw/leaflet.draw.css')}

LEAFLET_WIDGET_ATTRS = {
    'map_height': '500px',
    'map_width': '100%',
    'display_raw': 'true',
    'map_srid': 4326,
}

LEAFLET_FIELD_OPTIONS = {'widget': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}

FORMFIELD_OVERRIDES = {
    geomodels.PointField: LEAFLET_FIELD_OPTIONS,
    geomodels.MultiPointField: LEAFLET_FIELD_OPTIONS,
    geomodels.LineStringField: LEAFLET_FIELD_OPTIONS,
    geomodels.MultiLineStringField: LEAFLET_FIELD_OPTIONS,
    geomodels.PolygonField: LEAFLET_FIELD_OPTIONS,
    geomodels.MultiPolygonField: LEAFLET_FIELD_OPTIONS,
}

@admin.action(description='Disable selected practices')
def disable_practices(modeladmin, request, queryset):
    queryset.update(disabled=True)

@admin.action(description='Enable selected practices')
def enable_practices(modeladmin, request, queryset):
    queryset.update(disabled=False)

@admin.register(models.Practice)
class PracticeAdmin(admin.ModelAdmin):
    class Media:
        js = leaflet_js
        css = leaflet_css

    search_fields = ('name', 'address')
    list_display = ('name', 'pho_link', 'updated_at', 'disabled')
    list_filter = ('disabled', 'active', 'pho_link__name')
    actions = [disable_practices, enable_practices]
    formfield_overrides = FORMFIELD_OVERRIDES

@admin.register(models.Pho)
class PhoAdmin(admin.ModelAdmin):
    search_fields = ('name', 'module',)
    list_display = ('name', 'module', 'region')
    list_filter = ('region',)

@admin.register(models.Prices)
class PricesAdmin(admin.ModelAdmin):
    search_fields = ('practice__name',)
    list_display = ('practice', 'pho', 'from_age', 'to_age', 'price', 'csc', 'disabled')
    list_filter = ('practice__disabled', 'practice__pho_link',)
    history_list_display = ('price')

@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    class Media:
        js = leaflet_js
        css = leaflet_css

    search_fields = ('name',)
    list_display = ('name',)
    formfield_overrides = FORMFIELD_OVERRIDES
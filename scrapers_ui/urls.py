from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'pho', views.PhoViewSet)
router.register(r'logs', views.LogsViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'practice', views.PracticeViewSet)
router.register(r'prices', views.PricesViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^history$', views.price_history, name='history'),
    url(r'^scrape$', views.scrape, name='scrape')
]
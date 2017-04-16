from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'pho', views.PhoViewSet)
router.register(r'logs', views.LogsViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^ui$', views.index, name='index'),
    url(r'^start$', views.start, name='start')
]
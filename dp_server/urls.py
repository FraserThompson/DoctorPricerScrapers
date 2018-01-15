from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.authtoken import views as rest_views

from . import views

router = routers.DefaultRouter()
router.register(r'pho', views.PhoViewSet)
router.register(r'logs', views.LogsViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'practices', views.PracticeViewSet)
router.register(r'prices', views.PricesViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^history$', views.price_history, name='history'),
    url(r'^averages$', views.averages, name='averages'),
    url(r'^scrape$', views.scrape, name='scrape'),
    url(r'^submit$', views.submit, name='submit'),
    url(r'^task_status$', views.task_status, name='task_status'),
    url(r'^login/', rest_views.obtain_auth_token),
]
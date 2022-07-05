from django.urls import include, path
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
    path('api/', include(router.urls)),
    path('history/', views.price_history, name='history'),
    path('history/<str:type>/', views.model_price_history, name='model_history'),
    path('averages/', views.averages, name='averages'),
    path('averages/<str:type>/', views.model_averages, name='model_averages'),
    path('scrape/', views.scrape, name='scrape'),
    path('submit/', views.submit, name='submit'),
    path('task_status/', views.task_status, name='task_status'),
    path('login/', rest_views.obtain_auth_token),
]
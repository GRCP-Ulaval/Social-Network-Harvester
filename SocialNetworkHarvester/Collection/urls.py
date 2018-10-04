from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'create', create_collection),
    url(r'', collections_dashboard),
]

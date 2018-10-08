from django.conf.urls import url

from Collection.views.ajax import ajax_base
from .views import *

urlpatterns = [
    url(r'^form/(?P<form_name>[\w\.]+)$', form_base),
    url(r'^ajax/(?P<endpoint_name>[\w\.]+)$', ajax_base),
    url(r'^(?P<collection_id>\d+)$', collection_detail),
    url(r'^$', collections_dashboard),
]

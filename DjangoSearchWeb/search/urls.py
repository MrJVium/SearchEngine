from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url(r"^$", views.index),
    # path('search', views.search),
    # path('suggest', views.SearchSuggest.as_view())
]
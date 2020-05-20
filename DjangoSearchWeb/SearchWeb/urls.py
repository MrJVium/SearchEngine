"""SearchWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView
from search.views import SearchSuggest, SearchWeiBoView, IndexView, SearchNewsView, SearchRumorView, SearchAreaView, \
    SearchOverallView, SearchNewsByDayView
from django.conf.urls import include

from sentiment.views import PredictCountViews, WordCountViews, RealTimeDataView

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', IndexView.as_view(), name='index'),

    url(r'^suggest/$', SearchSuggest.as_view(), name='suggest'),
    # url(r'^backend/', include('search.urls')),
    url(r'^searchComment/$', SearchWeiBoView.as_view(), name='weibo_search'),
    url(r'^searchNews/$', SearchNewsView.as_view(), name='news_search'),
    url(r'^searchRumor/$', SearchRumorView.as_view(), name='rumor_search'),
    url(r'^searchArea/$', SearchAreaView.as_view(), name='area_search'),
    url(r'^searchOverall/$', SearchOverallView.as_view(), name='overall_search'),
    url(r'^sentimentPredict/$', PredictCountViews.as_view(), name='sentiment_predict'),
    url(r'^sentimentWordCount/$', WordCountViews.as_view(), name='sentiment_wordcount'),
    url(r'^realTimeData/$', RealTimeDataView.as_view(), name='realtimedata'),
    url(r'^newsbydate/$', SearchNewsByDayView.as_view(), name='newsbydate'),

]

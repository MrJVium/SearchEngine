from django.shortcuts import render
import json
import os
from bs4 import BeautifulSoup
import requests
import time
import re
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime

from django.views.generic.base import View
# Create your views here.

class WjwRecommend(View):
    def get(self, request):
        pass
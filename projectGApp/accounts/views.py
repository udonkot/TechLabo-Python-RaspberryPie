import asyncio

from urllib import request
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from .forms import LoginForm
from accounts.utils.ledUtils import gpioSetup, lightsOn, lightsOff, allLighting
from accounts.utils.motorUtils import roundMotor

import RPi.GPIO as GPIO

import sys
sys.path.append('/home/rpiuser/github_repo/TechLabo-Python-RaspberryPie/sampleScript')
from samplePattern import main as sampleMain

LIGHT_GROUP_ALL = [20,21,6,13,19,26,16,25]
#LIGHT_GROUP_ALL = [16,20,21]
LIGHT_GROUP_HEADS = [21]
LIGHT_GROUP_EYES = [20]
LIGHT_GROUP_SHOULDER_RIGHT_UP = [26]
LIGHT_GROUP_SHOULDER_LEFT_UP = [19]
LIGHT_GROUP_SHOULDER_RIGUT_DOWN = [16]
LIGHT_GROUP_SHOULDER_RIGUT_DOWN = [25]
LIGHT_GROUP_BODY_FRONT = [13]
LIGHT_GROUP_BODY_BACK = [6]

# 初期化
gpioSetup(LIGHT_GROUP_ALL)

class IndexView(TemplateView):
    template_name = 'index.html'
    
class LoginView(BaseLoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

class LogoutView(BaseLogoutView):
    success_url = reverse_lazy("accounts:index")

# 全点灯
def LedAllLightOn(request):

    lightsOn(LIGHT_GROUP_ALL)
    # JsonResponse({'result': 'ok'})
    return render(request, 'index.html')

# 全消灯
def LedAllLightOff(request):
    lightsOff(LIGHT_GROUP_ALL)
    # JsonResponse({'result': 'ok'})
    return render(request, 'index.html')

# 初期化
def LedInit(request):
    gpioSetup(LIGHT_GROUP_ALL)
    # JsonResponse({'result': 'ok'})
    return render(request, 'index.html')

# 一定時間点滅
def LedAllBlink(request):
    span = float(request.POST.get('span', 3))
    count =  int(request.POST.get('count', 3))
    allLighting(LIGHT_GROUP_ALL, span, count)
    return render(request, 'index.html')

# 一定時間点滅
def LedPattern(request):
    print('start LedPattern')
    asyncio.run(sampleMain())
    print('end LedPattern')
    return render(request, 'index.html')


def RoundMotor(request):
    count = int(request.POST.get('count', 3))
    roundMotor(count)
    return render(request, 'index.html')

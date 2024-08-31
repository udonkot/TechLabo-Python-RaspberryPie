import asyncio

from urllib import request
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from .forms import LoginForm
from accounts.utils.ledUtils import gpioSetup, lightsOn, lightsOff, allLighting, randomLighting
from accounts.utils.motorUtils import roundMotor
from accounts.utils.soubdUtils import play_music

import RPi.GPIO as GPIO
import json

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

# 全点灯（非同期）
def LedAllLightOnAjax(request):

    if request.method == 'POST':
        lightsOn(LIGHT_GROUP_ALL)
        return JsonResponse({'status': 'success', 'message': 'LED全点滅が実行されました'})
    return JsonResponse({'status': 'error', 'message': '無効なリクエスト'})    


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

def RandomLighting(request):
    print('start randomLighting')
    span = float(request.POST.get('span', 3))
    count =  int(request.POST.get('count', 3))
    randomLighting(LIGHT_GROUP_ALL, span, count)
    # asyncio.run(randomLighting(LIGHT_GROUP_ALL, 1, 3))
    print('end randomLighting')
    return render(request, 'index.html')


# 一定時間点滅
def PlaySound(request):
    print('start Sound')
    asyncio.run(play_music('/home/rpiuser/opt/sounds/kensirou.mp3'))
    print('end LedPattern')
    return render(request, 'index.html')

@csrf_exempt
def update_switch_state(request):
    print('update_switch_state')
    print(request.POST)
    if request.method == 'POST':
        data = json.loads(request.body)
        # switch_id = data.get('switchId')
        state = data.get('state')
        gpio_no = int(data.get('gpioNo'))
        

        # state = request.POST.get('state')
        # gpioNo = request.POST.get('gpioNo')
        print(state)
        print(gpio_no)
        if state:
            lightsOn([gpio_no])
        else:
            lightsOff([gpio_no])
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

import asyncio

import time
from urllib import request
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from .forms import LoginForm
from accounts.utils.ledUtils import gpioSetup, lightsOn, lightsOff, allLighting, randomLighting
from accounts.utils.motorUtils import roundMotor, moveMotor, resetMotor
from accounts.utils.soundUtils import play_music, stop_music

import RPi.GPIO as GPIO
import json

import sys
sys.path.append('/home/rpiuser/github_repo/TechLabo-Python-RaspberryPie/sampleScript')
from samplePattern import main as sampleMain

LIGHT_GROUP_ALL = [20,21,6,13,19,26,16,25,12,23,24]
#LIGHT_GROUP_ALL = [16,20,21]
LIGHT_GROUP_FACES = [21,20,12]
LIGHT_GROUP_FACE_HEAD = [21]
LIGHT_GROUP_FACE_EYES = [20]
LIGHT_GROUP_FACE_VALUCAN = [12]
LIGHT_GROUP_SHOULDERS = [26, 19, 16, 25]
LIGHT_GROUP_SHOULDER_RIGHT_UP = [26]
LIGHT_GROUP_SHOULDER_LEFT_UP = [19]
LIGHT_GROUP_SHOULDER_RIGHT_DOWN = [16]
LIGHT_GROUP_SHOULDER_LEFT_DOWN = [25]
LIGHT_GROUP_BODY_FRONT = [13]
LIGHT_GROUP_BODY_BACK = [6]
LIGHT_GROUP_BODY_WAIST = [24]
LIGHT_GROUP_LEG_THIGHS = [23]

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
    funcName = 'LedAllLightOn'

    lightsOn(LIGHT_GROUP_ALL)
    # JsonResponse({'result': 'ok'})
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})

# 全点灯（非同期）
def LedAllLightOnAjax(request):

    if request.method == 'POST':
        lightsOn(LIGHT_GROUP_ALL)
        ret = createJsonResponse(True, '')
    else:
        ret = createJsonResponse(False, '無効なリクエスト')
    return ret

# JSONレスポンスを生成する
def createJsonResponse(result, messae):
    if result:
        return JsonResponse({'status': 'success', 'message': messae})
    else:
        return JsonResponse({'status': 'error', 'message': messae})

# 全消灯
def LedAllLightOff(request):
    funcName = 'LedAllLightOff'

    lightsOff(LIGHT_GROUP_ALL)
    # JsonResponse({'result': 'ok'})
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})

# 初期化
def LedInit(request):
    funcName = 'LedInit'

    gpioSetup(LIGHT_GROUP_ALL)
    # JsonResponse({'result': 'ok'})
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})

# 一定時間点滅
def LedAllBlink(request):
    funcName = 'LedAllBlink'

    data = json.loads(request.body)
    
    span = float(data.get('val01', 3))
    count = int(data.get('val02', 1))
    # span = float(request.POST.get('span', 3))
    # count =  int(request.POST.get('count', 3))
    # print(str(span) + ' / ' + str(count))

    allLighting(LIGHT_GROUP_ALL, span, count)

    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})

# 一定時間点滅
def LedPattern(request):
    funcName = 'LedPattern'

    print('start LedPattern')
    asyncio.run(sampleMain())
    print('end LedPattern')
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})


def RoundMotor(request):
    funcName = 'RoundMotor'

    count = int(request.POST.get('count', 3))
    roundMotor(count)
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})

def MoveMotor(request):
    funcName = 'MoveMotor'

    data = json.loads(request.body)
    val = int(data.get('val01', 10))
    moveMotor(val)
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})

def ResetMotor(request):
    funcName = 'ResetMotor'

    # pwm = gpioSetup([18])
    resetMotor()
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})


def RandomLighting(request):
    funcName = 'RandomLighting'

    print('start randomLighting')
    span = float(request.POST.get('span', 3))
    count =  int(request.POST.get('count', 3))
    randomLighting(LIGHT_GROUP_ALL, span, count)
    # asyncio.run(randomLighting(LIGHT_GROUP_ALL, 1, 3))
    print('end randomLighting')
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})


# 
async def PlaySound(request):
    funcName = 'PlaySound'

    print('start Sound')
    fileName =  request.POST.get('sound', 'kensirou.mp3')
    filePath = '/home/rpiuser/opt/sounds/projectG/' + fileName
    print(filePath)

    asyncio.run(play_music(filePath))
    print('end Sound')
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})

def StopSound(request):
    funcName = 'StopSound'

    asyncio.run(stop_music())
    # return render(request, 'index.html')
    return JsonResponse({'status': 'success', 'message': funcName})

# スイッチ操作以下は、POSTでのリクエストを受け付けるための関数
@csrf_exempt
def update_switch_state(request):
    # print('update_switch_state')
    print(request.POST)
    if request.method == 'POST':
        data = json.loads(request.body)
        # switch_id = data.get('switchId')
        state = data.get('state')
        # gpio_no = int(data.get('gpioNo'))
        gpio_no = data.get('gpioNo')

        # ,で分割してリストに変換
        gpio_no = gpio_no.split(',')
        # リストの要素をint型に変換
        gpio_no = list(map(int, gpio_no))
        print(gpio_no)
       
        # state = request.POST.get('state')
        # gpioNo = request.POST.get('gpioNo')
        print(state)
        print(gpio_no)
        if state:
            lightsOn(gpio_no)
        else:
            lightsOff(gpio_no)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

async def PlayPattern(request):
    print('start PlayPattern')
    data = json.loads(request.body)
    # switch_id = data.get('switchId')
    patternNo = data.get('val01')


    # jsonfile read
    with open('/home/rpiuser/github_repo/TechLabo-Python-RaspberryPie/projectGApp/static/conf/lightingPattern.json') as f:
        data = json.load(f)
        print('[start PlayPattern]')

        #find patternNo
        for pattern in data['patternList']:
            if int(pattern['no']) == int(patternNo):
                # pattern hit

                filePath = '/home/rpiuser/opt/sounds/projectG/' + pattern['soundFile']
                task = asyncio.create_task(play_music(filePath))

                # await asyncio.gather(
                #     play_music(filePath),
                #     print('sleep start'),
                #     asyncio.sleep(int(pattern['soundStartSec']))
                #     # ledUtils.randomLighting(LIGHT_GROUP_ALL, 0.5, 5),
                #     # time.sleep(5),
                #     # ledUtils.lightsOn(LIGHT_GROUP_ALL),
                # )
                print('sleep start')

                await asyncio.sleep(int(pattern['soundStartSec'])),
                print('litght start')

                # sound play ajax
                # asyncio.run(play_music(filePath))

                # sleep
                # asyncio.sleep(int(pattern['soundStartSec']))

                for ligthingPattern in pattern['ligtingPatternList']:
                    print('sleepSec')
                    await asyncio.sleep(int(ligthingPattern['sleepSec']))
                    print(ligthingPattern['gpio'])
                    print(ligthingPattern['patternNo'])

                    if (ligthingPattern['patternNo'] == 1):
                        # lightsOn
                        print('start lightsOn')
                        lightsOn([ligthingPattern['gpio']])
                    elif (ligthingPattern['patternNo'] == 2):
                        print('start lightsOff')
                        lightsOff([ligthingPattern['gpio']])
                    elif (ligthingPattern['patternNo'] == 3):
                        print('start allLighting')
                        span = float(ligthingPattern['span'])
                        count = int(ligthingPattern['count'])
                        allLighting([ligthingPattern['gpio']], span, count)
                    elif (ligthingPattern['patternNo'] == 4):
                        print('start moveMotor')
                        angle = int(ligthingPattern['angle'])
                        moveMotor(angle)
                    elif (ligthingPattern['patternNo'] == 5):
                        print('start randomLighting')
                        span = float(ligthingPattern['span'])
                        count = int(ligthingPattern['count'])
                        randomLighting([ligthingPattern['gpio']], span, count)
                break

        print('[end PlayPattern]')

    return JsonResponse({'success': True})


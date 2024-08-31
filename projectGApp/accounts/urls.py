from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path("", views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('ledInit/', views.LedInit, name='ledInit'),
    path('ledAllLightOn/',  views.LedAllLightOn,  name='ledAllLightOn'),
    path('ledAllLightOff/', views.LedAllLightOff, name='ledAllLightOff'),
    path('ledAllBlink/', views.LedAllBlink, name='ledAllBlink'),
    path('roundMotor/', views.RoundMotor, name='roundMotor'),
    path('ledPattern/', views.LedPattern, name='ledPattern'),
    path('randomLighting/', views.RandomLighting, name='randomLighting'),   
    path('playSound/', views.PlaySound, name='playSound'),
    path('update-switch-state/', views.update_switch_state, name='update-switch-state/'),
    path('LedAllLightOnAjax/',  views.LedAllLightOnAjax,  name='LedAllLightOnAjax'),

]
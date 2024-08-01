from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('add/', views.add_item, name='add_item'),
    path('toggle-led/', views.toggle_led, name='toggle_led'),
    path('down-led/', views.down_led, name='down_led'),
]
from django.shortcuts import render, redirect
from .models import Item
from .forms import ItemForm

from django.http import HttpResponseRedirect
from django.urls import reverse
import RPi.GPIO as GPIO

# Setup GPIO
LED_PIN = 17 # Change this to your GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)


def item_list(request):
    items = Item.objects.all()
    return render(request, 'items/item_list.html', {'items': items})

def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'items/add_item.html', {'form': form})

def toggle_led(request):
    current_state = GPIO.input(LED_PIN)
    GPIO.output(LED_PIN, not current_state)  # Toggle LED state
    return render(request, 'items/item_list.html')


    # return HttpResponseRedirect(reverse('item_list'))  # Redirect back to your item list or wherever you prefer

def down_led(request):
    current_state = GPIO.output(LED_PIN, GPIO.HIGH)
    GPIO.output(LED_PIN, not current_state)  # Toggle LED state
    return render(request, 'items/item_list.html')

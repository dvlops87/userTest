from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from .models import chat_info, delivery_info
from account.models import User
from django.utils import timezone
from django.utils.safestring import mark_safe
import json
# Create your views here.


def home(request):
    order_list = delivery_info.objects.filter(is_delivered=0)
    return render(request, 'main.html', {'order_list':order_list})

def order(request, user_id=0):
    if user_id == 0:
        redirect('login')
    try:
        if request.method == 'POST':
            new_order = delivery_info()
            new_order.ordered_time = timezone.now()
            new_order.delivery_location = request.POST["delivery_location"]
            new_order.delivery_price = request.POST["delivery_price"]
            new_order.delivery_list = request.POST["delivery_list"]
            new_order.delivery_owner = User.objects.get(id=user_id)
            new_order.stuff_price = request.POST["stuff_price"]
            new_order.extra_order = request.POST["extra_order"]
            new_order.store_location = request.POST["store_location"]
            new_order.is_delivered = 0
            new_order.save()
            return redirect('home')
        return render(request, 'order.html')
    except ValueError:
            return redirect('login')

def order_delivery(request, order_id):
    order_list = get_object_or_404(delivery_info, pk=order_id)
    name = order_list.delivery_owner
    if order_list.is_delivered == 1 or order_list.is_delivered == 2:
        return render(request, 'order_detail.html', {'details':order_list, 'time':order_list.time_required})
    return render(request, 'delivery.html', {'order_list':order_list, 'order_id': order_id, 'name':name})

def start_delivery(request, user_id=0, order_id=0):
    if user_id == 0:
        redirect('login')
    try:
        details = get_object_or_404(User, id=user_id)
        if details.is_trial == 0:
            return render(request, 'school_email_page.html')
        else:
            order_detail = delivery_info.objects.get(id=order_id)
            delivery_history = delivery_info.objects.filter(delivery_man=user_id) 
            order_detail.time_required = 0
            user = User.objects.get(id=user_id)
            order_detail.delivery_man = user
            order_detail.is_delivered = 1
            order_detail.save()
            return render(request, 'my_delivery_history.html', {'delivery_history':delivery_history})
    except ValueError:
            return redirect('login')


def chat(request, room_name):
    chat_detail = chat_info.objects.get(id=room_name)
    order_man = User.objects.get(id = chat_detail.order)
    return render(request, 'chat.html', {'room_name': room_name, 'order_man':order_man})
  
def confirm(request, user_id=0, order_id=0):
    order_detail = delivery_info.objects.get(id=order_id)
    order_detail.time_required = 0
    user = User.objects.get(id=user_id)
    order_detail.delivery_man = user
    order_detail.is_delivered = 1
    order_detail.save()
    nickname = order_detail.delivery_owner.nickname
    return render(request, 'start_delivery.html', {'order_detail':order_detail, 'nickname':nickname})
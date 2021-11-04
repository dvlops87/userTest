from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from .models import delivery_info
from account.models import User
from django.utils import timezone
# Create your views here.


def home(request):
    order_list = delivery_info.objects.filter(is_delivered=0)
    return render(request, 'main.html', {'order_list':order_list})

def order(request, user_id):
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

def order_delivery(request, order_id):
    order_list = get_object_or_404(delivery_info, pk=order_id)
    name = order_list.delivery_owner
    return render(request, 'delivery.html', {'order_list':order_list, 'order_id': order_id, 'name':name})

def start_delivery(request, user_id, order_id):
    order_detail = delivery_info.objects.get(id=order_id)
    order_detail.time_required = 0
    user = User.objects.get(id=user_id)
    order_detail.delivery_man = user
    order_detail.is_delivered = 1
    order_detail.save()
    nickname = order_detail.delivery_owner.nickname
    return render(request, 'start_delivery.html', {'order_detail':order_detail, 'nickname':nickname})

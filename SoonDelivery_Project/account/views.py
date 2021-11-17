from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import RedirectView
from .models import User
from delivery.models import delivery_info
from django.contrib import auth
from .text import message
import jwt
import json
import bcrypt
from django.contrib.sites.shortcuts import get_current_site
from SoonDelivery_Project.settings import SECRET_KEY
from django.utils.encoding import force_bytes,force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.views.generic import View
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .tokens import account_activation_token 
from datetime import datetime, timezone
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
# Create your views here.
# def home(request):
#     return render(request, 'home.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST["nickname"]
        password = request.POST["password"]
        user = authenticate(username = username, password = password)
        
        if user is not  None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': '아이디와 비밀번호가 일치하지 않습니다.'})
    else:
        return render(request, 'login.html')

def activate(request, uid64, token):

    uid = force_text(urlsafe_base64_decode(uid64))
    user = User.objects.get(pk=uid)

    if user is not None and account_activation_token.check_token(user, token):
        user.is_trial = True
        user.save()
        auth.login(request, user)
        return redirect('home')
    else:
        return HttpResponse('비정상적인 접근입니다.')

def user_signup(request):    
    if request.method == "POST" :
        try :
            user = User.objects.create_user(
                nickname = request.POST["nickname"],
                username = request.POST["username"],
                password = request.POST["password"],
                department = request.POST["department"],
                school_email = request.POST["school_email"],
                school_number = request.POST["school_number"],
            )
            user.is_trial = True
            user.save()
            current_site = get_current_site(request) 
            message = render_to_string('user_activate_email.html',                         {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).encode().decode(),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = "[순부름] 회원가입 인증 메일입니다."
            user_email = user.school_email
            email = EmailMessage(mail_subject, message, to=[user_email])
            email.send()
            return redirect('home')
        except IntegrityError:
            return render(request, 'check.html')
    return render(request, 'signup.html')

def check(request):
    return render(request, 'check.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def find_id(request):
    if request.method == "POST":
        user_email = request.POST["school_email"]
        user = User.objects.get(school_email = user_email)
        message = render_to_string('find_email.html',                         {
            'username': user.username,
            'password': user.password
        })
        mail_subject = "[순부름] 아이디 찾기 메일입니다."
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.send()
        return redirect('login')
    return render(request, 'find_id.html')

def find_password(request):
    if request.method == "POST":
        user_email = request.POST["school_email"]
        user = User.objects.get(school_email = user_email)
        message = render_to_string('find_email.html',                         {
            'user': user
        })
        mail_subject = "[순부름] 비밀번호 찾기 메일입니다."
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.send()
        return redirect('login')
    return render(request, 'find_password.html')

def my_delivery_history(request, user_id=0):
    if user_id == 0:
        redirect('login')
    try:
        delivery_history = delivery_info.objects.filter(delivery_man=user_id) 
        return render(request, 'my_delivery_history.html', {'delivery_history':delivery_history})
    except ValueError:
        return redirect('login')

def my_order_history(request, user_id):
    order_history =delivery_info.objects.filter(delivery_owner=user_id)
    return render(request, 'my_order_history.html', {'order_history':order_history})

def delivery_detail(request, delivery_id):
    details = get_object_or_404(delivery_info, pk=delivery_id)
    return render(request, 'delivery_detail.html', {'details':details, 'time':details.time_required})

def order_detail(request, delivery_id):
    details = get_object_or_404(delivery_info, pk=delivery_id)
    return render(request, 'delivery_detail.html', {'details':details, 'time':details.time_required})

def finish_delivery(request, delivery_id):
    details = delivery_info.objects.get(id=delivery_id)
    if(details.is_delivered != 2):
        now = timezone.now()
        date_to_compare = details.ordered_time
        date_diff = now - date_to_compare
        time = int(round(date_diff.seconds / 60))
        details.is_delivered = 2
        details.time_required = time
        details.save()
    return render(request, 'delivery_detail.html', {'details':details, 'time':details.time_required})

def finish_order(request, delivery_id):
    details = delivery_info.objects.get(id=delivery_id)
    if(details.is_delivered != 2):
        now = timezone.now()
        date_to_compare = details.ordered_time
        date_diff = now - date_to_compare
        time = int(round(date_diff.seconds / 60))
        details.is_delivered = 2
        details.time_required = time
        details.save()
    return render(request, 'order_detail.html', {'details':details, 'time':details.time_required})

def mypage(request, user_id=0):
    if user_id == 0:
        redirect('login')
    else :
        try: 
            details = get_object_or_404(User, id=user_id)
            if request.method == "POST" and 'change_password' in request.POST:
                input_password = request.POST.get("old_password")
                if check_password(input_password, details.password):
                    details.set_password(request.POST.get("new_password"))
                    details.save()
                    return render(request, 'mypage.html', {'details':details})
                else:
                    error = '현재 비밀번호가 올바르지 않습니다'
                    return render(request, 'mypage.html', {'details':details, 'error':error})
            elif request.FILES.get('image') is not None:
                details.image = request.FILES.get('image')
                details.save()
                return render(request, 'mypage.html', {'details':details})
            else:
                return render(request, 'mypage.html', {'details':details})
        except ValueError:
            return redirect('login')

def checkNickname(request):
    try:
        user = User.objects.get(nickname=request.GET['nickname'])
    except Exception as e:
        user = None
    result = {
        'result':'success',
        # 'data' : model_to_dict(user)  # console에서 확인
        'data' : "not exist" if user is None else "exist"
    }
    return JsonResponse(result)

def checkUsername(request):
    try:
        user = User.objects.get(username=request.GET['username'])
    except Exception as e:
        user = None
    result = {
        'result':'success',
        # 'data' : model_to_dict(user)  # console에서 확인
        'data' : "not exist" if user is None else "exist"
    }
    return JsonResponse(result)
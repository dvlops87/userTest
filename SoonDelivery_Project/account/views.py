from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import User
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
        user.is_active = True
        user.save()
        auth.login(request, user)
        return redirect('home')
    else:
        return HttpResponse('비정상적인 접근입니다.')

def user_signup(request):    
    if request.method == "POST" :
        user = User.objects.create_user(
            nickname = request.POST["nickname"],
            username = request.POST["username"],
            password = request.POST["password"],
            department = request.POST["department"],
            school_email = request.POST["school_email"],
            school_number = request.POST["school_number"],
        )
        user.is_active = False
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
    return render(request, 'signup.html')

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
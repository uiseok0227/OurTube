from django.shortcuts import render,HttpResponse,HttpResponseRedirect,redirect
from homeapp import user
from .models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
import json

# Create your views here.
def index(request):
    return render(request,"homeapp/index.html")

def crete(request):
    return HttpResponse("Create!!")

def about(request):
    print("hi")
    return render(request,"homeapp/about.html")

def login(request):
    you = user.User() #객체 생성 
    you.credentials = user.login() #로그인 
    
    # 객체 설정 
    you.set_userId()
    you.set_userName()

    # 세션값 부여 
    request.session["userId"] = you.userId
    request.session["userName"] = you.userName
    request.session["token"] = you.get_access_token()

    # 처음 등록이면 db저장 
    check = User.objects.filter(userId=str(you.userId))
    if(len(check)==0):
        saving = User(userName = you.userName, userId= str(you.userId),comment="반갑습니다.")
        saving.save()
        return render(request,"homeapp/load.html")

    return HttpResponseRedirect("/main/dashboard")

def loading(request):
    return render(request,"homeapp/load.html")
    # return HttpResponseRedirect("/main/dashboard")

    
    


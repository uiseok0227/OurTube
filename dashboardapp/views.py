from django.shortcuts import render
from django.shortcuts import render,HttpResponse,HttpResponseRedirect,redirect
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
import requests
from .models import User_Subscription
from .models import Subscription,Category,Subscription_Category
from homeapp.models import User
from django.db import connection

# Create your views here.
def index(request):
    # 세션값의 고유아이디 가져옴 
    uId = request.session.get("userId")
    # user 객체를 user의 고유 아이디로 가져옴 
    users = User.objects.filter(userId=uId)
    for i in users:
        # user의 아이디를 가져옴 
        userId = i.id
        user = i
        # user.delete()
    check = User_Subscription.objects.filter(userId=userId)
    # 확인용 
    # check.delete()
    # 구독목록이 존재하지 않으면 초기 가져옴 
    if(len(check)==0):
        # 세션값으로 토큰 가져오기 
        token = request.session.get("token")
        make_request = "https://www.googleapis.com/youtube/v3/subscriptions?access_token="+token+"&part=snippet&mine=true"
        response = requests.get(make_request).json()

        # nextPageToken 존재여부 파악 
        next = "nextPageToken"
        if(next in response):
            nextPageToken = response["nextPageToken"]

            # 채널아이디 전부 가져오기 
            while("nextPageToken" in response):

                make_request = make_request+"&pageToken="+nextPageToken
                next_page = requests.get(make_request).json()
                response["items"] += next_page["items"]

                if "nextPageToken" not in next_page:
                    response.pop("nextPageToken",None)
                else:
                    nextPageToken = next_page["nextPageToken"]
        
        for item in response["items"]:
            channel = item["snippet"]["resourceId"]["channelId"]
            title = item["snippet"]["title"]
            channelImg = item["snippet"]["thumbnails"]["default"]["url"]

            print(item["snippet"]["title"])

            # Subscription 테이블에 채널 존재하지 않으면 추가해준다.
            check = Subscription.objects.filter(channelId=channel)
            if(len(check)==0):
                try:
                    save_channel = Subscription(channelName=title,channelId=channel,channelImg=channelImg)
                    save_channel.save()
                except:
                    continue

            channels = Subscription.objects.filter(channelId=channel)
            for c in channels:
                saving_channel = c

            # user_Subscription 테이블에 저장해주기
            save_user_channel = User_Subscription(userId = user,channelId=saving_channel)
            save_user_channel.save()
            
            # 제목 출력 
            print(item["snippet"]["title"])

            # 카테고리 저장하기
            check = Subscription_Category.objects.filter(channelId = saving_channel.id)
            print("길이:",len(check))
            if(len(check)==0):
                playlist = get_playlist(token,channel)
                for play in playlist:
                    categories = Category.objects.filter(cateId=play)
                    for cate in categories:
                        save_cate_channel = Subscription_Category(channelId=saving_channel,cateId=cate)
                        save_cate_channel.save()

            # 띠움
            print("-------------------------------------------------------------------")
    
    user_channel_list = User_Subscription.objects.filter(userId=userId)
    # context = {'channel_list': user_channel_list}
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select t3.category,t3.id,Count(t3.category)
        From ourtube.dashboardapp_user_subscription  t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_category t3
        Where t1.userId_id = '''
        +str(userId)+
        '''
        and t1.channelId_id=t2.channelId_id
        and t3.id=t2.cateId_id
        Group By t3.category
        ;
        '''
    )
    row = cursor.fetchall()
    print(row)
    row = list(row)
    row.sort(key = lambda _:-_[2])
    context = {"user_status":row}
    xdata = []
    ydata = []
    length = len(row)
    if(length<=7):
        for content in row:
            xdata.append(content[0])
            ydata.append(content[2])
    else:
        index = 0
        sum_of_etc = 0
        for content in row:
            if(index>=7):
                sum_of_etc += content[2] 
                continue
            xdata.append(content[0])
            ydata.append(content[2])
            index+=1 
        xdata.append('etc')
        ydata.append(sum_of_etc)
                
    x_data = json.dumps(xdata)
    y_data = json.dumps(ydata)
    context["xdata"] = x_data
    context["ydata"] = y_data
    print(context)
    context["username"] = user.userName
    return render(request, "dashboardapp/chart.html", context)

'''
카테고리 가져오기 함수 
'''
def get_playlist(token,channel):
    channel = channel[0] + "U" + channel[2:]
    try:
        playlist = "https://www.googleapis.com/youtube/v3/playlistItems?access_token="+token+"&part=snippet&playlistId="+channel
        # playlist 없으면 예외 처리 하기 
        response = requests.get(playlist).json()

        # 비디오 가져오기
        video_list = []

        for item in response["items"]:
            video_list.append(item["snippet"]["resourceId"]["videoId"])

        # print("비디오 목록 가져옴 ")
        # 카테고리 가져오기 
        category_list = []
        for video in video_list:
            category = "https://www.googleapis.com/youtube/v3/videos?access_token="+token+"&part=snippet&id="+video
            response = requests.get(category).json()

            for i in response["items"]:
                category_list.append(int(i["snippet"]["categoryId"]))
    except:
        category_list = [45]
    category_list = list(set(category_list))
    print(category_list)

    return category_list

def detail(request,category_id):
    uId = request.session.get("userId")
    # user 객체를 user의 고유 아이디로 가져옴 
    users = User.objects.filter(userId=uId)
    for i in users:
        # user의 아이디를 가져옴 
        userId = i.id
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select Distinct t1.channelId_id,t2.cateId_id,t3.channelName,t3.channelId,t3.channelImg
        From ourtube.dashboardapp_user_subscription t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_subscription t3
        Where userId_id = '''+str(userId)+
        '''
        and t1.channelId_id = t2.channelId_id
        and t2.cateId_id = '''+str(category_id)+
        '''
        and t2.channelId_id = t3.id
        ;
        '''
    )
    row = cursor.fetchall()
    print(row)
    cate_name = Category.objects.filter(id=category_id)
    print(cate_name)
    context = {"channel_list":row,"cate":cate_name}
    return render(request, "dashboardapp/detail.html", context)

def logout(request):
    if request.session.get('user'):
        del(request.session['user'])
    return redirect('/')

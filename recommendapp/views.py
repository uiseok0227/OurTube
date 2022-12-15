from django.shortcuts import render,HttpResponse,redirect
from homeapp.models import User
import random 
from django.db.models import Q
from dashboardapp.models import User_Subscription,Subscription,Subscription_Category,Category
from django.db import connection
import time 
from .models import ClickLog
from django.utils import timezone
from datetime import datetime

# Create your views here.
def index(request):
    start = time.time()

    # user 객체를 user의 고유 아이디로 가져옴
    uId = request.session.get("userId") 
    me = User.objects.get(userId = uId)
    cursor = connection.cursor()

    # 내 (카테고리, 카테고리별 개수) 가져옴 
    cursor.execute('''
    Select t5.category,count(*) As cnt
    From (Select t1.userName, t2.channelId_id, t3.cateId_id, t4.category
    From ourtube.homeapp_user t1,
    ourtube.dashboardapp_user_subscription t2,
    ourtube.dashboardapp_subscription_category t3,
    ourtube.dashboardapp_category t4
    Where t1.userId = '''+str(me.userId)+
    '''
    And t1.id = t2.userId_id
    And t2.channelId_id = t3.channelId_id
    And t3.cateId_id = t4.id) t5
    group by t5.category
    Order by cnt desc;
    ''')
    my_interest_list = cursor.fetchall()

    favorite_list = []
    for i in range(3):
        favorite_list.append(my_interest_list[i][0])


    # 내 구독 채널 총 개수 
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select Count(*)
        From ourtube.dashboardapp_user_subscription  t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_category t3
        Where t1.userId_id =
        '''+str(me.id)+
        '''
        and t1.channelId_id=t2.channelId_id
        and t3.id=t2.cateId_id
        ;
        '''
    )
    total = cursor.fetchall()
    total = total[0][0]

    # 나의 구독 목록의 카테고리별 비율 구해줌 
    interest_percent_list = []
    for cate,cate_count in my_interest_list:
        interest_percent_list.append([cate,cate_count/total])

    # 모든 유저 가져옴 
    users = User.objects.all()
    user_list = []
    # max_scaling 위해서 만들어줌
    max_similarity = 0
    for user in users:
        if(user==me):
            continue 
        else:
            # 유사도 파악해야함
            # 사용자 별 (카테고리, 카테고리 개수) 가져옴 
            cursor = connection.cursor()
            cursor.execute('''
            Select t5.category,count(*) As cnt
            From (Select t1.userName, t2.channelId_id, t3.cateId_id, t4.category
            From ourtube.homeapp_user t1,
            ourtube.dashboardapp_user_subscription t2,
            ourtube.dashboardapp_subscription_category t3,
            ourtube.dashboardapp_category t4
            Where t1.userId = '''+str(user.userId)+
            '''
            And t1.id = t2.userId_id
            And t2.channelId_id = t3.channelId_id
            And t3.cateId_id = t4.id) t5
            group by t5.category
            Order by cnt desc;
            ''')
            user_interest_list = cursor.fetchall()

            # 사용자별 구독 총 개수 가져옴 
            cursor = connection.cursor()
            cursor.execute(
                '''
                Select Count(*)
                From ourtube.dashboardapp_user_subscription  t1,
                ourtube.dashboardapp_subscription_category t2,
                ourtube.dashboardapp_category t3
                Where t1.userId_id =
                '''+str(user.id)+
                '''
                and t1.channelId_id=t2.channelId_id
                and t3.id=t2.cateId_id
                ;
                '''
            )
            user_total = cursor.fetchall()
            user_total = user_total[0][0]
            
            if(user_total == 0):
                continue 

            user_interest_percent_list = []
            for cate,cate_count in user_interest_list:
                user_interest_percent_list.append([cate,cate_count/user_total])

            msdsim = 0
            same = 0
            for i in interest_percent_list:
                for j in user_interest_percent_list:
                    if(i[0]==j[0]):
                        same+=1 
                        msdsim+=pow((i[1]-j[1]),2)
            msdsim =1 - (msdsim/same)
            jacard = same / (len(interest_percent_list)+len(user_interest_percent_list)-same)
            similarity = msdsim*jacard
            max_similarity = max(max_similarity,similarity)
            user_list.append([user,similarity])

    # 유사도가 높은 순서로 사용자 정렬 및 0-1로 scaling 
    user_list.sort(key = lambda _ : _[1],reverse=True)
    for user in user_list:
        user[1] = user[1]/max_similarity

    # 모든 구독 채널 데이터를 이용. SQL을 통해 아예 처음부터 자신이 구독하는 채널을 제외시킴 
    # 가중치를 유사도로 준다  

    recommendation = []
    for i in range(len(user_list)):
        recommend_man = user_list[i][0]
        weight = user_list[i][1]
        cursor = connection.cursor()
        cursor.execute('''
            Select t1.channelId_id,t4.channelName,t4.channelImg,t3.category, +'''+str(weight)+''' as weight,t4.channelId
            From ourtube.dashboardapp_user_subscription t1,
            ourtube.dashboardapp_subscription_category t2,
            ourtube.dashboardapp_category t3,
            ourtube.dashboardapp_subscription t4
            where 
            userId_id = '''+str(recommend_man.id)+'''
            And t1.channelId_id = t2.channelId_id
            And t2.cateId_id = t3.id
            And t1.channelId_id = t4.id
            And t1.channelId_id not in 
            (Select channelId_id From ourtube.dashboardapp_user_subscription
            Where userId_id = '''+str(me.id)+'''
            );
            ''')
        temp_recommendation = cursor.fetchall()
        recommendation += temp_recommendation
    # recommendation = recommendation[0]
    recommendation = list(map(list,recommendation))

    # 선호 카테고리에 있으면 가중치를 비율만큼 up시켜줌 
    max_recommend_weight = 0
    min_recommend_weight = 10
    for recommend in recommendation:
        recommend[4] = float(recommend[4])
        for i in range(len(interest_percent_list)):
            if(recommend[3] in interest_percent_list[i][0]):
                recommend[4] += interest_percent_list[i][1]
        max_recommend_weight = max(max_recommend_weight,recommend[4])
        min_recommend_weight = min(min_recommend_weight,recommend[4])

    # 전체를 0-1로 scaling해주기 
    for recommend in recommendation:
        # recommend[4]/=max_recommend_weight
        recommend[4] = (recommend[4]-min_recommend_weight)/(max_recommend_weight-min_recommend_weight)

    # sorting 하기 
    recommendation.sort(key = lambda _ : _[4],reverse=True)
    first_index = 0
    first = True 
    second_index = 0
    second = True 

    top_5percent = len(recommendation)*0.05
    top_10percent = len(recommendation)*0.1

    for r in range(len(recommendation)):
        if(first == True and r>top_5percent):
            first_index = r
            print("상위 5%:",first_index)
            first = False 
        if(second == True and r>top_10percent):
            second_index = r 
            print("상위 10%:",second_index)
            break 

    # 카테고리 2개는 관련도 높은 것
    first_rand_num = random.randint(0,first_index)
    second_rand_num = random.randint(0,second_index)
    if(first_rand_num == second_rand_num):
        same = True 
        while(same == True):     
            second_rand_num = random.randint(0,second_index)
            if(first_rand_num != second_rand_num):
                same = False
    fisrt_recommend = recommendation[first_rand_num]
    second_recommend = recommendation[second_rand_num]

    context = {"like_recommend_list1" : fisrt_recommend}
    context['like_recommend_list2'] = second_recommend

    # 카테고리 1개는 선호 카테고리 제외 랜덤 샘플링 
    third_recommend_list = []
    for r in recommendation:
        if(r[3] not in favorite_list):
            third_recommend_list.append(r)
    third_recommend = random.sample(recommendation,1)

    end = time.time()
    print("알고리즘 시간:",end-start)
    context['like_recommend_list3'] = third_recommend[0]
    context["userName"] = me.userName
    return render(request,"recommendapp/recommend.html",context)

def refresh(request):
    print("hi")
    now = datetime.now()
    print(now)
    uId = request.session.get("userId")
    user = User.objects.get(userId = uId)
    user_name = user.userName
    c  = ClickLog(userName = user_name,logtime = now)
    c.save()

    return redirect('/main/recommend')


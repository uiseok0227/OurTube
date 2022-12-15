from django.shortcuts import render,HttpResponse
from homeapp.models import User
from django.db.models import Q
from django.db import connection
from dashboardapp.models import Category 


# Create your views here.
# 친구목록 가져오기 
def index(request):
    # 세션으로 user가져오기 
    uId = request.session.get("userId")
    user = User.objects.get(userId = uId)
    # friend = User.objects.get(userName = '김의석')
    # print(friend)
    # friend.delete()
    # 친구 목록 
    friend_list = user.friends.all()
    context = {"friend_list":friend_list}

    return render(request,"friendapp/friend.html",context)

# 친구 검색하기 
def search(request):
    uId = request.session.get("userId")
    user = User.objects.get(userId = uId)
    friend_list = user.friends.all()
    context = {"friend_list":friend_list}

    users = User.objects.all().order_by('-id')
    search = request.GET.get('search','')
    if search:
        search_list = users.filter(
            Q(userName__icontains = search)
        )
        new_search_list = []
        for result in search_list:
            if(result.userName == request.session.get("userName")):
                continue 
            new_search_list.append(result)
            
        if(len(new_search_list)!=0):
        # context = {"search_list":new_search_list}
            context["search_list"] = new_search_list
        else:
            noresult = True 
            context["noresult"] = noresult
             
        return render(request,"friendapp/search.html",context)
    
    else:
        return render(request,"friendapp/search.html",context)

# 친구 추가하기 
def add_friend(request):
    uId = request.session.get("userId")
    user = User.objects.get(userId = uId)
    friend = request.GET.get('friend','')
    friend = User.objects.get(userName = friend)

    # 이미 친구인 경우 
    if(friend in user.friends.all()):
        already = True
        context = {"already": already }
        return render(request,"friendapp/search.html",context)
    
    # 새로 추가하는 경우 
    else:
        user.friends.add(friend)
        success = True
        context = {"success": success}
        return render(request,"friendapp/search.html",context)

# 친구 세부정보
def friendInfo(request):
    # 사용자 
    uId = request.session.get("userId")
    user = User.objects.get(userId = uId)
    # 친구 
    friend = request.GET.get('friendinfo','')
    friend = User.objects.get(userName = friend)

    friend_list = user.friends.all()
    context = {"friend_list":friend_list}

    # 전달목록 
    # 친구 이름, 친구와의 유사도, 친구 선호 카테고리 3가지 

    # 이름 
    print("친구이름: ",friend)
    context["friend_name"] = friend.userName
    # 흥미3가지
    cursor = connection.cursor()
    cursor.execute('''
    Select t5.category,count(*) As cnt
    From (Select t1.userName, t2.channelId_id, t3.cateId_id, t4.category
    From ourtube.homeapp_user t1,
    ourtube.dashboardapp_user_subscription t2,
    ourtube.dashboardapp_subscription_category t3,
    ourtube.dashboardapp_category t4
    Where t1.userId = '''+str(friend.userId)+
    '''
    And t1.id = t2.userId_id
    And t2.channelId_id = t3.channelId_id
    And t3.cateId_id = t4.id) t5
    group by t5.category
    Order by cnt desc
    Limit 3;
    ''')
    interest_list = cursor.fetchall()
    context["interest_list"]=interest_list

    # 유사도 
    # 본인 
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select t3.category,t3.id,Count(t3.category)
        From ourtube.dashboardapp_user_subscription  t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_category t3
        Where t1.userId_id = '''
        +str(user.id)+
        '''
        and t1.channelId_id=t2.channelId_id
        and t3.id=t2.cateId_id
        Group By t3.category
        Order By Count(t3.category) DESC
        ;
        '''
    )
    my_list = cursor.fetchall()

    # 내 구독 총 개수 
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
    total = cursor.fetchall()
    total = total[0][0]

    # 나의 구독 목록의 카테고리별 비율 구해줌 
    interest_percent_list = []
    for cate,cate_id,cate_count in my_list:
        interest_percent_list.append([cate_id,cate_count/total])

    # 친구 
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select t3.category,t3.id,Count(t3.category)
        From ourtube.dashboardapp_user_subscription  t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_category t3
        Where t1.userId_id = '''
        +str(friend.id)+
        '''
        and t1.channelId_id=t2.channelId_id
        and t3.id=t2.cateId_id
        Group By t3.category
        Order By Count(t3.category) DESC
        ;
        '''
    )
    friend_list = cursor.fetchall()

    # 친구 구독 총 개수 
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select Count(*)
        From ourtube.dashboardapp_user_subscription  t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_category t3
        Where t1.userId_id =
        '''+str(friend.id)+
        '''
        and t1.channelId_id=t2.channelId_id
        and t3.id=t2.cateId_id
        ;
        '''
    )
    friend_total = cursor.fetchall()
    friend_total = friend_total[0][0]

    # 구독 하나도 없는 경우 
    if(friend_total == 0):
        context["interest_list"]= [["구독목록 없음"]]
        context["similarity"] = 0
        context["subscription_list"] = friend_list
        return render(request,"friendapp/friend.html",context)


    # 친구의 구독 목록의 카테고리별 비율 구해줌 
    friend_interest_percent_list = []
    for cate,cate_id,cate_count in friend_list:
        friend_interest_percent_list.append([cate_id,cate_count/friend_total])

    msdsim = 0
    same = 0
    for i in interest_percent_list:
        for j in friend_interest_percent_list:
            if(i[0]==j[0]):
                same+=1 
                msdsim+=pow((i[1]-j[1]),2)
    msdsim =1 - (msdsim/same)
    jacard = same / (len(interest_percent_list)+len(friend_interest_percent_list)-same)
    similarity = msdsim*jacard

    similarity = round(similarity*100,2)
    print("유사도",similarity)
    
    context["similarity"] = similarity
    context["subscription_list"] = friend_list

    return render(request,"friendapp/friend.html",context)

# 친구삭제 
def delete(request):
    # 세션으로 user가져오기 
    uId = request.session.get("userId")
    user = User.objects.get(userId = uId)

    # 삭제 
    friend = request.GET.get('delete','')
    friend = User.objects.get(userName = friend)
    user.friends.remove(friend)
    
    # 친구 목록 
    friend_list = user.friends.all()
    context = {"friend_list":friend_list}

    return render(request,"friendapp/friend.html",context)

# 카테고리 정보 
# 친구정보,흥미 3가지, 구독정보, 이름, 유사도, 카테고리 
def interestInfo(request):
    interestinfo = request.GET.get('interestinfo')

    uId = request.session.get("userId")
    user = User.objects.get(userId = uId)

    friendname = request.GET.get('friend')
    friend = User.objects.get(userName = friendname)

    # 친구목록 
    friend_list = user.friends.all()
    context = {"friend_list":friend_list}
    
    # 친구정보 
    context["friend_name"] = friend.userName

    # 흥미3가지
    cursor = connection.cursor()
    cursor.execute('''
    Select t5.category,count(*) As cnt
    From (Select t1.userName, t2.channelId_id, t3.cateId_id, t4.category
    From ourtube.homeapp_user t1,
    ourtube.dashboardapp_user_subscription t2,
    ourtube.dashboardapp_subscription_category t3,
    ourtube.dashboardapp_category t4
    Where t1.userId = '''+str(friend.userId)+
    '''
    And t1.id = t2.userId_id
    And t2.channelId_id = t3.channelId_id
    And t3.cateId_id = t4.id) t5
    group by t5.category
    Order by cnt desc
    Limit 3;
    ''')
    interest_list = cursor.fetchall()
    context["interest_list"]=interest_list

    # 유사도 
    # 본인 
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select t3.category,t3.id,Count(t3.category)
        From ourtube.dashboardapp_user_subscription  t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_category t3
        Where t1.userId_id = '''
        +str(user.id)+
        '''
        and t1.channelId_id=t2.channelId_id
        and t3.id=t2.cateId_id
        Group By t3.category
        Order By Count(t3.category) DESC
        ;
        '''
    )
    my_list = cursor.fetchall()

    # 내 구독 총 개수 
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
    total = cursor.fetchall()
    total = total[0][0]

    # 나의 구독 목록의 카테고리별 비율 구해줌 
    interest_percent_list = []
    for cate,cate_id,cate_count in my_list:
        interest_percent_list.append([cate_id,cate_count/total])

    # 친구 
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select t3.category,t3.id,Count(t3.category)
        From ourtube.dashboardapp_user_subscription  t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_category t3
        Where t1.userId_id = '''
        +str(friend.id)+
        '''
        and t1.channelId_id=t2.channelId_id
        and t3.id=t2.cateId_id
        Group By t3.category
        Order By Count(t3.category) DESC
        ;
        '''
    )
    friend_list = cursor.fetchall()

    # 친구 구독 총 개수 
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select Count(*)
        From ourtube.dashboardapp_user_subscription  t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_category t3
        Where t1.userId_id =
        '''+str(friend.id)+
        '''
        and t1.channelId_id=t2.channelId_id
        and t3.id=t2.cateId_id
        ;
        '''
    )
    friend_total = cursor.fetchall()
    friend_total = friend_total[0][0]

    # 구독 하나도 없는 경우 
    if(friend_total == 0):
        context["interest_list"]= [["구독목록 없음"]]
        context["similarity"] = 0
        context["subscription_list"] = friend_list
        return render(request,"friendapp/friend.html",context)


    # 친구의 구독 목록의 카테고리별 비율 구해줌 
    friend_interest_percent_list = []
    for cate,cate_id,cate_count in friend_list:
        friend_interest_percent_list.append([cate_id,cate_count/friend_total])

    msdsim = 0
    same = 0
    for i in interest_percent_list:
        for j in friend_interest_percent_list:
            if(i[0]==j[0]):
                same+=1 
                msdsim+=pow((i[1]-j[1]),2)
    msdsim =1 - (msdsim/same)
    jacard = same / (len(interest_percent_list)+len(friend_interest_percent_list)-same)
    similarity = msdsim*jacard

    similarity = round(similarity*100,2)
    print("유사도",similarity)
    
    context["similarity"] = similarity
    context["subscription_list"] = friend_list

    # 카테고리 정보 
    cursor = connection.cursor()
    cursor.execute(
        '''
        Select Distinct t1.channelId_id,t2.cateId_id,t3.channelName,t3.channelId,t3.channelImg
        From ourtube.dashboardapp_user_subscription t1,
        ourtube.dashboardapp_subscription_category t2,
        ourtube.dashboardapp_subscription t3
        Where userId_id = '''+str(friend.id)+
        '''
        and t1.channelId_id = t2.channelId_id
        and t2.cateId_id = '''+str(interestinfo)+
        '''
        and t2.channelId_id = t3.id
        ;
        '''
    )
    row = cursor.fetchall()
    context["cate_info"] = row 
    
    cate_name = Category.objects.filter(id=interestinfo)
    cate_name = cate_name[0].category
    context["cate_name"] =cate_name

    return render(request,"friendapp/friend.html",context)


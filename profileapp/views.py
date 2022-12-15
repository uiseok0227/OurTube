from django.shortcuts import render
from homeapp.models import User
from dashboardapp.models import Subscription, User_Subscription,Subscription_Category,Category
from django.db import connection
# Create your views here.
def index(request):
    # 세션값 가져오기 
    userId = (request.session.get('userId'))
    userName = (request.session.get('userName'))
    
    user_list = User.objects.filter(userId = str(userId))
    cursor = connection.cursor()
    cursor.execute('''
    Select t5.category,count(*) As cnt
From (Select t1.userName, t2.channelId_id, t3.cateId_id, t4.category
From ourtube.homeapp_user t1,
ourtube.dashboardapp_user_subscription t2,
ourtube.dashboardapp_subscription_category t3,
ourtube.dashboardapp_category t4
Where t1.userId = '''+str(userId)+
'''
And t1.id = t2.userId_id
And t2.channelId_id = t3.channelId_id
And t3.cateId_id = t4.id) t5
group by t5.category
Order by cnt desc
Limit 3;
    ''')
    row = cursor.fetchall()
    print(row)
    context = {'user_list': user_list}  
    # context = {"interest_list" : user_list}
    # c = Subscription.objects.all()
    # c.delete()
    context["interest_list"]=row
    print(context)

    return render(request, 'profileapp/prof.html', context)
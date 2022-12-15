from django.db import models
from homeapp.models import User

# Create your models here.
class Subscription(models.Model):
    channelName = models.CharField(max_length=60)
    channelId = models.CharField(max_length=40)
    channelImg = models.CharField(max_length=300,null=True)

class Category(models.Model):
    cateId = models.IntegerField(null=True)
    category = models.CharField(max_length=30)

class User_Subscription(models.Model):
    userId = models.ForeignKey(User,on_delete=models.CASCADE)
    channelId = models.ForeignKey(Subscription,on_delete=models.CASCADE)

class Subscription_Category(models.Model):
    cateId = models.ForeignKey(Category,on_delete=models.CASCADE)
    channelId = models.ForeignKey(Subscription,on_delete=models.CASCADE)
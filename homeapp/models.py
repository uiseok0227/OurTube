from django.db import models

# Create your models here.
class User(models.Model):
    userName = models.CharField(max_length=50)
    userId = models.CharField(max_length=30)
    comment = models.CharField(max_length=100)
    friends = models.ManyToManyField('self')

    def __str__(self):
        return self.userName

# class Friend(models.Model):
#     from_user = models.ForeignKey(User,on_delete = models.CASCADE)
#     to_user = models.ForeignKey(User,on_delete = models.CASCADE)
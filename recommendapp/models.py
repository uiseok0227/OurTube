from django.db import models

# Create your models here.
class ClickLog(models.Model):
    userName = models.CharField(max_length=10)
    logtime = models.DateTimeField()
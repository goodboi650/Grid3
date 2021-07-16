from django.db import models

class Response(models.Model):
    IP = models.CharField(max_length=100)
    Hostname = models.CharField(max_length=100)
    MAC = models.CharField(max_length=100)
    OS = models.CharField(max_length=100)

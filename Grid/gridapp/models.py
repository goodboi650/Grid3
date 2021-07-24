from django.db import models


class Response(models.Model):
    ##
    IP = models.CharField(max_length=100, primary_key=True)
    Hostname = models.CharField(max_length=100)
    MAC = models.CharField(max_length=100)
    OS = models.CharField(max_length=100)
    ADDomain = models.CharField(max_length=100, null=True)
    Workgroup = models.CharField(max_length=100, null=True)
    # Domaininfo
    DomainInfo = models.CharField(max_length=100, null=True)
    Status = models.CharField(max_length=100, null=True)
    LastSeenAlive = models.TimeField(null=True)
    LastUpdated = models.TimeField(null=True)


class Creds(models.Model):
    Password = models.CharField(max_length=50)  # Secret
    Username = models.CharField(max_length=50)  # Secret
    Server = models.CharField(max_length=20)
    Port = models.IntegerField(blank=True, null=True)

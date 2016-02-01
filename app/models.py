from django.db import models

# Create your models here.
class Access_Token(models.Model):
    token = models.CharField(max_length=1024,default = '')
    expires_in = models.IntegerField(default = '7200')
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.token


class Jsapi_Ticket(models.Model):
    ticket = models.CharField(max_length=1024,default = '')
    expires_in = models.IntegerField(default = '7200')
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.ticket
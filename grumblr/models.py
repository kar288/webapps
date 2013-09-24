from django.db import models
from django.contrib.auth.models import User
from collections import *

class Field(models.Model):
	name = models.CharField(max_length= 50)
	placeholder = models.CharField(max_length=50)
	error = models.CharField(max_length = 50)
	type = models.CharField(max_length = 50)
	mandatory = models.BooleanField(default = True)

class IntField(Field):
	value = models.IntegerField()

class CharField(Field):
	value = models.CharField(max_length= 50)

class DateField(Field):
	value = models.DateTimeField()

def upload_to(instance, filename):
    return 'images/%s/%s' % (instance.user.user.username, filename)

class GrumblrUser(User):
    pic = models.ImageField(upload_to=upload_to)

class Grumble(models.Model):
    content = models.CharField(max_length=40)
    user = models.ForeignKey(GrumblrUser)
    time = models.DateTimeField(auto_now_add=True)

class GrumblrProfile(models.Model):
	user = models.OneToOneField(GrumblrUser)
	age = models.CharField(max_length = 50)
	location = models.CharField(max_length = 50)
	phone = models.CharField(max_length = 50)

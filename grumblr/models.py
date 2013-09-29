from django.db import models
from django.contrib.auth.models import User
from collections import *

def upload_to(instance, filename):
    return '/static/images/%s/%s' % (instance.user.user.username, filename)

class Document(models.Model):
    docfile = models.ImageField(upload_to='static/%Y/%m/%d')

class GrumblrUser(User):
	pic = models.ForeignKey(Document, related_name='user_document')
	following = models.ManyToManyField('self', related_name='user_following', symmetrical=False)
	blockers = models.ManyToManyField('self', related_name='user_blockers', symmetrical=False)

class Grumble(models.Model):
	commentType = models.BooleanField(default=False)
	comments = models.ManyToManyField('self', related_name='grumble_comments', symmetrical=False)
	content = models.CharField(max_length=40)
	user = models.ForeignKey(GrumblrUser, related_name='grumble_user')
	time = models.DateTimeField(auto_now_add=True)
	dislikes = models.ManyToManyField(GrumblrUser, related_name='grumble_dislikes')

class GrumblrProfile(models.Model):
	user = models.OneToOneField(GrumblrUser)
	age = models.CharField(blank = True, max_length = 50)
	location = models.CharField(blank = True, max_length = 50)
	phone = models.CharField(blank = True, max_length = 50)

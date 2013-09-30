from django import template
from grumblr.models import *

register = template.Library()

@register.tag('disliked')
def disliked(value):
	return value
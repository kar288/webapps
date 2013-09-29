from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'^$', 'django.contrib.auth.views.login', {'template_name':'sign-in.html'}, name='login'),
    # url(r'^sign-in.html', 'grumblr.views.signin'),
    # Route for built-in authentication with our own custom login page
    url(r'^login', 'django.contrib.auth.views.login', {'template_name':'sign-in.html'}, name='login'),
    url(r'^sign-in.html', 'django.contrib.auth.views.login', {'template_name':'sign-in.html'}, name='login'),
    
    url(r'^profile$', 'grumblr.views.profile', name='profile'),
    url(r'^registration$', 'grumblr.views.registration', name='registration'),
    url(r'^lost-password.html$', 'grumblr.views.lostpassword'),
    url(r'^recover-password$', 'grumblr.views.recoverpassword', name='recover-password'),
    url(r'^stream$', 'grumblr.views.stream', name = 'stream'),
    url(r'^profile/(?P<name>\w+)$', 'grumblr.views.other_user', name = 'other_user'),
    url(r'^profile/(?P<name>\w+)/information$', 'grumblr.views.other_user_info', name='other_user_info'),
    url(r'^edit-information$', 'grumblr.views.edit_information', name ='edit_information'),
    url(r'^search', 'grumblr.views.search', name = 'search'),
    url(r'^logout', 'grumblr.views.logout', name = 'logout'),
    url(r'^edit-password', 'grumblr.views.edit_password', name = 'edit_password'),
    url(r'^dislike', 'grumblr.views.dislike', name = 'dislike'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

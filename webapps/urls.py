from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'grumblr.views.signin'),
    url(r'^sign-in.html', 'grumblr.views.signin'),
    url(r'^profile.html$', 'grumblr.views.profile'),
    url(r'^registration.html$', 'grumblr.views.registration'),
    url(r'^lost-password.html$', 'grumblr.views.lostpassword'),
    url(r'^recover-password.html$', 'grumblr.views.recoverpassword'),
    url(r'^stream.html$', 'grumblr.views.stream'),
    url(r'^profile.html/(?P<name>\w+)$', 'grumblr.views.other_user'),
    url(r'^profile.html/(?P<name>\w+)/information$', 'grumblr.views.other_user_info'),
    url(r'^edit-information.html$', 'grumblr.views.edit_information'),
    url(r'^search.html', 'grumblr.views.search'),
    url(r'^logout.html', 'grumblr.views.logout'),
    url(r'^edit-password.html', 'grumblr.views.edit_password'),
    #(r'^sign-in.html/(?P<param>\w+)$', 'grumblr.views.signin2'),
)

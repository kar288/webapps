from django.shortcuts import render, redirect, get_object_or_404

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, authenticate
from django.contrib import auth

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Imports the Item class
from grumblr.models import *
from grumblr.forms import *
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.validators import *
from django.db import IntegrityError, transaction
from collections import *

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from mimetypes import guess_type

# Used to send mail from within Django
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator

@transaction.commit_on_success
def registration(request):
	context = {}

	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = RegistrationForm(auto_id=False)
		return render(request, 'registration.html', context)

	# Creates a bound form from the request POST parameters and makes the 
	# form available in the request context dictionary.
	form = RegistrationForm(request.POST)
	context['form'] = form

	# Validates the form.
	if not form.is_valid():
		return render(request, 'registration.html', context)

	# If we get here the form data was valid.  Register and login the user.
	new_user = GrumblrUser.objects.create_user(username=form.cleaned_data['username'],
										email = form.cleaned_data['email'],
										password=form.cleaned_data['password1'],
										picture = 'profile-pic.jpg')

	new_profile = GrumblrProfile.objects.create(user = new_user)
	new_profile.save() # Mark the user as inactive to prevent login before email confirmation.

	new_user.is_active = False
	new_user.save()

    # Generate a one-time use token and an email message body
	token = default_token_generator.make_token(new_user)

	email_body = """
Welcome to Grumblr!  Please click the link below to
verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))

	send_mail(subject="Verify your email address",
              message= email_body,
              from_email="team@grumblr.com",
              recipient_list=[new_user.email])

	context['email'] = form.cleaned_data['email']
	return render(request, 'needs-confirmation.html', context)

def needs_confirmation(request):
	return render(request)
    

@transaction.commit_on_success
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'confirmed.html', {})
    

@transaction.commit_on_success
@login_required
def logout(request):
	auth.logout(request)
	return redirect(reverse('login'))

def getGrumbls(context, user, own = True):
	if own:
		grumbls = Grumble.objects.filter(user = user)
	else:
		grumbls = Grumble.objects.filter(user__in = user.following.all())
	grumbls = grumbls.order_by('time').reverse()
	context['grumbls'] = grumbls

def getUserInfo(context, current_user, user):
	context['user'] = user
	context['current_user'] = current_user
	context['followees'] = user.following.all()
	context['followers'] = GrumblrUser.objects.filter(following__username=user.username)

@transaction.commit_on_success
@login_required
def profile(request):
	context = {}

	user = GrumblrUser.objects.filter(username = request.user)[0]
	getUserInfo(context, user, user)

	if request.method == 'POST':
		if 'content' in request.POST:
			grumble = Grumble(content = request.POST['content'], user = user)
			grumble.save()
		if 'comment' in request.POST:
		 	comment = Grumble(content = request.POST['comment'], user = user, commentType=True)
		 	comment.save()
		 	Grumble.objects.filter(id = request.POST['id'])[0].comments.add(comment)

	context['url'] = request.META['PATH_INFO']
	getGrumbls(context, user)
	context['own'] = True
	print context
	return render(request, 'profile.html', context)


@login_required
def get_photo(request, id):
	print "getting photo"
	user = get_object_or_404(GrumblrUser, id=id)
	if not user.picture:
		raise Http404

	print user.id
	content_type = guess_type(user.picture.name)
	return HttpResponse(user.picture, mimetype=content_type)

@transaction.commit_on_success
@login_required
def dislike(request):
	context = {}

	user = GrumblrUser.objects.filter(username = request.user)[0]
	getUserInfo(context, user, user)
	if request.GET:
		grumble = Grumble.objects.filter(id = request.GET['grumble'])[0]
		grumble.dislikes.add(user)
		return redirect(request.GET['next'])
	return render(request, 'profile.html', context)

@transaction.commit_on_success
@login_required
def disdislike(request):
	context = {}

	user = GrumblrUser.objects.filter(username = request.user)[0]
	getUserInfo(context, user, user)
	if request.GET:
		grumble = Grumble.objects.filter(id = request.GET['grumble'])[0]
		if user in grumble.dislikes.all():
			grumble.dislikes.remove(user)	
		return redirect(request.GET['next'])
	return render(request, 'profile.html', context)


@transaction.commit_on_success
def lostpassword(request):
	return render(request, 'lost-password.html', {})

@transaction.commit_on_success
def recoverpassword(request):
	return render(request, 'recover-password.html', {})

@transaction.commit_on_success
@login_required
def stream(request):
	context = {}

	user = GrumblrUser.objects.filter(username = request.user)[0]

	getGrumbls(context, user, False)
	getUserInfo(context, user, user)

	if request.POST and 'comment' in request.POST:
		comment = Grumble(content = request.POST['comment'], user = user, commentType=True)
		comment.save()
		Grumble.objects.filter(id = request.POST['id'])[0].comments.add(comment)

	return render(request, 'stream.html', context)

@transaction.commit_on_success
@login_required
def other_user (request, name):
	errors = []
	context = {}
	context['errors'] = errors;
	print request
	if 'information' in request.META['PATH_INFO']:
		print 'INFORMATION'
		context['info'] = True

	context['own'] = False
	current_user = GrumblrUser.objects.filter(username = request.user)[0]
	if current_user.username == name:
		return redirect(reverse('profile'))

	users = GrumblrUser.objects.filter(username = name)

	if not users or users[0] in GrumblrUser.objects.filter(blockers=current_user):
		raise Http404

	user = users[0]

	getUserInfo(context, current_user, user)
	getGrumbls(context, user)

	context['following'] = False
	if current_user.following.filter(username = name):
		context['following'] = True
	context['blocked'] = False
	if GrumblrUser.objects.filter(blockers__username=current_user.username):
		context['blocked'] = True
	
	context['url'] = '/profile/' + name
	
	userprofile = GrumblrProfile.objects.filter(user = user)[0]
	context['profile'] = userprofile
	context['values'] = {}
	for field in userprofile._meta.fields[2:]:
		val = getattr(userprofile, field.name)
		if not val:
			context['values'][field.name] = None
		else:
			context['values'][field.name] = (getattr(userprofile, field.name))


	if request.POST:
		if 'follow' in request.POST:
			current_user.following.add(user)
			current_user.save()
		if 'unfollow' in request.POST:
			current_user.following.remove(user)
			current_user.save()
		if 'block' in request.POST:
			user.blockers.add(current_user)
			if current_user in user.following.all():
				user.following.remove(current_user)
			user.save()
		if 'unblock' in request.POST:
			user.blockers.remove(current_user)
			user.save()
		if 'comment' in request.POST:
			comment = Grumble(content = request.POST['comment'], user = current_user, commentType=True)
			comment.save()
			Grumble.objects.filter(id = request.POST['id'])[0].comments.add(comment)


	return render(request, 'profile.html', context)

@transaction.commit_on_success
@login_required
def edit_information (request):

	context = {}
	errors = []
	context['success'] = []
	user = GrumblrUser.objects.filter(username = request.user)[0]
	getUserInfo(context, user, user)
	profile = GrumblrProfile.objects.filter(user = user)[0]

	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			user.picture = request.FILES['picture']
	else:
		form = DocumentForm() # A empty, unbound form

	context['form'] = DocumentForm()
	# Just display the registration form if this is a GET request.
	# if request.method == 'GET':
	context['profile_form'] = ProfileForm(auto_id=False)
	context['editUsername_form'] = EditUsernameForm(auto_id=False)
	context['editEmail_form'] = EditEmailForm(auto_id=False)	
	context['editUsername_form'].setval(user.username)
	context['editEmail_form'].setval(user.email)
	for field in profile._meta.fields[2:]:
		context['profile_form'].setval(getattr(profile, field.name), field.name)
	
		# return render(request, 'edit-information.html', context)

	# Validates the form.
	if request.POST:
		for field in profile._meta.fields[2:]:
			if field.name in request.POST and request.POST[field.name]:
				editProfile_form = ProfileForm(request.POST)
				context['profile_form'] = editProfile_form
				if not editProfile_form.is_valid():
					return render(request, 'edit-information.html', context)
			
				setattr(profile, field.name, editProfile_form.cleaned_data[field.name])
				profile.save()
				success = 'Successfully changed your information'
		
		if 'username' in request.POST:
			editUsername_form = EditUsernameForm(request.POST)
			context['editUsername_form'] = editUsername_form
			
			if not editUsername_form.is_valid():
				return render(request, 'edit-information.html', context)
			user.username = editUsername_form.cleaned_data['username']

		if 'email' in request.POST:
			editEmail_form = EditEmailForm(request.POST)
			context['editEmail_form'] = editEmail_form
			
			if not editEmail_form.is_valid():
				return render(request, 'edit-information.html', context)
			user.email = editEmail_form.cleaned_data['email']

		try:
			user.save()
			context['success'].append('Successfully changed')
		except IntegrityError, e:
			errors.append('Error')

	return render(request, 'edit-information.html', context)


@transaction.commit_on_success
@login_required
def edit_password(request):
	context = {}
	user = GrumblrUser.objects.filter(username = request.user)[0]
	getUserInfo(context, user)
	getGrumbls(context, user)
	
	context['success'] = ''
	context['own'] = True

	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = EditPasswordForm(user)
		return render(request, 'edit-password.html', context)

	# Creates a bound form from the request POST parameters and makes the 
	# form available in the request context dictionary.
	form = EditPasswordForm(user, request.POST)
	context['form'] = form

	# Validates the form.
	if not form.is_valid():
		return render(request, 'edit-password.html', context)

	user.set_password(request.POST['password2'])
	user.save()
	context['success'] = 'Successfully changed password'

	return render(request, 'edit-password.html', context)
	

@transaction.commit_on_success
@login_required
def search(request):
	user = GrumblrUser.objects.filter(username = request.user)[0]
	context = {}
	getUserInfo(context, user, user)

	if 'term' in request.GET and request.GET['term']:
		print user.username
		grumbls = Grumble.objects.exclude(user__blockers__username = user.username).filter(content__contains = request.GET['term']).reverse()
		print grumbls
		grumbls = grumbls.order_by('time').reverse()
		#FIX ME THIS IS A HACK, if grumble is a comment actually include parent
		l = []
		for grumble in grumbls:
			if grumble.commentType:
				l.append(Grumble.objects.filter(comments = grumble)[0])
				print grumbls
			else:
				l.append(grumble)
		term = request.GET['term']
		context['grumbls'] = l
		context['term'] = term;

	if request.POST and 'comment' in request.POST:
		comment = Grumble(content = request.POST['comment'], user = user, commentType=True)
		comment.save()
		Grumble.objects.filter(id = request.POST['id'])[0].comments.add(comment)

	return render(request, 'search.html', context)

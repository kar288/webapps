from django.shortcuts import render
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, authenticate
from django.contrib import auth
from django.db import transaction
from django.http import Http404

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Imports the Item class
from grumblr.models import *
from grumblr.forms import *
from django.http import HttpResponseRedirect
from django.core.validators import *
from django.db import IntegrityError
from collections import *

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

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

	pic = Document(docfile = 'profile-pic.jpg')
	pic.save()
	# If we get here the form data was valid.  Register and login the user.
	new_user = GrumblrUser.objects.create_user(username=form.cleaned_data['username'],
										email = form.cleaned_data['email'],
										password=form.cleaned_data['password1'],
										pic = pic)
	new_user.save()

	new_profile = GrumblrProfile.objects.create(user = new_user)
	new_profile.save()

	# Logs in the new user and redirects to his/her todo list
	new_user = authenticate(username=form.cleaned_data['username'], \
							password=form.cleaned_data['password1'])
	login(request, new_user)
	return redirect(reverse('profile'))

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

	current_user = GrumblrUser.objects.filter(username = request.user)[0]

	if current_user.username == name:
		return redirect(reverse('profile'))

	context['own'] = False
	users = GrumblrUser.objects.filter(username = name)

	if not users:
		errors.append('Did not find user.')
		return render(request, '/profile.html', context)

	user = users[0]

	print GrumblrUser.objects.filter(blockers=current_user)
	if user in GrumblrUser.objects.filter(blockers=current_user):
		raise Http404

	getUserInfo(context, current_user, user)
	getGrumbls(context, user)

	context['following'] = False
	if current_user.following.filter(username = name):
		context['following'] = True
	context['blocked'] = True
	if GrumblrUser.objects.filter(blockers__username=current_user.username):
		context['blocked'] = False

	context['url'] = '/profile/' + name

	if request.POST:
		if 'follow' in request.POST:
			current_user.following.add(user)
		if 'unfollow' in request.POST:
			current_user.following.remove(user)
		if 'comment' in request.POST:
			comment = Grumble(content = request.POST['comment'], user = user, commentType=True)
			comment.save()
			Grumble.objects.filter(id = request.POST['id'])[0].comments.add(comment)


	return render(request, 'profile.html', context)

@transaction.commit_on_success
@login_required
def other_user_info (request, name):
	errors = []
	context = {}
	context['errors'] = errors;
	context['info'] = True

	context['own'] = False
	current_user = GrumblrUser.objects.filter(username = request.user)[0]
	if current_user.username == name:
		context['own'] = True
		return redirect(reverse('profile'))

	users = GrumblrUser.objects.filter(username = name)

	if not users:
		errors.append('Did not find user.')
		return render(request, reverse('profile'), context)

	user = users[0]
	getUserInfo(context, current_user, user)
	getGrumbls(context, user)


	context['following'] = False
	if current_user.following.filter(username = name):
		context['following'] = True
	context['blocked'] = False
	if GrumblrUser.objects.filter(blockers__username=current_user.username):
		context['blocked'] = True

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

	return render(request, '/profile.html', context)

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
			newdoc = Document(docfile = request.FILES['docfile'])
			newdoc.save()
			user.pic = newdoc
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

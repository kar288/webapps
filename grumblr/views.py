from django.shortcuts import render
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, authenticate
from django.contrib import auth
from django.db import transaction

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Imports the Item class
from grumblr.models import *
from django.http import HttpResponseRedirect
from django.core.validators import *
from django.db import IntegrityError
from collections import *

@transaction.commit_on_success
def signin(request):
	context = {}
	errors = {}
	context['errors'] = errors

	if request.user.is_authenticated():
		return redirect('/profile.html')

	if request.GET and request.GET['next']:
		context['next'] = request.GET['next']

	if request.POST:
		username = request.POST['username']
		password = request.POST['password']

		try:
			user = authenticate(username=username, password=password)
			if user is None:
				# the authentication system was unable to verify the username and password
				errors['invalid'] = "The username and password were incorrect."
				return render(request, 'sign-in.html', context)

			# the password verified for the user
			if not user.is_active:
				errors['disabled'] = "The password is valid, but the account has been disabled!"
				return render(request, 'sign-in.html', context)

			login(request, user)

			if 'next' in request.POST and request.POST['next']:
				return redirect(request.POST['next'])

			return redirect('/profile.html')
		except Exception, e:
			print e


	return render(request, 'sign-in.html', context)

@transaction.commit_on_success
@login_required
def profile(request):
	context = {}

	user = GrumblrUser.objects.filter(username = request.user)[0]
	context['username'] = user.username
	picUrl = '/static/' + user.pic.url
	context['pic'] = picUrl

	if 'content' in request.POST:
		grumble = Grumble(content = request.POST['content'], user = user)
		grumble.save()

	grumbls = Grumble.objects.filter(user = user)
	grumbls = grumbls.order_by('time').reverse()

	context['grumbls'] = grumbls
	context['own'] = True
	
	return render(request, 'profile.html', context)

@transaction.commit_on_success
def registration(request):
	context = {}
	values = OrderedDict()
	context['values'] = values
	error = False

	values['email'] = CharField(name = 'email', placeholder = 'E-mail', type = "text")
	values['username'] = CharField(name = 'username', placeholder = 'Username', type = "text")
	values['password1'] = CharField(name = 'password1', placeholder = 'Password', type = "password")
	values['password2'] = CharField(name = 'password2', placeholder = 'Confirm Password', type = "password")
	
	if request.POST:
		email = request.POST['email']
		username = request.POST['username']
		password1 = request.POST['password1']
		password2 = request.POST['password2']
		context['email'] = email
		context['username'] = username

		#highlight missing field
		if email:
			try:
				validate_email(email)
				if GrumblrUser.objects.filter(email=email):
					values['email'].errors = 'Email is taken'
					error = True
			except ValidationError:
				values['email'].errors = 'Invalid email'
				error = True
		else:
			values['email'].errors = 'Add email'
			error = True
		if not username:
			values['username'].errors = 'Add username'
			error = True
		if username and GrumblrUser.objects.filter(username = username):
			values['username'].errors = 'Username is taken'
			error = True
		if not password1:
			values['password1'].errors = 'Add password'
			error = True
		elif not password2:
			values['password1'].errors = 'Confirm password'
			error = True
		elif password1 != password2:
			values['password1'].errors = 'Passwords dont coincide'
			error = True
		
		if not error:
			try:
				user = GrumblrUser.objects.create_user(email = email, username = username, password = password1, pic = 'profile-pic.jpg')
				user.save()
				profile = GrumblrProfile.objects.create(user = user)
				profile.save()
			except IntegrityError, e:
				values['username'].errors = 'Username is taken'
				error = True

		if error:
			return render(request, "registration.html", context)

		user = authenticate(username=username, password=password1)
		login(request, user)
		return redirect('profile.html')

	return render(request, "registration.html", context)


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
	context['user'] = user.username
	picUrl = '/static/' + user.pic.url
	context['pic'] = picUrl

	if 'content' in request.POST:
		grumble = Grumble(content = request.POST['content'], user = user)
		grumble.save()
	grumbls = Grumble.objects.exclude(user = user)
	grumbls = grumbls.order_by('time').reverse()
	context['grumbls'] = grumbls

	return render(request, 'stream.html', context)

@transaction.commit_on_success
@login_required
def other_user (request, name):
	errors = []
	context = {}
	context['errors'] = errors;

	user = GrumblrUser.objects.filter(username = request.user)[0]
	if user.username == name:
		return redirect("/profile.html")

	context['own'] = False
	user = GrumblrUser.objects.filter(username = name)[0]

	if not user:
		errors.append('Did not find user.')
		return render(request, 'profile.html', context)

	picUrl = '/static/' + user.pic.url
	
	grumbls = Grumble.objects.filter(user = user)
	grumbls = grumbls.order_by('time').reverse()

	context['user'] = user.username
	context['pic'] = picUrl
	context['grumbls'] = grumbls

	return render(request, 'profile.html', context)

@transaction.commit_on_success
@login_required
def other_user_info (request, name):
	errors = []
	context = {}
	context['errors'] = errors;
	context['info'] = True

	context['own'] = False
	user = GrumblrUser.objects.filter(username = request.user)[0]
	if user.username == name:
		context['own'] = True

	user = GrumblrUser.objects.filter(username = name)[0]
	profile = GrumblrProfile.objects.filter(user = user)[0]
	context['profile'] = profile
	context['values'] = {}
	for field in profile._meta.fields[2:]:
		val = getattr(profile, field.name)
		if not val:
			context['values'][field.name] = None
		else:
			context['values'][field.name] = (getattr(profile, field.name))

	if not user:
		errors.append('Did not find user.')
		return render(request, 'profile.html', context)

	picUrl = '/static/' + user.pic.url
	
	grumbls = Grumble.objects.filter(user = user)
	grumbls = grumbls.order_by('time').reverse()

	context['user'] = user
	context['pic'] = picUrl
	context['grumbls'] = grumbls

	return render(request, 'profile.html', context)

@transaction.commit_on_success
@login_required
def edit_information (request):

	errors = []
	success = []
	context = {}

	user = GrumblrUser.objects.filter(username = request.user)[0]
	picUrl = '/static/' + user.pic.url
	context['user'] = user
	context['pic'] = picUrl
	profile = GrumblrProfile.objects.filter(user = user)[0]
	context['profile'] = profile
	context['values'] = {}
	for field in profile._meta.fields[2:]:
		val = getattr(profile, field.name)
		if not val:
			context['values'][field.name] = None
		else:
			context['values'][field.name] = val


	if request.POST:
		if 'username' in request.POST:
			user.username = request.POST['username']
			try:
				user.save()
				success.append('Successfully changed username')
			except IntegrityError, e:
				errors.append('username is taken')

		if 'email' in request.POST:
			try:
				validate_email(request.POST['email'])
				if GrumblrUser.objects.filter(email=request.POST['email']):
					errors.append('email is taken')
				else:
					user.email = request.POST['email']
					user.save()
					success.append('Successfully changed e-mail')
			except ValidationError:
				errors.append('invalid email')
				
		if 'password' in request.POST:
			if not authenticate(username=user.username, password=request.POST['password']):
				errors.append("invalid password")
			elif request.POST['newpassword1'] != request.POST['newpassword2']:
				errors.append("passwords don't match")
			else:
				user.set_password(request.POST['newpassword1'])
				user.save()
				success.append('Successfully changed password')

		for field in profile._meta.fields[2:]:
			if field.name in request.POST and request.POST[field.name]:
				setattr(profile, field.name, request.POST[field.name])
				profile.save()
				success = 'Successfully changed your information'

		context['errors'] = errors
		context['succes'] = success

	return render(request, 'edit-information.html', context)


@transaction.commit_on_success
@login_required
def edit_password(request):
	context = {}
	values = OrderedDict()
	context['values'] = values
	error = False

	values['password'] = CharField(name = 'password', placeholder = 'Old Password', type = "password")
	values['password1'] = CharField(name = 'password1', placeholder = 'New Password', type = "password")
	values['password2'] = CharField(name = 'password2', placeholder = 'Confirm New Password', type = "password")

	success = ''
	user = GrumblrUser.objects.filter(username = request.user)[0]
	picUrl = '/static/' + user.pic.url

	if request.POST:				
		if 'password' in request.POST:
			if not authenticate(username=user.username, password=request.POST['password']):
				values['password'].errors = "Invalid password"
			elif request.POST['password1'] != request.POST['password2']:
				values['password1'].errors = "Passwords don't match"
			else:
				user.set_password(request.POST['password1'])
				user.save()
				success = 'Successfully changed password'

	return render(request, 'edit-password.html', {'user': user, 'pic': picUrl,\
	 'own': True, 'values': values, 'success': success})


@transaction.commit_on_success
@login_required
def search(request):
	user = GrumblrUser.objects.filter(username = request.user)[0]
	picUrl = '/static/' + user.pic.url
	context = {'user': user, 'pic': picUrl}

	if 'term' in request.GET and request.GET['term']:
		grumbls = Grumble.objects.filter(content__contains = request.GET['term']).reverse()
		grumbls = grumbls.order_by('time').reverse()
		term = request.GET['term']
		context['grumbls'] = grumbls
		context['term'] = term;

	return render(request, 'search.html', context)

@transaction.commit_on_success
@login_required
def logout(request):
	auth.logout(request)
	return redirect('/sign-in.html')
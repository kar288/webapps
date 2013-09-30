from django.core.validators import *
from django import forms
import grumblr.form_widget
from grumblr.models import *

class DocumentForm(forms.ModelForm):
	class Meta:
		model = GrumblrUser
		fields = ('picture', )
		widgets = {
			'picture': forms.FileInput(attrs={'title': 'Edit'}),
		}

class RegistrationForm(forms.Form):
	email = forms.CharField(max_length = 200, 
								widget=grumblr.form_widget.GrumblrTextInput(attrs={'class' : 'form-control', 'placeholder' : 'E-mail'}))
	username = forms.CharField(max_length = 20,
								widget=grumblr.form_widget.GrumblrTextInput(attrs={'class' : 'form-control', 'placeholder' : 'Username'}))
	password1 = forms.CharField(max_length = 200, 
								widget = grumblr.form_widget.GrumblrPasswordInput(attrs={'class' : 'form-control', 'placeholder' : 'Password'}))
	password2 = forms.CharField(max_length = 200, 
								widget = grumblr.form_widget.GrumblrPasswordInput(attrs={'class' : 'form-control', 'placeholder' : 'Confirm Password'}))


	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean(self):
		# Calls our parent (forms.Form) .clean function, gets a dictionary
		# of cleaned data as a result
		cleaned_data = super(RegistrationForm, self).clean()

		# Confirms that the two password fields match
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			self.fields['password1'].widget.error = 'Passwords did not match.'
			self.fields['password1'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("Passwords did not match.")

		# We must return the cleaned data we got from our parent.
		return cleaned_data


	# Customizes form validation for the username field.
	def clean_username(self):
		# Confirms that the username is not already present in the
		# User model database.
		username = self.cleaned_data.get('username')
		if GrumblrUser.objects.filter(username__exact=username):
			self.fields['username'].widget.error = 'Username is already taken.'
			self.fields['username'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("Username is already taken.")

		# We must return the cleaned data we got from the cleaned_data
		# dictionary
		return username

	# Customizes form validation for the email field.
	def clean_email(self):
		# Confirms that the email is not already present in the
		# User model database.
		email = self.cleaned_data.get('email')
		if GrumblrUser.objects.filter(email__exact=email):
			self.fields['email'].widget.error = 'E-mail is already taken.'
			self.fields['email'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("E-mail is already taken.")
		try:
			validate_email(email)	
		except ValidationError:
			self.fields['email'].widget.error = 'Not a valid e-mail.'
			self.fields['email'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("Not a valid e-mail.")
		# We must return the cleaned data we got from the cleaned_data
		# dictionary
		return email


class ProfileForm(forms.ModelForm):
	class Meta:
		model = GrumblrProfile
		exclude = ('user', )
		widgets = {
			'phone': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Phone', 'value': ''}),
			'age': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Age', 'value': ''}),
			'location': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Location', 'value': ''}),
		}

	def setval(self, val, field):
		self.fields[field].widget.attrs['value'] += val



class EditUsernameForm(forms.ModelForm):
	
	class Meta:
		model = GrumblrUser
		fields = ('username', )
		widgets = {
			'username': forms.TextInput(attrs={'class' : 'form-control user-name',\
											 'placeholder' : 'username', 'value': '',\
											 'data-toggle' : 'popover', 'data-placement' : 'right',\
											 'data-content' : 'Click me to edit me!'}),
		}
	
	# Customizes form validation for the username field.
	def clean_username(self):
		# Confirms that the username is not already present in the
		# User model database.

		username = self.cleaned_data.get('username')
		if GrumblrUser.objects.filter(username__exact=username):
			self.fields['username'].widget.error = 'Username is already taken.'
			self.fields['username'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("Username is already taken.")

		# We must return the cleaned data we got from the cleaned_data
		# dictionary
		return username

	def setval(self, val):
		self.fields['username'].widget.attrs['value'] += val


class EditEmailForm(forms.ModelForm):
	class Meta:
		model = GrumblrUser
		fields = ('email', )
		widgets = {
			'email': forms.TextInput(attrs={'class' : 'form-control user-data', 'placeholder' : 'E-mail', 'value': ''}),
		}
	
	# Customizes form validation for the username field.
	def clean_email(self):
		# Confirms that the email is not already present in the
		# User model database.
		email = self.cleaned_data.get('email')
		print email
		if GrumblrUser.objects.filter(email__exact=email):
			self.fields['email'].widget.error = 'E-mail is already taken.'
			self.fields['email'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("E-mail is already taken.")
		try:
			validate_email(email)	
		except ValidationError:
			self.fields['email'].widget.error = 'Not a valid e-mail.'
			self.fields['email'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("Not a valid e-mail.")
		# We must return the cleaned data we got from the cleaned_data
		# dictionary
		return email


	def setval(self, val):
		self.fields['email'].widget.attrs['value'] += val


class EditPasswordForm(forms.Form):
	password1 = forms.CharField(max_length = 200, 
								widget = grumblr.form_widget.GrumblrPasswordInput(attrs={'class' : 'form-control', 'placeholder' : 'Password'}))
	password2 = forms.CharField(max_length = 200, 
								widget = grumblr.form_widget.GrumblrPasswordInput(attrs={'class' : 'form-control', 'placeholder' : 'Confirm Password'}))

 	def __init__(self, user, data=None):
		self.user = user
		super(EditPasswordForm, self).__init__(data=data)

	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean(self):
		# Calls our parent (forms.Form) .clean function, gets a dictionary
		# of cleaned data as a result
		cleaned_data = super(EditPasswordForm, self).clean()

		# Confirms that the two password fields match
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		if not password1:
			self.fields['password1'].widget.error = 'Password is empty.'
			self.fields['password1'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("Passwords did not match.")
		if not password2:
			self.fields['password2'].widget.error = 'Password is empty.'
			self.fields['password2'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("Passwords did not match.")
		if not self.user.check_password(password1):
			self.fields['password1'].widget.error = 'Invalid password.'
			self.fields['password1'].widget.attrs['class'] += ' wrong'
			raise forms.ValidationError("Passwords did not match.")

		# We must return the cleaned data we got from our parent.
		return cleaned_data

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()
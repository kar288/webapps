from django import forms

class RegisterForm(forms.ModelForm):
	class Meta:
		model = User
		widgets = {
		'password': forms.PasswordInput()
	}
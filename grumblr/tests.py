"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from models import *
from views import *



class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
    

class GrumblrTest(TestCase):
	def test_signin(self):
		client = Client()
		response = client.get('/sign-in.html')
		self.assertEqual(response.status_code, 200)

	def test_register(self):
		client = Client()
		response = client.get('/registration.html')
		self.assertEqual(response.status_code, 200)

	def test_profile(self):
		user = GrumblrUser.objects.create_user(email = "bl@a.com", username = 'kar', password = '1234', pic = 'profile-pic.jpg')
		user.save()
		request = 
		login(request, user)
		client = Client()
		response = client.get('/profile.html')
		self.assertEqual(response.status_code, 200)

	# def test_editinformation(self):
	# 	client = Client()
	# 	response = client.get('/edit-information.html')
	# 	self.assertEqual(response.status_code, 200)
	
	# def test_lostpassword(self):
	# 	client = Client()
	# 	response = client.get('/lost-password.html')
	# 	self.assertEqual(response.status_code, 200)
	
	# def test_recoverpassword(self):
	# 	client = Client()
	# 	response = client.get('/recover-password.html')
	# 	self.assertEqual(response.status_code, 200)

	# def test_search(self):
	# 	client = Client()
	# 	response = client.get('/search.html')
	# 	self.assertEqual(response.status_code, 200)

	# def test_stream(self):
	# 	client = Client()
	# 	response = client.get('/stream.html')
	# 	self.assertEqual(response.status_code, 200)


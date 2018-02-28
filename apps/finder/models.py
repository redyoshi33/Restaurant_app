# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import re
import bcrypt

class usersmanager(models.Manager):
	def basic_validator_register(self, postData):
		errors = {}
		if len(postData['name']) == 0 | len(postData['uname']) == 0:
			errors['blname'] = "Can't leave the name fields empty"		
		elif User.objects.filter(uname=(postData['uname']).lower()).exists():
			errors['alreadyreg'] = "This username is already registered"
		if len(postData['pword']) < 1:
			errors['blpword'] = "Must include password"
		elif postData['pword'] != postData['cpword']:
			errors['cpword'] = 'Passwords do not match'
		if len(errors) == 0:	
			password = bcrypt.hashpw(postData['pword'].encode(), bcrypt.gensalt())
			uid = User.objects.create(name=postData['name'], uname=(postData['uname']).lower(), pword=password)
			errors['user'] = uid
		return errors
		
	def basic_validator_login(self, postData):
		errors={}
		if not User.objects.filter(uname=(postData['uname']).lower()).exists():
			errors['fail'] = 'Email/password input incorrect'
		elif not bcrypt.checkpw(postData['pword'].encode(), User.objects.get(uname=(postData['uname']).lower()).pword.encode()):
			errors['fail'] = 'Email/password input incorrect'
		else:
			uid = User.objects.get(uname=(postData['uname']).lower())
			errors['user'] = uid
		return errors

class Cuisine(models.Model):
	name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

class User(models.Model):
	name = models.CharField(max_length=255)
	username = models.CharField(max_length=255)
	password = models.CharField(max_length=255)
	likes = models.ManyToManyField(Cuisine, related_name='liked_by')
	dislikes = models.ManyToManyField(Cuisine, related_name='disliked_by')
	hates = models.ManyToManyField(Cuisine, related_name='hated_by')
	friends = models.ManyToManyField(User, related_name='friended_by')
	requests_given = models.ManyToManyField(User, related_name='requests_recieved')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects = usersmanager()

class Group(models.Model):
	name = models.CharField(max_length=255)
	members = models.ManyToManyField(User, related_name='groups_in')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

class Restaurant(models.Model):
	name = models.CharField(max_length=255)
	lon = models.DecimalField(max_digits=9, decimal_places=6)
	lat = models.DecimalField(max_digits=9, decimal_places=6)
	cuisine_type = models.ManyToManyField(Cuisine, related_name='restaurants')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
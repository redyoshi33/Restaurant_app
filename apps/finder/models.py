# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import re
import bcrypt

class usersmanager(models.Manager):
	def basic_validator_register(self, postData):
		errors = {}
		if len(postData['name']) == 0 or len(postData['username']) == 0:
			errors['blname'] = "Can't leave the name fields empty"		
		elif User.objects.filter(username=(postData['username']).lower()).exists():
			errors['alreadyreg'] = "This username is already registered"
		if len(postData['password']) < 1:
			errors['blpword'] = "Must include password"
		elif postData['password'] != postData['passwordconfirm']:
			errors['cpword'] = 'Passwords do not match'
		if len(errors) == 0:	
			password = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt())
			uid = User.objects.create(name=postData['name'], username=(postData['username']).lower(), password=password)
			errors['user'] = uid
		return errors
		
	def basic_validator_login(self, postData):
		errors={}
		if not User.objects.filter(username=(postData['username']).lower()).exists():
			errors['fail'] = 'Email/password input incorrect'
		elif not bcrypt.checkpw(postData['password'].encode(), User.objects.get(username=(postData['username']).lower()).password.encode()):
			errors['fail'] = 'Email/password input incorrect'
		else:
			uid = User.objects.get(username=(postData['username']).lower())
			errors['user'] = uid
		return errors

	def unfriend(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		friend = User.objects.get(id=id)
		user.friends.remove(friend)

	def add_like(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		cuisine = Cuisine.objects.get(id=id)
		user.likes.add(cuisine)

	def remove_like(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		cuisine = Cuisine.objects.get(id=id)
		user.likes.remove(cuisine)

	def add_dislike(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		cuisine = Cuisine.objects.get(id=id)
		user.dislikes.add(cuisine)

	def remove_dislike(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		cuisine = Cuisine.objects.get(id=id)
		user.dislikes.remove(cuisine)

	def add_hate(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		cuisine = Cuisine.objects.get(id=id)
		user.hates.add(cuisine)

	def remove_hate(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		cuisine = Cuisine.objects.get(id=id)
		user.hates.remove(cuisine)

class requestsmanager(models.Manager):
	def friend_request(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		friend_user = User.objects.get(id=id)
		user_request = Friendrequest.objects.create(sent_by=user, recieved_by=friend_user)
	def deny_request(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		friend_user = User.objects.get(id=id)
		userrequest = Friendrequest.objects.get(sent_by=friend_user, recieved_by=user)
		userrequest.delete()
	def accept_request(self, sessionid, id):
		user = User.objects.get(id=sessionid)
		friend_user = User.objects.get(id=id)
		user.friends.add(friend_user)
		Friendrequest.objects.deny_request(sessionid, id)

class groupsmanager(models.Manager):
	def make_group(self, postData, sessionid):
		group = Group.objects.create(name=postData['name'])
		user = User.objects.get(id=sessionid)
		group.members.add(user)
		return group.id
	def add_member(self, gid, mid):
		group = Group.objects.get(id=gid)
		user = User.objects.get(id=mid)
		group.members.add(user)
	def leave_group(self,id,sessionid):
		group = Group.objects.get(id=id)
		user = User.objects.get(id=sessionid)
		group.members.remove(user)
		if len(group.members.all()) ==0:
			group.delete()

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
	friends = models.ManyToManyField("self", related_name='friended_by')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects = usersmanager()

class Group(models.Model):
	name = models.CharField(max_length=255)
	members = models.ManyToManyField(User, related_name='groups_in')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects = groupsmanager()

class Restaurant(models.Model):
	name = models.CharField(max_length=255)
	lon = models.DecimalField(max_digits=9, decimal_places=6)
	lat = models.DecimalField(max_digits=9, decimal_places=6)
	cuisine_type = models.ManyToManyField(Cuisine, related_name='restaurants')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

class Friendrequest(models.Model):
	sent_by = models.ForeignKey(User, related_name='requests_sent')
	recieved_by = models.ForeignKey(User, related_name='requests_recieved')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects = requestsmanager()
























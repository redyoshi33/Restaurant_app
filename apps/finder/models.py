# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import re
import bcrypt
import requests
import json
import random


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
		user = User.objects.get(id=sessionid)
		plus='+'
		url = 'https://maps.googleapis.com/maps/api/geocode/json?address=?'
		address1 =  postData['address1'].split()
		address2 = postData['address2'].split()
		for x in address2:
			address1.append(x)
		temp = plus.join([str(x) for x in address1])
		url += temp
		apikey = '&key=AIzaSyB5OfM5SkK0FFmAIRQRKWn5J4yRvd8nq_Q'
		url += apikey
		response = requests.get(url)
		json_data = json.loads(response.text)
		if(json_data['results']):
			latitude =  json_data['results'][0]['geometry']['location']['lat']
			longitude = json_data['results'][0]['geometry']['location']['lng']
			group = Group.objects.create(name=postData['name'], lat=latitude, lon=longitude)
			group.members.add(user)
			return group.id
		return False
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
	def randomcuisine(self, id):
		group = Group.objects.get(id=id)
		members = group.members.all()
		cuisines = Cuisine.objects.all()
		excluded = []
		cuisinepoints = {}
		total = 0 
		for member in members:
			for hate in member.hates.all():
				if hate not in excluded:
					excluded.append(hate)
		for cuisine in cuisines:
			if cuisine not in excluded:
				cuisinepoints[cuisine.name] = 0
		for member in members:
			for likes in member.likes.all():
				if likes not in excluded:
					cuisinepoints[likes.name] += 1
			for dislikes in member.dislikes.all():
				if dislikes not in excluded:
					cuisinepoints[dislikes.name] -= 1
		for x in cuisinepoints:
			if cuisinepoints[x] > 0:
				total += cuisinepoints[x]
			
		for x in cuisinepoints:
			if cuisinepoints[x] > 0:
				cuisinepoints[x] = float(cuisinepoints[x])/float(total)

		apikey = 'o8NWFy7GaV5Eg6A42a4WUekBxdipkF0Cg7cfsdKMyzMG7qUiXbq--lOx4_FGX3_B8L6BnnXl743SPoB0QwYmz0k6nXcP5UJFr5nDWgFBhQypv10QjoI9W9UVS0-XWnYx'
		headers = {'Authorization': 'Bearer %s' % apikey}
		parameters = {
			'term':'restaurants',
			'latitude': group.lat,
			'longitude': group.lon,
			'radius':10000,
		}
		##Alias: is category
		
		response = requests.get("https://api.yelp.com/v3/businesses/search", params=parameters, headers=headers)
		json_data=json.loads(response.text)

		restaurants =[]
		for x in  json_data['businesses']:
			restaurant = {}
			restaurant['name']= x['name']
			restaurant['cuisine'] = x['categories'][0]['alias']
			restaurant['address'] = " ".join(x['location']['display_address'])
			restaurant['lat'] = x['coordinates']['latitude']
			restaurant['lon'] = x['coordinates']['longitude']
			restaurants.append(restaurant)

		random.shuffle(restaurants)

		selections = []
		for i in range(0,3):
			temp_sum = 0
			rand = random.random()
			for x in cuisinepoints:
				if cuisinepoints[x] > 0:
					if rand < temp_sum + cuisinepoints[x]:
						selections.append(x)
						break
					temp_sum += cuisinepoints[x]
		choices = []
		for selection in selections:		
			for rest in restaurants:
				if rest['cuisine'].lower() == selection.lower():
					if rest not in choices:
						choices.append(rest)
						break
		return choices

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
	lon = models.DecimalField(max_digits=9, decimal_places=6)
	lat = models.DecimalField(max_digits=9, decimal_places=6)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects = groupsmanager()


class Friendrequest(models.Model):
	sent_by = models.ForeignKey(User, related_name='requests_sent')
	recieved_by = models.ForeignKey(User, related_name='requests_recieved')
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	objects = requestsmanager()
























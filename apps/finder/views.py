# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import *
import bcrypt

def index(request):
	return render(request, 'finder/login.html')

def dashboard(request):
	if 'uid' not in request.session:
		return redirect('/main')
	user = User.objects.get(id=request.session['uid'])
	context = {
		'userinfo': User.objects.get(id=request.session['uid']),
		'sessionid': request.session['uid'],
		'myfriends': user.friends.all()
	}
	return render(request, 'finder/dashboard.html', context)

def regis(request):
	if request.method == 'POST':
		errors = User.objects.basic_validator_register(request.POST)
		if 'user' in errors:
			request.session['uid'] = errors['user'].id
			return redirect('/dashboard')
		else:
			for tag, error in errors.iteritems():
				messages.error(request, error, extra_tags=tag)
			return redirect('/main')

def login(request):
	if request.method == 'POST':
		errors = User.objects.basic_validator_login(request.POST)
		if 'user' not in errors:
			for tag, error in errors.iteritems():
				messages.error(request, error, extra_tags=tag)
			return redirect('/main')
		else:
			request.session['uid'] = errors['user'].id
			return redirect('/dashboard')

def profile(request, id):
	
	user = User.objects.get(id=request.session['uid'])
	friends = Friendrequest.objects.filter(recieved_by=user)
	user_friends = []
	for friend in friends:
		user_friends.append(friend.sent_by)
	context = {
		'user': User.objects.get(id=id),
		'sessionid': request.session['uid'],
		'friends': user_friends
	}
	return render(request, 'finder/profile.html', context)

def addfriends(request):
	#looping through friend requests to convert into user objects. comparing user objects with user objects if the request has been sent or recieved by this user.
	this_user = User.objects.get(id=request.session['uid'])
	users = User.objects.exclude(id=request.session['uid']).exclude(friends=this_user)
	requests = Friendrequest.objects.filter(sent_by=this_user)
	requests2 = Friendrequest.objects.filter(recieved_by=this_user)
	excludedusers = []
	newusers = []
	for x in requests:
		excludedusers.append(x.recieved_by)
	for x in requests2:
		excludedusers.append(x.sent_by)
	for x in users:
		if x not in excludedusers:
			newusers.append(x)
	context = {
		'users': newusers,
		'sessionid': request.session['uid'],
	}
	return render(request, 'finder/friends.html', context)

def requestfriends(request, id):
	Friendrequest.objects.friend_request(request.session['uid'], id)
	return redirect('/addfriends')

def denyfriends(request, id):
	Friendrequest.objects.deny_request(request.session['uid'], id)
	return redirect('/profile/'+str(request.session['uid']))

def acceptfriends(request, id):
	Friendrequest.objects.accept_request(request.session['uid'], id)
	return redirect('/profile/'+str(request.session['uid']))

def unfriend(request,id):
	User.objects.unfriend(request.session['uid'], id)
	return redirect('/dashboard')

def creategroup(request):
	context = {
		'sessionid': request.session['uid'],
	}
	return render(request, 'finder/creategroup.html', context)

def group(request, id):
	context = {
		'sessionid': request.session['uid'],
	}
	return render(request, 'finder/group.html', context)

def results(request, id):
	context = {
		'sessionid': request.session['uid'],
	}
	return render(request, 'finder/option.html', context)

def logout(request):
	request.session.clear()
	errors = {}
	errors['logout'] = "Successfully logged out!"
	for tag, error in errors.iteritems():
		messages.error(request, error, extra_tags=tag)
	return redirect('/main')

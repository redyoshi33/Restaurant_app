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
		'myfriends': user.friends.all(),
		'mygroups': Group.objects.filter(members=user)
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
	user = User.objects.get(id=id)
	friends = Friendrequest.objects.filter(recieved_by=user)
	user_friends = []
	for friend in friends:
		user_friends.append(friend.sent_by)
	if len(user_friends) > 0:
		no_request = False
	else:
		no_request = True
	context = {
		'user': user,
		'sessionid': request.session['uid'],
		'friends': user_friends,
		'likes': user.likes.all(),
		'dislikes': user.dislikes.all(),
		'hates': user.hates.all(),
		'no_request': no_request
	}
	return render(request, 'finder/profile.html', context)

def preferences(request):
	user = User.objects.get(id=request.session['uid'])
	likes = user.likes.all()
	dislikes = user.dislikes.all()
	hates = user.hates.all()
	cuisines = Cuisine.objects.all()
	othercuisines = []
	for x in cuisines:
		if x not in likes and x not in hates and x not in dislikes:
			othercuisines.append(x)
	context = {
		'user': User.objects.get(id=request.session['uid']),
		'likes': likes,
		'dislikes': dislikes,
		'hates': hates,
		'other': othercuisines,
	}
	return render(request, 'finder/preferences.html', context)

def add_like(request, id):
	User.objects.add_like(request.session['uid'], id)
	return redirect('/profile/preferences')

def remove_like(request, id):
	User.objects.remove_like(request.session['uid'], id)
	return redirect('/profile/preferences')

def add_dislike(request, id):
	User.objects.add_dislike(request.session['uid'], id)
	return redirect('/profile/preferences')

def remove_dislike(request, id):
	User.objects.remove_dislike(request.session['uid'], id)
	return redirect('/profile/preferences')

def add_hate(request, id):
	User.objects.add_hate(request.session['uid'], id)
	return redirect('/profile/preferences')

def remove_hate(request, id):
	User.objects.remove_hate(request.session['uid'], id)
	return redirect('/profile/preferences')

def addfriends(request):
	#looping through friend requests to convert into user objects. comparing user objects with user objects if the request has been sent or recieved by this user.
	this_user = User.objects.get(id=request.session['uid'])

	if request.method == 'POST':
		users = User.objects.exclude(id=request.session['uid']).exclude(friends=this_user).filter(name = request.POST['search'])

	else:
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

def submitgroup(request):
	if request.method == 'POST':
		groupid = Group.objects.make_group(request.POST, request.session['uid'])
		if(groupid):
			return redirect('/group/'+str(groupid))
		else:
			return redirect('/creategroup')

def group(request, id):
	group = Group.objects.get(id=id)
	group_members = group.members.all()
	user = User.objects.get(id=request.session['uid'])
	if request.method == 'POST':
		print request.POST['search']
		user_friends = user.friends.filter(name = request.POST['search'])
		print user_friends
	else:
		user_friends = user.friends.all()
	friends_to_add = []
	for x in user_friends:
		if x not in group_members:
			friends_to_add.append(x)
	context = {
		'sessionid': request.session['uid'],
		'group': group,
		'users': group_members,
		'myfriends': friends_to_add,
	}
	return render(request, 'finder/group.html', context)

def addmember(request, gid, mid):
	Group.objects.add_member(gid,mid)
	return redirect('/group/'+str(gid))

def leavegroup(request, id):
	Group.objects.leave_group(id,request.session['uid'])
	return redirect('/dashboard')

def generate(request, id):
	group = Group.objects.get(id=id)
	choices = Group.objects.randomcuisine(id)
	if len(choices) > 0:
		no_options = False
	else:
		no_options = True
	context = {
		'choices': choices,
		'group': group,
		'sessionid': request.session['uid'],
		'no_options': no_options,
	}
	return render(request, 'finder/option.html', context)


def logout(request):
	request.session.clear()
	errors = {}
	errors['logout'] = "Successfully logged out!"
	for tag, error in errors.iteritems():
		messages.error(request, error, extra_tags=tag)
	return redirect('/main')

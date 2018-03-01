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
	context = {
		'userinfo': User.objects.get(id=request.session['uid']),
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


def logout(request):
	request.session.clear()
	errors = {}
	errors['logout'] = "Successfully logged out!"
	for tag, error in errors.iteritems():
		messages.error(request, error, extra_tags=tag)
	return redirect('/main')

#!/usr/bin/env python
# coding: utf8
# author: $pdb & $vim

# django modules
from django.db.models import Q
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

# wam modules
from wam.settings import WAM_VENDOR_LOGO_URL
from wam.apps.am.models import Vendor, Rule, Diff, Package


@login_required(login_url='/login/')
def index_view(request):
    """ idm模块主页 """
    return render(request, 'idm/index.html')


@login_required(login_url='/login/')
def info_view(request):
    """ info_m Index"""
    return render(request, 'idm/info_m.html')

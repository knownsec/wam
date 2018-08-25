#!/usr/bin/env python
# coding: utf8
# author: $pdb & $vim

"""
    Login, Logout, Index, Settings.. @ 201508
"""

# django modules
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login, authenticate, logout as django_logout

# monitor modules
from monitor.core.settings import MONITOR_CHECK_INTERVAL, DOWNLOAD_MAX_BYTES, DIFF_FILTER_EXT

# wam modules
from wam.apps.main.models import Config


@login_required(login_url='/login/')
def index_view(request):
    """ wam系统主页 """
    return render(request, 'index.html')


def login_view(request):
    """ wam系统登录页面 """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if not user:
            response = '<script>alert("Failed to verify your username or password!");'
            response += 'location.href="/login/";</script>'
            return HttpResponse(response)

        django_login(request, user)
        return HttpResponseRedirect(reverse('index'))
    else:
        if not request.user.is_authenticated():
            return render(request, 'login.html')

        if request.user.is_authenticated():
            return redirect('/')


@login_required(login_url='/login/')
def logout_view(request):
    """ wam系统等出处理 """
    django_logout(request)
    return redirect('/login/')


@login_required(login_url='/login/')
def settings_view(request):
    """ wam系统全局参数设置页面 """
    return render(request, 'settings.html')


@login_required(login_url='/login/')
def set_am(request):
    if request.method == 'POST':
        try:
            monitor_check_interval = request.POST['MONITOR_CHECK_INTERVAL']
            download_max_bytes = request.POST['DOWNLOAD_MAX_BYTE']
            diff_filter_ext = request.POST['DIFF_FILTER_EXT']

            errors = []
            if int(monitor_check_interval) < 0:
                errors.append('invalid value "%r" of MONITOR_CHECK_INTERVAL' % monitor_check_interval)
            if int(download_max_bytes) < 0:
                errors.append('invalid value "%r" of DOWNLOAD_MAX_BYTEL' % monitor_check_interval)
            try:
                diff_filter_ext.split(',')
            except:
                errors.append('invalid format "%r" of DIFF_FILTER_EXTL' % diff_filter_ext)
            if errors:
                return HttpResponse('\n'.join(['<script>alert("%s")</script>' % _ for _ in errors]))

            mci = Config.objects.filter(key='MONITOR_CHECK_INTERVAL').first()
            if mci:
                mci.value = monitor_check_interval
                mci.save()
            dmb = Config.objects.filter(key='DOWNLOAD_MAX_BYTE').first()
            if dmb:
                dmb.value = download_max_bytes
                dmb.save()
            dfe = Config.objects.filter(key='DIFF_FILTER_EXT').first()
            if dfe:
                dfe.value = diff_filter_ext
                dfe.save()

            response = '<script>alert("Success!");location.href=document.referrer;</script>'
            return HttpResponse(response)
        except Exception, ex:
            response = '<script>alert("Cant update configs!");alert("%s");' % str(ex)
            response += 'location.href=document.referrer;</script>'
            return HttpResponse(response)
    else:
        configs = {}
        monitor_check_interval = Config.objects.filter(key='MONITOR_CHECK_INTERVAL').first()
        download_max_bytes = Config.objects.filter(key='DOWNLOAD_MAX_BYTES').first()
        diff_filter_ext = Config.objects.filter(key='DIFF_FILTER_EXT').first()

        if not monitor_check_interval:
            Config(key='MONITOR_CHECK_INTERVAL', value=MONITOR_CHECK_INTERVAL).save()
        if not download_max_bytes:
            Config(key='DOWNLOAD_MAX_BYTES', value=DOWNLOAD_MAX_BYTES).save()
        if not diff_filter_ext:
            Config(key='DIFF_FILTER_EXT', value=DIFF_FILTER_EXT).save()

        configs['mci'] = monitor_check_interval.value
        configs['dmb'] = download_max_bytes.value
        configs['dfe'] = diff_filter_ext.value

        return render(request, 'set_am.html', {'configs': configs})


@login_required(login_url='/login/')
def set_idm(request):
    return render(request, 'set_idm.html')

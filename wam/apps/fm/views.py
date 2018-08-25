#!/usr/bin/env python
# coding: utf8

# __buildin__ modules
import os
import re

# thirdparty modules
import requests

# django modules
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

# wam modules
from wam.settings import FILE_STORE_DIR
from wam.apps.am.models import Vendor
from wam.apps.fm.models import FRule, FFile, FDiff
from wam.apps.am.utils import check_filter, process_rule_rename, pagination

# monitor modules
from monitor.core.download import REQUEST_USER_AGENT


@login_required(login_url='/login/')
def check_file_filter_content(request):
    """ 使用匹配规则从下载地址中匹配出最终的下载链接 """
    if request.method == 'POST':
        source_url = request.POST['source_url']
        regex_content = request.POST['regex_content'].strip()
        if not regex_content or regex_content == '':
            response = 'No regex_content provided'
            return HttpResponse(response)

        try:
            response = requests.get(source_url, timeout=8, headers={'User-Agent': REQUEST_USER_AGENT})
        except requests.exceptions.RequestException:
            try:
                response = requests.get(source_url, timeout=8, headers={'User-Agent': REQUEST_USER_AGENT})
            except Exception, ex:
                response = 'Connection error! ("%s")' % str(ex)
                return HttpResponse(response)

        try:
            match = re.search(regex_content, response.content, re.DOTALL)
            content = '%s' % match.group('content') \
                if match else '(Nothing)'
            return HttpResponse(content)
        except Exception, ex:
            response = 'Fetch filter content error! ("%s")' % str(ex)
            return HttpResponse(response)
    else:
        response = 'POST method required'
        return HttpResponse(response)


@login_required(login_url='/login/')
def index_view(request):
    """ FM模块主页 """
    fdiffs = FDiff.objects.order_by('-add_time').all()[:20]
    avatar_list = ['elliot.jpg', 'jenny.jpg', 'joe.jpg', 'matt.jpg']
    return render(request, 'fm/index.html', {'fdiffs': fdiffs, 'avatar_list': avatar_list})


@login_required(login_url='/login/')
def frules_index(request):
    """ FM模块规则页面主页 """
    limit = 12  # 每页所显示的规则数量
    rules = FRule.objects.order_by('-add_time').all()
    paginator = Paginator(rules, limit)
    page = request.GET.get('page')
    try:
        frules = paginator.page(page)
    except PageNotAnInteger:
        frules = paginator.page(1)
    except EmptyPage:
        frules = paginator.page(paginator.num_pages)

    page_content = pagination(frules)

    # vendor list
    vendor_list = Vendor.objects.all()
    return render(request, 'fm/rules.html', {'frules': frules,
                                             'page_content': page_content,
                                             'vendor_list': vendor_list})


@login_required(login_url='/login/')
def frule_add(request):
    """ FM模块添加文件下载规则 """
    if request.method == 'GET':
        return redirect('/fm/rules/')
    else:
        try:
            name = request.POST['name']
            desc = request.POST['description']
            source_url = request.POST['source_url']
            regex = request.POST['regex']
            vendor_id = request.POST['vendor_id']
            regex_content = request.POST['regex_content'].strip()

            frule = FRule(name=name, desc=desc, source_url=source_url, regex=regex, regex_content=regex_content, vendor_id=vendor_id)
            frule.save()

            response = '<script>alert("Success!");location.href=document.referrer;</script>'
            return HttpResponse(response)
        except Exception, ex:
            response = '<script>alert("Error!");alert("%s");' % str(ex)
            response += 'location.href=document.referrer;</script>'
            return HttpResponse(response)


@login_required(login_url='login/')
def frule_edit(request, frule_id):
    """ FM模块编辑应用包下载规则 """
    try:
        frule = FRule.objects.filter(id=frule_id).first()
        if not frule:
            response = '<script>alert("Rule id not exist!");'
            response += 'location.href=document.referrer;</script>'
            return HttpResponse(response)

        name = request.POST['name'].strip()
        desc = request.POST['description'].strip()
        source_url = request.POST['source_url'].strip()
        regex = request.POST['regex'].strip()
        regex_content = request.POST['regex_content'].strip()
        vendor_id = request.POST['vendor_id']

        if name != frule.name:
            if check_filter(name):
                response = '<script>alert("New rule name contain filter chars!");'
                response += 'location.href=document.referrer;</script>'
                return HttpResponse(response)
            try:
                process_rule_rename(frule.id, name)
            except Exception, ex:
                response = '<script>alert("Cant rename rule!");alert("%s");' % str(ex)
                response += 'location.href=document.referrer;</script>'
                return HttpResponse(response)

        frule.name = name
        frule.desc = desc
        frule.source_url = source_url
        frule.regex = regex
        frule.regex_content = regex_content
        frule.vendor_id = vendor_id
        frule.save()

        response = '<script>alert("Success!");location.href=document.referrer;</script>'
        return HttpResponse(response)
    except Exception, ex:
        response = '<script>alert("Error!");alert("%s");' % str(ex)
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)


@login_required(login_url='/login/')
def frule_del(request, rule_id):
    """ FM模块删除文件下载规则 """
    try:
        FRule.objects.get(id=rule_id).delete()
        response = '<script>alert("Success!");location.href=document.referrer;</script>'
        return HttpResponse(response)
    except Exception, ex:
        response = '<script>alert("Error!");alert("%s");' % str(ex)
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)


@login_required(login_url='/login/')
def frules_list(request, rule_id):
    return render(request, 'fm/diff_list.html')


@login_required(login_url='/login/')
def fdiff_index(request):
    """ FM模块Diff页面主页 """
    limit = 8  # 每页显示Diff数量
    fdiffs = FDiff.objects.order_by('-add_time').all()

    paginator = Paginator(fdiffs, limit)
    page = request.GET.get('page')
    try:
        fdiffs = paginator.page(page)
    except PageNotAnInteger:
        fdiffs = paginator.page(1)
    except EmptyPage:
        fdiffs = paginator.page(paginator.num_pages)

    page_content = pagination(fdiffs)

    return render(request, 'fm/diff_index.html', {'fdiffs': fdiffs, 'page_content': page_content})


@login_required(login_url='/login/')
def fdiff_detail(request, fdiff_id):
    """ FM模块Diff详情页面 """
    fdiff = FDiff.objects.filter(id=fdiff_id).first()
    if fdiff:
        return render(request, 'fm/diff_detail.html', {'fdiff': fdiff})

    return redirect('/fm/diff/')


@login_required(login_url='/login/')
def file_download(request, package_id):
    """ FM模块文件下载处理 """
    def readfile(filepath, block=262144):
        f = open(filepath, 'rb')
        while True:
            c = f.read(block)
            if c:
                yield c
            else:
                break
        f.close()

    ffile = FFile.objects.filter(id=package_id).first()
    if not ffile:
        response = '<script>alert("Package Not Found!");'
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)

    path = ffile.path.encode('utf-8')
    absolute_path = os.path.join(FILE_STORE_DIR, path)
    if os.path.exists(absolute_path):
        response = StreamingHttpResponse(readfile(absolute_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=%s' \
                                          % (ffile.timestamp + '_' + ffile.filename)
        return response
    else:
        response = '<script>alert("Package Not Exists!");'
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)

#!/usr/bin/env python
# coding: utf8
# author: $pdb & $vim

"""
    AM Model: This module can monitor every updates on all of apps on internet,
    analysising the changes to make Tag and provide mail notification; @ 201508
"""

# __buildin__ modules
import re
import os
import json as simplejson
import datetime
import sys
from django.conf import settings
reload(sys)
sys.setdefaultencoding('utf8')

# thirdparty modules
import requests

# email modules
from mail import MAIL

# django modules
from django.http import StreamingHttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

# wam modules
from wam.settings import WAM_VENDOR_LOGO_URL, PACKAGE_SOTRE_DIR
from wam.apps.am.models import Vendor, Rule, Diff, Analysis, Package
from wam.apps.fm.models import FRule, FFile, FDiff
from wam.apps.am.utils import parse_analysis_result,process_rule_rename, check_filter, pagination

# monitor modules
from monitor.core.download import patch_download_url, REQUEST_USER_AGENT


@login_required(login_url='/login/')
def check_download_url(request):
    """ 使用匹配规则从下载地址中匹配出最终的下载链接 """
    if request.method == 'POST':
        source_url = request.POST['source_url']
        regex = request.POST['regex'].strip()
        if not regex or regex == '':
            response = 'No regex provided'
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
            match = re.search(regex, response.content, re.IGNORECASE)
            content = '%s' % patch_download_url(source_url, match.group('download_url')) \
                if match else '(Nothing)'
            return HttpResponse(content)
        except Exception, ex:
            response = 'Fetch download url error! ("%s")' % str(ex)
            return HttpResponse(response)
    else:
        response = 'POST method required'
        return HttpResponse(response)


@login_required(login_url='/login/')
def index_view(request):
    """ AM模块主页 /am/ """
    diffs = Diff.objects.order_by('-add_time').all()
    t_diffs = []
    for diff in diffs[:50]:
        analysis = Analysis.objects.filter(diff=diff).order_by('-add_time').first()
        analysis_result = parse_analysis_result(analysis.result)
        t_diffs.append({'diff': diff, 'analysis_result': analysis_result})

    return render(request, 'am/index.html',
                  {'t_diffs': t_diffs, 'logo_url': WAM_VENDOR_LOGO_URL})


@login_required(login_url='/login/')
def diff_index(request):
    """ AM模块Diff页面主页 /am/diff/ """
    limit = 8  # 每页显示Diff数量
    diffs = Diff.objects.order_by('-add_time').all()
    t_diffs = []
    for diff in diffs:
        analysis = Analysis.objects.filter(diff=diff).order_by('-add_time').first()
        analysis_result = parse_analysis_result(analysis.result)
        t_diffs.append({'diff': diff, 'analysis_result': analysis_result})

    paginator = Paginator(t_diffs, limit)
    page = request.GET.get('page')
    try:
        t_diffs = paginator.page(page)
    except PageNotAnInteger:
        t_diffs = paginator.page(1)
    except EmptyPage:
        t_diffs = paginator.page(paginator.num_pages)

    page_content = pagination(t_diffs)

    return render(request, 'am/diff_index.html', {'t_diffs': t_diffs,
                                                  'page_content': page_content})


@login_required(login_url='/login/')
def diff_detail(request, diff_id):
    """ AM模块Diff详情页面 /am/diff/detail/(\d+) """
    diff = Diff.objects.filter(id=diff_id).first()
    analysis = Analysis.objects.filter(diff=diff).first()
    analysis_result = parse_analysis_result(analysis.result)
    if diff:
        return render(request, 'am/diff_detail.html',
                      {'diff': diff, 'analysis_result': analysis_result})

    return redirect('/am/diff/')


@login_required(login_url='/login/')
def vendor_index(request):
    """ AM模块厂商页面主页 /am/vendor/ """
    vendors = Vendor.objects.order_by('-add_time').all()
    vendors_report = []
    all_rules = Rule.objects.all()
    for vendor in vendors:
        rules = Rule.objects.filter(vendor=vendor).all()
        packages = Package.objects.filter(rule__in=rules).order_by('-add_time').all()
        diffs = Diff.objects.filter(
            Q(s_package__in=packages) | Q(d_package__in=packages)).order_by('add_time').all()

        rules_count = rules.count()
        diffs_count = diffs.count()
        vendors_report.append((vendor, rules_count, diffs_count))

    return render(request, 'am/vendor.html',
                  {'all_rules': all_rules, 'vendors_report': vendors_report,
                   'LOGO_PATH': WAM_VENDOR_LOGO_URL, 'rules_count': all_rules.count(),
                   'vendor_count': vendors.count()})


@login_required(login_url='/login/')
def vendor_detail(request, vendor_id):
    """ AM模块厂商详情页面 /am/vendor/(\d+) """
    vendor = Vendor.objects.filter(id=vendor_id).first()
    rules = Rule.objects.filter(vendor=vendor).order_by('-add_time').all()
    packages = Package.objects.filter(rule__in=rules).order_by('-add_time').all()
    frule = FRule.objects.order_by('-add_time').filter(id=vendor_id)

    fdiffs = FDiff.objects.filter(
        Q(s_file__in=frule) | Q(d_file__in=frule)).order_by('-add_time').all()

    diffs = Diff.objects.filter(
        Q(s_package__in=packages) | Q(d_package__in=packages)).order_by('-add_time').all()
    t_diffs = []
    for diff in diffs:
        analysis = Analysis.objects.filter(diff=diff).order_by('-add_time').first()
        analysis_result = parse_analysis_result(analysis.result)
        t_diffs.append({'diff': diff, 'analysis_result': analysis_result})

    analysis_results = Analysis.objects.filter(diff__in=diffs).order_by('add_time').all()

    diff_report = [0] * 12
    for diff in diffs:
        m = diff.add_time.month
        diff_report[m - 1] += 1

    tags_report = {}
    for analysis_result in analysis_results:
        results = simplejson.loads(analysis_result.result)

        for result in results:
            tags_report[result['tag']] = [0] * 12

    for analysis_result in analysis_results:
        results = simplejson.loads(analysis_result.result)
        m = analysis_result.add_time.month
        for result in results:
            if result['reports']:
                tags_report[result['tag']][m - 1] += 1
    try:
        end_tdiff_time = t_diffs[0]['diff'].add_time
    except:
        end_tdiff_time = '2000-00-00'
    return render(request, 'am/vendor_detail.html',
                  {'vendor': vendor, 'logo_url': WAM_VENDOR_LOGO_URL,
                   't_diffs': t_diffs, 'diff_report': diff_report,
                   'tags_report': tags_report,
                   'f_diffs': fdiffs,
                   'end_tdiff_time': end_tdiff_time})


@login_required(login_url='/login/')
def vendor_add(request):
    """ AM模块添加厂商信息 """
    if request.method == 'GET':
        return redirect('/am/rules/')
    else:
        try:
            name = request.POST['name']
            website = request.POST['website']
            description = request.POST['description']

            logo = request.FILES.get('logo', None)
            if logo:
                vendor = Vendor(name=name, site=website, desc=description, logo=logo)
                vendor.save()
                # 取自动上传处理后的LOGO文件名作为LOGO信息存储
                vendor.logo.name = os.path.basename(vendor.logo.name)
                vendor.save()
            else:
                vendor = Vendor(name=name, site=website, desc=description)
                vendor.save()

            response = '<script>alert("Success!");location.href=document.referrer;</script>'
            return HttpResponse(response)
        except Exception, ex:
            response = '<script>alert("Error!");alert("%s");' % str(ex)
            response += 'location.href=document.referrer;</script>'
            return HttpResponse(response)


@login_required(login_url='/login/')
def vendor_edit(request, vendor_id):
    """ AM模块编辑厂商信息 """
    try:
        vendor = Vendor.objects.filter(id=vendor_id).first()
        if not vendor:
            response = '<script>alert("Vendor id not exist!");'
            response += 'location.href=document.referrer;</script>'
            return HttpResponse(response)

        name = request.POST['name']
        website = request.POST['website']
        description = request.POST['description']
        logo = request.FILES.get('logo', None)

        vendor.name = name
        vendor.site = website
        vendor.desc = description
        if logo:
            vendor.logo = logo
        vendor.save()
        # 取自动上传处理后的LOGO文件名作为LOGO信息存储
        vendor.logo.name = os.path.basename(vendor.logo.name)
        vendor.save()

        response = '<script>alert("Success!");location.href=document.referrer;</script>"'
        return HttpResponse(response)
    except Exception, ex:
        response = '<script>alert("Error!");alert("%s");' % str(ex)
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)


@login_required(login_url='/login/')
def vendor_del(request, vendor_id):
    """ AM模块删除厂商信息 ###未使用### """
    try:
        # TODO 外键引起的递归删除处理
        Vendor.objects.get(id=vendor_id).delete()
        response = '<script>alert("Success!");location.href=document.referrer;</script>"'
        return HttpResponse(response)
    except Exception, ex:
        response = '<script>alert("Error!");alert("%s");' % str(ex)
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)


@login_required(login_url='/login/')
def rules_index(request):
    """ AM模块规则页面主页 /am/rules/ """
    limit = 50  # 每页所显示的规则数量
    vendors = Vendor.objects.all()
    rules = Rule.objects.order_by('-add_time').all()
    paginator = Paginator(rules, limit)
    page = request.GET.get('page')
    try:
        rules = paginator.page(page)
    except PageNotAnInteger:
        rules = paginator.page(1)
    except EmptyPage:
        rules = paginator.page(paginator.num_pages)

    page_content = pagination(rules)

    return render(request, 'am/rules.html', {'vendors': vendors, 'rules': rules, 'page_content': page_content})

@login_required(login_url='/login/')
def rule_find(request, rule_id):
    limit = 50  # 每页所显示的规则数量
    vendors = Vendor.objects.all()
    rules = [Rule.objects.get(id=rule_id)]
    paginator = Paginator(rules, limit)
    page = request.GET.get('page')
    try:
        rules = paginator.page(page)
    except PageNotAnInteger:
        rules = paginator.page(1)
    except EmptyPage:
        rules = paginator.page(paginator.num_pages)

    page_content = pagination(rules)

    return render(request, 'am/rules.html', {'vendors': vendors, 'rules': rules, 'page_content': page_content})

@login_required(login_url='/login/')
def rules_search(request):
    """ AM模块规则页面搜索 /am/rules/search """
    vendors = Vendor.objects.all()
    keyword = request.GET.get('q')
    rules = Rule.objects.filter(name__icontains=keyword)
    response_data = {}
    response_data['results'] = []
    for rule in rules:
        item = {}
        if rule.vendor.logo.name:
            item['image'] = settings.WAM_VENDOR_LOGO_URL + rule.vendor.logo.name
        else:
            item['image'] = settings.WAM_VENDOR_LOGO_URL + "logo.png"
        item['title'] = rule.name
        item['url'] = '/am/rules/%s' %rule.id
        response_data['results'].append(item)

    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")

@login_required(login_url='/login/')
def rule_add(request):
    """ AM模块添加应用包下载规则 /am/rules/rule/add """
    if request.method == 'GET':
        return redirect('/am/rules/')
    else:
        try:
            vendor_id = request.POST['vendor_id']
            name = request.POST['name']
            source_url = request.POST['source_url']
            regex = request.POST['regex']

            vendor = Vendor.objects.filter(id=vendor_id).first()
            if not vendor:
                response = "<script>alert('Vendor required!');"
                response += "location.href=document.referrer;</script>"
                return HttpResponse(response)

            rule = Rule(name=name, vendor=vendor, source_url=source_url, regex=regex)
            rule.save()

            response = '<script>alert("Success!");location.href=document.referrer;</script>'
            return HttpResponse(response)
        except Exception, ex:
            response = '<script>alert("Error!");alert("%s");' % str(ex)
            response += 'location.href=document.referrer;</script>'
            return HttpResponse(response)


@login_required(login_url='login/')
def rule_edit(request, rule_id):
    """ AM模块编辑应用包下载规则 """
    try:
        rule = Rule.objects.filter(id=rule_id).first()
        if not rule:
            response = '<script>alert("Rule id not exist!");'
            response += 'location.href=document.referrer;</script>'
            return HttpResponse(response)

        vendor_id = request.POST['vendor_id'].strip()
        name = request.POST['name'].strip()
        source_url = request.POST['source_url'].strip()
        regex = request.POST['regex'].strip()

        vendor = Vendor.objects.filter(id=vendor_id).first()
        if not vendor:
            response = "<script>alert('Vendor required!');"
            response += "location.href=document.referrer;</script>"
            return HttpResponse(response)

        if name != rule.name:
            if check_filter(name):
                response = '<script>alert("New rule name contain filter chars!");'
                response += 'location.href=document.referrer;</script>'
                return HttpResponse(response)
            try:
                process_rule_rename(rule.id, name)
            except Exception, ex:
                response = '<script>alert("Cant rename rule!");alert("%s");' % str(ex)
                response += 'location.href=document.referrer;</script>'
                return HttpResponse(response)

        rule.vendor = vendor
        rule.name = name
        rule.source_url = source_url
        rule.regex = regex
        rule.save()

        response = '<script>alert("Success!");location.href=document.referrer;</script>'
        return HttpResponse(response)
    except Exception, ex:
        response = '<script>alert("Error!");alert("%s");' % str(ex)
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)


@login_required(login_url='/login/')
def rule_del(request, rule_id):
    """ AM模块删除应用包下载规则 /am/rules/rule/del/(\d+) """
    try:
        Rule.objects.get(id=rule_id).delete()
        response = '<script>alert("Success!");location.href=document.referrer;</script>'
        return HttpResponse(response)
    except Exception, ex:
        response = '<script>alert("Error!");alert("%s");' % str(ex)
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)


@login_required(login_url='/login/')
def package_download(request, package_id):
    """ AM模块应用包下载处理 """
    def readfile(filepath, block=262144):
        f = open(filepath, 'rb')
        while True:
            c = f.read(block)
            if c:
                yield c
            else:
                break
        f.close()

    package = Package.objects.filter(id=package_id).first()
    if not package:
        response = '<script>alert("Package Not Found!");'
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)

    path = package.path.encode('utf-8')
    absolute_path = os.path.join(PACKAGE_SOTRE_DIR, path)
    if os.path.exists(absolute_path):
        response = StreamingHttpResponse(readfile(absolute_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=%s' \
                                          % (package.timestamp + '_' + package.filename)
        return response
    else:
        response = '<script>alert("Package Not Exists!");'
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)

@login_required(login_url='/login/')
def send_mail(request):
    try:
        etime = datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        title = request.POST['title']
        email = request.POST['email']
        eurl  = request.POST['eurl']
        content = '''
        <body style="background-color:#ECECEC; padding: 35px;">
        <style>
        a {
            color: #4183c4;text-decoration: none;
        }
        </style>
        <div>
        <table cellpadding="0" align="center" style="width: 600px; margin: 0px auto; text-align: left; position: relative; border-top-left-radius: 5px; border-top-right-radius: 5px; border-bottom-right-radius: 5px; border-bottom-left-radius: 5px; font-size: 14px; font-family:微软雅黑, 黑体; line-height: 1.5; box-shadow: rgb(153, 153, 153) 0px 0px 5px; border-collapse: collapse; background-position: initial initial; background-repeat: initial initial;background:#fff;">
        <tbody>
        <tr>
        <th valign="middle" style="height: 25px; line-height: 25px; padding: 15px 35px; border-bottom-width: 1px; border-bottom-style: solid; border-bottom-color: #B33505;
        background-color: #CC2222;border-top-left-radius: 5px; border-top-right-radius: 5px; border-bottom-right-radius: 0px; border-bottom-left-radius: 0px;">
        <font face="微软雅黑" size="5" style="color: rgb(255, 255, 255); ">WAM (Notification)</font>
        </th>
        </tr>
        <tr>
        <td>
        <div style="padding:25px 35px 40px; background-color:#fff;">
        <h2 style="margin: 5px 0px; "><font color="#333333" style="line-height: 20px; "><font style="line-height: 22px; " size="4">近期监控到此 App 进行更新，可能存在安全隐患：</font></font></h2>
        <p>
        '''
        content += '<a href="%s">%s</a>' % (eurl, title)
        content += '<br><br>点击查看此次 Diff 更新的详细结果: <a href="%s">%s</a></p>' % (eurl, eurl)
        content += '<p align="right">WSL @ 知道创宇安全研究团队</p>'
        content += '<p align="right">%s</p>' % etime
        content += '''</div>
        </td>
        </tr>
        </tbody>
        </table>
        </div>
        </body>
        '''
        if email:
            m = MAIL()
            ret = m.send(subject = u'[WAM] Diff: %s' % title,
                         body = content,
                         to = (email),
                         fromName = "Wam",)
            return HttpResponse('<script>alert("发送成功！");history.go(-1);</script>')
            if not ret:
                ret = m.send(subject = u'[WAM] Diff: %s' % title,
                             body = content,
                             to = (email),
                             fromName = "Wam",)
                return HttpResponse('<script>alert("发送成功！");history.go(-1);</script>')
    except Exception, e:
        return HttpResponse('<script>alert("%s");history.go(-1);</script>'%str(e))
    return HttpResponse('<script>alert("False!");history.go(-1);</script>')

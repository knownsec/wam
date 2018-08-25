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
    """ vdr模块主页 """
    vendors = Vendor.objects.order_by('-add_time').all()
    vendors_report = []
    for vendor in vendors:
        rules = Rule.objects.filter(vendor=vendor).all()
        packages = Package.objects.filter(rule__in=rules).order_by('-add_time').all()
        diffs = Diff.objects.filter(
            Q(s_package__in=packages) | Q(d_package__in=packages)).order_by('add_time').all()

        rules_count = rules.count()
        diffs_count = diffs.count()
        packs_count = packages.count()
        vendors_report.append((vendor, rules_count, diffs_count, packs_count))

    return render(request, 'vdr/index.html',
                  {'vendors_report': vendors_report, 'LOGO_PATH': WAM_VENDOR_LOGO_URL})


@login_required(login_url='/login/')
def packages_list(request, vendor_id):
    """ vdr模块厂商包列表 """
    vendor = Vendor.objects.filter(id=vendor_id).first()
    rules = Rule.objects.filter(vendor=vendor).order_by('-add_time').all()
    packages = Package.objects.filter(rule__in=rules).order_by('-add_time').all()

    return render(request, 'vdr/packages_list.html',
                  {'packages': packages, 'vendor': vendor})


@login_required(login_url='/login/')
def package_edit(request, package_id):
    """ vdr模块厂商应用包编辑 """
    try:
        package = Package.objects.filter(id=package_id).first()
        if not package:
            response = '<script>alert("Package not found!");'
            response += 'location.href=document.referrer;</script>'
            return HttpResponse(response)

        shooter_id = '0' if request.POST['id'].strip() == '' else request.POST['id']
        shooter_link = request.POST['link']
        shooter_desc = request.POST['description']

        package.shooter_id = shooter_id
        package.shooter_link = shooter_link
        package.shooter_desc = shooter_desc
        package.save()

        response = '<script>alert("Success!");location.href=document.referrer;</script>'
        return HttpResponse(response)
    except Exception, ex:
        response = '<script>alert("Error!");alert("%s");' % str(ex)
        response += 'location.href=document.referrer;</script>'
        return HttpResponse(response)

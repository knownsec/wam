# coding: utf-8

# __buildin__ modules
import os
import re
import shutil
import json as simplesjson

# monitor modules
from monitor.core.settings import PACKAGE_SOTRE_DIR

# wam modules
from wam.apps.am.models import Rule, Package


def parse_analysis_result(result):
    """
    解析数据库 Analysis.result JSON数据为PY格式，方便前台获取信息

    output = {
        'has_reports': True,
        'plugins': {
            'sqli': 2,
            'xss': 1
            'backdoor': 0
        },
        'reports': [
            {
                'tag': 'sqli',
                'result': [
                    {
                        'file': 'xxxxx.php',
                        'line': 'xxxxxxx',
                        'desc': 'xxxxxxx'
                    },
                    {
                        'file': 'aaaaa.php',
                        'line': 'aaaaaaa',
                        'desc': 'bbbbbbb'
                    }
                ]
            },
            {
                'tag': 'xss',
                'result': [
                    {
                        'file': 'ccccc.php',
                        'line': 'xxxxxx',
                        'desc': 'nnnnnn'
                    }
                ]
            }
        ]
    }

    output = {
        'has_reports': False,
        'plugins': {
            'sqli': 0,
            'xss': 0,
            'backdoor': 0
        }
        'reports': []
    }
    """
    output = {
        'has_report': False,
        'plugins': {},
        'reports': []
    }
    results = simplesjson.loads(result)

    for result in results:
        tag = result['tag']
        reports = result['reports']

        if len(reports) == 0:
            output['plugins'][tag] = 0
        else:
            output['has_report'] = True
            output['plugins'][tag] = len(reports)

            p_reports = {
                'tag': tag,
                'result': reports
            }
            output['reports'].append(p_reports)

    return output


def check_filter(name):
    filter_c = r'[\\/:*?"<>|]'
    if re.search(filter_c, name):
        return True

    return False


def process_rule_rename(rule_id, new_name):
    rule = Rule.objects.filter(id=rule_id).first()
    if rule:
        vendor_name = rule.vendor.name
        rule_name = rule.name
        relative_path = os.path.join(vendor_name, rule_name)
        destpath = os.path.join(PACKAGE_SOTRE_DIR, relative_path)
        if os.path.isdir(destpath):
            alert_relative_path = os.path.join(vendor_name, new_name)
            alert_destpath = os.path.join(PACKAGE_SOTRE_DIR, alert_relative_path)
            try:
                shutil.move(destpath, alert_destpath)
            except Exception, ex:
                err = 'failed to move %s to %s' % (destpath, alert_destpath)
                raise Exception(err)

            packages = Package.objects.filter(rule=rule).all()
            for package in packages:
                timestamp = package.timestamp
                filename = package.filename
                r_path = os.path.join(vendor_name,
                                      os.path.join(new_name, timestamp + '_' + filename))
                package.path = r_path
                package.save()
        else:
            raise AssertionError('%s is not exesit' % destpath)
    else:
        raise ValueError('empty rule provied')


def pagination(page, begin_pages=2, end_pages=2, before_current_pages=4, after_current_pages=4):
    # Digg-like pages
    current = page.number
    before = max(page.number - before_current_pages - 1, 0)
    after = page.number + after_current_pages

    begin = page.paginator.page_range[:begin_pages]
    middle = page.paginator.page_range[before:after]
    end = page.paginator.page_range[-end_pages:]
    last_page_number = end[-1]

    def collides(firstlist, secondlist):
        """ Returns true if lists collides (have same entries)

        >>> collides([1,2,3,4],[3,4,5,6,7])
        True
        >>> collides([1,2,3,4],[5,6,7])
        False
        """
        return any(item in secondlist for item in firstlist)

    # If middle and end has same entries, then end is what we want
    if collides(middle, end):
        end = range(max(page.number-before_current_pages, 1), last_page_number+1)

        middle = []

    # If begin and middle ranges has same entries, then begin is what we want
    if collides(begin, middle):
        begin = range(1, min(page.number + after_current_pages, last_page_number)+1)

        middle = []

    # If begin and end has same entries then begin is what we want
    if collides(begin, end):
        begin = range(1, last_page_number+1)
        end = []

    return {'page': page, 'begin': begin, 'middle': middle, 'end': end, 'current': current}

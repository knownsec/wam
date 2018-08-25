#!/usr/bin/env python
# coding: utf-8

from baseframe import Plugin


class MyPlugin(Plugin):
    info = {
        'name': 'Sample XSS Match',
        'tag': 'xss'
    }

    rules = [
        {
            'desc': 'PHP常见XSS过滤函数',
            'rule': (
                r'(?i)htmlspecialchars\(|'
                r'htmlentities\(|'
                r'addslashes\(|'
                r'strip_tags\(|'
                r'strip_tags\(|'
                r'xss_filter\(|'
                r'HTMLPurifier\(|'
                r'RemoveXSS\(|'
                r'checkhtml\(|'
                r'json_encode\(|'
                r'[\'"]+onmouseleave[\'"]+,[ ]*[\'"]+onmousemove[\'"]+,[ ]*[\'"]onmouseout[\'"]'
            )
        },
        {
            'desc': 'ASP常见XSS过滤函数',
            'rule': r'(?i)HTMLEncode\('
        },
        {
            'desc': 'Python常见XSS过滤函数',
            'rule': r'(?i)cgi.escape\('
        },
        {
            'desc': 'Java常见XSS过滤函数',
            'rule': r'(?i)xssprotect\('
        },
    ]

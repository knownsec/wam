#!/usr/bin/env python
# coding: utf-8

from baseframe import Plugin


class MyPlugin(Plugin):
    info = {
        'name': 'Sample SQLi Match',
        'tag': 'sqli'
    }

    rules = [
        {
            'desc': 'PHP常见SQLi过滤函数',
            'rule': (
                r'(?i)get_magic_quotes_gpc\(|intval\(|addslashes\(|strip_tags\(|'
                r'str_replace\(|mysql_real_escape_string\(|stripslashes\('
            )
        },
        {
            'desc': 'ASP常见XSS过滤函数',
            'rule': (
                r'(?i)CheckSql\(|'
                r'Replace\((?P<quote>[\'"])(?P<char>.)(?P=quote),[ ]*(?P=quote)\\(?P=char)*(?P=quote)'
            )
        },
    ]

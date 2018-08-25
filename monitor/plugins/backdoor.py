#!/usr/bin/env python
# coding: utf-8

from baseframe import Plugin


class MyPlugin(Plugin):
    info = {
        'name': 'Sample Backdoor Match',
        'tag': 'backdoor'
    }

    rules = [
        {
            'desc': '常见Webshell特征检测',
            'rule': (
                r'(?i)\$_(GET|POST|REQUEST)\[.{0,15}\]\(\$_(GET|POST|REQUEST)\[.{0,15}\]\)|'
                r'base64_decode\([\'"][\w\+/=]{200,}[\'"]\)|'
                r'(?<!\w)eval\(base64_decode\(|'
                r'(?<!\w)eval\(\s*.*\s*\)|'
                r'assert\(\$_(POST|GET|REQUEST)\[.{0,15}\]\)|'
                r'\$[\w_]{0,15}\(\$_(POST|GET|REQUEST)\[.{0,15}\]\)|'
                r'wscript\.shell|'
                r'gethostbyname\(|'
                r'cmd\.exe|'
                r'shell\.application|'
                r'documents\s+and\s+settings|'
                r'system32|'
                r'serv-u|'
                r'提权|'
                r'phpspy|'
                r'后门|'
                r'webshell|'
                r'Program\s+Files'
            )
        },
    ]

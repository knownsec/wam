#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import os
import time
import hashlib


# wam modules
from wam.apps.main.models import Config


def get_config(key):
    """从数据库中获取全参数值"""
    config = Config.objects.filter(key=key).first()
    return config.value if config else None


def set_config(key, value):
    """设置数据库中全局参数值"""
    config = Config.objects.filter(key=key).first()
    if config:
        config.value = value
        config.save()
    else:
        config = Config(key=key, value=value)
        config.save()


def md5(string):
    """计算字符串的 md5 值"""
    return hashlib.md5(str(string)).hexdigest()


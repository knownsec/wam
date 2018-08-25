# coding: utf-8

# __buildin__ modules
import os

# django moduels
from django.db import models

# wam modules
from wam.settings import FILE_STORE_DIR

# Create your models here.


class Message(models.Model):
    """
    爬取的社区消息
    """
    # 字段说明=>
    #      url: 消息链接
    #     user: 所发消息的用户名称
    #    title: 消息标题
    #    topic: 消息所属话题
    #  content: 消息内容
    #  keyword: 爬取时使用的关键字
    # add_time: 记录添加时间
    url      = models.URLField(blank=True)
    user     = models.TextField(blank=True)
    title    = models.TextField(blank=True)
    topic    = models.TextField(blank=True)
    content  = models.TextField(blank=True)
    keyword  = models.TextField(blank=True)

    add_time = models.DateTimeField(auto_now_add=True)

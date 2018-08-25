# coding: utf-8

from django.db import models

# Create your models here.


class Config(models.Model):
    """
    全局配置
    """
    # 字段说明=>
    #    key: 参数名
    #  value: 参数值
    # module: 参数所属模块
    key   = models.CharField(max_length=60, unique=True)
    value = models.TextField()

    def __unicode__(self):
        return u'key=%s, value=%s' % (self.key, self.value)

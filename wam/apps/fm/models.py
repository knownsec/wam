# coding: utf-8

# __buildin__ modules
import os

# django moduels
from django.db import models

# wam modules
from wam.settings import FILE_STORE_DIR

# Create your models here.


class FLang(models.Model):
    """
    文件代码语言
    """
    # 字段说明=>
    # name: 名称（唯一）
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return u'name=%s' % self.name


class FRule(models.Model):
    """
    文件下载规则
    """
    # 字段说明=>
    #            name: 文件监控规则名称
    #            desc: 监控描述
    #      source_url: 监控文件所处的URL地址
    #           regex: 若需要正则匹配则使用该字段
    #   regex_content: 文件内容中需要进行监控的范围
    #            lang: 所监控文件的开发语言
    #  check_interval: 该规则的检查间隔（为空则应用全局检测间隔）
    # last_check_date: 最近一次完成检测时间
    #       vendor_id: 关联厂商的 ID
    name            = models.CharField(max_length=80, unique=True)
    desc            = models.TextField(blank=True)
    source_url      = models.URLField()
    regex           = models.TextField(blank=True)
    regex_content   = models.TextField(blank=True)
    lang            = models.ForeignKey(FLang, null=True)
    check_interval  = models.IntegerField(null=True)
    last_check_date = models.DateTimeField(null=True)
    vendor_id = models.IntegerField(null=True)

    add_time        = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'name=%s' % self.name


class FFile(models.Model):
    """
    监控文件
    """
    # 字段说明=>
    #            frule: 来源规则
    #              md5: 文件 md5 哈希
    #             size: 文件大小
    #             path: 文件相对于包存储路径的相对路径
    #         filename: 下载时获取的文件名
    #        timestamp: 下载完成时获取的时间戳
    # response_headers: 下载请求返回的完整响应头
    #         add_time: 添加数据库时间
    frule            = models.ForeignKey(FRule)
    md5              = models.CharField(max_length=32)
    size             = models.IntegerField()
    path             = models.FilePathField()
    filename         = models.TextField()
    timestamp        = models.TextField()
    response_headers = models.TextField()

    add_time         = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'filename=%s, size=%s, md5=%s, path=%s, add_time=%s' \
               % (self.filename, self.size, self.md5, self.path, self.add_time)

    def get_absolute_path(self):
        return os.path.join(FILE_STORE_DIR, self.path)


class FDiff(models.Model):
    """
    文件比较（Diff）结果
    """
    # 字段说明=>
    #      s_file: 比较源应用包
    #      d_file: 比较目的应用包
    #    raw_content: 通过 difflib 得到的原始结果
    # render_content: 渲染后的比较结果
    #       add_time: 添加时间
    s_file         = models.ForeignKey(FFile, related_name='s_file')
    d_file         = models.ForeignKey(FFile, related_name='d_file')
    raw_content    = models.BinaryField()
    render_content = models.BinaryField()

    add_time       = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u's_file_id=%s, d_file_id=%s, add_time=%s' \
               % (self.s_file.id, self.d_file.id, self.add_time)

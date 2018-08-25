# coding: utf-8

# __buildin__ modules
import os
import hashlib

# django modules
from django.db import models

# wam modules
from wam.settings import PACKAGE_SOTRE_DIR, WAM_VENDOR_LOGO_ROOT

# Create your models here.


def md5(string):
    return hashlib.md5(string).hexdigest()


def rename(instance, filename):
    return os.path.join(WAM_VENDOR_LOGO_ROOT,
                        md5(str(instance.name.encode('utf-8'))) + os.path.splitext(filename)[1])


class Vendor(models.Model):
    """
    厂商信息
    """
    # 字段说明=>
    #     name: 名称（唯一）
    #     site: 官网地址
    #     desc: 简介、描述
    #     logo: Logo 照片，Django 中存储形式为文件路径或文件名
    # add_time: 信息添加时间
    name     = models.CharField(max_length=50, unique=True)
    site     = models.URLField(blank=True)
    desc     = models.TextField(blank=True)
    logo     = models.FileField(upload_to=rename, null=True)

    add_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'name=%s, site=%s, add_time=%s' \
               % (self.name, self.site, self.add_time)


class Lang(models.Model):
    """
    应用开发主语言
    """
    # 字段说明=>
    # name: 名称（唯一）
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return u'name=%s' % self.name


class Rule(models.Model):
    """
    下载规则
    """
    # 字段说明=>
    #            name: 名称（唯一）
    #          vendor: 所属厂商
    #      source_url: 应用下载地址
    #           regex: 正则表达式用于从页面内容匹配出正确的下载链接
    #            lang: 规则对应应用所用的主要开发语言
    #  check_interval: 该规则的检测间隔（为空则应用全局检测间隔）
    # last_check_date: 最近一次完成检测时间
    #        add_time: 规则添加时间
    name            = models.CharField(max_length=80, unique=True)
    vendor          = models.ForeignKey(Vendor)
    source_url      = models.URLField()
    regex           = models.TextField(blank=True)
    lang            = models.ForeignKey(Lang, null=True)
    check_interval  = models.IntegerField(null=True)
    last_check_date = models.DateTimeField(null=True)

    add_time        = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'name=%s' % self.name
        # return u'name=%s, source_url=%s, regex=%s, add_time=%s' \
        #       % (self.name, self.source_url, self.regex, self.add_time)


class Package(models.Model):
    """
    应用包
    """
    # 字段说明=>
    #             rule: 来源规则
    #              md5: 应用包文件 md5 哈希
    #             size: 应用包大小
    #             path: 应用包相对于包存储路径的相对路径
    #         filename: 下载时获取的文件名
    #        timestamp: 下载完成时获取的时间戳
    # response_headers: 下载请求返回的完整响应头
    #         add_time: 添加数据库时间
    #       shooter_id: 对应的靶场ID
    #     shooter_link: 靶场链接
    #     shooter_desc: 漏洞和靶场的相关描述信息
    rule             = models.ForeignKey(Rule)
    md5              = models.CharField(max_length=32)
    size             = models.IntegerField()
    path             = models.FilePathField()
    filename         = models.TextField()
    timestamp        = models.TextField()
    response_headers = models.TextField()

    shooter_id       = models.IntegerField(default=0)
    shooter_link     = models.URLField(blank=True, default='')
    shooter_desc     = models.TextField(blank=True, default='')

    add_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'filename=%s, size=%s, md5=%s, path=%s, add_time=%s' \
               % (self.filename, self.size, self.md5, self.path, self.add_time)

    def get_absolute_path(self):
        return os.path.join(PACKAGE_SOTRE_DIR, self.path)


class Diff(models.Model):
    """
    包比较（Diff）结果
    """
    # 字段说明=>
    #      s_package: 比较源应用包
    #      d_package: 比较目的应用包
    #    raw_content: 通过 difflib 得到的原始结果
    # render_content: 渲染后的比较结果
    #       add_time: 添加时间
    s_package      = models.ForeignKey(Package, related_name='s_package')
    d_package      = models.ForeignKey(Package, related_name='d_package')
    raw_content    = models.BinaryField()
    render_content = models.BinaryField()

    add_time       = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u's_package_id=%s, d_package_id=%s, add_time=%s' \
               % (self.s_package.id, self.d_package.id, self.add_time)


class Analysis(models.Model):
    """
    分析结果
    """
    # 字段说明=>
    #     diff: 分析所属比较结果 id
    #   result: 分析结果 JSON 结构
    # add_time: 结果添加时间
    diff     = models.ForeignKey(Diff)
    result   = models.TextField()

    add_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'diff_id=%s, add_time=%s' % (self.diff.id, self.add_time)

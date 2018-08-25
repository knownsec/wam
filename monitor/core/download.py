#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import os
import re
import shutil
import tempfile
import urlparse
import HTMLParser

# thirdparty modules
import requests

# monitor modules
from monitor.core.exception import MonitorDownloadError
from monitor.core.settings import DOWNLOAD_MAX_BYTES
from monitor.utils.common import md5, get_config


REQUEST_TIMEOUT = 360
REQUEST_USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46'
                      '.0.2490.80 Safari/537.36')


def move_file(s_path, d_path, cid=False):
    """
    将文件移动到指定路径，cid 用于控制是否递归创建指定路径目录结构
    """
    if cid and not os.path.exists(os.path.dirname(d_path)):
        os.makedirs(os.path.dirname(d_path), mode=0755)
    try:
        shutil.move(s_path, d_path)
    except Exception, ex:
        err = 'unable move "%s" to "%s" ("%s")' % (s_path, d_path, ex)
        raise MonitorDownloadError(err)


def remove_file(filepath):
    """
    删除文件
    """
    try:
        os.unlink(filepath)
    except Exception, ex:
        err = 'unable remove "%s" ("%s")' % (filepath, ex)
        raise MonitorDownloadError(err)


def get_file_size(filepath):
    """
    获取文件大小
    """
    return os.path.getsize(filepath)


def get_download_url_with_regex(source_url, regex):
    """
    使用匹配规则从下载地址中匹配出最终的下载链接
    """
    try:
        response = requests.get(source_url, timeout=REQUEST_TIMEOUT, headers={'User-Agent': REQUEST_USER_AGENT}, verify=False)
    except requests.exceptions.RequestException:
        try:
            response = requests.get(source_url, timeout=REQUEST_TIMEOUT, headers={'User-Agent': REQUEST_USER_AGENT}, verify=False)
        except Exception, ex:
            err = 'unable to get download url with regex ("%s")' % ex
            raise MonitorDownloadError(err)

    match = re.search(regex, response.content, re.IGNORECASE)

    return match.group('download_url') if match else None


def patch_download_url(source_url, download_url):
    """
    修复匹配出的下载链接为不标准 URL 格式的问题
    e.g.
    (1)  match: //www.example.com/pacakge.zip => http://www.example.com/pacakge.zip
    (2)  match: /download/pacakge.zip => http://{source_url.host}/download/pacakge.zip
    (3)  match: download/package.zip => http://{source_url.path}download/package.zip
    (4)  match: &amp;&lt => &<
    (5)  match: ../package.zip => http://{soucre_url.path}/../package.zip
    """
    if not download_url:
        return None

    download_url = HTMLParser.HTMLParser().unescape(download_url)

    if download_url.startswith('//'):
        download_url = 'http:' + download_url
    elif re.search(r'^/[^/].*$', download_url):
        download_url = urlparse.urljoin(source_url, download_url)
    elif re.search(r'^[^/].*$', download_url):
        download_url = urlparse.urljoin(os.path.dirname(source_url) + '/', download_url)
    elif re.search(r'^[\.]{1,2}/[^/].*$', download_url):
        download_url = urlparse.urljoin(source_url, download_url)

    return download_url


def get_handler(url):
    """
    请求 url 返回响应句柄
    """
    try:
        handler = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT, headers={'User-Agent': REQUEST_USER_AGENT}, verify=False)
    except requests.exceptions.RequestException:
        try:
            handler = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT, headers={'User-Agent': REQUEST_USER_AGENT}, verify=False)
        except Exception, ex:
            err = 'unable to get response handler ("%s")' % ex
            raise MonitorDownloadError(err)

    if handler.status_code >= 400:
        err = 'bad response, response status code is {code}(url: {url}).'.format(code=handler.status_code, url=url)
        if handler.status_code in [404, 410]:
            err += 'file not found'
        raise MonitorDownloadError(err)

    return handler


def get_filename_from_headers(headers):
    """
    从响应头 Content-Disposition 字段中获取文件名
    """
    match = re.search(r'(?i)filename=(?P<filename>.*)[\'"]?',
                      headers.get('Content-Disposition', ''))

    return match.group('filename') if match else None


def get_filename_from_url(url):
    """
    从 url 中获取基础文件名
    """
    return os.path.basename(urlparse.urlsplit(url).path)


def get_filename_from_handler(handler):
    """
    从响应句柄中获取服务器返回的下载文件名称
    """
    filename = get_filename_from_headers(handler.headers)
    if not filename:
        filename = get_filename_from_url(handler.url)
    filename = filename.strip('"').strip("'")

    return filename


def get_content_length_from_handler(handler):
    """
    从响应句柄中获取文本数据大小
    """
    content_length = handler.headers.get('content-length', None)
    if not content_length:
        err = 'failed to get "content-length" in respone headers'
        raise MonitorDownloadError(err)

    return int(content_length)


def check_content_length_allowed(content_length, package_max_bytes):
    """
    检查响应数据内容大小是否在允许范围内
    """
    if not (int(content_length) <= int(package_max_bytes)):
        return False

    return True


def check_file_equal_size(filepath, check_size):
    """
    检查指定文件大小是否等于所给大小值
    """
    file_size = os.path.getsize(filepath)
    return int(file_size) == int(check_size)


def save_content_with_handler(handler, filename):
    """
    读取响应句柄中的数据内容，将其保存至临时目录，并以获取到的文件名命名
    """
    t_path = os.path.join(tempfile.gettempdir(), filename)
    try:
        with open(t_path, 'wb') as f:
            for chunk in handler.iter_content(chunk_size=524288):
                f.write(chunk)
                f.flush()
    except Exception, ex:
        err = 'unable to save content to "%s" ("%s")' % (filename, ex)
        raise MonitorDownloadError(err)

    return t_path


def get_file_md5(filepath):
    """
    计算文件 md5 哈希值
    """
    if not os.path.exists(filepath):
        err = 'unable to calculate md5 hash, '
        err += 'file "%s" not found' % filepath
        raise MonitorDownloadError(err)
    try:
        with open(filepath, 'rb') as f:
            f_md5 = md5(f.read(os.path.getsize(filepath)))
    except IOError, ex:
        err = 'unable to calculate md5 hash, '
        err += 'file "%s" cant open ("%s")' % (filepath, ex)
        raise MonitorDownloadError(err)

    return f_md5


def filter_content_with_file(filepath, regex_content):
    """
    使用正则过滤出想要保留的内容，直接操作原文件
    """
    if not os.path.exists(filepath):
        err = 'unable to open file and filter content, '
        err += 'file "%s" not found' % filepath
        raise MonitorDownloadError(err)
    try:
        content = ''
        with open(filepath, 'rb') as f:
            content = f.read()

        match = re.search(regex_content, content, re.DOTALL)
        if match:
            filter_content = match.group('content')
            if filter_content:
                with open(filepath, 'wb') as f:
                    f.write(filter_content)

    except IOError, ex:
        err = 'unable to open file and filter content, '
        err += 'file "%s" cant open ("%s")' % (filepath, ex)
        raise MonitorDownloadError(err)


def download_file(source_url, regex=None, regex_content=None, ignore_length_check=True):
    """
    使用下载地址和链接匹配规则下载应用包或文件
    """
    download_url = source_url if not regex \
        else patch_download_url(source_url, get_download_url_with_regex(source_url, regex))

    if not download_url:
        err = 'unable to fetch download url with regex, '
        err += 'check it again please.'
        raise MonitorDownloadError(err)

    handler = get_handler(download_url)
    filename = get_filename_from_handler(handler)
    if not ignore_length_check:
        content_length = get_content_length_from_handler(handler)
        download_max_bytes = get_config('DOWNLOAD_MAX_BYTES') \
            if get_config('DOWNLOAD_MAX_BYTES') else DOWNLOAD_MAX_BYTES
        if not check_content_length_allowed(content_length, download_max_bytes):
            err = 'content-length %s not allowed, ' % content_length
            err += 'file max %s bytes allowed' % download_max_bytes
            raise MonitorDownloadError(err)

    temp_filename = save_content_with_handler(handler, filename)
    if regex_content:
        filter_content_with_file(temp_filename, regex_content)

    t_size = get_file_size(temp_filename)
    if not ignore_length_check:
        if not (int(t_size) == int(content_length)):
            err = 'package saved size(%s) not equal to "content-length"(%s) in reponse' \
                  % (t_size, content_length)
            raise MonitorDownloadError(err)

    file_md5 = get_file_md5(temp_filename)
    response_headers = handler.headers
    package = dict(filename=filename,
                   md5=file_md5,
                   size=t_size,
                   temppath=temp_filename,
                   headers=response_headers)

    return package

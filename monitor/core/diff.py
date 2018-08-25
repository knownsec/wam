#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import os
import cgi
import shutil
import difflib
import tempfile

# thirdparty modules
import chardet
import patoolib

# monitor modules
from monitor.core.exception import MonitorDiffError
from monitor.core.settings import DIFF_FILTER_EXT, CONTENT_REPLACE
from monitor.utils.common import get_config


def remove_dir(dirpath):
    """
    删除文件目录
    """
    if os.path.isdir(dirpath):
        try:
            shutil.rmtree(dirpath)
        except Exception, ex:
            err = 'unable remove directory "%s" ("%s")' % (dirpath, ex)
            raise MonitorDiffError(err)


def quiet_remove_dirs(*args):
    """
    删除多个文件目录
    """
    for d in args:
        try:
            remove_dir(d)
        except Exception:
            pass


def unpack_package(p_path, d_dir=None):
    """
    使用第三方库 patoolib 解压应用包至指定路径
    """
    tempdir = tempfile.mkdtemp(prefix='wam_') if not d_dir else d_dir
    try:
        patoolib.extract_archive(p_path, verbosity=-1, outdir=tempdir, interactive=False)
        #add interactive=False 解决解压文件卡住的问题
    except Exception, ex:
        remove_dir(tempdir)

        err = 'unable to extract package "%s" ("%s")' % (p_path, ex)
        raise MonitorDiffError(err)

    return tempdir


def unpack_two_package(s_package_path, d_package_path):
    """
    解压两个应用包, 必须 s_package_path 和 d_package_path 都解压正确
    """
    s_unpack_dir = unpack_package(s_package_path)

    try:
        d_unpack_dir = unpack_package(d_package_path)
    except MonitorDiffError:
        remove_dir(s_unpack_dir)
        raise

    return s_unpack_dir, d_unpack_dir


def walk_dir(d_path, filter_ext=None):
    """
    遍历文件夹下所有文件，得到过滤后的文件列表
    """
    p_dir = os.path.dirname(os.path.realpath(d_path) + '/')
    filelist = []
    for root, dirs, files in os.walk(d_path):
        for f in files:
            # 基于监控文件的扩展名进行过滤
            if f.split('.')[-1].lower() not in filter_ext:
                continue
            f_path = os.path.realpath(os.path.join(root, f)).replace(p_dir, '').lstrip('/')
            filelist.append(f_path)

    return p_dir, filelist


def compare_list(s_list, d_list):
    """
    比较两个数组列表差别，返回相同部分，增加部分，删除部分的列表
    """
    same = list(set(s_list).intersection(set(d_list)))
    add = list(set(d_list).difference(set(s_list)))
    delete = list(set(s_list).difference(set(d_list)))

    return same, add, delete


def patch_line(l):
    """
    将原始 Diff 输出结果的每一行重新使用 utf-8 编码
    若转码失败，使用预先设置的替代问题替换该行内容
    """
    encoding = chardet.detect(l)['encoding']
    if encoding:
        if encoding == 'utf-8':
            return l
        else:
            try:
                l = l.decode(encoding, 'replace').encode('utf-8')
            except Exception, ex:
                l = l[0] + CONTENT_REPLACE
    else:
        l = l[0] + CONTENT_REPLACE
    return l


def get_hunks_generator(lines):
    """
    解析原始 Diff 输出结果，以文件比较为单位返回块数据
    """
    hunk = {'old_path': None, 'new_path': None, 'lines': []}
    for line in lines:
        if line.startswith('---'):
            if hunk['old_path'] and hunk['new_path'] and hunk['lines']:
                yield hunk
            hunk = {'old_path': line, 'new_path': None, 'lines': []}
        elif line.startswith('+++') and hunk['old_path']:
            hunk['new_path'] = line
        elif line.startswith('@@') \
                or (line.startswith('+') and not line.startswith('+++')) \
                or (line.startswith('-') and not line.startswith('---')) \
                or line.startswith(' '):
            hunk['lines'].append(line)
        else:
            hunk['lines'].append(line)

    if hunk['old_path'] and hunk['new_path']:
        if len(hunk['lines']) > 0:
            yield hunk


def render_raw_content(raw):
    """
    使用特定的 HTML 格式对原始 Diff 输出结果进行渲染，返回最终渲染结果
    """
    lines = raw.split('\n')
    hunks = get_hunks_generator(lines)
    r_content = ''
    for hunk in hunks:
        r_hunk = ''
        r_hunk += '<div class="div">\n  <div class="title active"><i class="dropdown icon"></i>' \
                  + cgi.escape(hunk['old_path'][4:]) + '</div>\n  <div class="content active" id="' + \
                  cgi.escape(hunk['old_path'][4:]) + '" name="' + cgi.escape(hunk['old_path'][4:]) + '">\n'
        for line in hunk['lines']:
            line = cgi.escape(line)
            if line.startswith('@@'):
                r_hunk += '  <span class="at2">' + line + '</span>\n'
            elif line.startswith('+'):
                r_hunk += '  <span class="plus">' + line + '</span>\n'
            elif line.startswith('-'):
                r_hunk += '  <span class="minus">' + line + '</span>\n'
            else:
                r_hunk += '  ' + line + '\n'

        r_hunk += '  </div>\n</div>\n\n'
        r_content += r_hunk

    return r_content


def differ_filelist_with_two_dirs(s_p_dir, d_p_dir, filelist, mode='0'):
    """
    使用 difflib 库对两个文件夹下的文件列表进行比较，输出原始结果
    """
    output = ''
    for f_path in filelist:
        s_file_path = os.path.join(s_p_dir, f_path) if mode != '1' else None
        d_file_path = os.path.join(d_p_dir, f_path) if mode != '2' else None
        fd1 = open(s_file_path, 'rbU') if s_file_path else None
        fd2 = open(d_file_path, 'rbU') if d_file_path else None
        fromlines = fd1.readlines() if fd1 else ''
        tolines = fd2.readlines() if fd2 else ''
        if fd1: fd1.close()
        if fd2: fd2.close()

        dresult = difflib.unified_diff(fromlines, tolines, f_path, f_path)
        for line in dresult:
            line = patch_line(line)
            if line.startswith('---'):
                line = '\n' + line
            output += line

    return output


def differ_two_packages(s_package_path, d_package_path):
    """
    对两个应用包进行 Diff 操作，返回原始输出结果
    流程: 解压, 对比, 删除解压临时目录
    """

    s_unpack_dir, d_unpack_dir = unpack_two_package(s_package_path, d_package_path)

    # TODO rename unpack_dir when different names unpacked
    s_unpack_dir_list = os.listdir(s_unpack_dir)
    d_unpack_dir_list = os.listdir(d_unpack_dir)
    if s_unpack_dir_list.__len__() == 1 and d_unpack_dir_list.__len__() == 1 \
            and s_unpack_dir_list != d_unpack_dir_list:
        os.rename(os.path.join(s_unpack_dir, s_unpack_dir_list[0]), os.path.join(s_unpack_dir, 'd'))
        os.rename(os.path.join(d_unpack_dir, d_unpack_dir_list[0]), os.path.join(d_unpack_dir, 'd'))
        s_unpack_dir = os.path.join(s_unpack_dir, 'd')
        d_unpack_dir = os.path.join(d_unpack_dir, 'd')

    try:
        diff_filter_ext = get_config('DIFF_FILTER_EXT')
    except Exception:
        diff_filter_ext = DIFF_FILTER_EXT
    #if get_config('DIFF_FILTER_EXT') else DIFF_FILTER_EXT

    filter_ext_list = [_.strip() for _ in diff_filter_ext.split(',') if _.strip() != '']
    src_p_dir, src_filelist = walk_dir(s_unpack_dir, filter_ext_list)
    dest_p_dir, dest_filelist = walk_dir(d_unpack_dir, filter_ext_list)
    same, add, delete = compare_list(src_filelist, dest_filelist)
    raw_content = ''
    for mode in ['0', '1', '2']:
        oo_raw = differ_filelist_with_two_dirs(
                    src_p_dir, dest_p_dir,
                    same if mode == '0' else (add if mode == '1' else delete),
                    mode=mode
                 )
        raw_content += oo_raw

        # 容错处理，不影响diff正常功能及结果, 应该做日志记录[!]
        quiet_remove_dirs(s_unpack_dir, d_unpack_dir)

    return raw_content


def differ_two_files(s_file_path, d_file_path):
    """
    对两个文件进行 Diff 操作，返回原始输出结果
    """
    s_filename = os.path.basename(s_file_path)
    d_filename = os.path.basename(d_file_path)
    fd1 = open(s_file_path, 'rbU') if s_file_path else None
    fd2 = open(d_file_path, 'rbU') if d_file_path else None
    fromlines = fd1.readlines() if fd1 else ''
    tolines = fd2.readlines() if fd2 else ''
    if fd1: fd1.close()
    if fd2: fd2.close()

    raw_content = ''
    dresult = difflib.unified_diff(fromlines, tolines, s_filename, d_filename)
    for line in dresult:
        line = patch_line(line)
        if line.startswith('---'):
            line = '\n' + line
        raw_content += line

    return raw_content

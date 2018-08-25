#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import os
import re
import sys
import json as simplejson

# monitor modules
from monitor.core.exception import MonitorAnalysisError
from monitor.core.settings import ANALYSIS_PLUGIN_DIR


FILTER_MODULES = ['__init__.py', 'baseframe.py']


def import_module_with_path(path):
    abspath = os.path.abspath(os.path.expanduser(path))
    dirpath, filename = os.path.split(abspath)

    if dirpath not in sys.path:
        sys.path.insert(0, dirpath)

    module_name, ext = os.path.splitext(filename)
    try:
        return __import__(module_name, fromlist=['*'])
    except ImportError:
        raise ImportError('Error on import "%s"' % abspath)
    except Exception, e:
        raise Exception('Error on import "%s" [%s]' % (abspath, e))


def import_all_modules_with_dirname(dirpath, pattern=r'(?P<filename>^.+\.py$)'):
    absdirpath = os.path.abspath(os.path.expanduser(dirpath))
    filenames = os.listdir(absdirpath)
    matchs = []

    for filename in filenames:
        match = re.search(pattern, filename)
        if match:
            if match.group('filename') not in FILTER_MODULES:
                module_path = os.path.join(absdirpath, match.group('filename'))
                matchs.append(module_path)

    return [import_module_with_path(path) for path in matchs]


def load_all_plugins(plugin_dir):
    plugins = []
    modules = import_all_modules_with_dirname(plugin_dir)
    for module in modules:
        try:
            plugins.append(module.MyPlugin)
        except:
            continue

    return plugins


def analysis_content(raw_content):
    """
    加载分析器插件对原始 Diff 结果进行分析，并输出检测结果
    """
    result = []
    plugins = load_all_plugins(ANALYSIS_PLUGIN_DIR)
    for plugin in plugins:
        try:
            m_plugin = plugin()
            m_result = m_plugin.scan(raw_content)
            result.append(m_result) if m_result else ''
        except Exception, ex:
            continue

    return simplejson.dumps(result)

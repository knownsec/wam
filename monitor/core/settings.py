#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import os


# 监控程序循环间隔(秒)
MONITOR_CHECK_INTERVAL = 3600

# 下载大小限制(字节)
DOWNLOAD_MAX_BYTES = 104857600  # 1024*1024*100 = 100MB

# 应用包存储路径
PACKAGE_SOTRE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../wam/packages/')
FILE_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../wam/files/')

# Diff 比较的文件扩展名
DIFF_FILTER_EXT = 'php,jsp,js,asp,aspx,py,css,html,htm,txt,cs,xml,inc,info,rb,md,ini,java'

# 当强行编码 Diff 原始输出结果出错时，用替代内容代替该行
CONTENT_REPLACE = '***** line contains special binary bytes cant show here *****\n'

# 分析器插件所在路径
ANALYSIS_PLUGIN_DIR = os.path.join(os.path.dirname(__file__), '../plugins')

# 日志存储路径
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs/wam.log')

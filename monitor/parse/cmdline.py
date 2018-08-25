#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import argparse


_OPTIONS_HELP_ = {
    'MODULE': 'Run in module mode',
    'TYPE': 'Run monitor type, "app" or "file"',
    'SOURCEURL': 'Downlaod rule source url',
    'REGEX': 'Download rule regex',
    'SRCPACKAGE': 'Source package path',
    'DESTPACKAGE': 'Dest package path',
    'FILE': 'Raw diff output content file path',
}


def parse_command():
    parser = argparse.ArgumentParser()

    # 控制日志输出级别
    # parser.add_argument('-v', dest='VERBOSE',
    #                     type=int, default=1, choices=range(0, 4),
    #                     help=VERBOSE_HELP)

    # parser.add_argument('-d', dest='DAEMON',
    #                     type=str, choices=['start', 'restart', 'stop', 'status'],
    #                     help=DAEMON_HELP)

    parser.add_argument('-m', dest='MODULE',
                        type=str, choices=['download', 'diff', 'analysis'],
                        help=_OPTIONS_HELP_['MODULE'])
    parser.add_argument('-t', dest='TYPE',
                        type=str, choices=['app', 'file'],
                        help=_OPTIONS_HELP_['TYPE'])

    download = parser.add_argument_group('download')
    download.add_argument('--url', dest='SOURCEURL',
                          type=str, help=_OPTIONS_HELP_['SOURCEURL'])
    download.add_argument('--regex', dest='REGEX',
                          type=str, help=_OPTIONS_HELP_['REGEX'])

    diff = parser.add_argument_group('diff')
    diff.add_argument('--src-package', dest='SRCPACKAGE',
                      type=str, help=_OPTIONS_HELP_['SRCPACKAGE'])
    diff.add_argument('--dest-package', dest='DESTPACKAGE',
                      type=str, help=_OPTIONS_HELP_['DESTPACKAGE'])

    analysis = parser.add_argument_group('analysis')
    analysis.add_argument('--src-file', dest='FILE',
                          type=str, help=_OPTIONS_HELP_['FILE'])

    return parser.parse_args()

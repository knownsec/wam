#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import os
import sys

# django modules
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wam.settings')
django.setup()


if __name__ == '__main__':
    # monitor modules
    from monitor.parse.cmdline import parse_command
    from monitor.core.download import download_file
    from monitor.core.diff import differ_two_packages
    from monitor.core.analysis import analysis_content
    from monitor.core.api import AppMonitor, FileMonitor

    args = parse_command()

    if args.MODULE:
        try:
            if args.MODULE == 'download':
                print download_file(args.SOURCEURL, args.REGEX)
            elif args.MODULE == 'diff':
                print differ_two_packages(args.SRCPACKAGE, args.DESTPACKAGE)
            elif args.MODULE == 'analysis':
                print analysis_content(open(args.FILE, 'rb').read())
        except Exception, ex:
            print ex
            sys.exit()

    else:
        if args.TYPE == 'app':
            try:
                monitor = AppMonitor(is_immediate=True)
                monitor.run()
            except KeyboardInterrupt:
                sys.exit()
        elif args.TYPE == 'file':
            try:
                monitor = FileMonitor(is_immediate=True)
                monitor.run()
            except KeyboardInterrupt:
                sys.exit()
        else:
            print 'invalid arguments'

#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import os
import time

from multiprocessing.dummy import Pool as ThreadPool

# monitor modules
from monitor.core.log import logger
from monitor.core.exception import MonitorDownloadError
from monitor.core.exception import MonitorDiffError
from monitor.core.exception import MonitorAnalysisError
from monitor.core.settings import MONITOR_CHECK_INTERVAL, PACKAGE_SOTRE_DIR, FILE_STORE_DIR
from monitor.core.download import download_file, move_file, remove_file
from monitor.core.diff import differ_two_packages, render_raw_content, differ_two_files
from monitor.core.analysis import analysis_content
from monitor.utils.common import get_config
from monitor.utils.mail import sendmail

# django moudles
from django.utils import timezone

# wam modules
from wam.apps.am.models import Rule, Package, Diff, Analysis
from wam.apps.fm.models import FRule, FFile, FDiff


class AppMonitor(object):

    def __init__(self, is_immediate=False):
        self._is_immediate = is_immediate

    def process_with_rule(self, rule=None):
        try:
            self._process_with_rule(rule)
        except Exception, ex:
            err = str(ex) + ', ("%r")' % rule
            logger.error(err)
            return

    @staticmethod
    def _process_with_rule(rule=None):
        logger.debug('starting to download package, ("%r")' % rule)
        try:
            package = download_file(rule.source_url, rule.regex, False)
        except MonitorDownloadError, ex:
            err = str(ex) + ', ("%r")' % rule
            logger.debug(err)

            # mail info
            err_msg = ex.message
            mail_content = ''
            if err_msg.startswith('unable to fetch download url'):
                mail_content = "Download package url is unavailable."
            # connect to target host failed, view on 'get_handler' function
            elif err_msg.startswith('unable to get response handler'):
                # DNS lookup of the host name failed
                if any(_ in err_msg for _ in ['Name or service not known',
                        'nodename nor servname provided', 'No address associated with hostname']):
                    mail_content = "Download file failed(DNS lookup failed)."
            elif err_msg.startswith('bad response'):
                if 'file not found' in err_msg:
                    mail_content = "Download file failed(file not found)."

            if mail_content:
                mail_content = "{info}\nrule name: {name}, url: {url}".format(info=mail_content, name=rule.name.encode('utf-8'), url=rule.source_url)

                try:
                    sendmail('[WAM Error Report] download package failed', mail_content)
                except Exception as ex:
                    err = "send mail error. {}".format(ex)
                    logger.error(err)

                info_msg = "send mail info: {}".format(mail_content.replace("\n", ''))
                logger.info(info_msg)
            return

        last_package = Package.objects.filter(rule=rule).order_by('-add_time').first()
        if last_package and last_package.md5 == package.get('md5', ''):
            remove_file(package['temppath'])
            logger.debug('package downloaded\'s md5 equal to the last package, ("%r")' % rule)
            return

        vendor_name = rule.vendor.name
        rule_name = rule.name
        timestamp = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        filename = package['filename']
        relative_path = os.path.join(vendor_name,
                                     os.path.join(rule_name, timestamp + '_' + filename))
        destpath = os.path.join(PACKAGE_SOTRE_DIR, relative_path)
        try:
            move_file(package['temppath'], destpath, cid=True)
        except MonitorDownloadError, ex:
            err = str(ex) + ', ("%r")' % rule
            logger.error(err)
            return
        to_package = Package(rule=rule, md5=package['md5'], size=package['size'],
                             path=relative_path, filename=filename,
                             timestamp=timestamp, response_headers=package['headers'])
        to_package.save()
        rule.last_check_date = timezone.now()
        rule.save()
        logger.info('package updating detected, ("%r")' % rule)

        # 如果不存在同一规则的上一个应用包记录，则不进行 Diff 比较操作，直接记录
        if not last_package:
            err = 'unable to differ with pre package, '
            err += 'no pre package found, ("%r")' % rule
            logger.debug(err)
            return

        try:
            raw_content = differ_two_packages(last_package.get_absolute_path(),
                                                to_package.get_absolute_path())
        except MonitorDiffError, ex:
            err = str(ex) + ', ("%r")' % rule
            logger.error(err)
            # Diff 过程出错时，删除当前下载的应用包以及相关记录
            to_package.delete()
            package_path = to_package.get_absolute_path()
            remove_file(package_path)
            return

        render_content = render_raw_content(raw_content)
        diff = Diff(s_package=last_package, d_package=to_package,
                    raw_content=raw_content, render_content=render_content)
        diff.save()
        logger.info('diff inserted, ("%r")' % rule)

        try:
            analysis_result = analysis_content(raw_content)
        except MonitorAnalysisError, ex:
            err = str(ex) + ', ("%r")' % rule
            logger.error(err)
            return

        analysis = Analysis(diff=diff, result=analysis_result)
        analysis.save()
        logger.info('analysis result inserted, ("%r")' % rule)

    def run(self):
        """
        循环读取数据库中所记录的下载规则，
        调用 process_with_rule() 函数进行处理
        """
        last_check_time = time.time()
        logger.info('monitor at %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        while True:
            check_interval = get_config('MONITOR_CHECK_INTERVAL') \
                if get_config('MONITOR_CHECK_INTERVAL') else MONITOR_CHECK_INTERVAL
            check_interval = int(check_interval)
            check_time = time.time()
            if self._is_immediate or (check_time - last_check_time) > check_interval:
                last_check_time = check_time
                self._is_immediate = False

                rules = Rule.objects.all()
                if not rules:
                    logger.info('no rules found in database')
                    continue

                logger.info('starting to process %s rules found in database' % len(rules))
                _l = [rule for rule in rules]
                pool = ThreadPool(10)
                pool.map(self.process_with_rule, _l)
                pool.close()
                cast_time = int(time.time() - last_check_time)
                logger.info('all rules check finished, next time in %ss'
                            % (MONITOR_CHECK_INTERVAL - cast_time))
            else:
                time.sleep(360 / 2)


class FileMonitor(object):

    def __init__(self, is_immediate=False):
        self._is_immediate = is_immediate

    def process_with_frule(self, frule=None):
        try:
            self._process_with_frule(frule)
        except Exception, ex:
            err = str(ex) + ', ("%r")' % frule
            logger.error(err)
            return

    @staticmethod
    def _process_with_frule(frule=None):
        logger.debug('starting to download file, ("%r")' % frule)
        try:
            ffile = download_file(frule.source_url, frule.regex, frule.regex_content)
        except MonitorDownloadError, ex:
            err = str(ex) + ', ("%r")' % frule
            logger.debug(err)
            return

        last_ffile = FFile.objects.filter(frule=frule).order_by('-add_time').first()
        if last_ffile and last_ffile.md5 == ffile.get('md5', ''):
            remove_file(ffile['temppath'])
            logger.debug('file downloaded\'s md5 equal to the last file, ("%r")' % frule)
            return

        frule_name = frule.name
        timestamp = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        filename = ffile['filename']
        relative_path = os.path.join(frule_name, timestamp + '_' + filename)
        destpath = os.path.join(FILE_STORE_DIR, relative_path)
        try:
            move_file(ffile['temppath'], destpath, cid=True)
        except MonitorDownloadError, ex:
            err = str(ex) + ', ("%r")' % frule
            logger.error(err)
            return
        to_ffile = FFile(frule=frule, md5=ffile['md5'], size=ffile['size'],
                         path=relative_path, filename=filename,
                         timestamp=timestamp, response_headers=ffile['headers'])
        to_ffile.save()
        frule.last_check_date = timezone.now()
        frule.save()
        logger.info('file updating detected, ("%r")' % frule)

        # 如果不存在同一规则的上一个文件记录，则不进行 Diff 比较操作，直接记录
        if not last_ffile:
            err = 'unable to differ with pre file, '
            err += 'no pre file found, ("%r")' % frule
            logger.debug(err)
            return

        try:
            raw_content = differ_two_files(last_ffile.get_absolute_path(),
                                           to_ffile.get_absolute_path())
        except MonitorDiffError, ex:
            err = str(ex) + ', ("%r")' % frule
            logger.error(err)
            # Diff 过程出错时，删除当前下载的文件以及相关记录
            to_ffile.delete()
            package_path = to_ffile.get_absolute_path()
            remove_file(package_path)
            return
        render_content = render_raw_content(raw_content)
        fdiff = FDiff(s_file=last_ffile, d_file=to_ffile,
                      raw_content=raw_content, render_content=render_content)
        fdiff.save()
        logger.info('diff inserted, ("%r")' % frule)

    def run(self):
        """
        循环读取数据库中所记录的下载规则，
        调用 process_with_rule() 函数进行处理
        """
        last_check_time = time.time()
        logger.info('monitor at %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        while True:
            check_interval = get_config('MONITOR_CHECK_INTERVAL') \
                if get_config('MONITOR_CHECK_INTERVAL') else MONITOR_CHECK_INTERVAL
            check_interval = int(check_interval)
            check_time = time.time()
            if self._is_immediate or (check_time - last_check_time) > check_interval:
                last_check_time = check_time
                self._is_immediate = False

                frules = FRule.objects.all()
                if not frules:
                    logger.info('no rules found in database')
                    continue

                logger.info('starting to process %s rules found in database' % len(frules))
                _l = [frule for frule in frules]
                pool = ThreadPool(10)
                pool.map(self.process_with_frule, _l)
                pool.close()
                cast_time = int(time.time() - last_check_time)
                logger.info('all frules check finished, next time in %ss'
                            % (MONITOR_CHECK_INTERVAL - cast_time))
            else:
                time.sleep(360 / 2)

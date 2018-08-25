#!/usr/bin/env python
# coding: utf-8


class MonitorBaseError(Exception):
    pass


class MonitorDownloadError(MonitorBaseError):
    pass


class MonitorDiffError(MonitorBaseError):
    pass


class MonitorAnalysisError(MonitorBaseError):
    pass

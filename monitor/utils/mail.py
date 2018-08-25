#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import smtplib
from email.mime.text import MIMEText

from monitor.utils.settings import EMAIL_SERVER
from monitor.utils.settings import EMAIL_PORT
from monitor.utils.settings import EMAIL_USER
from monitor.utils.settings import EMAIL_PASS
from monitor.utils.settings import EMAIL_FROM_ADDR
from monitor.utils.email_list import EMAIL_LIST


def _sendmail(to_list, subject, content):
    """
    params:
        to_addr[list]:
        subject[str]:
        content[str]: plain content
    """
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM_ADDR
    msg['To'] = ', '.join(to_list)

    smtp = smtplib.SMTP_SSL()
    smtp.set_debuglevel(0)
    smtp.connect(EMAIL_SERVER, EMAIL_PORT)
    smtp.login(EMAIL_USER, EMAIL_PASS)
    smtp.sendmail(EMAIL_FROM_ADDR, to_list, msg.as_string())
    smtp.quit()


def sendmail(subject, content):
    """
    params:
        subject[str]:
        content[str]: plain content
    """
    if EMAIL_LIST:
        _sendmail(EMAIL_LIST, subject, content)
    else:
        raise ValueError('email list is empty')

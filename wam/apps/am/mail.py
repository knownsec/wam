#!/usr/bin/env python
# coding=utf-8
# by Fooying 2014/02/19
# by Evi1m0  2015/11/17

from smtp import NetEase_SMTP,SendGrid_SMTP,Google_SMTP,QQ_SMTP

SmtpDict = {
    'qq':QQ_SMTP,
    'google':Google_SMTP,
    '163':NetEase_SMTP,
    'anquan':SendGrid_SMTP
    }

UserConfig = {
    'google': ('user','passwd'),
    '163': ('user','passwd'),
    'qq': ('user','passwd'),
    'anquan': ('user','passwd')
    }

class MAIL:
    '''邮件发送封装类
    '''

    def __init__(self, sendBy='163', **args):
        '''sendBy指定作为发信服务器
        '''
        smtp = SmtpDict[sendBy]()
        result = smtp.connect()
        self.__mail = False
        if result[0]:
            try:
                result = smtp.login(args['user'],args['passwd'])
            except:
                result = smtp.login(UserConfig[sendBy][0],UserConfig[sendBy][1])
            if result[0]:
                self.__mail = smtp
            else:
                print result[2]

    def send(self, **mailDict):
        '''邮件发送方法
        '''
        if self.__mail:
            to = mailDict['to']
            subject = mailDict.get('subject', '')
            body = mailDict.get('body', '')
            fromName = mailDict.get('fromName', 'Dc Team')
            replyName = mailDict.get('replyName', '')
            replyTo = mailDict.get('replyto', '')
            cc = mailDict.get('cc', ())
            bcc = mailDict.get('bcc', ())
            files = mailDict.get('files', [])

            if to:
                to = [to] if isinstance(to, basestring) else to
                if files:
                    files = [files] if isinstance(files, basestring) else files
                else:
                    files = []
                if replyTo and replyName:
                    reply = (replyName, replyTo)
                else:
                    reply = ()
                if cc:
                    cc = (cc, cc)
                else:
                    cc = ()
                if bcc:
                    bcc = (bcc, bcc)
                else:
                    bcc = ()

                ret = self.__mail.sendmail(to, subject, body, fromName, reply, files, cc, bcc)
                return ret[0]
            else:
                return False
        return False

if __name__ == '__main__':
    mailList = ('root@163.com')
    m = MAIL()
    ret = m.send(subject=u'[测试邮件] test_has_reply', body='this is a test emailx', to=mailList, fromName="WAM",
            replyTo='root@163.com', replyName='wam', cc='', bcc='')
    print 'End!', ret

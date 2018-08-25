#!/usr/bin/env python
# -*- coding=utf-8 -*-
#Coded by 一只死猫
#Time:2010-11-2
"""
Google/网易邮件发送接口
"""
import os
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import formataddr


class smtps:
    def __init__(self):
        pass

    def connect(self,host):
        self.host=host
        try:
            self.s=SMTP(host)
        except Exception,e:
            return (False,self.host,"Connect:"+str(e))
        else:
            return (True,self.host,"Connect:everything OK")

    def login(self,user,psw):
        try:
            self.user=user
            self.s.login(user,psw)
        except Exception,e:
            return (False,user,"Login:"+str(e))
        else:
            return (True,user,"Login:everything OK")

    def sendmail(self,mail_list,subject,message, from_name=u"test", reply_to=(), files=[], cc=(), bcc=()):
        msg=MIMEMultipart()
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="ISO-8859-1,utf-8"
        author = formataddr((str(Header(from_name, 'utf-8')), 'noreply@wam.com'))
        if len(reply_to) != 2 or not reply_to[1]:
            reply_to = author
        else:
            reply_to = formataddr((str(Header(reply_to[0], 'utf-8')), reply_to[1]))

        msg["From"]=author
        msg.add_header("Reply-To", reply_to)
        to_list = []
        if cc:
            cc_to = formataddr((str(Header(cc[0], 'utf-8')), cc[1]))
            msg["Cc"] = cc_to
            to_list.append(cc[1])

        if bcc:
            bcc_to = formataddr((str(Header(bcc[0], 'utf-8')), bcc[1]))
            msg["Bcc"] = bcc_to
            to_list.append(bcc[1])

        msg["Subject"]=subject
        #txt=MIMEText(message,"plain")
        #txt=MIMEText(message)
        #txt.set_charset("utf-8")
        txt=MIMEText(message.encode('utf-8'),"html", "utf-8")
        msg.attach(txt)

        for f in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)

        try:
            for contact in mail_list:
                msg["To"]=contact
                to_list.append(contact)

            #for contact in mail_list:
                #self.s.sendmail(self.user,contact,msg.as_string())

            print to_list
            self.s.sendmail(self.user,to_list, msg.as_string())

        except Exception,e:
            print e
            return (False,self.host,"Sendmail:"+str(e))
        else:
            return (True,self.host,"Sendmail:everything OK")

class Google_SMTP(smtps):
    def __init__(self):
        smtps.__init__(self)
        pass

    def connect(self,host="smtp.googlemail.com"):
        self.host=host
        try:
            self.s=SMTP(host)
        except Exception,e:
            return (False,self.host,"Connect:"+str(e))
        else:
            return (True,self.host,"Connect:everything OK")

    def login(self,user,psw):
        self.user=user
        self.s.docmd("EHLO server")
        self.s.starttls()
        try:
            self.s.login(user,psw)
        except Exception,e:
            return (False,user,"Login:"+str(e))
        else:
            return (True,user,"Login:everything OK")

class QQ_SMTP(smtps):
    def __init__(self):
        smtps.__init__(self)
        pass

    def connect(self,host="smtp.exmail.qq.com"):
        self.host=host
        try:
            self.s=SMTP(host)
        except Exception,e:
            return (False,self.host,"Connect:"+str(e))
        else:
            return (True,self.host,"Connect:everything OK")

class SendGrid_SMTP(smtps):
    def __init__(self):
        smtps.__init__(self)
        pass

    def connect(self,host="smtp.sendgrid.net"):
        self.host=host
        try:
            self.s=SMTP(host, 587)
        except Exception,e:
            return (False,self.host,"Connect:"+str(e))
        else:
            return (True,self.host,"Connect:everything OK")



class NetEase_SMTP(smtps):
    def __init__(self):
        smtps.__init__(self)
        pass

    def connect(self,host="smtp.163.com"):
        self.host=host
        try:
            self.s=SMTP(host)
        except Exception,e:
            return (False,self.host,"Connect:"+str(e))
        else:
            return (True,self.host,"Connect:everything OK")

def mail():
    config = {
        'google_account': '1',
        'google_password': '1',
        'netease_account': 'a2',
        'netease_password': '2',
        'qq_account': '3',
        'qq_password': '3',
        'sendgrid_account': '4',
        'sendgrid_password': '4'
    }

    ns = SendGrid_SMTP()
    result = ns.connect()
    if result[0]:
        result = ns.login(config['sendgrid_account'], config['sendgrid_password'])
        if result[0]:
            return ns
        else:
            print result[2]
    return False

if __name__ == '__main__':
    print mail()


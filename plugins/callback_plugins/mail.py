# -*- coding: utf-8 -*-
#Auther: Wood
#Date: Mon Jul 01 15:00:00 CST 2017
#Desc: 用于结果的邮件发送

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import smtplib
import json
import email.MIMEMultipart # import MIMEMultipart  
import email.MIMEText      # import MIMEText  
import email.MIMEBase      # import MIMEBase  
from email.header import Header  

from ansible.compat.six import string_types
from ansible.module_utils._text import to_bytes
from ansible.plugins.callback import CallbackBase

TEXTCHATSET = "utf-8" #设置字符集
    
def sendmail(subject='Ansible error mail', sender=None, pw=None, to=None, cc=None, body=None, smtphost=None):
    
    if sender is None:
        sender='<root>'
    if to is None:
        to='root'
    else:
        to = to[:]

    if smtphost is None:
        smtphost=os.getenv('SMTPHOST', 'localhost')

    if body is None:
        body = subject

    smtp = smtplib.SMTP()
    smtp.connect(smtphost)    
    
    to.append(u'xxx@xxx.com')
    to.append(u'xxx@xxx.com')
    to = ','.join(to)
    b_sender = to_bytes(sender)
    b_to = to_bytes(to)
    b_cc = to_bytes(cc)
    b_subject = to_bytes(subject)
    b_body = to_bytes(body)
    #得到To的邮箱
    b_addresses = b_to.split(b',')
    if cc:
        b_addresses += b_cc.split(b',')
      
    charset_subject = Header(b_subject, TEXTCHATSET)
    # 构造MIMEMultipart对象做为根容器
    main_msg = email.MIMEMultipart.MIMEMultipart()  
    # 构造MIMEText对象做为邮件显示内容并附加到根容器  
    text_msg = email.MIMEText.MIMEText(b_body, "html", _charset=TEXTCHATSET)  
    main_msg.attach(text_msg) 
    # 设置根容器属性  
    main_msg['From'] = "%s<monitor@xxx.com>" % Header("运维部邮箱","utf-8")
    main_msg['To'] = b_to
    main_msg['Subject'] = charset_subject
    main_msg['Date'] = email.Utils.formatdate()
    
    # 得到格式化后的完整文本  
    fullText = main_msg.as_string()      
    
    try:  
        smtp.login(b_sender, to_bytes(pw))
        smtp.sendmail("%s<monitor@feeyo.com>" % Header("运维部邮箱","utf-8"), b_addresses, fullText)
    finally:  
        smtp.quit()  
        
class CallbackModule(CallbackBase):
    """
    This Ansible callback plugin mails errors to interested parties.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'mail'
    CALLBACK_NEEDS_WHITELIST = False
    TIME_FORMAT='%Y-%m-%d %H:%M:%S'
    SENDER = 'xxx@xxx.com'
    PASSWD = 'xxxxxx'
  
    def v2_playbook_on_start(self, playbook):
        self.result = {"body": "", "to_address": [], "proj_id": ""}

    def v2_runner_on_failed(self, res, ignore_errors=False):

        host_name = res._host.get_name()
        role_name = res._task._role._role_name
        #if ignore_errors:
        #    return
            
        #只有部署代码的playbook才会发送邮件
        if role_name != 'deploy':
            return
        
        #get task
        task = res._task
        #get host
        host = res._host
        # get role
        role = task._role
        # get vars
        role_vars = role._variable_manager
        # get proj_id
        proj_id = role_vars.extra_vars.get('proj_id')
        # get group
        group = [g for g in host.groups if to_bytes(g.name) == proj_id][0]
        self.result['proj_id'] = proj_id
        self.result['to_address'] = group.vars.get('to_address', [])
        
        #subject = u'【上线结果通知-%s】「%s」: %s' %('failed', proj_id, host_name)
        body = u'<font color=red>node %s: 上线失败</font>' %host_name
        body += u'<br>'

        if 'stdout' in res._result.keys() and res._result['stdout']:
            body += u'<p>%s </p>' %"with the following output in standard output:"
            body += u'<p>%s </p>' % res._result['stdout']
        if 'stderr' in res._result.keys() and res._result['stderr']:
            body += u'<p>%s </p>' %"with the following output in standard stderr:"
            body += u'<p>%s </p>' % res._result['stderr']        
        if 'msg' in res._result.keys() and res._result['msg']:
            body += u'<p>%s </p>' %"with the following message:"
            body += u'<p>%s </p>' % res._result['msg']
        body += u'<br>'    
        self.result['body'] += body
        #sendmail(sender=self.SENDER, pw=self.PASSWD, to=to_address, smtphost='smtp.exmail.qq.com', subject=subject, body=body)

    def v2_runner_on_unreachable(self, res, ignore_errors=False):

        host_name = res._host.get_name()
        role_name = res._task._role._role_name
        #if ignore_errors:
        #    return
            
        #只有部署代码的playbook才会发送邮件
        if role_name != 'deploy':
            return
            
        #get task
        task = res._task
        #get host
        host = res._host
        # get role
        role = task._role
        # get vars
        role_vars = role._variable_manager
        # get proj_id
        proj_id = role_vars.extra_vars.get('proj_id')
        # get group
        group = [g for g in host.groups if to_bytes(g.name) == proj_id][0]
        self.result['proj_id'] = proj_id
        self.result['to_address'] = group.vars.get('to_address', [])
        
        #subject = u'【上线结果通知-%s】「%s」: %s' %('failed', proj_id, host_name)
        body = u'<font color=red>node %s: 主机不可达</font>' %host_name
        body += u'<br>'
        
        self.result['body'] += body
        
        #body += u'<p>An error occurred for %s, with the following message: </p>' %host_name
        #if isinstance(result, string_types):
        #    body += u'<p>%s </p>' %result
        #else:
        #    body += u'<p>%s </p>' %result['msg']
        #sendmail(sender=self.SENDER, pw=self.PASSWD, to=to_address, smtphost='smtp.exmail.qq.com', subject=subject, body=body)

    def v2_runner_on_ok(self, res, ignore_errors=False):

        host_name = res._host.get_name()
        role_name = res._task._role._role_name
        if ignore_errors:
            return
        #只有部署代码的playbook才会发送邮件
        if role_name != 'deploy':
            return
        #get task
        task = res._task
        #get host
        host = res._host
        # get role
        role = task._role
        # get vars
        role_vars = role._variable_manager
        # get proj_id
        proj_id = role_vars.extra_vars.get('proj_id')
        # get group
        group = [g for g in host.groups if to_bytes(g.name) == proj_id][0]
        self.result['proj_id'] = proj_id
        self.result['to_address'] = group.vars.get('to_address', [])
 
        if res._result['changed']:
            #subject = u'【上线结果通知-%s】「%s」: %s' %('successed', proj_id, host_name)
            body = u'<font color=green>node %s: 上线成功</font>' %host_name
        else:
            #subject = u'【上线结果通知-%s】「%s」: %s' %('failed', proj_id, host_name)
            body = u'<font color=red>node %s: 上线失败: 已更新过此次代码</font>' %host_name
        body += u'<br>'
        if res._result['files']:
            body += u'<p>%s </p>' % u"更新文件如下:"
            unzipfiles = u''
            for file in res._result['files']:
                unzipfiles += u'<p>%s </p>' %file
            body += unzipfiles
        body += u'<br>'    
        self.result['body'] += body        
        #sendmail(sender=self.SENDER, pw=self.PASSWD, to=to_address, smtphost='smtp.exmail.qq.com', subject=subject, body=body)
        
    def v2_playbook_on_stats(self, stats):
        subject = u'【上线结果通知】「%s」' %(self.result['proj_id'])
        to_address = self.result['to_address']
        body = self.result['body']
        sendmail(sender=self.SENDER, pw=self.PASSWD, to=to_address, smtphost='smtp.exmail.qq.com', subject=subject, body=body)

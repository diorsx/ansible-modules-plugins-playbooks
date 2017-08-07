# -*-coding:utf-8 -*-
#Auther: Wood
#Date: Mon Jul 01 15:00:00 CST 2017
#Desc: 用于结果的存储

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import time
import datetime
import pymongo

from ansible import constants as C
from ansible.compat.six import string_types
from ansible.module_utils._text import to_bytes
from ansible.plugins.callback import CallbackBase

TIME_FORMAT='%Y-%m-%d %H:%M:%S'

def log_to_mongo(msg, *args, **kwargs):
    time.mktime(datetime.datetime.now().timetuple())
    msg.update({"timestamp": time.mktime(datetime.datetime.now().timetuple())})
    operlog.insert_one(msg)

class CallbackModule(CallbackBase):
    """
    This Ansible callback plugin mails errors to interested parties.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'mongo'
    CALLBACK_NAME = 'log_to_mongo'
    CALLBACK_NEEDS_WHITELIST = False
    CALLBACK_MONGO_USER = 'xxx'
    CALLBACK_MONGO_PASS = 'xxx'
    CALLBACK_MONGO_HOST = 'xxx.xxx.xxx.xxx'
    CALLBACK_MONGO_PORT = 27017    

    def v2_playbook_on_start(self, playbook):
        self.mongo = pymongo.MongoClient(self.CALLBACK_MONGO_HOST, self.CALLBACK_MONGO_PORT)
        self.db = self.mongo.test
        self.db.authenticate(self.CALLBACK_MONGO_USER, self.CALLBACK_MONGO_PASS)
        self.operlog = self.db.fy_operlog    

    def v2_playbook_on_play_start(self, play):
        self.extra_vars = play._variable_manager.extra_vars
        if self.extra_vars.get('proj_id', ''):
            self.proj_id = self.extra_vars.get('proj_id')
        else:
            self.proj_id = 'default'
        timestamp = int(time.time())
        self.res = dict(proj_id=self.proj_id, timestamp=timestamp, res=list())

    def v2_playbook_on_task_start(self, task, is_conditional):
        #获取转义后task name
        self.task_name = task.name.strip()

    def v2_playbook_on_stats(self, stats):
        #res存至mongo
        self.operlog.insert_one(self.res)
        self.mongo.close()

    def v2_runner_on_ok(self, res, ignore_errors=False):
        host_name = self.get_info(res)
        changed = int(res._result['changed'])
        ok = 1
        result = dict(task_name=self.task_name, host_name=host_name, changed=changed, ok=ok)
        self.res['res'].append(result)

    def v2_runner_on_unreachable(self, res, ignore_errors=False):
        host_name = self.get_info(res)       
        unreachable = 1
        result = dict(task_name=self.task_name, host_name=host_name, unreachable=unreachable)        
        self.res['res'].append(result)

    def v2_runner_on_failed(self, res, ignore_errors=False):
        host_name = self.get_info(res)
        failed = 1
        result = dict(task_name=self.task_name, host_name=host_name, failed=failed)

        if 'stdout' in res._result.keys() and res._result['stdout']:
            result['stdout'] = res._result['stdout']
        if 'stderr' in res._result.keys() and res._result['stderr']:
            result['stderr'] = res._result['stderr']       
        if 'msg' in res._result.keys() and res._result['msg']:
            result['msg'] = res._result['msg']
        self.res['res'].append(result)    

    def get_info(self, res):
        #get host
        host = res._host
        host_name = host.get_name().strip()
    
        #此处获取的task name是没有转义的
        #get task
        #task = res._task
        #task_name = task.get_name().strip()
        return host_name

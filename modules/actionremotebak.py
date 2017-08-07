#!/usr/bin/python
# -*- coding: utf-8 -*-
#Type: action
#Auther: wood
#Desc: 打包远程服务器上文件并备份至本地
#Date: 2017年5月8日10:10:30

DOCUMENTATION = '''
---
module: remotebak
version_added: "historical"
short_description: Copies remote files to locations.
description:
     - The M(remotebak) module copies files on the remote locations to local. Use the M(fetch) module to copy files from remot
e locations to the local box.
options:
  src:
    description:
      - Remote path to a file to copy to the local; It should be absolute.
        If path is a directory, it is copied recursively. In this case, if path ends
        with "/", only inside contents of that directory are copied to destination.
        Otherwise, if it does not end with "/", the directory itself with all contents
        is copied. This behavior is similar to Rsync.
    required: ture
  dest:
    description:
      - Local absolute directory where the file should be copied to.
    required: true
    type: path
  prefix:
    description:
      - Local files prefix-name for remote files.
    required: true
'''
EXAMPLES = ''''''
RETURN = ''''''

__auther__ = 'wood'
__version__ = 'v0.1'

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import base64

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_bytes
from ansible.plugins.action import ActionBase
from ansible.utils.boolean import boolean
from ansible.utils.hashing import checksum, checksum_s, md5, secure_hash
from ansible.utils.path import makedirs_safe

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        source = self._task.args.get('src', None)
        dest = self._task.args.get('dest', None)
        prename = self._task.args.get('prefix', None)

        if source is None:
            result['failed'] = True
            result['msg'] = "src are required"
            return result
        if dest is None:
            result['failed'] = True
            result['msg'] = "dest are required"
            return result
        if not os.path.isdir(dest):
            result['failed'] = True
            result['msg'] = "%s should be absolute directory" %dest
            return result                   
        if prename is None:
            result['failed'] = True
            result['msg'] = "prefix are required"
            return result

        new_module_args = self._task.args.copy()
        new_module_args.update(src=source, dest=dest, prename=prename)
        module_return = self._execute_module(module_name='remotebak',module_args=new_module_args, task_vars=task_vars)
        module_executed = True
        bakfile = module_return.get('bakfile')
        if not module_return.get('failed'):
            self._connection.fetch_file(bakfile, dest)
        result.update(module_return)
        result.update(dest=dest)
        result.pop(bakfile)
        return result
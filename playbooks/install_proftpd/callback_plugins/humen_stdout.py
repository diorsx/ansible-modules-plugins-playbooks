# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json

from ansible.plugins.callback import CallbackBase

from ansible.playbook.play import Play
from ansible.playbook.task import Task
from ansible.executor.task_result import TaskResult
from ansible.executor.stats import AggregateStats
from ansible import constants as C

FIELDS = ['cmd', 'command', 'start', 'end', 'delta', 'msg', 'stdout', 'stderr']

class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'humen_stdout'
    CALLBACK_NAME = 'humen_stdout'
    CALLBACK_NEEDS_WHITELIST = False
    CALLBACK_AUTHOR = 'wood'

    def v2_runner_on_ok(self, res, ignore_errors=False):
        self.human_log(res)

    def v2_runner_on_failed(self, res, ignore_errors=False):
        self.human_log(res)

    def human_log(self, res):
        result = res._result
        if type(result) == type(dict()):
            for field in FIELDS:
                if field in result.keys():
                    print_info = u'\n{0}:\n{1}'.format(field, result[field])
                    self._display.display(print_info, color=C.COLOR_OK)
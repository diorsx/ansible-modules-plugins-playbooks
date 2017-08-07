#-*-coding:utf-8-*-
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
 
class CallbackModule(CallbackBase):
    """
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'history_stdout'
    CALLBACK_NAME = 'history_stdout'
    CALLBACK_NEEDS_WHITELIST = False
    CALLBACK_AUTHOR = 'wood'
 
    def __init__(self):
 
        super(CallbackModule, self).__init__()
        self.playbookid = None
        self.playid = None
        self.taskid = None
 
        self.plays = {}
        self.tasks = {}
        self.history = []
        self.valid = [Play,Task,TaskResult,AggregateStats]

    def v2_playbook_on_start(self, playbook):
        print_info = "Playbook start by %s" %self.CALLBACK_AUTHOR
        self._display.display(print_info, color=C.COLOR_OK)
 
    def v2_on_any(self, *args, **kwargs): 
        if args:
            # first arg should be an instance of a play/task/etc object
            arg = args[0]
 
            # do object specific actions
            if type(arg) not in self.valid:            
                pass
            else:
                if isinstance(arg, Play):                
                    # keep track of plays
                    hist = {}
                    hist['type'] = 'play'
                    hist['parent'] = self.playid
                    hist['id'] = id(arg)
                    if arg.name:
                        hist['name'] = arg.name
                    self.history.append(hist)
                    self._display.display('Start play[%s]: %s' %(hist['id'], hist['name']), color=C.COLOR_OK) 

                elif isinstance(arg, Task):
                    hist = {}
                    hist['type'] = 'task'
                    hist['parent'] = self.playid
                    hist['id'] = id(arg)
                    self.history.append(hist)
                    if arg.name:
                        hist['name'] = arg.name                        
                    else:
                        hist['name'] = u'未命名'
                    self._display.display('Start task[%s]: %s' %(hist['id'], hist['name']), color=C.COLOR_OK)

    def v2_playbook_on_stats(self, stats):
        self._display.display('Playbook End', color=C.COLOR_OK)
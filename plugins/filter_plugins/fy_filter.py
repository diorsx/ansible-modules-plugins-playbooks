#-*-coding:utf-8 -*-
#by wood

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.listify import listify_lookup_plugin_terms

try:
    import jmespath
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def to_str(value, separator=' '):
    if isinstance(value, list):
        return separator.join(value)

class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'to_str': to_str
        }
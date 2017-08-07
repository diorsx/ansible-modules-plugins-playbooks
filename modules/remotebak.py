#!/usr/bin/python
# -*- coding: utf-8 -*-
#Type: modules
#Auther: wood
#Desc: 打包远程服务器上文件并备份至本地
#Date: 2017年5月8日10:10:30

import os
import datetime
import socket
import tarfile
from ansible.module_utils.basic import AnsibleModule, get_module_path

def main():
    module = AnsibleModule(
        argument_spec = dict(
            src=dict(required=True, aliases=['src']),
            dest=dict(required=True, aliases=['dest']),
            prename=dict(required=True, aliases=['prename'])
        ),
        supports_check_mode=True
    )
    result = dict()
    src = module.params['src']
    dest = module.params['dest']
    prename = module.params['prename']
    fmt = '%b-%d-%y:%H:%M:%S'
    t = datetime.datetime.now().strftime(fmt)
    tmp_tar_file = '/tmp/' + prename + '_' + socket.gethostname() + '.tar.gz'
    files = src.split(',')
    count = 0
    not_exist_files = ''
    tar = tarfile.open(tmp_tar_file, 'w:gz')
    for f in files:
        try:
            tar.add(f)
        except:
            count = count + 1
            not_exist_files = not_exist_files + ' ' + f
    tar.close()
    if count == len(files):
        module.fail_json(msg="Source %s not found" % (not_exist_files))
    else:
        result.update(changed=True, bakfile=tmp_tar_file)
        module.exit_json(**result)

if __name__ == '__main__':
    main()
# -*- Coding:utf-8 -*-
"""

"""
import os
import datetime
import json
import shutil

from color import print_bold, print_warning, print_error


def operation_protocol(action):
    action_name = action.__name__
    print('action_name: ', action_name)
    
    def _operation_protocol(self, *args, **kwargs):
        def full_filled_action():
            result = action(self, *args, **kwargs)
            self.write_log_back()
            return result
    
        if self.batch_id:  # in a batch
            return full_filled_action()
        else:
            def single_action_wrapper():
                self.batch_id = Op.gen_batch_id()
                
                # exec finally block before return
                try:
                    return full_filled_action()
                finally:
                    self.batch_id = None

            return single_action_wrapper()
    
    return _operation_protocol


class Op:
    def __init__(self, app_id, base_path=os.path.abspath(os.curdir)):
        """
        :param app_id: for distinguish different shell app using shell-op, used in name log file
        :param base_path: op base path
        """
        self.app_id = app_id
        self.base_path = base_path
        self.batch_id = None
        
        self.log_path = os.path.join(base_path, '.shell_op_{0}.log'.format(app_id))
        self.log_dict = self.read_op_log()

    def read_op_log(self):
        if not os.path.exists(self.log_path):
            return {
                'undo': [],
                'redo': []
            }

        with open(self.log_path) as fr:
            return json.load(fr)
    
    def write_log_back(self):
        with open(self.log_path, 'w') as fw:
            json.dump(self.log_dict, fw)

    @staticmethod
    def gen_batch_id():
        now = datetime.datetime.now()
        return int(now.timestamp() * 1_000_000)

    def get_path(self, path):
        if os.path.isabs(path):
            return path
        
        return os.path.join(self.base_path, path)

    def __enter__(self):
        self.batch_id = Op.gen_batch_id()
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.batch_id = None

    @operation_protocol
    def mv(self, src, dst):
        full_src = self.get_path(src)
        full_dst = self.get_path(dst)

        self.do_mv(full_src, full_dst)

        self.log_dict['undo'].append({
            'batch_id': self.batch_id,
            'action': 'mv',
            'kwargs': {
                'src': full_src,
                'dst': full_dst
            }
        })
    
    def undo_mv(self, src, dst):
        self.do_mv(dst, src)
    
    def redo_mv(self, src, dst):
        self.do_mv(src, dst)

    def do_mv(self, full_src, full_dst):
        os.makedirs(full_dst, exist_ok=True)
        shutil.move(full_src, full_dst)

    def undo(self):
        self._do('undo')

    def redo(self):
        self._do('redo')

    def _do(self, do_type):
        """
        :param do_type: [undo | redo]
        :return:
        """
        all_do_types = ['undo', 'redo']
        all_do_types.remove(do_type)
        other_do_type = all_do_types[0]

        actions = []
        first_action_id = None
        for action in reversed(self.log_dict[do_type]):
            if first_action_id is None:
                first_action_id = action['batch_id']
            elif first_action_id != action['batch_id']:
                break
            
            actions.append(action)

        for action in actions:
            print_bold('try %s action: %s ' % (do_type, action['action']), end='')
            for key, value in action['kwargs'].items():
                print_bold('{0}: {1}'.format(key, value), end='')
            print_bold()

            reverse_action_func = getattr(self, '%s_%s' % (do_type, action['action']))
            try:
                reverse_action_func(**action['kwargs'])
            except Exception as ex:
                print_error(ex)
                print_warning('skipping it')

        self.log_dict[other_do_type].extend(actions)
        self.log_dict[do_type] = self.log_dict[do_type][:-len(actions)]
        self.write_log_back()


if __name__ == '__main__':
    with Op('test', r'H:\tmp\tianxing\vpn') as op:
        #op.mv('cert', 'cert2')
        op.undo()
        #op.redo()

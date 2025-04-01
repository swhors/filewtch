"""
File-Walk-Watch
"""

import os
import datetime
import difflib
import redis
import signal
import time
import sys
from parse_arg import parse_args

is_run = True

redis_handle = redis.StrictRedis(host='localhost', port=6379, db=0)
key = 'file_watch_list1'


def sig_handler(sig_num, frame):
    """Signal Handler"""
    global is_run
    if sig_num in [signal.SIGINT, signal.SIGKILL, signal.SIGTERM]:
        is_run = False


def lpush(key, value):
    redis_handle.lpush(key, value)


def create_file_list(root_dir: str, list_file_name: str):
    """ read file list and store to file """
    if os.path.isfile(list_file_name):
        os.remove(list_file_name)
    file_lists = os.walk(root_dir)
    file_dicts = {}
    for root, dirs, files in file_lists:
        file_dicts[root] = files
    fp = open(list_file_name, 'at')
    for k in file_dicts:
        if len(file_dicts[k]) > 0:
            for v in file_dicts[k]:
                if k.endswith('/'):
                    fp.write(k + v + '\n')
                else:
                    fp.write(k + "/" + v + '\n')
    fp.close()


def check_update(root_dir: str, list_file_name: str):
    """ check file update status """
    pre_list = ""
    result = ""
    if os.path.exists(list_file_name):
        with open(list_file_name) as fd:
            pre_list = fd.readlines()
    else:
        print(f'check_update : file open error [{list_file_name}]')
    create_file_list(root_dir, list_file_name)
    with open(list_file_name) as fd:
        result = fd.readlines()
    out_fd = open('result.txt', 'wt')
    if len(pre_list) > 0:
        # Find and print the diff:
        for line in difflib.unified_diff(pre_list, result, lineterm=''):
            if line.startswith('+/'):
                lpush(key, line)
    out_fd.close()


def loop_run(root_dir: str, list_file_name: str):
    """ loop """
    cnt = 0
    print(f'loop_run-start')
    while is_run:
        print(f'loop_run-{cnt}')
        check_update(root_dir=root_dir, list_file_name=list_file_name)
        time.sleep(1)
        cnt += 1
    print(f'loop_run-end')


def perf_test(root_dir: str, list_file_name: str):
    """ perf test """
    print(f'[{root_dir}/{list_file_name}] - start : {datetime.datetime.now()}')
    check_update(root_dir=root_dir, list_file_name=list_file_name)
    print(f'[{root_dir}/{list_file_name}] - end   : {datetime.datetime.now()}')


def run(*args):
    print(args)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    if args[2] == 1:
        perf_test(args[0], args[1])
    else:
        loop_run(args[0], args[1])


if __name__=="__main__":
    """ main """
    mode, args = parse_args()
    run(args)
 

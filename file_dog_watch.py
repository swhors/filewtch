"""
FileDogWatch
"""
import os
import sys
import signal
import time
import redis
import logging
from watchdog.observers.polling import PollingObserver
from watchdog.observers.polling import PollingObserverVFS
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
from crontab import CronTab
import sqlite3
from parse_arg import parse_args


redis_handle = redis.StrictRedis(host='localhost',
        port=6379, db=0)
is_run = True
key = 'file_watch_list1'


logging.basicConfig(level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')


def lpush(key, value):
    """Push File_Create_Event to Redis"""
    redis_handle.lpush(key, value)


def sig_handler(sig_num, frame):
    """Signal Handler"""
    global is_run
    if sig_num in [signal.SIGINT, signal.SIGKILL, signal.SIGTERM]:
        is_run = False


def cron_initialize(look_path: str):
    with CronTab(user='root') as cron:
        job_command = f'echo "file_dog_watch";ls -al {look_path}'
        cron.remove_all(command=job_command)
        job = cron.new(command=job_command)
        job.minute.every(1)


def db_initialize(look_path: str):
    """Initialize Database"""
    dbcon = sqlite3.connect("file:/var/lib/filewatch/filewatch.db")
    cur = dbcon.cursor()
    cur.execute("drop table if exists file_list")
    cur.execute("create table file_list(id integer primary key, name varchar(512))")
    file_names = os.walk(look_path)
    for root, _, names in file_names:
        name_list = []
        file_prefix = "/"
        if root.endswith('/'):
            file_prefix = ""
        for name in names:
            name_list.append([None, root + file_prefix + name])
        cur.executemany("insert into file_list(id, name) values(?, ?)", name_list)
    cur.close()
    dbcon.close()


def insert_path(file_path: str):
    """Insert FilePath to Database"""
    dbcon = sqlite3.connect("file:/var/lib/filewatch/filewatch.db")
    cur = dbcon.cursor()
    retult = False
    return_val = cur.execute(f'select * from file_list where name="{file_path}"').fetchall()
    if len(return_val) == 0:
        cur.execute(f'insert into file_list(name) values("{file_path}")')
        result = True
    cur.close()
    dbcon.close()
    return result


def delete_path(file_path: str):
    """Delete FilePath on Database"""
    dbcon = sqlite3.connect("file:/var/lib/filewatch/filewatch.db")
    cur = dbcon.cursor()
    cur.execute('delete from file_list where name="{file_path}"')
    cur.close()
    dbcon.close()


class EventHandler(FileSystemEventHandler):
    """Listening Event Handler"""
    def on_created(self, event):
        if not event.is_directory:
            print(f'created: {event.src_path}')
            if insert_path(event.src_path):
                redis_handle.lpush(key, event.src_path)
                print(f'created: {event.src_path}, new')
            else:
                print(f'created: {event.src_path}, existed')

    def on_deleted(self, event):
        if not event.is_directory:
            delete_path(event.src_path)
            #redis_handle.lpush(key, event.src_path)
            print(f'deleted: {event.src_path}')


def watch_inotify(look_path: str):
    """Add File Update Listening Events"""
    event_handler = LoggingEventHandler()
    observer = PollingObserver()
    observer.schedule(EventHandler(), look_path, recursive=True)
    observer.start()
    try:
        while is_run:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    print('-'*5 + ' terminated ' + '-'*5)
    #observer.join()


def run(*args):
    """Main runner"""
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    cron_initialize(look_path=args[0])
    db_initialize(look_path=args[0])
    watch_inotify(look_path=args[0])


if __name__=="__main__":
    """Main"""
    mode, args = parse_args()
    run(args)
 

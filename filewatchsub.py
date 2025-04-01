import redis
import time
import signal
import sys
import datetime

redis_handle = redis.StrictRedis(host='localhost', port=6379, db=0)

key = 'file_watch_list1'

is_run = True


def sig_handler(sig_num, frame):
    global is_run
    if sig_num in [signal.SIGINT, signal.SIGKILL, signal.SIGTERM]:
        is_run = False


def rpop(key: str) -> str:
    return redis_handle.rpop(key)


if __name__=="__main__":
    if len(sys.argv) >= 2:
        key = sys.argv[1]
    print(f'redis_key = {key}')
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    data = rpop(key)
    with open("file_list.txt", "wt") as fd:
        while is_run:
            if data == None or len(data) <= 0:
                time.sleep(1)
            else:
                line = f'{datetime.datetime.now()} : {data}'
                print(line)
                fd.write(line + "\n")
            data = rpop(key)
        fd.close()
 

<h1>FileWatch</h1>
<br>
<hr>

# 설명
```text
틀정 폴더에 파일이 추가 되는 이벤트를 감지하여 레디스에 이벤트를 전송합니다.
```
<img src="images/system_01.png" />

# 실행 방법

```text
usage: python filewatchpub.py [-h] [-m MODE] [-r ROOT] [-f FILELIST] [-p PERF]

틀정 폴더에 파일이 추가 되는 이벤트를 감지하여 레디스에 이벤트를 전송합니다.

options:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  allowed : walk or dog
  -r ROOT, --root ROOT
  -f FILELIST, --filelist FILELIST
  -p PERF, --perf PERF


설명:
  1. mode :
     os.walk를 이용할 경우에는 walk
     watchdog를 이용할 경우에는 dog
  2. root :
     감시할 폴더의 위치
  3. filelist :
     os.walk 일 경우에 지정.
     백업 파일 리스트 이름
  4. perf : 
     os.walk 일 경우에 지점.
     perf 테스트를 할 경우에 1을 지정, 아닌 경우에는 0
```

# 테스트 예제

### walk mode

```bash
(venv) root@nfstest:/opt/filewatch# python filewatchpub.py --mode walk --filelist filelist.db --root /data --perf 0
('/data', 'filelist.db', 0)
loop_run-start
loop_run-0
check_update : file open error [filelist.db]
loop_run-1
loop_run-2
loop_run-3
loop_run-4
loop_run-5
^Cloop_run-end
```

### dog mode

```bash
(venv) root@nfstest:/opt/filewatch# python filewatchpub.py --mode dog --root /data

created: /data/5.txt
created: /data/5.txt, new
^C----- terminated -----
(venv) root@nfstest:/opt/filewatch# 
```

# 주의
- root를 "/"로 지정하시 마세요.
- 종료 할 경우에는 CTRL+C를 눌러 주세요.
- 실핼 전에 redis가 설치 되어 얐어야 합니다.

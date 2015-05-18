#encoding=utf-8
import logging
import os
from datetime import datetime

__all__ = ["DEBUG", "INFO", "WARN", "ERROR"]

if not os.path.isdir('./log'):
    os.mkdir('log')

logging.basicConfig(level=logging.DEBUG,
        format='[PID:%(process)d] [TID:%(thread)d] %(asctime)s %(filename)s[line:%(lineno)d] - %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='./log/'+str(datetime.now())+'.log',
                filemode='w')


console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('[PID:%(process)d] [TID:%(thread)d] %(asctime)s %(filename)s[line:%(lineno)d] - %(levelname)s %(message)s')
console.setFormatter(formatter)
logger = logging.getLogger('')
logger.addHandler(console)

# debug信息不会打印在屏幕上，但是会写入日志文件
DEBUG = logger.debug
INFO = logger.info
WARN = logger.warn
ERROR = logger.error

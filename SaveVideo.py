# coding=utf-8
import logging
import GlobalParams
from LogModule import setup_logging
from threading import Thread
import datetime
import subprocess
setup_logging()
logger = logging.getLogger(__name__)

class SaveVideo(Thread):  # Resources are what Site knows how to deal with
    def __init__(self):
        Thread.__init__(self)


    def run(self):
        logger.info("SaveVideo Thread " + self.getName() + " Start Running")
        dtime = str(datetime.datetime.now()).replace(':','').replace(' ','').replace('-','').replace('.','')
        cmd = './ffmpeg -i rtsp://admin:admin@10.25.12.182:554/cam/realmonitor?channel=1 -vcodec copy ' + dtime + '.avi'
        p = subprocess.Popen(cmd,shell=True)
        logger.info('开始记录视频')
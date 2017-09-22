# -*- coding=utf-8 -*-

#import pymssql
import MySQLdb
from DBUtils.PooledDB import PooledDB
from MySQLdb.cursors import DictCursor
import ConfigParser

from LogModule import setup_logging


import logging
import os
setup_logging()
logger = logging.getLogger(__name__)

#为了使连接池只初始化一次创建此处2个全局变量，因为涉及别人的代码，导致设计上有出入，造成了circular dependency between the modules
#所以此处新建了一个专门管理数据库的全局变量
class GlobalParams1(object):
    cp = ConfigParser.SafeConfigParser()
    #path = "D:/pyworkspace/server/config/config.ini"
    cp.read('config/config.ini')
    #cp.read('config.ini')
    pool = PooledDB(creator = MySQLdb,mincached=1, maxcached=5,host = cp.get('db','my_host'),
                    port = int(cp.get('db','my_port')), user = cp.get('db', 'my_user'),
                    passwd = cp.get('db', 'my_passwd'),db = cp.get('db', 'my_db'),
                    use_unicode=False, charset = cp.get('db','my_dbcharset'), cursorclass = DictCursor)


def init():
    pass


def GetPool():
    logger.info('Create a new pool')
    return GlobalParams1.pool

if __name__ == '__main__':
    cp = ConfigParser.SafeConfigParser()
    # path = "D:/pyworkspace/server/config/config.ini"
    cp.read('config.ini')
    print cp.get('db','my_host')






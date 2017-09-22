# coding=utf-8
import ConfigParser
import logging
from LogModule import setup_logging
import Queue
import copy
import json
import sys
import threading
import time
from CreateSQL import SQLCluster
import threadpool

import AlarmUtil
setup_logging()
logger = logging.getLogger(__name__)

# 配置utf-8输出环境
reload(sys)
sys.setdefaultencoding('utf-8')

class Node:
    def __init__(self, id=0, data={'kind': 'aa', 'level': 1, 'position': ''}, children=None):
        self.id = id
        self.data = data
        self.children = children

    def setChildren(self, children={}):
        self.children = children

class AlarmNode:
    def __init__(self, id=0, org=0, req_que_size=100, resp_que_size=100, threadpo=None,
                 alarmDura={}, accu_threshold=0, max_alarm_level=5, parentRespQueue=None,
                 posLevel = None, alarmRules = None, alarmAddNum = None, alarmMerge = None, alarmStopNum = None):
        self.sqlcluster = SQLCluster()
        self.id = id
        self.org = org
        self.req_que_size = req_que_size
        self.resp_que_size = resp_que_size
        self.threadpo = threadpo
        self.alarmDura = alarmDura
        self.alarmList = []
        self.alarmScoreMap = {}
        self.packageId = -1
        self.preTime = 0
        self.duration = 0
        self.accu_threshold = accu_threshold
        self.reqQueue = Queue.Queue(maxsize=self.req_que_size)
        self.respQueue = Queue.Queue(maxsize=self.resp_que_size)
        self.max_alarm_level = max_alarm_level
        self.parentRespQueue = parentRespQueue
        self.logger = logger
        self.isStop= True
        self.threads = threadpool.makeRequests(self.alaMsg, [(None, None)])
        self.lock = threading.Lock()
        self.currentAlarmLevel = {'level': 0, 'alarmId': 0}
        self.maxAlarmId = 0
        #for version2
        self.allAlarmList = []
        self.alarmMapList = {}
        self.alarmLevel = 0
        #get a AlarmUtil
        self.alarmUtil = AlarmUtil.AlarmUtil()

        #for version2
        self.posLevel = posLevel
        self.alarmMerge = alarmMerge
        self.alarmRules = alarmRules
        self.alarmAddNum = alarmAddNum
        self.allAlarmTypeList = []
        self.allAlarmList = []
        self.alarmMapList = {}
        self.alarmLevel = 0
        self.alarmStopNum = alarmStopNum

    def endPackage(self, reason, packageId, userName=None, time=None, record=None):
        self.alarmList = []
        self.alarmScoreMap = {}
        self.preTime = 0
        self.duration = 0
        self.currentAlarmLevel = {'level': 0, 'alarmId': 0}
        self.maxAlarmId = 0
        self.parentRespQueue.put({'packageId': packageId, 'stop': reason, 'userName': userName, 'time': time, 'record': record})
        if packageId == self.packageId:
            self.packageId = -1
        #version2
        self.allAlarmTypeList = []
        self.allAlarmList = []
        self.alarmMapList = {}
        self.alarmLevel = 0
    def start(self):

        self.threadpo.putRequest(self.threads[0])

    def per(self, xs):
        if len(xs) == 0 or len(xs) == 1:
            return [xs]
        result = []
        for i in xs:
            temp_list = xs[:]
            temp_list.remove(i)
            temp = self.per(temp_list)
            for j in temp:
                j[0:0] = [i]
                result.append(j)
        return result

    def alaMsg(self):

        while True:

            msg = self.reqQueue.get()
            self.logger.debug("org %s, get msg %s" % (self.org, msg))
            if 'stop' in msg:
                self.logger.debug('org %d end self.packageId: %s, package by %s' % (self.org, self.packageId, msg['stop']))
                if 'userName' in msg:
                    if self.packageId == msg['packageId']:
                        self.isStop = True

                    self.endPackage(msg['stop'], msg['packageId'], msg['userName'], msg['time'], msg['record'])
                elif self.packageId > 0:
                    self.isStop = True
                    self.logger.warning('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                    if msg['stop'] == 'maxlevel':
                        self.logger.warning('满级结束报警包-包ID：' + str(self.packageId))
                    if msg['stop'] == 'timeout':
                        self.logger.warning('超时结束报警包-包ID：' + str(self.packageId))
                    if msg['stop'] == 'maxnum':
                        self.logger.warning('警情数量上限结束报警包-包ID：' + str(self.packageId))
                    self.endPackage(msg['stop'], self.packageId)
                self.logger.debug('self.is_stop: %s' % (self.isStop))
                break
            if self.isStop:
                self.logger.debug('org %s, begin a new package!' % (self.org))
                # 开启一个新包的线程

                self.packageId = self.alarmUtil.createPackage(self.org, msg['currentAlarmLevel'], msg['id'])
                self.logger.warning('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                self.logger.warning('开启报警包-包ID：' + str(self.packageId))
                self.isStop = False
            alarmId = msg['alarmId']
            # deviceId = msg['deviceId']
            # level = msg['currentAlarmLevel']
            #self.logger.debug('get msg: %s, duration: %s, level: %s'
            #                  % (msg, self.duration, self.currentAlarmLevel))

            # self.alarmList.append(alarmId)
            # if (not (alarmId in self.alarmScoreMap)):
            #     self.alarmScoreMap.setdefault(alarmId, {'num': 1, 'level': level})
            # else:
            #     self.alarmScoreMap[alarmId]['num'] += 1
            #     newLevel = (int)(self.alarmScoreMap[alarmId]['num'] / self.accu_threshold) + level
            #     if(newLevel < self.max_alarm_level and newLevel > self.alarmScoreMap[alarmId]['level']):
            #         self.alarmScoreMap[alarmId]['level'] = newLevel
            #     elif newLevel >= self.max_alarm_level:
            #         self.alarmScoreMap[alarmId]['level'] = self.max_alarm_level
            # if self.currentAlarmLevel['level'] < self.alarmScoreMap[alarmId]['level']:
            #     self.currentAlarmLevel['level'] = self.alarmScoreMap[alarmId]['level']
            #     self.currentAlarmLevel['alarmId'] = alarmId

            #for version2
            self.allAlarmList.append(msg)
            self.allAlarmTypeList.append(msg['alarmId'])
            msg_copy = copy.copy(msg)
            msg_copy.pop('id')
            msg_str = json.dumps(msg_copy)
            msg_posLevel = msg_copy['posLevel']
            msg_alarm_level = msg_copy['currentAlarmLevel']
            msg_alarm_id = msg_copy['alarmId']
            self.logger.warning('报警级别-初始-报警类型：' + self.sqlcluster.selectNameByAlarmType(int(msg['alarmId'])) + ',级别：' +  self.sqlcluster.selectNameByAlarmLevel(int(msg['currentAlarmLevel'])))
            if not (msg_str in self.alarmMapList):
                self.alarmMapList.setdefault(msg_str, {'num': 1, 'msg_alarm_id': msg_alarm_id, 'posLevel': msg_posLevel, 'currentAlarmLevel': msg_alarm_level, 'currentAlarmLevel': msg_alarm_level})
            else:
                self.alarmMapList[msg_str]['num'] += 1
                self.alarmMapList[msg_str]['currentAlarmLevel'] = msg_alarm_level
                #rule no.1
                add_level = self.alarmMapList[msg_str]['num'] / self.alarmMerge[msg_alarm_level]['alarm_add_steps']
                max_level = self.alarmMerge[msg_alarm_level]['alarm_add_sum']
                add_level = add_level if add_level <  max_level else max_level
                self.logger.debug("add_level %d" % add_level)
                self.alarmMapList[msg_str]['currentAlarmLevel'] = self.alarmMapList[msg_str]['currentAlarmLevel'] + add_level \
                    if self.alarmMapList[msg_str]['currentAlarmLevel'] + add_level < self.max_alarm_level else self.max_alarm_level
                self.logger.debug('rule1 alarmMapList %s' % (json.dumps(self.alarmMapList)))
                self.logger.debug("rule1 currentAlarmLevel %s" % self.alarmMapList[msg_str]['currentAlarmLevel'])
            #rule no.2
            newLevel = self.alarmMapList[msg_str]['currentAlarmLevel'] +  self.posLevel[msg_posLevel]
            self.alarmMapList[msg_str]['currentAlarmLevel'] = newLevel \
                if 0 <= newLevel <= self.max_alarm_level else self.alarmMapList[msg_str]['currentAlarmLevel']
            self.logger.debug('rule2 alarmMapList %s' % (json.dumps(self.alarmMapList)))
            self.logger.debug("rule2 currentAlarmLevel %s" % self.alarmMapList[msg_str]['currentAlarmLevel'])
            #rule no.3
            self.currentAlarmLevel['level'] = 0
            self.currentAlarmLevel['alarmId'] = msg_alarm_id
            for item in self.alarmMapList:
                if self.currentAlarmLevel['level'] == self.max_alarm_level:
                    break
                if self.alarmMapList[item]['currentAlarmLevel'] == self.currentAlarmLevel['level'] and self.currentAlarmLevel['level'] < self.max_alarm_level:
                    self.currentAlarmLevel['level'] += 1
                if self.alarmMapList[item]['currentAlarmLevel'] > self.currentAlarmLevel['level'] and self.alarmMapList[item]['currentAlarmLevel'] <= self.max_alarm_level:
                    self.currentAlarmLevel['level'] = self.alarmMapList[item]['currentAlarmLevel']
            self.logger.debug('rule3 alarmMapList %s' % (json.dumps(self.alarmMapList)))
            self.logger.debug("rule3 currentAlarmLevel %s" % self.currentAlarmLevel)
            self.logger.warning('报警级别-基础规则-报警类型：' + self.sqlcluster.selectNameByAlarmType(int(msg['alarmId'])) + ',级别：' +  self.sqlcluster.selectNameByAlarmLevel(int(self.currentAlarmLevel['level'])))
           # rule no.4
            for pa in self.alarmRules:
                length = len(pa)
                self.logger.debug("begin compare pa %s" % json.dumps(pa))
                for pp in self.per(pa):
                    #self.logger.debug("begin compare pp %s" % json.dumps(pa))
                    for i in range(0, len(self.allAlarmTypeList) - length + 1):
                        if cmp(self.allAlarmTypeList[i: i + length], pp) == 0 and self.currentAlarmLevel['level'] < self.max_alarm_level:
                            self.currentAlarmLevel['level'] += 1
                            self.logger.debug("%s contains %s at index %d" % (self.allAlarmTypeList, pp, i))
                            st = []
                            for id in pp:
                                st.append(self.sqlcluster.selectNameByAlarmType(int(id)))
                            self.logger.warning('报警级别-额外规则-动作序列-报警类型：' + self.sqlcluster.selectNameByAlarmType(int(msg['alarmId'])) + ',--发现动作序列：' +  ','.join(st))
                            break

            self.logger.debug('rule4 alarmMapList %s' % (json.dumps(self.alarmMapList)))
            self.logger.debug("rule4 currentAlarmLevel %s" % self.currentAlarmLevel)
            self.logger.warning('报警级别-额外规则-报警类型：' + self.sqlcluster.selectNameByAlarmType(int(msg['alarmId'])) + ',级别：' +  self.sqlcluster.selectNameByAlarmLevel(int(self.currentAlarmLevel['level'])))
            self.preTime = time.time()
            self.duration = self.alarmDura[alarmId]
            #self.logger.debug('get msg: %s, duration: %s, level: %s'
            #                  % (msg, self.duration,self.currentAlarmLevel))

            #self.logger.debug('alarmMapList %s' % (json.dumps(self.alarmMapList)))
            #self.logger.debug('allAlarmList %s' % (json.dumps(self.allAlarmList)))
            self.logger.debug('allAlarmTypeList %s' % (json.dumps(self.allAlarmTypeList)))
            self.logger.debug("currentAlarmLevel %s" % self.currentAlarmLevel)
            if self.currentAlarmLevel['level'] > self.max_alarm_level:
                self.currentAlarmLevel['level'] = self.max_alarm_level
            #更新包
            self.alarmUtil.updatePackageInfo(self.packageId, msg['id'], self.currentAlarmLevel['level'])

            if len(self.allAlarmTypeList) >= self.alarmStopNum and not (self.isStop):
                self.logger.debug('stop by maxmum, orgId %d' % (self.org))
                self.reqQueue.put({'stop': 'maxnum'})
            if self.currentAlarmLevel['level'] >= self.max_alarm_level  and not (self.isStop):
                self.logger.debug('stop by maxlevel, orgId %d' % (self.org))
                self.reqQueue.put({'stop': 'maxlevel'})


class MockCmd:
    reqQue = None
    respQue = None

    @staticmethod
    def sendMsg(msg):
        MockCmd.reqQue.put(msg)

class AutoScore:

    count = 1
    def __init__(self):
        self.sqlcluster = SQLCluster()
        self.logger = logger
        cp = ConfigParser.SafeConfigParser()
        cp.read('config/config.ini')
        self.req_que_size = (int)(cp.get('autoLevel', 'req_que_size'))
        self.resp_que_size = (int)(cp.get('autoLevel', 'resp_que_size'))
        self.threadpoolSize = (int)(cp.get('autoLevel', 'threadpoolSize'))
        self.accu_threshold = (int)(cp.get('autoLevel', 'accu_threshold'))
        self.max_alarm_level = (int)(cp.get('autoLevel', 'max_alarm_level'))
        self.threadpo = threadpool.ThreadPool(self.threadpoolSize)
        self.root = Node()
        self.reqQueue = Queue.Queue(maxsize=self.req_que_size)
        self.respQueue = Queue.Queue(maxsize=self.resp_que_size)
        self.alarmDura = {}
        children = {}

        #for version2
        self.posLevel = {}
        self.alarmMerge = {}
        self.alarmRules = []
        self.alarmAddNum = (int)(cp.get('autoLevel', 'alarm_add'))
        self.microsecond = 0
        self.lastmsg = {'id': -1}
        self.alarmUtil = AlarmUtil.AlarmUtil()
        self.stop_with_no_num = (int)(cp.get('autoLevel', 'stop_with_no_num'))
        self.alarmTimeWin = (int)(cp.get('autoLevel', 'alarm_time_win'))
        logger.warning('程序开始')
        logger.warning('读取配置文件-相同警情过滤时间间隔：' + str(self.alarmTimeWin) + 's')
        for i in cp.get('autoLevel', 'pos_level').split(','):
            self.posLevel[(int)(i.split('@')[0])] =  (int)(i.split('@')[1])
        for i in cp.get('autoLevel', 'alarm_merge').split(','):
            alarm_level = (int)(i.split('-')[0])
            alarm_add_steps = (int)(i.split('-')[1])
            alarm_add_per_step = (int)(i.split('-')[2])
            alarm_add_sum = (int)(i.split('-')[3])
            self.alarmMerge[alarm_level] = {'alarm_add_steps':  alarm_add_steps, 'alarm_add_per_step': alarm_add_per_step, 'alarm_add_sum': alarm_add_sum}
        for i in cp.get('autoLevel', 'alarm_rules').split(',') :
            li = []
            [ li.append((int)(item))  for item in i.split('-')]
            self.alarmRules.append(li)
        self.logger.debug('posLevel %s' % json.dumps(self.posLevel))
        self.logger.debug('alarmMerge %s' % json.dumps(self.alarmMerge))
        self.logger.debug('alarmRules %s' % json.dumps(self.alarmRules))
        self.logger.debug('alarmAddNum %s' % json.dumps(self.alarmAddNum))


        for i in cp.get('autoLevel', 'alarm').split(','):
            key = (int)(i.split('-')[0])
            value = (int)(i.split('-')[1])
            self.alarmDura[key] = value
        for key in cp.get('autoLevel', 'org').split(','):
            children[(int)(key)] = AlarmNode(org=(int)(key), req_que_size=self.req_que_size,
                                             resp_que_size=self.resp_que_size, threadpo=self.threadpo,
                                             alarmDura=self.alarmDura, accu_threshold=self.accu_threshold,
                                             max_alarm_level=self.max_alarm_level, parentRespQueue=self.respQueue,
                                             posLevel = self.posLevel, alarmRules = self.alarmRules, alarmAddNum = self.alarmAddNum, alarmMerge = self.alarmMerge, alarmStopNum = self.stop_with_no_num )
        self.logger.debug('init: %s, %s' % (self.alarmDura, children))
        self.root.setChildren(children)
        self.alaMsgTask = threadpool.makeRequests(self.alaMsg, [(None, None)])
        self.scanTimeTask = threadpool.makeRequests(self.scanTime, [(None, None)])
        self.threadpo.putRequest(self.alaMsgTask[0])
        self.threadpo.putRequest(self.scanTimeTask[0])

    def alaMsg(self):
        while True:
            # msg = self.reqQueue.get()
            # org = (int)(msg['orgId'])
            # self.root.children[org].reqQueue.put(msg)

            msg = self.reqQueue.get()
            org = (int)(msg['orgId'])
            old = self.microsecond
            self.microsecond = time.time() * 1000
            inter = self.microsecond - old
            lastmsg = self.lastmsg
            self.lastmsg = msg
            self.logger.debug("inter is : %d" % inter)
            # self.logger.debug("msg['alarmId'] is : %d" % int(msg['alarmId']))
            # self.logger.debug("lastmsg['alarmId'] is : %d" % int(lastmsg['alarmId']))
            pre = copy.copy(lastmsg)
            pre.pop('id')
            cur = copy.copy(msg)
            cur.pop("id")

            if inter < self.alarmTimeWin and pre == cur:
                self.logger.debug('ignore the msg: %s with in the timeWindow %d, old %d, now %d' % (json.dumps(msg), inter, old, self.microsecond))
                self.logger.warning('过滤报警-报警类型：' + self.sqlcluster.selectNameByAlarmType(int(msg['alarmId'])) + ',时间间隔：' +  str(inter) + '毫秒')
                self.alarmUtil.updateIgnoreMessage(-1, msg['id'])
            else:
                if org in self.root.children :
                    self.root.children[org].reqQueue.put(msg)
                else:
                    self.logger.debug('no orgid %d', org)


    def scanTime(self):
        while True:
            for i in self.root.children:
                leftSeconds = self.root.children[i].duration - (time.time() - self.root.children[i].preTime);
                #if leftSeconds >= -10:
                #    self.logger.debug('org %d close to %ds' % (self.root.children[i].org, leftSeconds))
                #    self.logger.debug(self.root.children[i].isStop)
                if (leftSeconds < 0 and not (self.root.children[i].isStop)):
                    self.logger.debug('stop by timeout, orgId %s' % (self.root.children[i].org))
                    self.root.children[i].reqQueue.put({'stop': 'timeout'})

                if (not self.root.children[i].reqQueue.empty()) and self.root.children[i].isStop:
                    self.root.children[i].start()
            time.sleep(1)

if __name__ == '__main__':
    # msg = {'orgId': 1, 'deviceId': 2, 'alarmId': 3, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 0}
    # node = Node()
    # autoScore = AutoScore()
    #
    # while True:
    #     msg = input('')
    #     autoScore.reqQueue.put(msg)
    autoScore = AutoScore()
    autoScore.reqQueue.put({'orgId': 2, 'deviceId': 2, 'alarmId': 7, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 2, 'id': 1, 'posLevel': 1})
    while True:
        msg = input('input::')
        autoScore.reqQueue.put(msg)

#autoScore.respQueue.get()
# {'orgId': 1, 'deviceId': 2, 'alarmId': 3, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 2, 'id': 1}
# {'orgId': 1, 'deviceId': 2, 'alarmId': 2, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 2}
# {'orgId': 1, 'deviceId': 2, 'alarmId': 1, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 2}
# {'orgId': 2, 'deviceId': 2, 'alarmId': 3, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 2}
# {'orgId': 3, 'deviceId': 2, 'alarmId': 3, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 2}
# {'orgId': 1, 'stop': 'user', 'userName': 'ss', 'time': '22-22', 'record': '11'}
# {'orgId'
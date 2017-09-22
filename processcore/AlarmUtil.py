# -*- coding=utf-8 -*-
import logging

import GlobalParams
from CreateSQL import SQLCluster
from LogModule import setup_logging
from MsgParserBox import MsgParser

setup_logging()
logger = logging.getLogger(__name__)
class AlarmUtil:
    def __init__(self):

        self.sqlcluster = SQLCluster()
    '''

    params: orgId, positionId, alarmId, dateArrId, timeArrId, alarmLevel
    alarmLevel:
        gentable = GenTable()
        gentable.query([DicOrgType,DicPosition,DicAlarmType,DicDateAttribute,DicTimeAttribute])
    '''

    def saveAlarmInfo(self, dictAlarmEvent):

        id = 1

        orgId = self.sqlcluster.deviceID2orgID(dictAlarmEvent['DeviceID'])
        orgType = self.sqlcluster.selectOrgTypeByOrgId(orgId)#Type
        positionId = self.sqlcluster.deviceID2position(dictAlarmEvent['DeviceID'])
        alarmId = int(dictAlarmEvent['AlarmType'])
        dateArrId = int(dictAlarmEvent['DateAttribute'])
        timeArrId = int(dictAlarmEvent['TimeAttribute'])

        gentable = GlobalParams.GetGenTable()
        alarmLevel = gentable.query([orgType, positionId, alarmId, dateArrId, timeArrId])

        parser = MsgParser()
        # save as db

        id = self.sqlcluster.insertAlarmEvent(dictAlarmEvent, alarmLevel)
        #logger.info("Message has been inserted into db successfully, id: " + str(id))
        if int(dictAlarmEvent['AlarmType']) != 9:
            logger.warning('----------------------------------------------------------')
            logger.warning('收到报警-' + '报警类型：' + self.sqlcluster.selectNameByAlarmType(int(dictAlarmEvent['AlarmType'])) + ' 报警级别：' + self.sqlcluster.selectNameByAlarmLevel(int(alarmLevel)))
        auSco = GlobalParams.GetAutoScoreInstance()
        if (int(alarmId) != 9):
            logger.debug('alarm type: ' + str(alarmId))
            auSco.reqQueue.put({'orgId': orgId, 'deviceId': dictAlarmEvent['DeviceID'], 'alarmId': alarmId, 'dateArrId': dateArrId, 'timeArrId': timeArrId, 'currentAlarmLevel': alarmLevel, 'id': int(id), 'posLevel' : 2})
        else:
            logger.debug('get 999999')


    def saveOriginalInfo(self, dictdata):
        self.sqlcluster.insertOriginalInfo(dictdata)

    def createPackage(self, orgId, level, id, isDeal = 0, isFinish = 0):
        print "create package !"
        #创建新包
        packageId = self.sqlcluster.createPackage(orgId, level, isDeal, isFinish)

        #更新AlarmEvent中的packageid
        self.sqlcluster.updateAlarmEvent(packageId, id)

        #通知客户端
        notice_queue = GlobalParams.getNoticeProcessQueue()
        notice_queue.put(packageId)
        logger.info("create package: " + str(packageId))
        return packageId

    def updatePackageInfo(self, packageId, id, level):
        #更新包信息
        self.sqlcluster.updatePackageLevel(packageId, level)

        #更新AlarmEvent中的packageid
        self.sqlcluster.updateAlarmEvent(packageId, id)

        #通知客户端
        notice_queue = GlobalParams.getNoticeProcessQueue()
        notice_queue.put(packageId)
    def updateIgnoreMessage(self, packageId, id):
        #更新包信息
        # self.sqlcluster.updatePackageLevel(packageId, level)

        #更新AlarmEvent中的packageid
        self.sqlcluster.updateAlarmEvent(packageId, id)

        #通知客户端
        # notice_queue = GlobalParams.getNoticeProcessQueue()
        # notice_queue.put(packageId)
    def getMsg1(self):
        # 获取要结包的packageId
        auSco = GlobalParams.GetAutoScoreInstance()
        dict = auSco.respQueue.get()
        self.sqlcluster.updatePackageFinishInfo(dict['packageId'])


    def endPackageByUser(self, packageId, userName, time, record):
        msg = {}
        auSco = GlobalParams.GetAutoScoreInstance()
        #self.sqlcluster.updatePackageFinishInfoByUser(packageId, userName, time, record)
        orgId = self.sqlcluster.selectOrgIdByPackageId(packageId)
        msg['orgId'] = orgId
        msg['userName'] = userName
        msg['time'] = time
        msg['record'] = record
        msg['packageId'] = packageId
        msg['stop'] = 'End by client'
        auSco.reqQueue.put(msg)
        #auSco.reqQueue.put({'orgId': 1, 'stop': 1})

if __name__ == '__main__':
    pass


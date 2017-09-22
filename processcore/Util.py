import Logging
import threading
import random
import json, datetime
import time
class AlarmUtil:
    def __init__(self, autoSco):
        self.logger = Logging.getLogger()
        self.auSco = None
        self.mutex = threading.Lock()
        self.msg_id = 1
        self.pak_id = 1
        self.autoSco = autoSco

    def produce_msg_id(self):
        msg_id = 0
        if self.mutex.acquire():
            msg_id = self.msg_id
            self.msg_id = msg_id + 1
            self.mutex.release()
            return msg_id
        return -1

    def produce_pak_id(self):
        pak_id = 0
        if self.mutex.acquire():
            pak_id = self.pak_id
            self.pak_id = pak_id + 1
            self.mutex.release()
            return pak_id
        return -1

    def produce_msg(self):
        msg = {}

        return msg

    def saveAlarmInfo(self, dictAlarmEvent):
        msg = {}
        #{'orgId': 3, 'deviceId': 2, 'alarmId': 3, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 2}
        i = random.randint(16, 19)
        if i == 19:
            i = 21

        msg['orgId'] = i
        msg['deviceId'] = i + 1
        msg['alarmId'] = random.randint(1, 5)
        msg['dateArrId'] = 1
        msg['timeArrId'] = 1
        msg['currentAlarmLevel'] = random.randint(1, 5)
        msg['id'] = self.produce_msg_id()
        self.logger.info('save msg : %s' % (json.dumps(msg)) )
        #self.autoSco.reqQueue.put(msg)

    def saveAlarmInfoIgnore(self, dictAlarmEvent):
        msg = {}
        # {'orgId': 3, 'deviceId': 2, 'alarmId': 3, 'dateArrId': 4, 'timeArrId': 5, 'currentAlarmLevel': 2}
        i = random.randint(16, 19)
        if i == 19:
            i = 21

        msg['orgId'] = i
        msg['deviceId'] = i + 1
        msg['alarmId'] = random.randint(1, 5)
        msg['dateArrId'] = 1
        msg['timeArrId'] = 1
        msg['currentAlarmLevel'] = random.randint(1, 5)
        msg['id'] = self.produce_msg_id()
        self.logger.info('save msg : %s' % (json.dumps(msg)))

    def createPackage(self, orgId, level, id, isDeal = 0, isFinish = 0):
        pak_id = self.produce_pak_id()
        self.logger.info('create pakage: pak_id %s, orgid %s, level %s, id %s' % (pak_id, orgId, level, id))
        return pak_id

    def updatePackageInfo(self, packageId, id, level):
        self.logger.info('updatePackageInfo: pak_id %s, id %s, level %s' % (packageId, id, level))

    #get the package for end!
    def getMsg(self):
        pass

    def endPackageByUser(self, packageId, userName, time, record):
        self.logger.info('endbyuser packageId %s, userName %s, time %s, record %s' % (packageId, userName, time, record))


if __name__ == "__main__":
    # alarmUtil = AlarmUtil({})
    # for i in range(1, 10):
    #     alarmUtil.saveAlarmInfo({})
    #     alarmUtil.createPackage(1, 1, 1)
    print time.time()

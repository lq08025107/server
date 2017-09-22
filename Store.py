from MsgParserBox import MsgParser
from CreateSQL import SQLCluster
from threading import Thread
import Queue
from processcore.AlarmUtil import AlarmUtil
from LogModule import setup_logging
import datetime
import logging

setup_logging()
logger = logging.getLogger(__name__)

class StoreProcessThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.StoreQueue = Queue.Queue()
        self.IsRunning = True
        self.sqlcluster = SQLCluster()
    def StopThread(self):
        self.IsRunning = False

    def run(self):
        logger.info("Store " + self.getName() + " Start Running")

        while self.IsRunning:
            while self.StoreQueue.not_empty:
                try:
                    message = self.StoreQueue.get()

                    parser = MsgParser()
                    alarmUtil = AlarmUtil()

                    data = parser.jsonParser(message)
                    alarmUtil.saveOriginalInfo(data)

                    deviceid = self.sqlcluster.deviceName2deviceID(data['SensorId'])

                    alarmtype = self.sqlcluster.alarmCode2alarmType(data['EventType'])
                    #2000-01-01T09:34:54.311CST
                    alarmtime = data['StartTime'].replace('CST', '')
                    alarmtime = alarmtime.replace('T', ' ')

                    dattribute = 0
                    if datetime.datetime.now().weekday() in [5, 6]:
                        dattribute = 2
                    else:
                        dattribute = 1

                    xmlstring = parser.xmlbuilder(alarmtype,alarmtime, 0, deviceid,0,dattribute)
                    dataList = parser.parseAlarmEvent(xmlstring)

                    alarmUtil.saveAlarmInfo(dataList)

                    # save as db
                    #insertsql = parser.constrAlarmEventSQL(dataList)
                    #id = ms.executeAndGetId(insertsql)
                    #logger.info("Message has been inserted into db successfully, id: " + str(id))

                    # send to application module
                    #notice_queue = GlobalParams.getNoticeProcessQueue()
                    #notice_queue.put(id)

                except Exception, e:
                    # log as file
                    logger.error("Error occured!!!", exc_info=True)
        logger.info("Store " + self.getName() + " Stop Run")




from xml.dom.minidom import parseString, parse
from xml.dom import minidom
import json
from LogModule import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)
class MsgParser(object):
    def docparse(self):
        dom = parse("D:\\tcp.xml")
        nodeList = []
        AlarmTypeID = dom.getElementsByTagName("AlarmTypeID")[0].childNodes[0].nodeValue
        nodeList.append(AlarmTypeID)
        PictureData = dom.getElementsByTagName("PictureData")[0].childNodes[0].nodeValue
        nodeList.append(PictureData)
        return nodeList

    def jsonParser(self, jsoncontent):
        message = json.loads(jsoncontent)
        return message

    def xmlbuilder(self, alarmtypeid= 0, alarmtime=0, score=0, deviceid=0, channelid=0, dateattribute=1, timeattribute=1, procedure=0, picturedata=0):
        impl = minidom.getDOMImplementation()
        dom = impl.createDocument(None, 'WarningData', None)
        root = dom.documentElement

        msg = dom.createElement('AlarmTypeID')
        data = dom.createTextNode(str(alarmtypeid))
        msg.appendChild(data)
        root.appendChild(msg)

        msg = dom.createElement('AlarmTime')
        data = dom.createTextNode(str(alarmtime))
        msg.appendChild(data)
        root.appendChild(msg)

        msg = dom.createElement('Score')
        data = dom.createTextNode(str(score))
        msg.appendChild(data)
        root.appendChild(msg)


        msg = dom.createElement('DeviceID')
        data = dom.createTextNode(str(deviceid))
        msg.appendChild(data)
        root.appendChild(msg)

        msg = dom.createElement('ChannelID')
        data = dom.createTextNode(str(channelid))
        msg.appendChild(data)
        root.appendChild(msg)

        msg = dom.createElement('DateAttribute')
        data = dom.createTextNode(str(dateattribute))
        msg.appendChild(data)
        root.appendChild(msg)


        msg = dom.createElement('TimeAttribute')
        data = dom.createTextNode(str(timeattribute))
        msg.appendChild(data)
        root.appendChild(msg)


        msg = dom.createElement('Procedure')
        data = dom.createTextNode(str(procedure))
        msg.appendChild(data)
        root.appendChild(msg)

        msg = dom.createElement('PictureData')
        data = dom.createTextNode(str(picturedata))
        msg.appendChild(data)
        root.appendChild(msg)

        xmlstring = dom.toxml();
        return xmlstring
    def parseAlarmEvent(self, xmlcontent):

        dom = parseString(xmlcontent)
        nodeList = {}
        AlarmTypeID = dom.getElementsByTagName("AlarmTypeID")[0].childNodes[0].nodeValue
        nodeList['AlarmType'] = AlarmTypeID
        
        AlarmTime = dom.getElementsByTagName("AlarmTime")[0].childNodes[0].nodeValue
        nodeList['AlarmTime'] = AlarmTime

        Score = dom.getElementsByTagName("Score")[0].childNodes[0].nodeValue
        nodeList['Score'] = Score
        
        DeviceID = dom.getElementsByTagName("DeviceID")[0].childNodes[0].nodeValue
        nodeList['DeviceID'] = DeviceID

        ChannelID = dom.getElementsByTagName("ChannelID")[0].childNodes[0].nodeValue
        nodeList['ChannelID'] = ChannelID
        
        Procedure = dom.getElementsByTagName("Procedure")[0].childNodes[0].nodeValue
        nodeList['Procedure'] = Procedure

        PictureData = dom.getElementsByTagName("PictureData")[0].childNodes[0].nodeValue
        nodeList['PictureData'] = PictureData

        DateAttribute = dom.getElementsByTagName("DateAttribute")[0].childNodes[0].nodeValue
        nodeList['DateAttribute'] = DateAttribute

        TimeAttribute = dom.getElementsByTagName("TimeAttribute")[0].childNodes[0].nodeValue
        nodeList['TimeAttribute'] = TimeAttribute
        return nodeList

    def parseRegisterData(self, xmlcontent):
        Channels = {}
        DeviceID = None
        try:
            xmlfile = minidom.parseString(xmlcontent)
            if xmlfile.getElementsByTagName("RegisterData") != None:
                DeviceID = xmlfile.getElementsByTagName("DeviceID")[0].childNodes[0].nodeValue
                for channel in xmlfile.getElementsByTagName("Channel"):
                    channel_id = channel.getAttribute("id")
                    channel_ip = channel.getElementsByTagName("ChannelIP")[0].firstChild.nodeValue
                    channel_port = channel.getElementsByTagName("ChannelPort")[0].firstChild.nodeValue
                    channel_name = channel.getElementsByTagName("ChannelName")[0].firstChild.nodeValue
                    channel_type = channel.getElementsByTagName("ChannelType")[0].firstChild.nodeValue
                    Channels[channel_id] = [channel_ip, channel_port, channel_name, channel_type]
            else:
                DeviceID = xmlfile.getElementsByTagName("DeviceID")[0].childNodes[0].nodeValue

        except Exception, e:
            logger.error("This is not a well formed xml.", exc_info=True)

        return DeviceID, Channels



def main():
    msgparser = MsgParser()
    xml = """<?xml version="1.0" encoding="utf-8"?>
<WarningData>
<AlarmTypeID>1</AlarmTypeID>
<AlarmTime>2016-04-12 08:48:54.000</AlarmTime>
<Score>65.2</Score>
<DeviceID>1</DeviceID>
<ChannelID>1</ChannelID>
<DateAttribute>1</DateAttribute>
<TimeAttribute>1</TimeAttribute>
<Procedure>Closing(time,1) -> 4 -> Foot(time,1) -> 4 -> Face(time,1) -> 1 -> Foot(time,1)</Procedure>
<PictureData>ftp://10.25.18.30/foo/bar/something.jpg</PictureData>
</WarningData>
    """

    registerxml = """<?xml version="1.0" encoding="utf-8"?>
<RegisterData>
    <DeviceInfo>
		<DeviceID>1</DeviceID>
    </DeviceInfo>
    <Channels>
        <Channel id="1">

            <ChannelIP>10.25.18.9</ChannelIP>
            <ChannelPort>8080</ChannelPort>
        </Channel>
        <Channel id="2">
            <ChannelIP>10.25.18.9</ChannelIP>
            <ChannelPort>8080</ChannelPort>
        </Channel>
    </Channels>
</RegisterData>
"""
    jsoncontent = '''
    {
	"AlarmLevel":1,
	"CutboardBox":null,
	"CutboardTimeOffset":null,
	"EventType":220,
	"EventTypeProbability":0,
	"FrameRate":15,
	"HotspotId":"undefined",
	"Id":"564afcf66c38520001000853",
	"PeopleId":"e92aae53b7fb415ba08c92692f559740",
	"PlanetId":"undefined",
	"SceneId":"undefined",
	"SensorId":"a1f20f44503532313300000500d10008",
	"SliceLength":8510,
	"StartTime":"2015-11-17T18:09:57.532CST",
	"TimeLength":8510,
	"UserId":""
}
    '''
    msgParser = MsgParser()
    #dataList = msgParser.docparse()
    dataList = msgParser.jsonParser(jsoncontent)
    print dataList
    xmlcontent = msgParser.xmlbuilder()
    print xmlcontent
    #querytest = msgParser.constrAlarmEventSQL(dataList,1)

    #msgParser.constrAlarmEventSQL(dataList)
    #deviceid, channels = msgParser.parseRegisterData(registerxml)
    #print deviceid
    #print channels['1']



if __name__ == '__main__':
    main()

        

# coding=utf-8
from twisted.web.server import Site  # Site is a server factory for HTTP
from twisted.web.resource import Resource
from twisted.internet import reactor
import logging
import GlobalParams
from LogModule import setup_logging
from threading import Thread
import json
setup_logging()
logger = logging.getLogger(__name__)

class PrintPostBody(Resource, Thread):  # Resources are what Site knows how to deal with
    def __init__(self):
        Thread.__init__(self)

    isLeaf = True  # Disable child lookup

    def render_POST(self, request):  # Define a handler for POST requests
        queue = GlobalParams.getStoreProcessQueue()
        # newdata = request.content.getvalue()
        newdata = request.content.read()

        #logger.info(newdata)
        if int(json.loads(newdata)['EventType']) != 220:
            logger.info('报警类型: ' + str(json.loads(newdata)['EventType']))
        queue.put(newdata)
        #logger.info("Received post request from host: " + str(request.client.host) + ".")
        return '200'
    def run(self):
        logger.info("Post Thread " + self.getName() + " Start Running")
        reactor.listenTCP(8000, Site(PrintPostBody()))
        reactor.run(installSignalHandlers=0)
from amqplib import client_0_8 as amqp
from settings import *
import socket
from amqplib.client_0_8.exceptions import *
from pjutils.exc import ChainedException
from pjutils.MessagingServer.MessagingServer import MQServer


class NoRegisterCenterURLDefined(ChainedException):
    pass


class LTRegisterQueue(object):
    mqServer = None
    queueName = "po_box"
    exchangeName = "sorting_room"
    routingKey = "jason"
    
    persistentMessageMode = 2
    sett = False


    def __init__(self, mqServer):
        # define properties
        self.mqServer = mqServer
        self.MQServer = self.mqServer

        # we create the queues and exchanges everytime we create and instance of this class
        # this way client code does not need to worry whether exchanges have been created or not
        # this will work since the exchanges are reused, if they already exists
        self.CreateQueues()
        pass

    def InitialiseImport(self, url = None):
        """ Will initialise queue with a single message, witch will mean that a specific URL must be parsed
        and inserted as LT Geo Data. The page will contain links to deeper levels, which will be
        later inserted as other messoges"""

        # send initial message with a defined URL in GlobalSettings
        if url is None:
            raise NoRegisterCenterURLDefined("""Please pass a --url param to specify which part of the web page to parse.
Root url is %s, but you can pass any sub url if you want to parse only sub-pages """ % "http://www.registrucentras.lt/adr/p/")
        else:
            self.SendMessage(url)


    def SendMessage(self, msgBody):
        msgBody = str(msgBody)
        msg = amqp.Message(msgBody)
        msg.properties["delivery_mode"] = self.persistentMessageMode
        self.mqServer.Channel.basic_publish(msg, exchange=self.exchangeName, routing_key= self.routingKey)


        

    def CreateQueues(self):
        """ Creates all neded queues and bindings needed to work with RegistruCentras.lt """
        # create a queue used for reading from http://www.registrucentras.lt/adr/p/index.php
        if LTRegisterQueue.sett == True:
            return
        self.mqServer.Channel.queue_declare(queue=self.queueName, durable=True, exclusive=False, auto_delete=False)
        self.mqServer.Channel.exchange_declare(exchange = self.exchangeName, type="direct", durable=True, auto_delete=False,)

        # create binding - from po_box to sorting room
        self.mqServer.Channel.queue_bind(queue=self.queueName, exchange= self.exchangeName, routing_key= self.routingKey)

        LTRegisterQueue.sett = True

    def ConsumeMessage(self, msg):
        self.mqServer.Channel.basic_ack(msg.delivery_tag)

    def ReadMessage(self):
        msg = self.mqServer.readMessage(self.queueName)
        return msg

    def _clear(self):
        count = 0
        self.MQServer.BeginTransaction()
        while True:
            msg = self.ReadMessage()
            if msg is None:
                break
            count += 1
            self.ConsumeMessage(msg)
        self.MQServer.Commit()

    def Clear(self):
        """ Clear the queue of any pending messages. This is done by reading manually all messages
        until there is none.
        """
        count = self._clear()

        self._clear()
        print "cleared  total %s messages " % count


    def IsEmpty(self):
        """ Tells if RegisterQueue is empty.
        If queue is empty, then it means that either processing has finished, or has not started at all.
        Initiaiate processing by inserting new Root message"""
        return self.MQServer.isEmpty(self.queueName)

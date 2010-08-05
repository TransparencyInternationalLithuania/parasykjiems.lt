from amqplib import client_0_8 as amqp
from FeatureBroker import *
from settings import *
import socket
from pjutils.exc import ChainnedException


class ConnectToMessageServerFailed(ChainnedException):
    pass

class MQServer:
    """ Helps establish a connection to RabbitMQ server, and initialise all default queu
    """
    Connection = None
    Channel = None

    def __init__(self):
        # open connection to localhost server
        try:
            self.Connection = amqp.Connection(host="localhost:5672", userid="guest", password="guest", virtual_host="/", insist=False)
        except socket.error as e:
            raise ConnectToMessageServerFailed("""Failed to connect to RabbitMQ server on localhost. Did you not forget to start it?
On windows start rabbitmq-server.bat to start it as console program""", e)
        self.Channel = self.Connection.channel()
        

    def BeginTransaction(self):
        self.Channel.tx_select()

    def Commit(self):
        self.Channel.tx_commit()

    def Rollback(self):
        self.Channel.tx_rollback()


    def __del__(self):
        """ Destructs connection and channel objects"""
        if (self.Channel is not None):
            self.Channel.close()
            self.Channel.close()



class LTRegisterQueue(Component):
    mqServer = RequiredFeature("MQServer", IsInstanceOf(MQServer))
    queueName = "po_box"
    exchangeName = "sorting_room"
    routingKey = "jason"
    
    persistentMessageMode = 2


    def __init__(self):
        # define properties
        self.MQServer = self.mqServer

        # we create the queues and exchanges everytime we create and instance of this class
        # this way client code does not need to worry whether exchanges have been created or not
        # this will work since the exchanges are reused, if they already exists
        self.CreateQueues()
        pass

    def InitialiseImport(self):
        """ Will initialise queue with a single message, witch will mean that a specific URL must be parsed
        and inserted as LT Geo Data. The page will contain links to deeper levels, which will be
        later inserted as other messoges"""

        # send initial message with a defined URL in GlobalSettings
        self.SendMessage(GlobalSettings.LTGeoDataParseUrl)


    def SendMessage(self, msgBody):
        msgBody = str(msgBody)
        msg = amqp.Message(msgBody)
        msg.properties["delivery_mode"] = self.persistentMessageMode
        self.mqServer.Channel.basic_publish(msg, exchange=self.exchangeName, routing_key= self.routingKey)


        

    def CreateQueues(self):
        """ Creates all neded queues and bindings needed to work with RegistruCentras.lt """
        # create a queue used for reading from http://www.registrucentras.lt/adr/p/index.php
        self.mqServer.Channel.queue_declare(queue=self.queueName, durable=True, exclusive=False, auto_delete=False)
        self.mqServer.Channel.exchange_declare(exchange = self.exchangeName, type="direct", durable=True, auto_delete=False,)

        # create binding - from po_box to sorting room
        self.mqServer.Channel.queue_bind(queue=self.queueName, exchange= self.exchangeName, routing_key= self.routingKey)

    def ConsumeMessage(self, msg):
        self.mqServer.Channel.basic_ack(msg.delivery_tag)

    def ReadMessage(self):
        msg = self.mqServer.Channel.basic_get(self.queueName)
        return msg

    def Clear(self):
        """ Clear the queue of any pending messages. This is done by reading manually all messages
        until there is none.
        """

        count = 0
        while (True):
            msg = self.ReadMessage()
            if (msg is None):
                break;
            count += 1
            self.ConsumeMessage(msg)
        print "cleared  total %s messages " % count


    def IsEmpty(self):
        """ Tells if RegisterQueue is empty.
        If queue is empty, then it means that either processing has finished, or has not started at all.
        Initiaiate processing by inserting new Root message"""
        msg = self.ReadMessage()
        empty = msg is None

        # force to resend a message, so that we don't accidentally consume it
        # requeue must be True, otherwise the same consumer will not receive it again
        self.mqServer.Channel.basic_recover(requeue = True)

        # return if queue is empty
        return empty

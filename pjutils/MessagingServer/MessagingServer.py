from pjutils.exc import ChainnedException
from _socket import socket
from amqplib import client_0_8 as amqp

class ConnectToMessageServerFailed(ChainnedException):
    pass

class MQServer:
    """ Helps establish a connection to RabbitMQ server, and initialise all default queu
    """
    def __init__(self):
        # open connection to localhost server
        self.reconnect()
        self.messages = {}

    def reconnect(self):
        self.Connection = amqp.Connection(host="localhost:5672", userid="guest", password="guest", virtual_host="/", insist=False)
        #raise ConnectToMessageServerFailed("Failed to connect to RabbitMQ server on localhost. Did you not forget to start it? On windows start rabbitmq-server.bat to start it as console program", e)
        self.Channel = self.Connection.channel()
        self.isInTransaction = False

    def readMessage(self, queueName):
        if self.messages.has_key(queueName):
            lst = self.messages[queueName]
            if len(lst) != 0:
                msg = lst[0]
                others = lst[1:]
                self.messages[queueName] = others
                return msg
        return self.Channel.basic_get(queueName)

    def isEmpty(self, queueName):
        msg = self.readMessage(queueName)
        if msg is None:
            return True
        self.messages.setdefault(queueName, [])
        self.messages[queueName].append(msg)
        return False

    def BeginTransaction(self):
        if self.isInTransaction:
            return
        self.Channel.tx_select()
        self.isInTransaction = True

    def Commit(self):
        if self.isInTransaction == False:
            return
        self.isInTransaction = False
        self.Channel.tx_commit()

    def Rollback(self):
        if self.isInTransaction == False:
            return
        self.isInTransaction = False
        self.Channel.tx_rollback()


    def __del__(self):
        """ Destructs connection and channel objects"""
        if self.Channel is not None:
            self.Channel.close()

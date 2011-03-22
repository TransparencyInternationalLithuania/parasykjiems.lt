from pjutils.exc import ChainnedException
from _socket import socket
from amqplib import client_0_8 as amqp

class ConnectToMessageServerFailed(ChainnedException):
    pass

class MQServer:
    """ Helps establish a connection to RabbitMQ server, and initialise all default queu
    """
    Connection = None
    Channel = None

    def __init__(self):
        # open connection to localhost server
        self.Connection = amqp.Connection(host="localhost:5672", userid="guest", password="guest", virtual_host="/", insist=False)
        #raise ConnectToMessageServerFailed("Failed to connect to RabbitMQ server on localhost. Did you not forget to start it? On windows start rabbitmq-server.bat to start it as console program", e)
        self.Channel = self.Connection.channel()


    def BeginTransaction(self):
        self.Channel.tx_select()

    def Commit(self):
        self.Channel.tx_commit()

    def Rollback(self):
        self.Channel.tx_rollback()


    def __del__(self):
        """ Destructs connection and channel objects"""
        if self.Channel is not None:
            self.Channel.close()

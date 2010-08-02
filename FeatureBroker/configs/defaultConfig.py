from FeatureBroker.FeatureBroker import *
from contactdb.LTRegisterCenter.mqbroker import MQServer

""" import this package to initialize FeatureBroker with default settings for ParasykJiems.lt project"""

# first param is the key ussed to identify feature, another is the object the pass as the feature
# will have to refactor this in the future
features.Provide("MQServer", MQServer) # <-- singleton lifestyle
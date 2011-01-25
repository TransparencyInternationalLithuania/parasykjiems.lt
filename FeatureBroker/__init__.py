""" As simple Dependency Injection framework for ParasykJiems.lt project.

As a consumer simply import one of the config files, such as defaultConfig to initialise FeatureBroker with components.
Then simply instantiate objects you want to have, and they will get other components injected automagically

When you want to use this DI package, call this code
from FeatureBroker import *
This will import only the required infrastructe classes (not configs). Then see demo.py how to define component usage

See demo.py to see a small example"""

from FeatureBroker import Component, RequiredFeature, IsInstanceOf
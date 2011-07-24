""" LTRegisterCenter module
Responsible for loading geographical data for Republic of Lithuania. Data is not in geographic coordinates, but
is simply a hierarchical structure. This is due to the fact no geographical data is accessible freely now.

The hierarchical data will be extracted from official Lithuanian company site: http://www.registrucentras.lt/adr/p/index.php
RabbitMQ message broker will be used to distribute the load, since import process might take a while. Also, the admin
of the registrucentras.lt might limit the number of request we can make daily/ hourly. A solution to use MQ is solely
to solve this problem. In the future it might also be used to run separate clients simulatenously.

"""
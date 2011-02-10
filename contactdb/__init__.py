""" contactdb module provides two main functions:
a. Establishes a model for storing contact data. This includes everything from member of parliaments to
constituencies, to districts. Geo data also is included here.

Geo data can be two-fold:
 1. geo data based on coordinates. this is the preferred method
 2. geo data based on hierarchical units data. Districts are composed of cities, cities from streets.
This data is not that accurate, but currently in Lithuania the only available free data


b. contactdb module at the moment is also responsible for importing Lithuanian data. This will be refactored out
to other modules in the future, when more countries join this project



Enhancments:
Some files should be renamed to reflect python style.
There are probably quite a few naming inconsistencies, camelcase vs normal case. This should be standartized
No license headers at the moment



Terminology used in this module:
District - a biggest region in a country.
City
Street



Political division in country:
Constituency - each constituency has exactly one elected member of parliament
PollingDistrict - one constituency is usually sub-divided into many smaller regions called polling districts.


Other term
MPs - members of parliament

"""
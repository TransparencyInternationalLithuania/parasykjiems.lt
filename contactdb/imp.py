#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import re
import os
from pjutils.exc import ChainnedException
from pjutils.deprecated import deprecated
from cdb_lt_mps.models import Constituency, Constituency
from cdb_lt_mps.parseConstituencies import ExpandedStreet

class ImportSourceNotExistsException(ChainnedException):
    pass

class ImportSources:
    LithuanianConstituencies = os.path.join("contactdb", "sources", "apygardos.txt")
    LithuanianMPs = os.path.join("contactdb", "sources", "parliament members.csv")
    LithuanianCivilParishMembers = os.path.join("contactdb", "sources", "LithuanianCivilParishMembers.csv")
    LithuanianMunicipalityMembers = os.path.join("contactdb", "sources", "LithuanianMunicipalityMembers.csv")
    LithuanianSeniunaitijaMembers  = os.path.join("contactdb", "sources", "LithuanianSeniunaitijaMembers.csv")
    LithuanianStreetIndex  = os.path.join("contactdb", "sources", "LithuanianStreetIndex.csv")
    LithuanianMunicipalities  = os.path.join("contactdb", "sources", "LithuanianMunicipalities.csv")

    @classmethod
    def EsnureExists(clas, importSource):
        """ Checks that a given import source exists on file system. if not, throw an exception,
         so that user would know how to donwload that source"""
        file = os.path.join(os.getcwd(), importSource)
        exists = os.path.exists(file)
        if (exists == False):
            raise ImportSourceNotExistsException("""File '%s' does not exist on your file system. Usually this means
that an appropriate google doc was not downloaded yet.  You can do that by calling manage.py downloadDocs """ % file) 

class GoogleDocsSources:
    """ collection of google docs documents for Lithuanian data"""

    # parliament members
    LithuanianMPs = "parasykjiems.lt 2"
    # Seniūnai / Foreman
    LithuanianCivilParishMembers = "parasykjiems.lt 3 seniunai"
    # Municipality mayors
    LithuanianMunicipalityMembers = "parasykjiems.lt 4 merai"
    # Seniūnaičiai
    LithuanianSeniunaitijaMembers = "parasykjiems.lt 5 seniunaiciai"

    LithuanianStreetIndex = "Lithuanian street index"
    LithuanianMunicipalities = "Contact DB LT Municipalities"
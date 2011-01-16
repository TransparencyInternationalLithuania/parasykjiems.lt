#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pjutils.exc import ChainnedException

class ImportSourceNotExistsException(ChainnedException):
    pass

class ImportSources:
    Delimiter = ","

    constituencyPath = os.path.join("contactdb", "sources", "import data")
    LithuanianConstituencies = os.path.join(constituencyPath, "apygardos.txt")

    commonPath = os.path.join("contactdb", "sources", "import data", "members")
    LithuanianMPs = os.path.join(commonPath, "parliament members.csv")
    LithuanianCivilParishMembers = os.path.join(commonPath, "LithuanianCivilParishMembers.csv")
    LithuanianMunicipalityMembers = os.path.join(commonPath, "LithuanianMunicipalityMembers.csv")
    LithuanianSeniunaitijaMembers  = os.path.join(commonPath, "LithuanianSeniunaitijaMembers.csv")
    LithuanianMunicipalities  = os.path.join(commonPath, "LithuanianMunicipalities.csv")
    LithuanianCivilParishes  = os.path.join(commonPath, "LithuanianCivilParishes.csv")

    @classmethod
    def EsnureExists(clas, importSource, downloadCommand = "downloadDocs"):
        """ Checks that a given import source exists on file system. if not, throw an exception,
         so that user would know how to donwload that source"""
        file = os.path.join(os.getcwd(), importSource)
        exists = os.path.exists(file)
        if (exists == False):
            raise ImportSourceNotExistsException("""File '%s' does not exist on your file system. Usually this means
that an appropriate google doc was not downloaded yet.  You can do that by calling manage.py %s """ % (file, downloadCommand))

class GoogleDocsSources:
    """ collection of google docs documents for Lithuanian data. The data from these sources
    are downloaded and saved on disk, for further much faster access. A relating ImportSources variable
     is used for the file name when storing on disk"""

    # parliament members
    LithuanianMPs = "parasykjiems.lt 2"
    # Seniūnai / Foreman
    LithuanianCivilParishMembers = "parasykjiems.lt 3 seniunai"
    # Municipality mayors
    LithuanianMunicipalityMembers = "parasykjiems.lt 4 merai"
    # Seniūnaičiai
    LithuanianSeniunaitijaMembers = "parasykjiems.lt 5 seniunaiciai"

    LithuanianMunicipalities = "Contact DB LT Municipalities"
    LithuanianCivilParishes = "Contact DB LT CivilParishes"
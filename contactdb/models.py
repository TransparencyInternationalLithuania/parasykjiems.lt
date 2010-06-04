from django.db import models


class ParliamentMember(models.Model):
    electoralDistrict = models.CharField(max_length = 200)
    name = models.CharField(max_length = 50)
    surname = models.CharField(max_length = 50)
    email = models.CharField(max_length = 100)

    @property
    def fullName():
        """returns Name + surname"""
        return name + surname;

    def __unicode__(self):
        return self.fullName


class County(modesl.Model):
    """ Contains counties, for example:
     County: Dan�s rinkim� apygarda Nr. 19
     Baltijos rinkim� apygarda Nr. 20
     Kauno�K�daini� rinkim� apygarda Nr. 65
     etc
     """
    name = models.CharField(max_length = 100)
    nr = models.IntegerField()

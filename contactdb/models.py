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


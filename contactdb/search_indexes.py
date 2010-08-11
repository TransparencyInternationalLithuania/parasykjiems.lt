import datetime
from haystack import indexes
from haystack import site
from parasykjiems.contactdb.models import PollingDistrictStreet, HierarchicalGeoData

class PollingDistrictStreetIndex(indexes.SearchIndex):
    street = indexes.CharField(use_template=True, document=True)
    city = indexes.CharField(model_attr='city')
    district = indexes.CharField(model_attr='district')

    def get_queryset(self):
        "Used when the entire index for model is updated."
        return PollingDistrictStreet.objects.all()

site.register(PollingDistrictStreet, PollingDistrictStreetIndex)


# -*- coding: utf-8 -*-

import haystack.indexes as indexes
from haystack import site
from unidecode import unidecode
from search.search_indexes import join_text
import models


class ThreadIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)

    def prepare_text(self, thread):
        strings = list()
        for m in thread.message_set.all():
            strings.extend([m.sender_name, m.recipient_name, m.subject, m.body_text])
        return join_text(strings)


site.register(models.Thread, ThreadIndex)

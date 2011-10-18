# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _
from models import Thread
from web.utils import summary


class ThreadsFeed(Feed):
    title = _(u"ParašykJiems threads")
    link = "/threads/"

    def items(self):
        return (Thread.objects.filter(is_public=True)
                .order_by('-created_at')[:10])

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        try:
            return summary(item.messages[0].body_text)
        except IndexError:
            return u''

    def item_pubdate(self, item):
        return item.created_at

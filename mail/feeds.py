# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _
from models import Thread


class ThreadsFeed(Feed):
    title = _(u"ParašykJiems threads")
    link = "/threads/"

    def items(self):
        return (Thread.objects.filter(is_open=True)
                .order_by('-sent_at')[:10])

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        # TODO: Improve description text.
        return u''

    def item_pubdate(self, item):
        return item.created_at

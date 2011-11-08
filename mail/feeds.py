# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from models import Thread, Message
from web.utils import summary


class ThreadsFeed(Feed):
    title = _(u"ParašykJiems threads")
    link = "/threads/"
    description_template = "feeds/thread.html"

    def items(self):
        return (Thread.objects.filter(is_public=True)
                .order_by('-created_at')[:10])

    def item_title(self, item):
        return item.subject

    def item_pubdate(self, item):
        return item.created_at


class ThreadFeed(Feed):
    def get_object(self, request, thread_slug):
        return get_object_or_404(
            Thread,
            is_public=True,
            slug=thread_slug)

    def title(self, obj):
        return u'ParašykJiems – {}'.format(obj.subject)

    def items(self, obj):
        return Message.objects.filter(thread=obj).order_by('-date')

    def item_title(self, item):
        return item.subject

    def item_pubdate(self, item):
        return item.date

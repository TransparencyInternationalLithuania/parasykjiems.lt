# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from search.models import Institution
from models import Thread, Message


class ThreadsFeed(Feed):
    description_template = "feeds/thread.html"

    def get_object(self, request, institution_slug=None):
        if institution_slug:
            return get_object_or_404(Institution, slug=institution_slug)
        else:
            return None

    def title(self, obj):
        if obj:
            return obj.name + u' – ' + _(u"ParašykJiems threads")
        else:
            return _(u"ParašykJiems threads")

    def link(self, obj):
        if obj:
            return "/threads/" + obj.slug + "/"
        else:
            return "/threads/"

    def items(self, obj):
        if obj:
            return obj.recent_threads(count=10)
        else:
            return (Thread.objects.filter(is_public=True)
                    .order_by('-created_at')[:10])

    def item_title(self, item):
        return item.subject

    def item_pubdate(self, item):
        return item.created_at


class ThreadFeed(Feed):
    description_template = "feeds/message.html"

    def get_object(self, request, slug):
        return get_object_or_404(
            Thread,
            is_public=True,
            slug=slug)

    def title(self, obj):
        return u'ParašykJiems – {}'.format(obj.subject)

    def items(self, obj):
        return Message.objects.filter(
            thread=obj,
            is_error=False,
            sent=True).order_by('-date')

    def link(self, obj):
        return obj.get_absolute_url()

    def item_title(self, item):
        return item.subject

    def item_pubdate(self, item):
        return item.date

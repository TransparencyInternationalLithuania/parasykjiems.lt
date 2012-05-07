# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from search.models import Institution
from models import Thread, Message


class ThreadsFeed(Feed):
    description_template = "feeds/thread.html"

    def get_object(self, request):
        if 'q' in request.GET:
            q = request.GET['q'].strip()
            if q == '':
                return None
            else:
                return q
        else:
            return None

    def title(self, q):
        if q:
            return q + u' – ' + _(u"ParašykJiems threads")
        else:
            return _(u"ParašykJiems threads")

    def link(self, q):
        if q:
            return "/threads/?q=" + q.replace(' ', '+')
        else:
            return "/threads/"

    def items(self, q):
        threads = Thread.objects.filter(is_public=True).order_by('-created_at')
        if q:
            threads = threads.filter(Thread.make_filter_query(q))
        return threads[:20]

    def item_title(self, thread):
        return thread.subject

    def item_author_name(self, thread):
        return thread.sender_name

    def item_pubdate(self, thread):
        return thread.created_at


class ThreadFeed(Feed):
    description_template = "feeds/message.html"

    def get_object(self, request, slug):
        return get_object_or_404(
            Thread,
            is_public=True,
            slug=slug)

    def title(self, thread):
        return u'{} – ParašykJiems'.format(thread.subject)

    def items(self, thread):
        return thread.messages.order_by('-date')

    def link(self, thread):
        return thread.get_absolute_url()

    def item_title(self, message):
        return message.subject

    def item_author_name(self, message):
        return message.sender_name

    def item_pubdate(self, message):
        return message.date

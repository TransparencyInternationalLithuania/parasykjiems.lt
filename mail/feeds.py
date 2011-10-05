# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _
from models import Enquiry


class ThreadsFeed(Feed):
    title = _(u"ParašykJiems threads")
    link = "/threads/"

    def items(self):
        return (Enquiry.objects
                .filter(is_open=True, is_sent=True, parent=None)
                .order_by('-sent_at')[:10])

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return _("Sent from {} to {}").format(
            item.sender_name,
            item.recipient_name)

    def item_pubdate(self, item):
        return item.sent_at

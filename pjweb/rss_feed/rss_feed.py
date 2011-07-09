from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from pjweb.models import Email
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site

class PublicMailsFeed(Feed):
    title = "Public mails to your representatives"
    link = Site.objects.get_current().domain
    description = "See all public mails sent to representatives on %s" % Site.objects.get_current().domain

    def item_link(self, item):
        return '/public/%s/' % item.id

    def items(self):
        # deliver only latest 30
        # only public
        return Email.objects.filter(public=True).filter(msg_state__exact='Confirmed').order_by('-mail_date')[:30]

    def item_title(self, item):
        return '%s -> %s' % (item.sender_name, item.recipient_name)

    def item_description(self, item):
        return "%s \n\n %s" % (item.subject, item.message)

"""class SingleMailFeed(Feed):
    description_template = 'feeds/single_mail.html'

    def get_object(self, request, mail_id):
        return get_object_or_404(Email, id=mail_id)

    def title(self, obj):
        return "News for mail %s" % obj.subject

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "Response from %s to %s" % (obj.recipient_name, obj.sender_name)

    def items(self, obj):
        return Email.objects.filter(id=obj.id).order_by('-mail_date')"""
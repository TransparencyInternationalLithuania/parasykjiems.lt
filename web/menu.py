"""Defines the menu and a context processor that puts the menu into a
template's context.
"""

from django.utils.translation import ugettext as _


class MenuItem:
    def __init__(self, name, href):
        self.name = name
        self.href = href


def create_menu(location):
    return (
        MenuItem(_('Representative search'), '/'),
        MenuItem(_('Public letters'), '/letters'),
        MenuItem(_('About project'), '/about'),
    )


def context_processor(request):
    return {'MENU': create_menu(request.path)}

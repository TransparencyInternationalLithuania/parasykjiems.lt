from django import template
from search import utils


register = template.Library()


@register.filter
def shorten_institution(name):
    """This filter tries to shorten an institution's name. It removes
    the municipality portion from elderates.
    """
    return utils.split_institution_name(name)[0]

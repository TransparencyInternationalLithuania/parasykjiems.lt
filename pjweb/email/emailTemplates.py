from django.utils.translation import get_language
from django.template import loader

def renderEmailTemplate(templateName, templateParams, lang = None):
    # get language from current user setting
    if lang is None:
        lang = get_language()
        if len(lang) > 2:
            lang = lang[0:2]
    templateName = u"pjweb/emails/%s/%s" % (lang, templateName)
    message = loader.render_to_string(templateName, templateParams)
    return message
  
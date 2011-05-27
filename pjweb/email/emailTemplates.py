from django.utils.translation import get_language
from django.template import loader

def renderEmailTemplate(templateName, templateParams):
    lang = get_language()
    templateName = u"pjweb/emails/%s/%s" % (lang, templateName)
    message = loader.render_to_string(templateName, templateParams)
    return message
  
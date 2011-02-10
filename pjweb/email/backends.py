from pjutils.exc import ChainnedException

_ = lambda s: s


class MailDoesNotExistInDBException(ChainnedException):
    pass

class MailHashIsNotCorrect(ChainnedException):
    pass

class CanNotExtractEmailIdAndHash(ChainnedException):
    pass

class EmailInfoInToField(object):

    # this prefix will be attached to every email sent to representatives
    # Final reply_to field will be calculated more or less like this:
    # reply_to = '%s%s_%s@%s' % (DefaultMailPrefix, mail.id, mail.response_hash, GlobalSettings.MAIL_SERVER)
    DefaultMailPrefix = "reply"
    Email_public_host = ""
    DefaultSubjectPrefix = _(u'You got a letter from %(sender_name)s')

    def getReplyTo(self, mail = None):
        # determine reply address
        reply_to = '%s%s_%s@%s' % (self.DefaultMailPrefix, mail.id, mail.response_hash, self.Email_public_host)
        return reply_to

    def getSubject(self, mail):
        subject = self.DefaultSubjectPrefix % {'sender_name' : mail.sender_name}
        return subject

    def getEmailId(self, header_to = None, header_from=None, header_subject=None, header_received=None):
        """ Gets an email id in the database from existing email.
        This backend searches for email id in the database, and checks if hash values match"""
        # import Email not at the module level, but in class level
        # since otherwise we get circular error with settings.py file
        from pjweb.models import Email


        # if to: field does not contain our defined mail prefix
        # delete the email, and continue processing other mails
        if self.DefaultMailPrefix not in header_to:
            raise CanNotExtractEmailIdAndHash(message="header_to '%s' does not contain default prefix '%s'" % (header_to, self.DefaultMailPrefix))

        receiver = header_to.split('_')
        msg_id = receiver[0].replace(self.DefaultMailPrefix,'')
        msg_hash = int(receiver[1])

        mail = None
        try:
            mail = Email.objects.get(id=msg_id)
        except Email.DoesNotExist as e:
            raise MailDoesNotExistInDBException(message="We do not have email in database with id '%s'" % msg_id, inner=e)

        # print mail.response_hash, mail_info['msg_hash']
        if mail.response_hash != msg_hash:
            params = (msg_id, mail.response_hash, msg_hash)
            raise MailHashIsNotCorrect(message="Hash for mail '%s' was not correct. It should be '%s', but was '%s'" % params)
        return mail.id




class EmailInfoInSubject(object):
    DefaultReplyTo = ""
    DefaultSubjectPrefix = _(u'You got a letter from %(sender_name)s')
    DefaultMailPrefix = "reply"

    def getSubject(self, mail):
        subject = self.DefaultSubjectPrefix % {"sender_name": mail.sender_name}
        reply_to = '%s%s_%s' % (self.DefaultMailPrefix, mail.id, mail.response_hash)
        subject = "%s---%s" % (subject, reply_to)
        return subject

    def getReplyTo(self, mail = None):
        return self.DefaultReplyTo

    def getEmailId(self, header_to = None, header_from=None, header_subject=None, header_received=None):
        """ Gets an email id in the database from existing email.
        This backend searches for email id in the database, and checks if hash values match"""

        # import Email not at the module level, but in class level
        # since otherwise we get circular error with settings.py file
        from pjweb.models import Email
        

        # if to: field does not contain our defined mail prefix
        # delete the email, and continue processing other mails
        if self.DefaultMailPrefix not in header_subject:
            raise CanNotExtractEmailIdAndHash(message="header_==subjectto '%s' does not contain default prefix '%s'" % (header_to, self.DefaultMailPrefix))

        receiver = header_subject.split('---')[1]
        receiver = receiver.split('_')
        msg_id = receiver[0].replace(self.DefaultMailPrefix,'')
        msg_hash = int(receiver[1])

        mail = None
        try:
            mail = Email.objects.get(id=msg_id)
        except Email.DoesNotExist as e:
            raise MailDoesNotExistInDBException(message="We do not have email in database with id '%s'" % msg_id, inner=e)

        # print mail.response_hash, mail_info['msg_hash']
        if mail.response_hash != msg_hash:
            params = (msg_id, mail.response_hash, msg_hash)
            raise MailHashIsNotCorrect(message="Hash for mail '%s' was not correct. It should be '%s', but was '%s'" % params)
        return mail.id

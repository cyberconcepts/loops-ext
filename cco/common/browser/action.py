# cco.common.browser.action

""" Common action classes.
"""

import urllib

from zope.cachedescriptors.property import Lazy

from loops.browser.action import TargetAction


class MailToAction(TargetAction):

    receiver = None
    receivers = None
    targetWindow = 'blank'
    bodyAttribute = 'description'
    subjectAttribute = 'title'

    @Lazy
    def url(self):
        mailto = 'mailto:'
        target = self.target
        prefix = False
        if self.receiver:
            receiver = getattr(target, self.receiver)
            if receiver.email:
                mailto += receiver.email
                prefix = True
        if self.receivers:
            for receiver in getattr(target, self.receivers):
                if receiver.email:
                    if prefix:
                        mailto += ', '
                    mailto += receiver.email
                    prefix = True
        subject = getattr(target, self.subjectAttribute, '')
        if not subject:
            subject = target.title or ''
        mailto += '?subject=' + self.escape(subject)
        body = getattr(target, self.bodyAttribute, '')
        if not body:
            body = ''
        mailto += '&body=' + self.escape(body)
        return mailto

    def escape(self, s):
        def enc(c):
            try:
                return c.encode('utf-8')
            except UnicodeEncodeError:
                return '.'
        s = s[:1000]
        return urllib.parse.quote(''.join(enc(c) for c in s))

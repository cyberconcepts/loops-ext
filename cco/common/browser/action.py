#  coding=utf-8
#
#  Copyright (c) 2018 Helmut Merz helmutm@cy55.de
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Common action classes.
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
        return urllib.quote(''.join(enc(c) for c in s))

# cyberapps.commerce.util

""" Utility functions.
"""

from email.mime.text import MIMEText
from zope import component
from zope.i18nmessageid import MessageFactory
from zope.sendmail.interfaces import IMailDelivery


_ = MessageFactory('cyberapps.commerce')


def sendEMail(subject, message, sender, recipients):
    if isinstance(message, unicode):
        message = message.encode('UTF-8')
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    mailhost = component.getUtility(IMailDelivery, 'Mail')
    mailhost.send(sender, recipients, msg.as_string())

# cco.member.browser

""" Login, logout, unauthorized stuff.
"""

try:
    import python_jwt as jwt
    import jwcrypto.jws as jws
except ImportError:
    pass
from datetime import timedelta
from email.mime.text import MIMEText
import logging
from zope.authentication.interfaces import IAuthentication
from zope.authentication.interfaces import ILogout, IUnauthenticatedPrincipal
from zope.browserpage import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy
from zope import component
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from zope.publisher.interfaces.http import IHTTPRequest
from zope.security.interfaces import Unauthorized as DefaultUnauth
from zope.sendmail.interfaces import IMailDelivery

from cco.member.auth import getCredentials, getPrincipalFromCredentials,\
    getPrincipalForUsername, JWT_SECRET
from cco.member.interfaces import IPasswordChange, IPasswordReset
from cco.member.pwpolicy import checkPassword
from cybertools.composer.schema.browser.common import schema_macros
from cybertools.composer.schema.browser.form import Form
from cybertools.composer.schema.schema import FormState, FormError
from loops.browser.concept import ConceptView
from loops.browser.node import NodeView, getViewConfiguration
from loops.common import adapted
from loops.organize.interfaces import IMemberRegistrationManager
from loops.organize.party import getPersonForUser
from loops.organize.util import getPrincipalForUserId, getPrincipalFolder

try:
    import config
except ImportError:
    config = None

log = logging.getLogger('cco.member.browser')

_ = MessageFactory('cco.member')

template = ViewPageTemplateFile('auth.pt')


def validateToken(token, secret=None):
    if not secret:
        secret = JWT_SECRET
        try:
            header, claims = jwt.verify_jwt(token, secret, ['PS256'])
        except (jwt._JWTError, jws.InvalidJWSSignature,
                jws.InvalidJWSObject, ValueError):
            return False
        return True


class LoginConcept(ConceptView):

    @Lazy
    def macro(self):
        return template.macros['login_form']


class LoginForm(NodeView):

    @Lazy
    def macro(self):
        return template.macros['login_form']

    @Lazy
    def item(self):
        return self

    @Lazy
    def isVisible(self):
        return self.isAnonymous

    def update(self, topLevel=True):
        if 'SUBMIT' in self.request.form and not self.isAnonymous:
            self.request.response.redirect(self.topMenu.url)
            return False
        return True


class TanForm(LoginForm):

    @Lazy
    def macro(self):
        return template.macros['tan_form']

    @Lazy
    def credentials(self):
        return getCredentials(self.request)

    def sendTanEmail(self):
        if self.credentials is None:
            log.warn('credentials missing')
            return None
        person = None
        cred = self.credentials
        principal = getPrincipalFromCredentials(
                            self.context, self.request, cred)
        if principal is not None:
            person = adapted(getPersonForUser(
                            self.context, self.request, principal))
        if person is None:     # invalid credentials
            log.warn('invalid credentials: %s, %s' % (cred.login, cred.tan))
            # TODO: display message
            return None
        tan = self.credentials.tan
        recipient = getattr(person, 'tan_email', None) or person.email
        recipients = [recipient]
        lang = self.languageInfo.language
        subject = translate(_(u'tan_mail_subject'), target_language=lang)
        message = translate(_(u'tan_mail_text_$tan', mapping=dict(tan=tan)),
                            target_language=lang)
        senderInfo = self.globalOptions('email.sender')
        sender = senderInfo and senderInfo[0] or 'info@loops.cy55.de'
        #sender = sender.encode('UTF-8')
        msg = MIMEText(message, 'plain', 'UTF-8')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        mailhost = component.getUtility(IMailDelivery, 'Mail')
        mailhost.send(sender, recipients, msg.as_string())
        return recipient


@implementer(ILogout)
class Logout(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        nextUrl = self.request.get('nextURL') or self.request.URL[-1]
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = component.getUtility(IAuthentication)
            ILogout(auth).logout(self.request)
        return self.request.response.redirect(nextUrl)


class LogoutView(NodeView):

    @Lazy
    def body(self):
        nextUrl = self.topMenu.url
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = component.getUtility(IAuthentication)
            ILogout(auth).logout(self.request)
        return self.request.response.redirect(nextUrl)


class Unauthorized(ConceptView):

    isTopLevel = True

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        response = self.request.response
        response.setStatus(403)
        # make sure that squid does not keep the response in the cache
        response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
        response.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate')
        response.setHeader('Pragma', 'no-cache')
        if self.nodeView is None:
            v = DefaultUnauth(self.context, self.request)
            return v()
        url = self.nodeView.topMenu.url
        if self.isAnonymous:
            response.redirect(url)
        else:
            response.redirect(url + '/unauthorized')


class PasswordChange(NodeView, Form):

    interface = IPasswordChange
    message = _(u'message_password_changed')

    formErrors = dict(
        confirm_nomatch=FormError(_(u'error_password_confirm_nomatch')),
        wrong_oldpw=FormError(_(u'error_password_wrong_oldpw')),
        invalid_pw=FormError(_(u'error_password_invalid_pw')),
    )

    label = label_submit = _(u'label_change_password')

    @Lazy
    def macro(self):
        return schema_macros.macros['form']

    @Lazy
    def item(self):
        return self

    @Lazy
    def data(self):
        return dict(oldPassword=u'', password=u'', passwordConfirm=u'')

    def update(self):
        form = self.request.form
        if not form.get('action'):
            return True
        formState = self.formState = self.validate(form)
        if formState.severity > 0:
            return True
        pw = form.get('password')
        if not checkPassword(pw):
            fi = formState.fieldInstances['password']
            fi.setError('invalid_pw', self.formErrors)
            formState.severity = max(formState.severity, fi.severity)
            return True
        pwConfirm = form.get('passwordConfirm')
        if pw != pwConfirm:
            fi = formState.fieldInstances['password']
            fi.setError('confirm_nomatch', self.formErrors)
            formState.severity = max(formState.severity, fi.severity)
            return True
        oldPw = form.get('oldPassword')
        regMan = IMemberRegistrationManager(self.loopsRoot)
        principal = self.request.principal
        result = regMan.changePassword(principal, oldPw, pw)
        if not result:
            fi = formState.fieldInstances['oldPassword']
            fi.setError('wrong_oldpw', self.formErrors)
            formState.severity = max(formState.severity, fi.severity)
            return True
        url = '%s?error_message=%s' % (self.url, self.message)
        self.request.response.redirect(url)
        return False

    def validate(self, data):
        formState = FormState()
        for f in self.schema.fields:
            fi = f.getFieldInstance()
            value = data.get(f.name)
            fi.validate(value, data)
            formState.fieldInstances.append(fi)
            formState.severity = max(formState.severity, fi.severity)
        return formState


class PasswordReset(PasswordChange):

    interface = IPasswordReset
    message = _(u'message_password_reset_successfully')
    reset_mail_message = _(u'message_password_reset_mail')

    formErrors = dict(
        invalid_pw=FormError(_(u'error_password_invalid_pw')),
        invalid_token=FormError(_(u'error_reset_token_invalid')),
        invalid_username=FormError(_(u'error_username_invalid')),
    )

    label = label_submit = _(u'label_reset_password')
    password_reset_period = 15
    ignoreRedirect = False

    @Lazy
    def macro(self):
        return template.macros['reset_form']

    @Lazy
    def item(self):
        return self

    @Lazy
    def data(self):
        return dict(password=u'')

    @Lazy
    def token(self):
        return self.request.form.get('token')

    @Lazy
    def fields(self):
        result = super(PasswordReset, self).fields
        if self.token and validateToken(self.token):
            result = [r for r in result if r.name == 'password']
        else:
            result = [r for r in result if r.name == 'username']
        return result

    def getSubject(self, lang=None, domain=None):
        if not lang:
            lang = self.languageInfo.language
        if not domain:
            try:
                domain = config.baseDomain
            except:
                domain = self.request.getHeader('HTTP_HOST')
        result = translate(_(u'pw_reset_mail_subject_$domain',
                             mapping=dict(domain=domain)),
                           target_language=lang)
        return result

    def getMessage(self, token, lang=None):
        if not lang:
            lang = self.languageInfo.language
        reset_url = '%s?token=%s' % (self.request.getURL(), token)
        message = translate(_(u'pw_reset_mail_text_$link',
                              mapping=dict(link=reset_url)),
                            target_language=lang)
        return message

    def sendPasswordResetMail(self, sender, recipients=[], subject='',
                              message=''):
        msg = MIMEText(message, 'html', 'UTF-8')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        mailhost = component.getUtility(IMailDelivery, 'Mail')
        mailhost.send(sender, recipients, msg.as_string())

    def validateToken(self, token, secret=None):
        return validateToken(token, secret)

    def update(self):
        form = self.request.form
        if not form.get('action'):
            return True
        principal = self.request.principal
        if principal and principal.id != 'zope.anybody':
            return True
        formState = self.formState = self.validate(form)
        if formState.severity > 0:
            return True
        token = form.get('token')
        secret = JWT_SECRET
        if token:
            if not validateToken(token):
                fi = formState.fieldInstances['password']
                fi.setError('invalid_token', self.formErrors)
                formState.severity = max(formState.severity, fi.severity)
                return True
            header, claims = jwt.verify_jwt(token, secret, ['PS256'])
            username = claims.get('username')
            principal = getPrincipalForUsername(username, self.context,
                                                self.request)
            if not principal:
                fi = formState.fieldInstances['password']
                fi.setError('invalid_username', self.formErrors)
                formState.severity = max(formState.severity, fi.severity)
                return True
            pw = form.get('password')
            if not checkPassword(pw):
                fi = formState.fieldInstances['password']
                fi.setError('invalid_pw', self.formErrors)
                formState.severity = max(formState.severity, fi.severity)
                return True
            principal.setPassword(pw)
        else:
            username = form.get('username')
            principal = getPrincipalForUsername(username, self.context,
                                                self.request)
            person = getPersonForUser(self.context, self.request, principal)
            if not person:
                fi = formState.fieldInstances['username']
                fi.setError('invalid_username', self.formErrors)
                formState.severity = max(formState.severity, fi.severity)
                return True
            person = adapted(person)
            payload = dict(username=username)
            token = jwt.generate_jwt(payload, secret, 'PS256',
                                     timedelta(minutes=getattr(
                                         self, 'password_reset_period', 15)))
            addr = self.getMailAddress(person)
            if addr:
                recipients = [addr]
            else:
                fi = formState.fieldInstances['username']
                fi.setError('invalid_username', self.formErrors)
                formState.severity = max(formState.severity, fi.severity)
                return True
            lang = self.languageInfo.language
            try:
                domain = config.baseDomain
            except:
                domain = self.request.getHeader('HTTP_HOST')
            senderInfo = self.globalOptions('email.sender')
            sender = senderInfo and senderInfo[0] or 'info@loops.cy55.de'
            #sender = sender.encode('UTF-8')
            self.sendPasswordResetMail(sender, recipients, self.getSubject(),
                                       self.getMessage(token))
            url = '%s?error_message=%s' % (self.url, self.reset_mail_message)
            if not self.ignoreRedirect:
                self.request.response.redirect(url)
            return False

        url = '%s?error_message=%s' % (self.url, self.message)
        self.request.response.redirect(url)
        return False

    def getMailAddress(self, person):
        return person.email

    def validate(self, data):
        formState = FormState()
        for f in self.schema.fields:
            fi = f.getFieldInstance()
            value = data.get(f.name)
            fi.validate(value, data)
            formState.fieldInstances.append(fi)
            formState.severity = max(formState.severity, fi.severity)
        return formState

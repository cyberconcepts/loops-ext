# cco.common.util

""" Utility functions.
"""

import xlrd
import math
import mmap
from datetime import timedelta, datetime
from logging import getLogger
from lxml import etree
from urllib.parse import urlencode
from urllib.request import urlopen

from zope import component
from zope.i18nmessageid import MessageFactory
from zope.i18n.locales import locales

from loops.concept import Concept
from loops.organize.personal.notification import Notifications
from loops.setup import addAndConfigureObject

try:
    from lovely.memcached.interfaces import IMemcachedClient
except ImportError:
    IMemcachedClient = None

try:
    from config import GOOGLE_MAPS_API_KEY
except:
    GOOGLE_MAPS_API_KEY = ''

_ = MessageFactory('cco.common')
logger = getLogger('create object')


def getOrCreateObject(self, identifier, typeName=None, **kw):
        if typeName is None:
            typeName = self.typeName
        if identifier is None:
            logger.warn('*** getOrCreateObject: no identifer: %s' %
                        self.__class__)
        name = self.makeName(identifier, typeName=typeName)
        manager = self.getOrCreateConceptManager(typeName=typeName)
        return addAndConfigureObject(manager, Concept, name,
                                     conceptType=self.concepts[typeName], **kw)


def parseNumber(num, type='decimal', lang='de', pattern=None):
    if isinstance(num, float):
        return num
    if num:
        num = str(num)
    loc = locales.getLocale(lang)
    fmt = loc.numbers.getFormatter(type)
    return fmt.parse(num, pattern=pattern)


def floatEq(f1, f2, maxdiff=0.01):
    return abs(float(f1) - float(f2)) <= maxdiff


def escapeString(s):
    s = s.replace('"', '&quot;').replace("'", "\\'")
    s = s.replace('\n', ' ').replace('\r', ' ')
    return s


def getLastDayOfMonth(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1,
                        day=1) - timedelta(days=1)


def renderTextAsGroups(text, groupNumberCount=4):
    if text:
        textList = list(text)
        hits = 0
        for idx, letter in enumerate(textList):
            numb = idx + 1
            if not numb % groupNumberCount:
                textList.insert(numb + hits, ' ')
                hits += 1
        return u''.join(textList)
    return text


def XLSDictReader(f, sheet_index=0):
    book = xlrd.open_workbook(
        file_contents=mmap.mmap(f.fileno(),
                                0,
                                access=mmap.ACCESS_READ))
    sheet = book.sheet_by_index(sheet_index)
    headers = dict(
        (i, sheet.cell_value(0, i)) for i in range(sheet.ncols))
    return (
        dict(
            (headers[j], sheet.cell_value(i, j)) for j in headers)
        for i in range(1, sheet.nrows))


def XLSListReader(f, sheet_index=0,
                  ignore_sheets=[]):
    book = xlrd.open_workbook(
        file_contents=mmap.mmap(f.fileno(), 0,
                                access=mmap.ACCESS_READ))
    # sheet = book.sheet_by_index(sheet_index)
    values = []
    for sheet in book.sheets():
        if sheet.name in ignore_sheets:
            continue
        for row in range(sheet.nrows):
            col_value = []
            for col in range(sheet.ncols):
                value = (sheet.cell(row, col).value)
                #value = unicode(value)  # str(int(value))
                col_value.append(value)
            values.append(col_value)
    return values


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


sepaCharacters = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                  'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                  'y', 'z',
                  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                  'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                  'Y', 'Z',
                  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                  '/', '?', ':', '(', ')', '.', ',', '\'', '+', '-', ' ')


def replaceNoneSepaCharacters(string, length=None):
    if not isinstance(string, str):
        return string
    result = u''
    for s in string:
        if s in sepaCharacters:
            result += s
    if length:
        result = result and result[:length] or u''
    return result


def getDistance(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi / 180.0
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians
    theta1 = long1 * degrees_to_radians
    theta2 = long2 * degrees_to_radians
    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    arc = math.acos(cos)
    return arc * 6373.0


def getCoordinates(queryString):
    baseUrl = u'https://maps.googleapis.com/maps/api/geocode/xml?'
    key = GOOGLE_MAPS_API_KEY
    params = urlencode(dict(address=queryString.encode('utf-8'),
                            key=key))
    url = baseUrl + params
    try:
        response = urlopen(url)
    except:
        return []
    root = etree.fromstring(response.read())
    if root.find('status').text != 'OK':
        return []
    resultTypes = root.findall('.//result/type')
    elemTexts = [elem.text for elem in resultTypes]
    # if 'political' not in elemTexts and 'postal_code' not in elemTexts:
    #    return []
    lat = root.find('.//geometry/location/lat').text
    lng = root.find('.//geometry/location/lng').text
    result = [float(lat), float(lng)]
    if 'political' in elemTexts:
        southWestLat = root.find('.//southwest/lat').text
        southWestLng = root.find('.//southwest/lng').text
        northEastLat = root.find('.//northeast/lat').text
        northEastLng = root.find('.//northeast/lng').text
        diameter = getDistance(float(southWestLat),
                               float(southWestLng),
                               float(northEastLat),
                               float(northEastLng))
        result.append(diameter)
    return result


def createNotification(senderPerson, receiverPerson, targetObject, text):
    notif = Notifications(receiverPerson)
    notif.add(targetObject, senderPerson, text)

def cache(getIdentifier, lifetime=3600):
    def _cache(fct):
        def __cache(*args, **kw):
            id = getIdentifier(*args, **kw)
            client = component.getUtility(IMemcachedClient)
            client.trackKeys = True
            value = client.query(id)
            if value is None:
                value = fct(*args, **kw)
                client.set(value, id, lifetime=lifetime)
            return value
        return __cache
    return _cache

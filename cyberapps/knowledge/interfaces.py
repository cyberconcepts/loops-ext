#
#  Copyright (c) 2015 Helmut Merz helmutm@cy55.de
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
Interfaces for knowledge and skills management specials.
"""

from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Attribute
from zope import schema

from cybertools.composer.schema.grid.interfaces import KeyTable
from loops.interfaces import ILoopsAdapter
from loops.knowledge.survey.interfaces import IQuestionnaire
from loops.table import IDataTable
from loops.util import _

_ = MessageFactory('cyberapps.knowledge')


class IJobPosition(ILoopsAdapter):

    pass


class IJPDescription(ILoopsAdapter):

    header = Attribute('Header data.')
    administrativeData = Attribute('Administrative job data.')
    workDescription = Attribute('Work description.')


class IIPSkillsRequired(ILoopsAdapter):

    requirements = Attribute('Required interpersonal skills.')


class IQualificationsRequired(ILoopsAdapter):

    requirements = Attribute('Required qualifications.')


class IQualification(IDataTable):

    data = KeyTable(title=_(u'Qualification Schema'),
        description=_(u'Data fields for specifying the qualification.'),
        required=False)

    certVocabulary = schema.List(title=_(u'Certification Vocabulary'),
        description=_(u'List of proposed certificates.'),
        required=False)


class IQualificationsRecorded(ILoopsAdapter):

    data = Attribute('Qualifications recorded for person.')


class ISkillsRecorded(ILoopsAdapter):

    data = Attribute('Skills recorded for person.')



class IIPSkillsQuestionnaire(IQuestionnaire):
    """ Allow specialized questionnaire implementation that limits
        question groups according to competences required for person.
    """

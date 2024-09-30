# cco.webapi.node

""" API node implementations.
"""

from zope.interface import implementer

from cco.webapi.interfaces import IApiNode, IApiNodeContained
from loops.view import Node


@implementer(IApiNode, IApiNodeContained)
class ApiNode(Node):

    pass

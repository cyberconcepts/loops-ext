# cco.common.migration

""" Base Class for imports.
"""

from datetime import datetime, time
from logging import getLogger
import os
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import desc
import transaction
from zope.cachedescriptors.property import Lazy
from zope.dublincore.interfaces import IZopeDublinCore
from zope.event import notify
from zope.lifecycleevent import ObjectRemovedEvent
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName

from cybertools.tracking.btree import TrackingStorage

from loops.common import adapted, baseObject, normalizeName
from loops.concept import Concept, ConceptManager
from loops.expert.query import getObjects, Identifier
from loops.predicate import adaptedRelation
from loops.setup import addAndConfigureObject, addObject
from loops import util

try:
    from config import dbengine, dbuser, dbpassword, dbhost, dbport, dbname
    kwargs = dict(encoding='utf-8')
    if 'oracle' in dbengine:
        kwargs['coerce_to_unicode'] = True
# cybertools.pyscript.script

""" Simple implementation of Python scripts.
"""

import os, re
#import compiler.pycodegen
from io import StringIO
from persistent import Persistent
#import RestrictedPython.RCompile
#from RestrictedPython.SelectCompiler import ast
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.interface import implementer
from zope.proxy import removeAllProxies
#from zope.security.untrustedpython.builtins import SafeBuiltins
#from zope.security.untrustedpython.rcompile import RestrictionMutator as BaseRM
from zope.traversing.api import getParent, getPath

from cybertools.pyscript.interfaces import IPythonScript, IScriptContainer

HAS_R = use_R = bool(os.environ.get('USE_RLIBRARY', True))

if use_R:
    try:
        #from cybertools.pyscript.rstat import r, rpy
        import rpy
        from rpy import r
        HAS_R = True
    except ImportError:
        HAS_R = False


unrestricted_objects = ('rpy', 'r', 'as_py', 'rstat')


def compile(text, filename, mode):
    if not isinstance(text, str):
        raise TypeError("Compiled source must be string")
    gen = RExpression(text, str(filename), mode)
    gen.compile()
    return gen.getCode()


#class RExpression(RestrictedPython.RCompile.RestrictedCompileMode):
class RExpression(object):

    #CodeGeneratorClass = compiler.pycodegen.ExpressionCodeGenerator

    def __init__(self, source, filename, mode="eval"):
        self.mode = mode
        RestrictedPython.RCompile.RestrictedCompileMode.__init__(
            self, source, filename)
        self.rm = RestrictionMutator()


#class RestrictionMutator(BaseRM):
class RestrictionMutator(object):

    unrestricted_objects = unrestricted_objects

    def visitGetattr(self, node, walker):
        _getattr_name = ast.Name("getattr")
        node = walker.defaultVisitNode(node)
        if node.expr.name in self.unrestricted_objects:
            return node     # no protection
        return ast.CallFunc(_getattr_name,
                            [node.expr, ast.Const(node.attrname)])


@implementer(IPythonScript)
class PythonScript(Contained, Persistent):
    """Persistent Python Page - Content Type
    """

    _v_compiled = None

    title = u''
    parameters = u''
    source = u''
    contentType=u'text/plain'

    def __init__(self, title=u'', parameters=u'', source=u'',
                 contentType=u'text/plain'):
        """Initialize the object."""
        super(PythonScript, self).__init__()
        self.title = title
        self.source = source
        self.contentType = contentType
        self.parameters = parameters or u''

    def __filename(self):
        if self.__parent__ is None:
            filename = 'N/A'
        else:
            filename = getPath(self)
        return filename

    def setSource(self, source):
        """Set the source of the page and compile it.

        This method can raise a syntax error, if the source is not valid.
        """
        self.__source = source
        self.__prepared_source = self.prepareSource(source)
        # Compile objects cannot be pickled
        self._v_compiled = Function(self.__prepared_source,  self.parameters,
                                    self.__filename())

    _tripleQuotedString = re.compile(
        r"^([ \t]*)[uU]?([rR]?)(('''|\"\"\")(.*)\4)", re.MULTILINE | re.DOTALL)

    def prepareSource(self, source):
        """Prepare source."""
        # compile() don't accept '\r' altogether
        source = source.replace("\r\n", "\n")
        source = source.replace("\r", "\n")
        if isinstance(source, unicode):
            # Use special conversion function to work around
            # compiler-module failure to handle unicode in literals
            try:
                source = source.encode('ascii')
            except UnicodeEncodeError:
                return self._tripleQuotedString.sub(_print_usrc, source)
        return self._tripleQuotedString.sub(r"\1print \2\3", source)


    def getSource(self):
        """Get the original source code."""
        return self.__source

    source = property(getSource, setSource)

    def __call__(self, request, *args, **kw):
        output = StringIO()
        if self._v_compiled is None:
            self._v_compiled = Function(self.__prepared_source, self.parameters,
                                        self.__filename(),)
        parent = getParent(self)
        kw['request'] = request
        kw['script'] = self
        kw['untrusted_output'] = kw['printed'] = output
        kw['context'] = parent
        kw['script_result'] = None
        if IScriptContainer.providedBy(parent):
            parent.updateGlobals(kw)
        self._v_compiled(args, kw)
        result = kw['script_result']
        if result == output:
            result = result.getvalue().decode('unicode-escape')
        return result


class Function(object):
    """A compiled function.
    """

    parameters = []

    def __init__(self, source, parameters='', filename='<string>'):
        lines = []
        if parameters:
            self.parameters = [str(p).strip() for p in parameters.split(',')]
        #print('*** Function.parameters:', repr(self.parameters))
        lines.insert(0, 'def dummy(): \n    pass')
        for line in source.splitlines():
            lines.append('    ' + line)
        lines.append('script_result = dummy()')
        source = '\n'.join(lines)
        #print('*** source:', source)
        self.code = compile(source, filename, 'exec')

    def __call__(self, args, globals):
        globals['__builtins__'] = SafeBuiltins
        for idx, p in enumerate(self.parameters):
            # TODO: handle parameters with default values like ``attr=abc``
            globals[p] = args[idx]
        exec(self.code, globals, None)


def _print_usrc(match):
    string = match.group(3)
    raw = match.group(2)
    if raw:
        #return match.group(1)+'print '+`string`
        return match.group(1) + 'print(' + eval('string') + ')'
    return match.group(1) + 'print(' + match.group(3).encode('unicode-escape') + ')'


@implementer(IScriptContainer)
class ScriptContainer(BTreeContainer):

    unrestricted_objects = ('rstat',)  # not used (yet)

    def getItems(self):
        return self.values()

    def updateGlobals(self, globs):
        if HAS_R:
            from cybertools.pyscript import rstat
            context = globs['context']
            request = globs['request']
            globs['rstat'] = rstat.RStat(context, request)
            globs['r'] = r
            globs['rpy'] = rpy

    engine = create_engine('%s://%s:%s@%s:%s/%s' % (dbengine, dbuser, dbpassword,
                                                    dbhost, dbport,
                                                    dbname), **kwargs)
except:
    dbengine = dbuser = dbpassword = dbhost = dbport = dbname = ''


# necessary for proper encoding with Oracle
os.environ['NLS_LANG'] = 'German_Germany.UTF8'

meta = MetaData()

try:
    import config
except:
    config = None

useSchema = getattr(config, 'db_use_schema', False)
logger = getLogger('migration')


class ImportBase(object):

    logger = logger
    dataTableName = ''

    @Lazy
    def loopsRoot(self):
        return self.context.getLoopsRoot()

    @Lazy
    def concepts(self):
        return self.loopsRoot.getConceptManager()

    def getDataTable(self, dataTableName=None):
        if not dataTableName:
            dataTableName = self.dataTableName
        return adapted(self.concepts[dataTableName])

    @Lazy
    def dataTable(self):
        return self.getDataTable()

    @Lazy
    def typePredicate(self):
        return self.concepts.getTypePredicate()

    @Lazy
    def hasTypePredicate(self):
        return self.concepts['hasType']


    def getOrCreateConceptManager(self, typeName=None):
        if typeName is None:
            mName = self.type.conceptManager
        else:
            mName = adapted(self.concepts[typeName]).conceptManager
        if not mName:
            mName = 'concepts'
        manager = self.loopsRoot.get(mName)
        if not manager:
            manager = addObject(self.loopsRoot, ConceptManager, mName)
        return manager

    def getOrCreateRecordManager(self, name, trackFactory):
        records = self.loopsRoot['records']
        manager = records.get(name)
        if manager is None:
            manager = records[name] = TrackingStorage(
                trackFactory=trackFactory)
        return manager

    def getObject(self, identifier, typeName=None):
        if typeName is None:
            typeName = self.typeName
        name = self.makeName(identifier, typeName=typeName)
        manager = self.getOrCreateConceptManager(typeName=typeName)
        return manager.get(name)

    def deleteObject(self, identifier, typeName=None, obj=None):
        if typeName is None:
            typeName = self.typeName
        if obj is None:
            obj = self.getObject(identifier, typeName=typeName)
        if obj:
            manager = self.getOrCreateConceptManager(typeName=typeName)
            logger.warn('*** deleteObject: %s' % getName(obj))
            notify(ObjectRemovedEvent(obj))
            del manager[getName(obj)]

    def getOrCreateObject(self, identifier, typeName=None, **kw):
        if typeName is None:
            typeName = self.typeName
        name = self.makeName(identifier, typeName=typeName)
        manager = self.getOrCreateConceptManager(typeName=typeName)
        return addAndConfigureObject(manager, Concept, name,
                                     conceptType=self.concepts[typeName], **kw)

    def getObjectForTitle(self, title, typeName=None):
        if not typeName:
            typeName = self.typeName
        typeConcept = self.loopsRoot['concepts'][typeName]
        for c in typeConcept.getChildren([self.hasTypePredicate]):
            if c.title and c.title.lower() == title.lower():
                return c

    @Lazy
    def type(self):
        return adapted(self.concepts[self.typeName])

    def makeName(self, identifier, typeName=''):
        if not typeName:
            prefix = self.type.namePrefix
        else:
            prefix = adapted(self.concepts[typeName]).namePrefix
        if isinstance(identifier, str):
            identifier = identifier.lower()
        return prefix + str(identifier)

    def getPersonForUserShortId(self, identifier, typeName):
        if identifier:
            identifier = normalizeName(identifier.lower())
            for p in getObjects(Identifier(identifier).apply(),
                                self.loopsRoot):
                return p
        return None

    def setRelation(self, obj, related, predicate, role):
        obj = baseObject(obj)
        relations = obj.getChildRelations([predicate], child=related)
        for relation in relations:
            if not adaptedRelation(relation).role:
                adaptedRelation(relation).role = role
            if adaptedRelation(relation).role == role:
                return
        relation = obj.createChildRelation(related, predicate=predicate)
        adaptedRelation(relation).role = role

    def setMetaData(self, obj, creation, modified, author):
        if obj:
            dc = IZopeDublinCore(obj, None)
            t = time(0, 0)
            if creation:
                dc.created = datetime.combine(creation, t)
            if modified:
                dc.modified = datetime.combine(modified, t)
            if author:
                dc.creators = ['steg.' + author.lower()]


class ImportRelationalTable(ImportBase):

    tableName = ''
    columnPrefix = ''
    recordManager = ''
    schema = None
    logInfo = ''
    keyColumns = ()
    engine = engine

    @property
    def sortColumns(self):
        return [self.columnPrefix + 'id']

    def getIdentifier(self, data):
        return '-'.join([normalizeName(str(self.getRawValue(data, colName)).lower())
                         for colName in self.keyColumns])

    def getRawValue(self, data, colName):
        colName = self.columnPrefix + colName
        for key in data.iterkeys():
            if key.lower() == colName.lower():
                return data[key]

    def getTable(self, tableName=None, engine=None):
        if engine is None:
            engine = self.engine
        if tableName is None:
            tableName = self.tableName
        for t in meta.sorted_tables:
            if t.name.lower() == tableName.lower():
                return t
        return Table(tableName, meta, schema=self.schema,
                     autoload=True, autoload_with=engine)

    def getColumn(self, table, colName):
        colName = self.columnPrefix + colName
        for col in table.columns:
            if col.name.lower() == colName.lower():
                return col

    def __init__(self, context, request):
        self.context = removeSecurityProxy(context)
        request.form['organize.suppress_tracking'] = True
        util.saveRequest(request)
        self.request = request
        self.table = self.getTable()

    def __call__(self, start=0, stop=0, engine=None):
        if engine is None:
            engine = self.engine
        form = self.request.form
        offset = int(start or form.get('start') or 0)
        limit = int(stop or form.get('stop') or 0)
        changedSince = form.get('changedSince')
        createdSince = form.get('createdSince')
        conn = engine.connect()
        s = select([self.table])
        if changedSince:
            changedSince = datetime.strptime(changedSince, '%Y-%m-%d')
            moddatColumn = self.getColumn(self.table, 'moddat')
            s = s.where(moddatColumn >= changedSince)
        if createdSince:
            createdSince = datetime.strptime(createdSince, '%Y-%m-%d')
            anldatColumn = self.getColumn(self.table, 'anldat')
            s = s.where(anldatColumn >= createdSince)
        if offset:
            s = s.offset(offset)
        if limit:
            s = s.limit(limit)
        if self.sortColumns:
            sortCols = []
            for cn in self.sortColumns:
                if cn.endswith('.desc'):
                    sortCols.append(desc(self.table.c.get(cn[:-5])))
                else:
                    sortCols.append(self.table.c.get(cn))
                s = s.order_by(*sortCols)
        result = conn.execute(s)
        count = offset
        for row in result:
            self.update(row)
            count += 1
            if count % 10 == 0:
                info = self.logInfo and ('/%s' % self.logInfo) or ''
                logger.info('Importing: %s%s: %i' % (self.tableName,
                                                     info, count))
            if count % 50 == 0:
                transaction.commit()
        transaction.commit()
        result.close()
        logger.info('********** Imported: %s: %i' % (self.tableName, count))
        return str(count)

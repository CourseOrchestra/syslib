# coding: utf-8
import security
from ru.curs.celesta import Celesta
from ru.curs.celesta.score import Score
from ru.curs.celesta import ConnectionPool
from ru.curs.celesta import CallContext
from ru.curs.celesta import SessionContext
# from common import navigator, sysfunctions
# from common.xmlutils import XMLJSONConverter
#
# #try:
# #    from java.lang import String111
# #except:
# #    from java.lang import Integer as III
#
#
# import sys, os
# import common
# #from security.grid import permissions
#
a = Celesta.getInstance()
conn = ConnectionPool.get()
sesContext = SessionContext('admin', 'testsession')
context = CallContext(conn, sesContext)
# #print context.getCelesta()
# from security.xform import permissions
import org.activiti.engine.ProcessEngineConfiguration as ProcessEngineConfiguration
import org.apache.log4j.PropertyConfigurator as PropertyConfigurator
import org.activiti.image.ProcessDiagramGenerator as ProcessDiagramGenerator
import org.activiti.bpmn.BPMNLayout as BPMNLayout
import org.activiti.bpmn.BpmnAutoLayout as BpmnAutoLayout
import org.activiti.bpmn.converter.BpmnXMLConverter as BpmnXMLConverter
import org.junit.Assert.assertEquals as assertEquals
import org.junit.Assert.assertNotNull as assertNotNull
import org.junit.Assert.assertNull as assertNull
import java.io.FileOutputStream as FileOutputStream
import java.io.File as File
import jarray
import java.util.Calendar as Calendar
import javax.xml.stream.XMLInputFactory as XMLInputFactory
from java.io import InputStreamReader, FileInputStream
import java.io.ByteArrayInputStream as ByteArrayInputStream
import java.nio.file.Files as Files
import java.nio.file.Paths as Paths
# from workflow.grid.processVersionsGrid import gridDataAndMeta
# from workflow.webtext.processesImage import webtextData
import base64
import array
try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory
from common._common_orm import numbersSeriesCursor, linesOfNumbersSeriesCursor
from workflow import processUtils
import os
from workflow.webtext import tasksImage, processesImage
# import processtest

from workflow.datapanel.processes import manageProcesses


a = [(1, 1), (1, 0)]
if (1, 1) in a:
    print a
else:
    print 'no'

session = """{"sessioncontext":{"sid":"67D5D000-7477-430C-A6B1-B28AE10F0E75","userdata":"default","phone":"","username":"bobkova","fullusername":"bobkova","email":"","login":"bobkova","sessionid":"603769A65A9FD1B4953585026E066919","related":{"gridContext":{"currentColumnId":"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0437\u0430\u0434\u0430\u0447\u0438","gridFilterInfo":"","pageInfo":{"@size":"20","@number":"1","#text":""},"liveInfo":{"@totalCount":"0","@pageNumber":"1","@offset":"0","@limit":"50","#text":""},"partialUpdate":"false","currentDatapanelWidth":"1646","@id":"tasksGrid","currentDatapanelHeight":"933","currentRecordId":"10072","#text":""},"#text":""},"ip":"0:0:0:0:0:0:0:1","#text":""},"#text":""}"""

def proc2(context):
    print tasksImage.webtextData(context, session=session)

def proc1(context):
    # log4jConfPath = "log4j.properties"
    # PropertyConfigurator.configure(log4jConfPath)

    processEngine = EngineFactory.getActivitiProcessEngine()
    # здесь коннект идёт уже к MS SQL (описано в activiti.cfg.xml)
#    try:
#
#    except:
#        conf = ProcessEngineConfiguration.createStandaloneProcessEngineConfiguration()
#        conf.setDatabaseType("postgres")
#        conf.setJdbcUrl("jdbc:postgresql://localhost:5432/activiti")
#        conf.setJdbcDriver("org.postgresql.Driver")
#        conf.setJdbcUsername("postgres")
#        conf.setJdbcPassword("F708420Dx")
#
#        processEngine = conf.buildProcessEngine()
    # processUtils.getProcessDefinition('simplebookorder', None)

    runtimeService = processEngine.getRuntimeService()
    activ = processUtils.ActivitiObject()
    repositoryService = processEngine.getRepositoryService()

    processDefinition = repositoryService.createProcessDefinitionQuery() \
                                                         .processDefinitionKey("bookorder").latestVersion() \
                                                         .singleResult()

#     diagramResourceName = processDefinition.getDiagramResourceName()
#     imageStream = repositoryService.getResourceAsStream(processDefinition.getDeploymentId(), diagramResourceName)

    stringout = u''
    byteArray = [-1, -1, -1]
#     while True:
#         byteArray[0] = imageStream.read()
#         byteArray[1] = imageStream.read()
#         byteArray[2] = imageStream.read()
#         if byteArray[0] == -1:
#             break
#         elif byteArray[1] == -1:
#             stringout += base64.b64encode(array.array('B', byteArray[0:1]).tostring())
#             break
#         elif byteArray[2] == -1:
#             stringout += base64.b64encode(array.array('B', byteArray[0:2]).tostring())
#             break
#         else:
#             stringout += base64.b64encode(array.array('B', byteArray).tostring())
    print stringout
#    while True:
#        try:
#            c = imageStream.read()
#            fout.write(c);
#            if c == -1:
#                break
#        except:
#            print 1
#            break
#    imageStream.close()
#    fout.close()


    # разворачиваем процесс из потока
#     repositoryService.createProcessDefinitionQuery().latestVersion().list()[0]
    a = FileInputStream(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fp.bpmn"))
    repositoryService.createDeployment().addInputStream("fp.bpmn", a).deploy()

    # стартуем инстанс по айдишнику
#     processInstance = runtimeService.startProcessInstanceByKey("bookorder")
    # print "id " + processInstance.getId() + " " + processInstance.getProcessDefinitionId()




proc2(context)
#    from dirusing._dirusing_orm import filtersConditionsCursor
#    filtersConditions = filtersConditionsCursor(context)
#    filtersConditions.id = 1
#    filtersConditions.prefix = None
#
#    if not filtersConditions.tryInsert():
#        filtersConditions.update()

# ConnectionPool.putBack(conn)



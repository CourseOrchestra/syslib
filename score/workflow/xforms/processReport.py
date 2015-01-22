# coding: utf-8
'''
Created on 04.08.2014

@author: m.prudyvus
'''

import simplejson as json

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.jython import JythonDownloadResult
except:
    pass

try:
    from ru.curs.celesta.showcase.utils import XMLJSONConverter
except:
    pass

from ru.curs.flute.xml2spreadsheet import XML2Spreadsheet
import os
from java.io import File, FileInputStream, FileOutputStream, ByteArrayInputStream
from java.lang import String
from java.nio.charset import StandardCharsets
from workflow.processUtils import ActivitiObject
from java.text import SimpleDateFormat
import datetime

from bup._bup_orm import clListFacultyCursor

def cardData(context, main, add, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":""}
                  }
    xformssettings = {"properties":{"event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":[{"@id": "processesGrid",
                                                                                "add_context": ''}]
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def createOrderReport(context, main=None, add=None, filterinfo=None, session=None, elementId=None, data=None):
    listFaculty = clListFacultyCursor(context)
    activiti = ActivitiObject()
    orderDict = {"root":
                 {"context":
                     {"@header": u"Статистика прохождения документов по приказам",
                      "@date": SimpleDateFormat("dd.MM.yyyy").format(datetime.datetime.now()),
                      "faculties":
                         {"faculty": []}}}}

    listFaculty.orderBy("FacultyName")
    for listFaculty in listFaculty.iterate():
        agreementNumberA = 0.0
        agreementTimeA = 0.0
        refinementNumberA = 0.0
        refinementTimeA = 0.0
        agreementNumberR = 0.0
        agreementTimeR = 0.0
        refinementNumberR = 0.0
        refinementTimeR = 0.0
        orders = activiti.historyService.createHistoricProcessInstanceQuery()\
                    .processDefinitionKey('documentApprovingProcess')\
                    .variableValueEquals('facultyId', unicode(listFaculty.FacultyID))

        if len(orders.list()) == 0:
            continue

        onAgreement = activiti.runtimeService.createProcessInstanceQuery().active()\
                        .processDefinitionKey('documentApprovingProcess')\
                        .variableValueEquals('processStatus', 'onAgreement')\
                        .variableValueEquals('facultyId', unicode(listFaculty.FacultyID))

        #     detailquery имеет только инстанс, он не знает про свой ключ
        allAgreementTime = 0.0
        for processInstance in orders.list():
            onAgreementHistory = activiti.historyService.createHistoricDetailQuery()\
                                .processInstanceId(processInstance.processInstanceId).variableUpdates()\
                                .orderByTime().asc()
            agreementNumberA = 0.0
            agreementTimeA = 0.0
            refinementNumberA = 0.0
            refinementTimeA = 0.0
    #         теперь смотрим для каждого инстанса, когда было согласовано, когда отклонено..
            for detail in onAgreementHistory.list():
                if detail.name == 'processStatus':
                    if detail.value == 'onAgreement':
                        agreementNumberA += 1
                        agreementTimeA += detail.time.getTime()
                    if detail.value == 'refinement':
                        refinementNumberA += 1
                        refinementTimeA += detail.time.getTime()
            if agreementNumberA != refinementNumberA:
                if processInstance.getEndTime() is None:
                    agreementTimeA -= detail.time.getTime()
                    agreementNumberA -= 1
                else:
                    refinementTimeA += processInstance.getEndTime().getTime()
                    refinementNumberA += 1
            allAgreementTime += refinementTimeA - agreementTimeA
        allAgreementTime = allAgreementTime / (1000 * 60 * 60 * 24)

        refinement = activiti.runtimeService.createProcessInstanceQuery().active()\
                        .processDefinitionKey('documentApprovingProcess')\
                        .variableValueEquals('processStatus', 'refinement')\
                        .variableValueEquals('facultyId', unicode(listFaculty.FacultyID))

        allRefinementTime = 0.0
        for processInstance in orders.list():
            onAgreementHistory = activiti.historyService.createHistoricDetailQuery()\
                                .processInstanceId(processInstance.processInstanceId).variableUpdates()\
                                .orderByTime().asc()
            agreementNumberR = 0.0
            agreementTimeR = 0.0
            refinementNumberR = 0.0
            refinementTimeR = 0.0
    #         теперь смотрим для каждого инстанса, когда было согласовано, когда отклонено..
            for detail in onAgreementHistory.list():
                if detail.name == 'processStatus':
                    if detail.value == 'onAgreement' and refinementNumberR > 0:
                        agreementNumberR += 1
                        agreementTimeR += detail.time.getTime()
                    if detail.value == 'refinement':
                        refinementNumberR += 1
                        refinementTimeR += detail.time.getTime()
            if agreementNumberR != refinementNumberR:
                refinementTimeR -= detail.time.getTime()
                refinementNumberR -= 1
            allRefinementTime += (agreementTimeR - refinementTimeR)
        allRefinementTime = allRefinementTime / (1000 * 60 * 60 * 24)

        finished = activiti.historyService.createHistoricProcessInstanceQuery()\
                    .processDefinitionKey('documentApprovingProcess').finished()\
                    .variableValueEquals('facultyId', unicode(listFaculty.FacultyID))

        finishedTime = 0.0
        for process in finished.list():
            finishedTime += (process.getEndTime().getTime() - process.getStartTime().getTime()) / (1000 * 60 * 60 * 24)

        facultyDict = {}
        facultyDict["@name"] = listFaculty.FacultyName
        facultyDict["@orderNumber"] = len(orders.list())
        facultyDict["@apprNumber"] = len(onAgreement.list())
        facultyDict["@apprAvgTime"] = round(allAgreementTime / (agreementNumberA + refinementNumberA), 1) \
                                                            if (agreementNumberA + refinementNumberA) != 0 else 0
        facultyDict["@reworkNumber"] = len(refinement.list())
        facultyDict["@reworkAvgTime"] = round(allRefinementTime / (agreementNumberR + refinementNumberR), 1) \
                                                            if (agreementNumberR + refinementNumberR) != 0 else 0
        facultyDict["@submitNumber"] = len(finished.list())
        facultyDict["@submitAvgTime"] = round(finishedTime / len(finished.list()), 1) if len(finished.list()) != 0 else 0
        orderDict["root"]["context"]["faculties"]["faculty"].append(facultyDict)

    data = String(XMLJSONConverter.jsonToXml(json.dumps(orderDict)))
    stream = ByteArrayInputStream(data.getBytes(StandardCharsets.UTF_8))

    filePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources')
    template = File(os.path.join(filePath, 'order.xls'))
    descriptor = File(os.path.join(filePath, 'order-Descriptor.xml'))
    result = FileOutputStream(os.path.join(filePath, 'report.xls'))

    try:
        XML2Spreadsheet.process(stream, descriptor, template, False, result)
    finally:
        result.close()
    report = File(os.path.join(filePath, 'report.xls'))
    return JythonDownloadResult(FileInputStream(report), 'report.xls')

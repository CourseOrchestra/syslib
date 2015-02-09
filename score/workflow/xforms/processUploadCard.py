# coding: utf-8
'''
Created on 02.10.2014

@author: A.Vasilyev.
'''


import simplejson as json

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO

try:
    from ru.curs.showcase.core.selector import ResultSelectorData
    from ru.beta2.extra.gwt.ui.selector.api import DataRecord
except:
    from ru.curs.celesta.showcase import ResultSelectorData, DataRecord
    
try:
    from ru.curs.showcase.activiti import  EngineFactory
except:
    from workflow import testConfig as EngineFactory
# 
# from workflow import testConfig as EngineFactory
    
from java.io import InputStream, FileInputStream
from jarray import zeros

#from common.xmlutils import XMLJSONConverter
from ru.curs.celesta.showcase.utils import XMLJSONConverter

def cardData(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":'',
                            "files":{}
                            }
                  }
    xformssettings = {"properties":{
                                    "event":[{"@name": "single_click",
                                              "@linkId": "1",
                                              "action":{"main_context": "current",
                                                        "datapanel":{"@type": "current",
                                                                     "@tab": "current",
                                                                     "element":{"@id": "processesGrid",
                                                                                "add_context": 'current'}
                                                                     }
                                                        }
                                              }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)
                 
def processUpload(context,main,add,filterinfo,session,elementId,xformsdata,filename,file):
    #raise Exception(main,add,filterinfo,session,elementId,xformsdata,filename,file)
    #fio = FileInputStream("C:/jprojects/celesta/manage/general/score/workflow/uploadFile1.xml")
    '''
    out = FileOutputStream('C:/jprojects/celesta/manage/general/score/workflow/files/uploadFile.xml')
    buf = zeros(1024, 'b')  # equal to new byte[1024] in Java
    while True:
        length = file.read(buf)
        if length > 0:
            out.write(buf, 0, length)
        else:
            break
    out.close()
    '''
#     f = open("C:/jprojects/celesta/manage/general/score/workflow/files/uploadTest.txt","w")
#     while True:
#         byte = file.read()
#         if byte != -1:
#             f.write(str(byte)+"\n")
#         else:
#             break
#     f.close()
     
    processEngine = EngineFactory.getActivitiProcessEngine()
    repositoryService = processEngine.getRepositoryService()
#     #a = InputStream(file)
    repositoryService.createDeployment().addInputStream(filename, file).deploy()



def cardSave(context, main, add, filterinfo, session, elementId, data):
    #здесь необходимо описать сохранение
    '''
    print 'Save xform data from Celesta Python procedure.'
    print 'User %s' % context.userId
    print 'main "%s".' % main
    print 'add "%s".' % add
    print 'filterinfo "%s".' % filterinfo
    print 'session "%s".' % session
    print 'elementId "%s".' % elementId
    print 'data "%s".' % data
    '''
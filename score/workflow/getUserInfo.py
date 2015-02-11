# coding: utf-8

'''
Created on 28.01.2015

@author: tr0glo)|(I╠╣ 
'''

from processUtils import parse_json

from common.sysfunctions import tableCursorImport

class userNameClass():
    def __init__(self,context,content):
        content = content["userInfo"]["getUserName"]
        if content['grain'] != 'celesta':
            self.users = tableCursorImport(content['grain'],content['table'])(context)
        else:
            syscur = __import__('ru.curs.celesta.syscursors',globals(),locals(),"%sCursor"%(content["table"]),-1)
            self.users = getattr(syscur,"%sCursor"%(content["table"]))(context)
        self.idField = content["idField"]
        self.nameField = content["nameField"]
    
    def getUserName(self,userId):
        self.users.setRange(self.idField, userId)
        if self.users.tryFirst():
            return getattr(self.users, self.nameField)
        else:
            return u'Пользователь не найден'
        
class userGroupsClass():
    def __init__(self,context,content):
        content = content["userInfo"]["getUserGroups"]
        if content['grain'] != 'celesta':
            self.groups = tableCursorImport(content['grain'],content['table'])(context)
        else:
            syscur = __import__('ru.curs.celesta.syscursors',globals(),locals(),"%sCursor"%(content["table"]),-1)
            self.groups = getattr(syscur,"%sCursor"%(content["table"]))(context)
        self.idField = content["idField"]
        self.nameField = content["nameField"]
    
    def getUserGroups(self,userId):
        u'''функция, которая возвращает список групп, в которые входит пользователь'''
        groupsList = []
        self.groups.setRange(self.idField, userId)

        if self.groups.tryFirst():
            while True:
                groupsList.append(getattr(self.groups, self.nameField))
                if not self.groups.next():
                    break   
        return groupsList
        
class groupUsersClass():
    def __init__(self,context,content):
        content = content["userInfo"]["getGroupUsers"]
        if content['grain'] != 'celesta':
            self.groups = tableCursorImport(content['grain'],content['table'])(context)
        else:
            syscur = __import__('ru.curs.celesta.syscursors',globals(),locals(),"%sCursor"%(content["table"]),-1)
            self.groups = getattr(syscur,"%sCursor"%(content["table"]))(context)
        self.idField = content["idField"]
        self.nameField = content["nameField"]
    
    def getGroupUsers(self,groupId):
        u'''функция, которая возвращает список пользователей,которые входят в группу'''
        userList = []
        self.groups.setRange(self.idField, groupId)

        if self.groups.tryFirst():
            while True:
                userList.append(getattr(self.groups, self.nameField))
                if not self.groups.next():
                    break   
        return userList        
        
#coding : utf-8

from common.hierarchy import generateSortValue

def matchingCircuitPreInsert(rec):
    rec.sort = generateSortValue(unicode(rec.number))

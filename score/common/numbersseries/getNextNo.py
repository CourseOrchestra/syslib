# coding=UTF-8

from datetime import datetime
from common._common_orm import linesOfNumbersSeriesCursor
from ru.curs.celesta import CelestaException


def getNextNoOfSeries(context, seriesId, linesOfNumbersSeries=None, updateNum=True):
    if linesOfNumbersSeries is None:
        linesOfNumbersSeries = linesOfNumbersSeriesCursor(context)
    linesOfNumbersSeries.setRange('seriesId', seriesId)
    linesOfNumbersSeries.setRange('isOpened', True)

    if linesOfNumbersSeries.count() > 1:
        raise Exception("There is more than one opened line")

    linesOfNumbersSeries.setRange('startingDate',
                                  datetime.strptime('1900-01-01', '%Y-%m-%d'),
                                  datetime.today())
    if linesOfNumbersSeries.tryFindSet():
        seriesObject = GettingNextNumberOfSeries(linesOfNumbersSeries.lastUsedNumber,
                                                 linesOfNumbersSeries.startingNumber,
                                                 linesOfNumbersSeries.endingNumber,
                                                 linesOfNumbersSeries.incrimentByNumber,
                                                 linesOfNumbersSeries.isFixedLength)
        nextNum = seriesObject.getNextNum()
        linesOfNumbersSeries.lastUsedNumber = int(nextNum)
        linesOfNumbersSeries.lastUsedDate = datetime.today()
        if updateNum:
            linesOfNumbersSeries.update()
        return '%s%s%s' % (linesOfNumbersSeries.prefix, nextNum, linesOfNumbersSeries.postfix)
    else:
        CelestaException("There are no available numbers in the current series!")


class GettingNextNumberOfSeries():
    def __init__(self, lastUsed, startNum=0, endNum=0, incr=1, isFixedLength=True):
        self.startNum = startNum
        self.endNum = endNum
        self.lastUsed = lastUsed
        self.isFixedLength = isFixedLength
        self.incr = incr if incr >= 1 else 1

        if int(self.startNum) > int(self.endNum):
            raise Exception('Min value more then max value')

    def getNextNum(self):
        """Finding next num"""
        if not self.lastUsed:
            return unicode(self.startNum)
        elif self.lastUsed < self.endNum:
            nextNum = unicode(self.lastUsed + self.incr)
            if int(nextNum) > self.endNum:
                raise Exception('Next number value more than max value')
            if self.isFixedLength:
                nextNum = '0' * (len(unicode(self.endNum)) - len(nextNum)) + nextNum
                """If nextNum == '2' but it should be like '0002' """

        else:
            raise CelestaException('Last used value more than max value')

        return nextNum

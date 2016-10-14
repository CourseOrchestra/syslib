#   coding=utf-8

from common.grainssettings import SettingsManager

import xml.etree.ElementTree
import StringIO
import re
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email.header import Header


def test(context):
    class DummyFlute:

        def __init__(self):
            self.params = """<letter>
    <header>
        <template>template3.txt</template><!-- Имя шаблона -->
        <to>iponomarev@mail.ru</to> <!-- Далеее идёт любая комбинация тэгов to и cc, в которых перечислены получатели -->
        <cc>informer@rambler.ru</cc>
    </header>
    <body>
        <field name="id">1123</field> <!-- id сообщения -->
        <field name="uid">1123</field> <!-- сквозной номер сообщения -->
        <field name="datecreated">2012-01-01</field><!-- Дата создания (в любом формате, на самом деле, меня интересует лишь текст) -->
        <repeat id="attachments"> <!-- В данном примере повторяющийся блок состоит всего из одного-единственного поля, поэтому код кажется избыточным.
        однако, в каждом тэге repeat может быть определено сколько угодно полей, а также - потенциально - другие тэги repeat...-->
            <field name="attachment">foo.doc</field>
        </repeat>
        <repeat id="attachments">
            <field name="attachment">bar.doc</field>
        </repeat>
        <field name="url">http://www.yandex.ru</field>
    </body>
</letter>
"""
    dummyFlute = DummyFlute()
    sendmail(context, dummyFlute)
    print 'test run!'


def sendmail(context, flute):
    settingsObject = SettingsManager(context)

    templatespath = settingsObject.getGrainSettings('mailsender/templatespath', 'common')[0]
    mailfrom = settingsObject.getGrainSettings('mailsender/mailfrom', 'common')[0]
    smtphost = settingsObject.getGrainSettings('mailsender/smtphost', 'common')[0]
    port = settingsObject.getGrainSettings('mailsender/port', 'common')[0]
    login = settingsObject.getGrainSettings('mailsender/login', 'common')[0]
    is_auth = settingsObject.getGrainSettings('mailsender/isauth', 'common')[0]
    password = settingsObject.getGrainSettings('mailsender/password', 'common')[0]

    # 1. Parse XML and make from it a convenient data sctructure
    xmlcontext = xml.etree.ElementTree.iterparse(StringIO.StringIO(flute.params.encode('utf-16')), ['start', 'end'])

    to = []
    cc = []
    bcc = []

    data = {}
    curdata = data

    for evttype, e in xmlcontext:
        tagname = e.tag
        if evttype == 'start':
            if tagname == 'repeat':
                curdata = {}
        elif evttype == 'end':
            if tagname == "template":
                template = templatespath + e.text
            elif tagname == "to":
                to.append(e.text)
            elif tagname == "cc":
                cc.append(e.text)
            elif tagname == "bcc":
                bcc.append(e.text)
            elif tagname == "from":
                mailfrom = "\"%s\" <%s>" % (Header(e.text, 'utf-8'), mailfrom)
            elif tagname == "field":
                curdata[e.attrib['name']] = '' if e.text is None else e.text.encode('utf-8')
            elif tagname == "repeat":
                repeatid = e.attrib['id']
                if not (repeatid in data.keys()):
                    data[repeatid] = []
                data[repeatid].append(curdata)
                curdata = data

    # 2. Now we are parsing template and preparing a message subject and body
    class Parser(object):
        BODY = 1
        REPEATBLOCK = 2
        REPEMPTYBLOCK = 3
        IFDEFBLOCK = 4
        ELSEBLOCK = 5

        def __init__(self):
            self.subject = ''
            self.body = ''
            self.__reset()
            self.PARSEMAP = {Parser.BODY: lambda line: self.__parsebody(line),
                             Parser.REPEATBLOCK: lambda line: self.__parserepeat(line),
                             Parser.REPEMPTYBLOCK: lambda line: self.__parseempty(line),
                             Parser.IFDEFBLOCK: lambda line: self.__parseifdef(line),
                             Parser.ELSEBLOCK: lambda line: self.__parseelse(line)}

        def parseline(self, line):
            # Every remark is skipped
            m = re.search("^REM:", line)
            if m is not None:
                return
            self.PARSEMAP[self.state](line)

        def __reset(self):
            self.curdata = data
            self.state = Parser.BODY
            self.ifblock = []
            self.elseblock = []
            self.ifValue = False

        def __finalizeRepeat(self):
            if len(self.curdata) > 0:
                for c in self.curdata:
                    for l in self.ifblock:
                        self.body += (l % c)
            else:
                for l in self.elseblock:
                    self.body += (l % data)
            self.__reset()

        def __finalizeIf(self):
            block = self.ifblock if self.ifValue else self.elseblock
            for l in block:
                self.body += (l % self.curdata)
            self.__reset()

        def __parsebody(self, line):
            m = re.search("^SUBJECT: *(.*)", line)
            if m is not None:
                self.subject = m.group(1) % data
                return
            m = re.search("^REPEAT\(([^)]+)\):", line)
            if m is not None:
                if m.group(1) in data.keys():
                    self.curdata = data[m.group(1)]
                else:
                    self.curdata = []
                self.state = Parser.REPEATBLOCK
                return
            m = re.search("^IFDEF\(([^)]+)\):", line)
            if m is not None:
                self.ifValue = m.group(1) in data.keys()
                self.state = Parser.IFDEFBLOCK
                return

            self.body += (line % self.curdata)

        def __parserepeat(self, line):
            m = re.search("^END:", line)
            if m is not None:
                self.__finalizeRepeat()
                return
            m = re.search("^EMPTY:", line)
            if m is not None:
                self.state = Parser.REPEMPTYBLOCK
                return

            self.ifblock.append(line)

        def __parseempty(self, line):
            m = re.search("^END:", line)
            if m is not None:
                self.__finalizeRepeat()
                return
            self.elseblock.append(line)

        def __parseifdef(self, line):
            m = re.search("^ELSE:", line)
            if m is not None:
                self.state = Parser.ELSEBLOCK
                return
            m = re.search("^END:", line)
            if m is not None:
                self.__finalizeIf()
                return
            self.ifblock.append(line)

        def __parseelse(self, line):
            m = re.search("^END:", line)
            if m is not None:
                self.__finalizeIf()
                return
            self.elseblock.append(line)

    template = open(template, 'r')
    parser = Parser()

    try:
        for line in template.readlines():
            parser.parseline(line)
    finally:
        template.close()

    # 3. All done, sending message
    msg = MIMEMultipart()
    msg["To"] = ",".join(to)
    msg["CC"] = ",".join(cc)
    msg["From"] = mailfrom
    msg["Subject"] = Header(parser.subject, 'utf-8')
    msg['Date'] = formatdate(localtime=True)

    # attach a message
    part1 = MIMEText(parser.body, 'plain', 'utf-8')
    msg.attach(part1)
    port = int(port) if port != '' else 25
    server = smtplib.SMTP(smtphost, port)
    server.set_debuglevel(1)  # connection log
    if is_auth == "True":
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(login, password)

    try:
        server.sendmail(mailfrom, to + cc + bcc, msg.as_string())
    finally:
        server.close()

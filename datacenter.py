# -*- coding: cp936 -*-
import MySQLdb
from mysqldb import ImgMysql
from orcdb import Orc
from inicof import DataCenterIni
##from disk import DiskState
import logging
import logging.handlers
import time,datetime,os
import re

platecolor = {'����':1,'����':2,'����':3,'����':4,'����':5,'����':6}
#direction = {'0':'����','1':'����','2':'�ɶ�����','3':'��������','4':'��������','5':'�ɱ�����'}

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def version():
    return 'SX-datacenter V0.1.1'

def initLogging(logFilename):
    """Init for logging"""
    path = os.path.split(logFilename)
    if os.path.isdir(path[0]):
        pass
    else:
        os.makedirs(path[0])
    logging.basicConfig(
                    level    = logging.DEBUG,
                    format   = '%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s',
                    datefmt  = '%Y-%m-%d %H:%M:%S',
                    filename = logFilename,
                    filemode = 'a');
    
class DataCenter:
    def __init__(self,trigger):
        #print 'Welcome to %s'%version()
        self.trigger = trigger
        self.style_red = 'size=4 face=arial color=red'
        self.style_blue = 'size=4 face=arial color=blue'
        self.style_green = 'size=4 face=arial color=green'
        initLogging(r'log\datacenter.log')
        dataCenterIni = DataCenterIni()
        mysqlset = dataCenterIni.getMysqlConf()
        self.imgMysql = ImgMysql(mysqlset['host'],mysqlset['user'],mysqlset['passwd'])
        orcset = dataCenterIni.getOrcConf()
        self.orc = Orc(orcset['host'],orcset['user'],orcset['passwd'],orcset['sid'])
        self.direction = {'0':u'����','1':u'����','2':u'�ɶ�����','3':u'��������','4':u'��������','5':u'�ɱ�����'}
        self.wlcp = {}
        self.wlcp_list=[]
        self.bkcp = {}
        self.bkcp_list = []
        syst = dataCenterIni.getSyst()
        self.disk = syst['disk'].split(',')
        self.activedisk = syst['activedisk']
            
    def __del__(self):
        del self.imgMysql
        del self.orc
        #print 'datacenter quit'

    def setupMysql(self):
        try:
            self.imgMysql.login()
        except Exception,e:
            now = getTime()
            print now,e
            #logging.exception(e)
            print now,'Reconn after 15 seconds'
            time.sleep(15)
            self.setupMysql()
        else:
            pass        
            
    def setupOrc(self):
        try:
            self.orc.login()
        except Exception,e:
            now = getTime()
            print now,e
            #logging.exception(e)
            print now,'Reconn after 15 seconds'
            time.sleep(15)
            self.setupOrc()
        else:
            pass

    def loginMysql(self):
        self.imgMysql.login()
    
            
    def loginOrc(self):
        self.orc.login()

    def getFuzzy(self,str1,str2='_'):
        return str1.find(str2)
    
    def getSiteID(self):
        self.site = {}
        try:
            for i in self.orc.getConfigInfo():
                self.site[i['TYPE_ALIAS']] = i['TYPE_VALUE']
        except Exception,e:
            print getTime(),e

    def getWlcp(self):
        for i in self.orc.getWlcp():
            if self.getFuzzy(i[0])==-1:
                self.wlcp[i[0]]='W'
            else:
                self.wlcp_list.append(i[0].replace('_', '[^*]')+'*')

    def getBkcp(self):
        for i in self.orc.getBkcp():
            if self.getFuzzy(i[0])==-1:
                self.bkcp[i[0]]='B'
            else:
                self.bkcp_list.append(i[0].replace('_', '[^*]')+'*')
                
    def checkWlcpPlate(self,plate):
        if self.wlcp.get(plate,'F')=='W':
            return True
        elif len(self.wlcp_list)>0:
            for i in self.wlcp_list:
                r1 = re.compile(i)
                if r1.search(plate):
                    return True
            return False
        else:
            return False
        
    def checkBkcpPlate(self,plate):
        if self.bkcp.get(plate,'F')=='B':
            return True
        elif len(self.bkcp_list)>0:
            for i in self.bkcp_list:
                r1 = re.compile(i)
                if r1.search(plate):
                    return True
            return False
        else:
            return False
        
    def setData(self):
        #plateinfo = self.imgMysql.getPlateInfo()
        values = []
        w_values = []
        try:
            plateinfo = self.imgMysql.getPlateInfo2()
            count = len(plateinfo)
            s = {}
            if count > 0:
                for s in plateinfo:
                    if self.checkWlcpPlate(s['platecode'].encode('gbk')):
                        w_values.append((self.direction.get(s['directionid'],u'����').encode('gbk'),s['platecode'].encode('gbk'),s['platetype'].encode('gbk'),s['platecolor'].encode('gbk'),s['passdatetime'],s['carspeed'],s['imgpath'].encode('gbk'),'SpreadData'+s['disk'].encode('gbk'),'0','F','F','F','F',s['roadname'].encode('gbk'),s['limitspeed'],s['channelid'].encode('gbk'),self.site.get(s['roadname'].encode('gbk'),'0'),s['channelid'].encode('gbk'),s['vehiclecolor'].encode('gbk'),int(s['vehiclecoltype']),s['vehiclelen'].encode('gbk')))
                    else:
                        if self.checkBkcpPlate(s['platecode'].encode('gbk')):
                            bj = 'B'
                        elif s['overspeed']>=5.0:
                            bj = 'O'
                        else:
                            bj = 'F'
                        values.append((self.direction.get(s['directionid'],u'����').encode('gbk'),s['platecode'].encode('gbk'),s['platetype'].encode('gbk'),s['platecolor'].encode('gbk'),s['passdatetime'],s['carspeed'],s['imgpath'].encode('gbk'),'SpreadData'+s['disk'].encode('gbk'),'0',bj,'F','F','F',s['roadname'].encode('gbk'),s['limitspeed'],s['channelid'].encode('gbk'),self.site.get(s['roadname'].encode('gbk'),'0'),s['channelid'].encode('gbk'),s['vehiclecolor'].encode('gbk'),int(s['vehiclecoltype']),s['vehiclelen'].encode('gbk')))
                    self.imgMysql.flagManyIniIndex(s['id'])
                if self.orc.addWcltx(values,w_values):
                    self.imgMysql.sqlCommit()
                    self.orc.orcCommit()
                    carstr =  '%s %s %s | %s | %s | %s���� | IP:%s'%(getTime(),s['platecode'].encode("gbk"),s['platecolor'].encode("gbk"),s['roadname'].encode("gbk"),self.direction.get(s['directionid'],u'����').encode("gbk"),s['channelid'].encode("gbk"),s['pcip'].encode("gbk"))
                    self.trigger.emit("<font %s>%s</font>"%(self.style_blue,carstr))
                #print getTime(),'update %s plateinfo'%count
            else:
                time.sleep(0.25)
        except MySQLdb.Error,e:
            #print 'setData mysql',e // ,'%s |'%self.direction.get(s['directionid'],u'����'),'%s����'%s['channelid']
            raise
        except Exception,e:
            #print getTime(),'setData',e
            raise
##
##def main():
##    dataCenter = DataCenter()
##    dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    dataCenter.getSiteID()
##    dataCenter.getWlcp()
##    dataCenter.getBkcp()
##    diskstate = DiskState()
##    count = 0
##    while True:
##        try:
##            dataCenter.setData()
##            time.sleep(0.125)
##            count += 1
##            if count >= 80:
##                ds = diskstate.checkDisk()
##                for i in dataCenter.disk:
##                    print getTime(),i,"%0.2f%%"%ds.get(i,'none')
##                dataCenter.getSiteID()
##                dataCenter.getWlcp()
##                dataCenter.getBkcp()
##                count = 0
##        except MySQLdb.Error,e:
##            print getTime(),'MYSQLdb',e
##            dataCenter.setupMysql()
##        except Exception,e:
##            #print str(e)[:3]
##            if str(e)[:3] == 'ORA':
##                dataCenter.setupOrc()
##            print getTime(),e
       
if __name__ == "__main__":
    #main()
    ds = DiskState()
    print ds.checkDisk()
        
##    dataCenter = DataCenter()
##    dataCenter.setupOrc()
##    dataCenter.getBkcp()
##    print dataCenter.bkcp
##    print dataCenter.bkcp_list
##    print dataCenter.checkBkcpPlate('��23423')

    
##    #dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    s = dataCenter.getSiteID()
##    print s['��ˮ�����꿨��']
##    dataCenter = DataCenter()
##    dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    dataCenter.main()
##
##    del dataCenter


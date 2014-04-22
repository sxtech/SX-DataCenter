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

platecolor = {'其他':1,'蓝牌':2,'黄牌':3,'白牌':4,'黑牌':5,'绿牌':6}
#direction = {'0':'进城','1':'出城','2':'由东往西','3':'由南往北','4':'由西往东','5':'由北往南'}

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

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
    def __init__(self,trigger=('',1)):
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
        self.direction = {'0':u'进城','1':u'出城','2':u'由东往西','3':u'由南往北','4':u'由西往东','5':u'由北往南'}
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

    def getIPState(self):
        try:
            iplist = self.imgMysql.getIPList()
            now = datetime.datetime.now() - datetime.timedelta(minutes = 1)
            conn_state =0
            #ftp_state = 0
            for i in iplist:
                if i['activetime'] > now:
                    conn_state = 2
                else:
                    conn_state = 0
                self.trigger.emit("%s"%i['ip'],conn_state)
                
        except MySQLdb.Error,e:
            raise
        except Exception,e:
            raise

    def setNewIniTime(self):
        try:
            self.imgMysql.setNewIniTime()
        except MySQLdb.Error,e:
            raise
        except Exception,e:
            raise
        
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
        values = []
        w_values = []
        try:
            plateinfo = self.imgMysql.getNewPlateInfo()
            if len(plateinfo) == 0:
                plateinfo = self.imgMysql.getPlateInfo()
            num = len(plateinfo)

            if num > 0:
                for s in plateinfo:
                    if self.checkWlcpPlate(s['platecode'].encode('gbk')):
                        w_values.append((self.direction.get(s['directionid'],u'其他').encode('gbk'),s['platecode'].encode('gbk'),s['platetype'].encode('gbk'),s['platecolor'].encode('gbk'),s['passdatetime'],s['carspeed'],s['imgpath'].encode('gbk'),'SpreadData'+s['disk'].encode('gbk'),'0','F','F','F','F',s['roadname'].encode('gbk'),s['limitspeed'],s['channelid'].encode('gbk'),self.site.get(s['roadname'].encode('gbk'),'0'),s['channelid'].encode('gbk'),s['vehiclecolor'].encode('gbk'),int(s['vehiclecoltype']),s['vehiclelen'].encode('gbk')))
                    else:
                        if self.checkBkcpPlate(s['platecode'].encode('gbk')):
                            bj = 'B'
                        elif s['overspeed']>=5.0:
                            bj = 'O'
                        else:
                            bj = 'F'
                        values.append((self.direction.get(s['directionid'],u'其他').encode('gbk'),s['platecode'].encode('gbk'),s['platetype'].encode('gbk'),s['platecolor'].encode('gbk'),s['passdatetime'],s['carspeed'],s['imgpath'].encode('gbk'),'SpreadData'+s['disk'].encode('gbk'),'0',bj,'F','F','F',s['roadname'].encode('gbk'),s['limitspeed'],s['channelid'].encode('gbk'),self.site.get(s['roadname'].encode('gbk'),'0'),s['channelid'].encode('gbk'),s['vehiclecolor'].encode('gbk'),int(s['vehiclecoltype']),s['vehiclelen'].encode('gbk')))
                    self.imgMysql.flagManyIniIndex(s['id'])
                if self.orc.addWcltx(values,w_values):
                    self.imgMysql.sqlCommit()
                    self.orc.orcCommit()
                    carstr = '<table><tr style="font-family:arial;font-size:14px;color:blue"><td>%s<td><td width="100">%s</td><td width="40">%s</td><td width="160">%s</td><td width="70">%s</td><td width="40">%s车道</td></tr></table>'%(getTime(),plateinfo[-1]['platecode'].encode("gbk"),plateinfo[-1]['platecolor'].encode("gbk"),plateinfo[-1]['roadname'].encode("gbk"),self.direction.get(plateinfo[-1]['directionid'],u'其他').encode("gbk"),plateinfo[-1]['channelid'].encode("gbk"))
                    self.trigger.emit("%s"%carstr,1)
            else:
                time.sleep(0.125)
        except MySQLdb.Error,e:
            raise
        except Exception,e:
            raise

       
if __name__ == "__main__":
    #main()
    ds = DiskState()
    print ds.checkDisk()
        
##    dataCenter = DataCenter()
##    dataCenter.setupOrc()
##    dataCenter.getBkcp()
##    print dataCenter.bkcp
##    print dataCenter.bkcp_list
##    print dataCenter.checkBkcpPlate('粤23423')

    
##    #dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    s = dataCenter.getSiteID()
##    print s['淡水伯公坳卡口']
##    dataCenter = DataCenter()
##    dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    dataCenter.main()
##
##    del dataCenter


# -*- coding: cp936 -*-
import cx_Oracle

class Orc:
    def __init__(self,host='localhost',user='fire', passwd='kakou',sid='ORCL'):
        self.host    = host
        self.user    = user
        self.passwd  = passwd
        self.port    = 1521
        self.sid     = sid
        self.cur = None
        self.conn = None
        
    def __del__(self):
        if self.cur != None:
            self.cur.close()
        if self.conn != None:
            self.conn.close()
        
    def login(self):
        try:
            self.conn = cx_Oracle.connect(self.user,self.passwd,self.host+':'+str(self.port)+'/'+self.sid)
            self.cur = self.conn.cursor()
            #print self.passwd
        except Exception,e:
            raise

    def setupOrc(self):
        import time
        try:
            self.login()
        except Exception,e:
            #print now,e
            #logging.exception(e)
            #print now,'Reconn after 15 seconds'
            time.sleep(15)
            self.setupOrc()
        else:
            pass

    def getConfigInfo(self):
        try:
            self.cur.execute("select ID,TYPE_VALUE,TYPE_ID,TYPE_ALIAS from config_info  where type_name='卡口名称'")
        except Exception,e:
            raise
        else:
            return self.rowsToDictList()
    
    def getWlcp(self):
        try:
            self.cur.execute("select HPHM from wlcp where clbj='T'")
        except Exception,e:
            raise
        else:
            return self.cur.fetchall()

    def getBkcp(self):
        try:
            self.cur.execute("select HPHM from bkcp where clbj='T'")
        except Exception,e:
            raise
        else:
            return self.cur.fetchall()
        
    def addCltx(self,values):
        try:
            self.cur.executemany('insert into cltx(FXBH,HPHM,HPZL,HPYS,JGSJ,CLSD,TJTP,QMTP,JLLX,CLBJ,HDGG,QBGG,CFGG,WZDD,CLXS,CDBH,KKBH,FJDM,CSYS,CSYSSQ,CSCD) values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20,:21)',values)
        except Exception,e:
            self.conn.rollback()
            return False
            raise
        else:
            return True

    def addWcltx(self,values,w_values):
        s=False
        try:
            self.cur.executemany('insert into cltx(FXBH,HPHM,HPZL,HPYS,JGSJ,CLSD,TJTP,QMTP,JLLX,CLBJ,HDGG,QBGG,CFGG,WZDD,CLXS,CDBH,KKBH,FJDM,CSYS,CSYSSQ,CSCD) values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20,:21)',values)
            if len(w_values)>0:
                self.cur.executemany('insert into wcltx(FXBH,HPHM,HPZL,HPYS,JGSJ,CLSD,TJTP,QMTP,JLLX,CLBJ,HDGG,QBGG,CFGG,WZDD,CLXS,CDBH,KKBH,FJDM,CSYS,CSYSSQ,CSCD) values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20,:21)',w_values)
        except Exception,e:
            self.conn.rollback()
            raise
        else:
            s=True
            self.conn.commit()
        finally:
            return s

    def addWcltx2(self,values):
        s=False
        try:
            self.cur.executemany('insert into wcltx(FXBH,HPHM,HPZL,HPYS,JGSJ,CLSD,TJTP,QMTP,JLLX,CLBJ,HDGG,QBGG,CFGG,WZDD,CLXS,CDBH,KKBH,FJDM,CSYS,CSYSSQ,CSCD) values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20,:21)',values)
        except Exception,e:
            print e
            self.conn.rollback()
            raise
        else:
            s=True
            self.conn.commit()
        finally:
            return s
        
    def rowsToDictList(self):
        columns = [i[0] for i in self.cur.description]
        return [dict(zip(columns, row)) for row in self.cur]

    def orcCommit(self):
        self.conn.commit()

if __name__ == "__main__":
    import datetime
    orc = Orc()
    #values = []
    orc.setupOrc()
    values = []
    w_values=[]
    #while True:
        #print '2'
    #s=orc.getBkcp()
    #s = orc.rowsToDictList()
    #print s
    #time.sleep(3)
        #row_list = orc.rows_to_dict_list()
    #print len(row_list)
    time = datetime.datetime(2013,3,3,01,01,01)
    #path = r'ImageFile\20130115\09\10.44.240.2\02\160001000.jpg'
    #print path
    #print path.decode('gbk')
    #w_values.append(('\xbd\xf8\xb3\xc7', '\xd4\xc1B1VC58', '', '\xc0\xb6\xc5\xc6', datetime.datetime(2014, 1, 13, 16, 58, 36), 14, '20140321\\12\\192.168.17.80\\1\\20140113165836670.jpg', 'SpreadDataG', '0', 'F', 'F', 'F', 'F', 'F', '\xc6\xbd\xcc\xb6\xce\xda\xcc\xc1\xbf\xa8\xbf\xda', 80, '1', '0', '1', '0', 0, '0'))
    w_values.append(('\xbd\xf8\xb3\xc7','\xd4\xc1B1VC58', '', '\xc0\xb6\xc5\xc6', datetime.datetime(2014, 1, 13, 16, 58, 36), 14, '20140321\\12\\192.168.17.80\\1\\20140113165836670.jpg', 'SpreadDataG', '0', 'F', 'F', 'F', 'F','F', '\xc6\xbd\xcc\xb6\xce\xda\xcc\xc1\xbf\xa8\xbf\xda', 80, '1', '0', '1', '0', 0, '0'))
    #w_values.append(('\xbd\xf8\xb3\xc7','\xd4\xc1B1VC58','','\xc0\xb6\xc5\xc6',datetime.datetime(2014, 1, 13, 16, 58, 36),63,'20140321\\12\\192.168.17.80\\1\\20140113165836670.jpg','SpreadDataG','0','F','F','F','F','\xc6\xbd\xcc\xb6\xce\xda\xcc\xc1\xbf\xa8\xbf\xda',80,'1','0','1','123',23,'234'))
    #values.append(('进城','粤B','0','黄牌',time,45,'ImageFile\20130115\09\10.44.240.2\02\160001001.jpg'.decode('gbk').encode('gbk'),'SpreadDataG','0','T','F','F','F','测试卡口',80,'1','卡口编号','1','124',24,'235'))
    print orc.addWcltx2(w_values)
    orc.orcCommit()
    #orc.test()
    del orc

from datacenter import DataCenter
from PyQt4 import QtGui, QtCore
import sys,time,datetime,os
import MySQLdb
import cx_Oracle
import logging
import logging.handlers
from singleinstance import singleinstance2
import gl

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

def version():
    return 'SX-DataCenter V0.2.0'


#ds = DiskState()
#print ds.checkDisk()
 
class MyThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str,int)
 
    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)
 
    def run(self):
        m = dcmain(self.trigger)
        m.mainloop()

class dcmain:
    def __init__(self,trigger):
        self.style_red = 'size=4 face=arial color=red'
        self.style_blue = 'size=4 face=arial color=blue'
        self.style_green = 'size=4 face=arial color=green'
        self.trigger = trigger
        self.dc = DataCenter(trigger)
        initLogging(r'log\datacenter.log')
        self.count = 0
        self.loginmysqlflag = True
        self.loginorcflag = True
        self.loginmysqlcount = 0
        self.loginorccount = 0
        self.setupflag = False

        self.trigger.emit("<font %s>%s</font>"%(self.style_green,"Welcome to "+version()),1)


    def __del__(self):
        del self.dc

    def loginMYSQL(self):
        now = getTime()
        try:
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Start to connect mysql server '),1)
            self.dc.loginMysql()
            self.dc.getIPState()
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Connect mysql success! '),1)
        except MySQLdb.Error,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+'Reconn after 15 seconds'),1)
            logging.exception(e)
            self.loginmysqlflag = True
            self.loginmysqlcount = 1
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            logging.exception(e)
        else:
            self.loginmysqlflag = False
            self.loginmysqlcount = 0
            
    def loginORC(self):
        now = getTime()
        try:
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Start to connect Oracle server '),1)
            self.dc.loginOrc()
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Connect Oracle success! '),1)
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+'Reconn after 15 seconds'),1)
            logging.exception(e)
            self.loginorcflag = True
            self.loginorccount = 1
        else:
            self.loginorcflag = False
            self.loginorccount = 0
            
    def mainLoop(self):
        #print 'loop'
        try:   
            self.dc.setData()
            time.sleep(0.125)
            self.count += 1
            if self.count >= 80:
                self.dc.getSiteID()
                self.dc.getWlcp()
                self.dc.getBkcp()
                self.dc.getIPState()
                self.count = 0
        except MySQLdb.Error,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            logging.exception(e)
            self.loginmysqlflag = True
            self.loginmysqlcount = 1
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            logging.exception(e)
            if str(e)[:3] == 'ORA':
                self.loginorcflag = True
                self.loginorccount = 1
        
    def setup(self):
        #print 'setup'
        try:
            self.dc.getSiteID()
            self.dc.getWlcp()
            self.dc.getBkcp()
            self.dc.getIPState()
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            logging.exception(e)
            self.loginorcflag = True
            self.loginorccount = 1
        else:
            self.setupflag = True

    def mainloop(self):                    
        while True:
            #print 'count ',self.count
            #time.sleep(1)
            if gl.qtflag == False:
                gl.dcflag = False
                break
            
            if self.loginmysqlflag == True:
                #print '123'
                if self.loginmysqlcount==0:
                    self.loginMYSQL()
                elif self.loginmysqlcount<=15:
                    self.loginmysqlcount += 1
                    time.sleep(1)
                else:
                    self.loginmysqlcount = 0

            elif self.loginorcflag == True:
                #print '456'
                if self.loginorccount==0:
                    self.loginORC()
                    self.dc.getIPState()
                elif self.loginorccount<=15:
                    self.loginorccount += 1
                    time.sleep(1)
                else:
                    self.loginorccount = 0
            else:
                if self.setupflag:
                    self.mainLoop()
                else:
                    self.setup()
    
class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):  
        super(MainWindow, self).__init__(parent)
        self.resize(650, 450)
        self.setWindowTitle(version())

        self.tree = QtGui.QTreeWidget()
        self.tree.setMinimumWidth(200)
        self.tree.setMaximumWidth(250)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['IP','Conn'])

        self.root = QtGui.QTreeWidgetItem(self.tree)
        self.root.setText(0,'State')

        self.count = 0
        self.ipdict = {}
        self.statelist = [('off',QtGui.QColor(255,0,0)),('on',QtGui.QColor(0,200,50))]
        self.statedict = {0:self.statelist[0],2:self.statelist[1]}
        
        self.tree.addTopLevelItem(self.root)

        self.setCentralWidget(self.tree)
        
        self.text_area = QtGui.QTextBrowser()
        self.text_area.setMinimumWidth(500)
        self.text_area.setMinimumHeight(400)
 
        central_widget = QtGui.QWidget()
        central_layout = QtGui.QHBoxLayout()
        central_layout.addWidget(self.tree)
        central_layout.addWidget(self.text_area)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        self.statusBar()

        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit)
        
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)
        
        #self.setGeometry(300, 300, 250, 150)
        #self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('icons/logo2.png'))
        
        self.start_threads()
        
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            gl.qtflag = False
            while gl.dcflag == True:
                #print 'gl.dcflag',gl.dcflag
                time.sleep(1)
            event.accept()
        else:
            event.ignore()
            
    def start_threads(self):
        self.threads = []              # this will keep a reference to threads
        thread = MyThread(self)    # create a thread
        thread.trigger.connect(self.update_text)  # connect to it's signal
        thread.start()             # start the thread
        self.threads.append(thread) # keep a reference
            
 
    def update_text(self, message,m_type):
        if m_type == 1:
            self.text_area.append(unicode(message, 'gbk'))
            self.count += 1
            if self.count >1000:
                self.text_area.clear()
                self.count = 0
        else:
            if self.ipdict.get(message,0) == 0:
                self.ipdict[message] = QtGui.QTreeWidgetItem(self.root)
            else:
                pass
            one = self.statedict.get(m_type,(self.statelist[0],self.statelist[0]))
            self.ipdict[message].setText(0,message)
            self.ipdict[message].setText(1,one[0])
            self.ipdict[message].setTextColor(1,one[1])
 
if __name__ == '__main__':
    myapp = singleinstance2()
    if myapp.aleradyrunning():
        print version(),'已经启动!3秒后自动退出...'
        time.sleep(3)
        sys.exit(0)
    
    app = QtGui.QApplication(sys.argv)
 
    mainwindow = MainWindow()
    mainwindow.show()
    #print 'after show'
 
    sys.exit(app.exec_())

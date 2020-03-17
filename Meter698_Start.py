import UI_Meter698, sys, serial, serial.tools.list_ports, threading, Meter698_core, time, UI_Meter698_config, \
    configparser, os, datetime, re
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QTableWidgetItem, QHeaderView, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from Comm import makestr, get_list_sum, makelist
from binascii import b2a_hex, a2b_hex
from traceback import print_exc


class MainWindow(QMainWindow):
    __switch = pyqtSignal(str)
    _signal_text = pyqtSignal(str)

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = UI_Meter698.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('模拟表程序 v1.56')
        self.addItem = self.GetSerialNumber()
        while 1:
            if self.addItem is None:
                warn = QMessageBox.warning(self, '警告', '未检测到串口', QMessageBox.Reset | QMessageBox.Cancel)
                if warn == QMessageBox.Cancel:
                    self.close()
                if warn == QMessageBox.Reset:
                    self.addItem = self.GetSerialNumber()
                continue
            else:
                break
        self.addItem.sort()
        self.load_ini()
        self.Connect = Connect()

        for addItem in self.addItem:
            self.ui.comboBox.addItem(addItem)
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.ui.pushButton.clicked.connect(self.serial_prepare)
        self._signal_text.connect(self.Warming_message)
        self.config = Config()
        self.ui.toolButton.clicked.connect(self.showd)
        self.__switch.connect(self.Show_Hidden)
        self.setWindowIcon(QIcon('source/taxi.ico'))
        self.ui.pushButton_2.setToolTip('清空当前窗口记录')
        self.ui.toolButton.setToolTip('设置')
        self.ui.label_5.setText('')

    def log_session(self, message):
        if self.ui.checkBox.isChecked():
            text = open(datetime.datetime.now().strftime('%y%m%d.log'), 'a+')
            text.write(message + '\n')

    def showd(self):
        self.config.setWindowModality(Qt.ApplicationModal)
        self.config.exec()

    def closeEvent(self, *args, **kwargs):
        try:
            self.config.close()
        finally:
            sys.exit()

    def load_ini(self):
        self.conf = configparser.ConfigParser()
        try:
            if os.path.exists('config.ini'):
                self.conf.read('config.ini', encoding='utf-8')
                print("read config.ini")
                if self.conf.has_section('MeterData698') is True and self.conf.has_section('MeterData645'):
                    print("read config.ini ok")
                    return 0
                else:
                    print("read config.ini false")
                    self.ini()
            else:
                print("no config.ini")
                self.ini()
        except:
            print_exc(file=open('bug.txt', 'a+'))

    def ini(self):
        try:
            ini = open('config.ini', 'w', encoding='utf-8')
            self.conf.add_section('MeterData698')
            data = open('source\\698data', 'r', encoding='utf-8')
            while 1:
                text = data.readline()
                if text == '\n' or text == '':
                    break
                text = text.split(' ')
                self.conf.set('MeterData698', text[0], text[1] + ' ' + text[2][:-1])

            self.conf.add_section('MeterData645')
            data = open('source\\07data', 'r', encoding='utf-8')
            while 1:
                text = data.readline()
                if text == '\n' or text == '':
                    break
                text = text.split(' ')
                self.conf.set('MeterData645', text[0], text[2] + ' ' + text[3][:-1])
            self.conf.write(ini)
        except:
            print("error: ", text)
            print_exc(file=open('bug.txt', 'a+'))

    def serial_prepare(self):
        try:
            self.Connect.setDaemon(True)
            self.Connect.start()
            self.ui.pushButton.disconnect()
            self.ui.pushButton.clicked.connect(self.Connect.switch)
            self.__switch.emit('1')
            self.Run = RuningTime()
            self.Run.setDaemon(True)
            self.Run.start()
            self.ui.pushButton.clicked.connect(lambda: self.Run.res())
        except:
            print_exc(file=open('bug.txt', 'a+'))

    def GetSerialNumber(self):
        SerialNumber = []
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) <= 0:
            print("The Serial port can't find!")
        else:
            for i in list(port_list):
                SerialNumber.append(i[0])
            return SerialNumber

    def Warming_message(self, message):
        if message == 'ERROR':
            QMessageBox.warning(self, 'ERROR', '无法打开串口')
        else:
            self.ui.textEdit.append(message)

    def Show_Hidden(self, num):
        if num == '0':
            self.ui.comboBox.setDisabled(0)
            self.ui.comboBox_2.setDisabled(0)
            self.ui.comboBox_3.setDisabled(0)
            self.ui.comboBox_4.setDisabled(0)
        else:
            self.ui.comboBox.setDisabled(1)
            self.ui.comboBox_2.setDisabled(1)
            self.ui.comboBox_3.setDisabled(1)
            self.ui.comboBox_4.setDisabled(1)


class RuningTime(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sec = 0

    def run(self):
        # self.start_ = time.time()
        while 1:
            time.sleep(1)
            self.sec += 1
            # self.end = start_ + sec
            a = int(self.sec)
            if 3600 > a > 60:
                b = a // 60
                MainWindow.ui.label_5.setText('运行时间: ' + str(b) + ' 分钟 ' + str(a % 60) + ' 秒')
            elif a >= 3600:
                b = a // 3600
                MainWindow.ui.label_5.setText('运行时间: ' + str(b) + ' 时 ' + str(a % 3600 // 60) + ' 分钟')
            else:
                MainWindow.ui.label_5.setText('运行时间: ' + str(a) + ' 秒')

    def res(self):
        self.sec = 0


class Connect(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.serial = serial.Serial()
        self.__runflag = threading.Event()
        self.config = Config()

    def switch(self):
        if self.__runflag.isSet():
            MainWindow.ui.pushButton.setText('启动')
            print('关闭状态')
            MainWindow.Show_Hidden('0')
            self.__runflag.clear()
            MainWindow.ui.label_5.hide()

        else:
            MainWindow.ui.pushButton.setText('关闭')
            print('启动状态')
            MainWindow.Show_Hidden('1')
            self.__runflag.set()
            MainWindow.ui.label_5.show()

    def run(self):
        self.__runflag.set()
        while 1:
            if self.__runflag.isSet():
                try:
                    revalue = self.serial_open()
                    print('revalue', revalue)
                    if revalue == 1:
                        print('clear')
                        self.__runflag.clear()
                        MainWindow.Show_Hidden('0')
                        MainWindow.ui.pushButton.setText('启动')
                        continue
                    if revalue is None:
                        continue
                except:
                    print('ERROR')
                    print_exc(file=open('bug.txt', 'a+'))
                    self.__runflag.clear()
            else:
                self.__runflag.wait()
                print('sleep1')

    def serial_open(self):
        if self.serial.isOpen() is True:
            print('close')
            self.serial.close()
        else:
            try:
                self.serial.port = MainWindow.ui.comboBox.currentText()
                self.serial.baudrate = int(MainWindow.ui.comboBox_2.currentText())
                self.serial.parity = MainWindow.ui.comboBox_3.currentText()
                self.serial.stopbits = int(MainWindow.ui.comboBox_4.currentText())
                self.serial.timeout = 1
                self.serial.open()
                MainWindow.ui.pushButton.setText('关闭')
                print('启动')
                global data
                data = ''
                while self.__runflag.isSet():
                    time.sleep(0.2)
                    if self.serial.isOpen is False:
                        break
                    num = self.serial.inWaiting()
                    data = data + str(b2a_hex(self.serial.read(num)))[2:-1]
                    try:
                        if data != '':
                            if data[0] == '6' and data[1] == '8' and len(data) > 20:
                                if data[-1] == '6' and data[-2] == '1':
                                    print('Received: ', data)
                                    Received_data = '收到:\n' + makestr(data)
                                    MainWindow._signal_text.emit(Received_data)
                                    MainWindow.log_session(Received_data)
                                    self.Meter = Meter698_core
                                    wild = Meter698_core.Wild_match_Analysis(data.replace(' ', ''))
                                    if wild == 0:
                                        print('检测到通配地址')
                                        times = Meter698_core.re_max()
                                        sent = self.Meter.Analysis(data.replace(' ', ''))
                                        self._Sent(sent)
                                    elif wild == 1:  # add 645
                                        sent = self.Meter.Analysis(data.replace(' ', ''))
                                        self._Sent(sent)
                                        continue
                                    elif wild == 2:
                                        data = ''
                                        continue
                                    else:
                                        print('???')
                            else:
                                try:
                                    while 1:
                                        print('data:', data)
                                        if data[-1] == '6' and data[-2] == '1' and len(data) > 20:
                                            if data[0] == '6' and data[1] == '8':
                                                print('完整报文:', data)
                                                break
                                            elif data[0] == 'f' and data[1] == 'e':
                                                data = data[2:]
                                                continue
                                        if data[0] == '6' and data[1] == '8':
                                            if Meter698_core.check(makelist(data)) == 0:
                                                print('找出有效报文', data)
                                                break
                                            else:
                                                print('不完整报文!继续接收:', data)
                                                break
                                        if data[0] == 'f' and data[1] == 'e':
                                            data = data[2:]
                                            continue
                                        print('Abort')
                                        data = ''
                                        break
                                except:
                                    pass
                            continue
                        else:
                            continue
                    except:
                        print_exc(file=open('bug.txt', 'a+'))
                        continue
            except:
                MainWindow._signal_text.emit('ERROR')
                print('无法打开串口')
                print_exc(file=open('bug.txt', 'a+'))
                return 1

    def _Sent(self, sent):
        global data, LargeOAD, frozenSign, data_list
        if sent == 1:
            message = "抄表地址在黑名单内不与返回或存在不支持项,具体原因在bug.txt中查看"
            MainWindow._signal_text.emit(message)
            MainWindow.log_session(message)
            LargeOAD = ''
            data_list = []
            data = ''
            frozenSign = 0
            self.Meter.ReturnMessage().clear_OI()
            MainWindow._signal_text.emit('--------------------------------')
            MainWindow.log_session('--------------------------------')
        if sent == 3:
            message = "开启白名单以启用搜698表"
            MainWindow._signal_text.emit(message)
            MainWindow.log_session(message)
            LargeOAD = ''
            data_list = []
            data = ''
            frozenSign = 0
            self.Meter.ReturnMessage().clear_OI()
            MainWindow._signal_text.emit('--------------------------------')
            MainWindow.log_session('--------------------------------')
        # elif sent == 2:
        #     message = "2130为旧规约,不返回内容"
        #     MainWindow._signal_text.emit(message)
        #     MainWindow.log_session(message)
        #     LargeOAD = ''
        #     data_list = []
        #     data = ''
        #     frozenSign = 0
        #     self.Meter.ReturnMessage().clear_OI()
        elif sent != 1:
            self.serial.write(a2b_hex(sent))
            self.Meter.ReturnMessage()
            content = self.Meter.ReturnMessage().transport()
            # print('content:', content)
            message = '数据标识:' + get_list_sum(content) + '\n表地址:' + Meter698_core.black_white_SA_address  # 显示
            sent = '发送:\n' + makestr(sent)
            MainWindow._signal_text.emit(message)
            MainWindow.log_session(message)
            MainWindow._signal_text.emit(sent)
            MainWindow.log_session(sent)
            ct = time.time()
            local_time = time.localtime(ct)
            data_head = time.strftime("%H:%M:%S", local_time)
            data_secs = (ct - int(ct)) * 1000
            time_stamp = "%s.%3d" % (data_head, data_secs)
            MainWindow._signal_text.emit(time_stamp)
            MainWindow.log_session(time_stamp)
            MainWindow._signal_text.emit('--------------------------------')
            MainWindow.log_session('--------------------------------')
            LargeOAD = ''
            data_list = []
            data = ''
            frozenSign = 0
            self.Meter.ReturnMessage().clear_OI()
        else:
            data = ''


class Config(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.ui = UI_Meter698_config.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.running)
        self.ui.pushButton_3.clicked.connect(self.list_increas)
        self.ui.pushButton_4.clicked.connect(self.list_decreas)
        self.conf = configparser.ConfigParser()
        self.deal_list()
        self.ui.pushButton_6.clicked.connect(self.clear)
        self.ui.pushButton_5.clicked.connect(self.output_log)
        self.get_max()
        self.setWindowIcon(QIcon('source/taxi.ico'))
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.WindowStaysOnTopHint and Qt.MSWindowsFixedSizeDialogHint)

        self.ui.checkBox_3.setToolTip('00100200 随软件启动时间逐步递增')
        self.ui.checkBox_2.setToolTip('返回抄表报文内的时标')
        self.ui.checkBox.setToolTip('返回抄表报文内的时标,若抄表报文无时标则返回当前系统日期')
        self.ui.checkBox_4.setToolTip('日冻结数据随日冻结时标距离当前系统日期的差值进行变化(Selector 09 无效)')
        self.ui.checkBox_5.setToolTip('明文回复附带MAC‘0A0B0C0D’')
        self.ui.checkBox_6.clicked.connect(self.Curve_leak)

    def running(self):
        self.get_auto_day_frozon()
        self.get_auto_curve_frozon()
        self.get_auto_increase()
        self.get_auto_increase_5004020000100200()
        self.close()
        self.list_save()
        self.bw()
        self.set_max()
        self.set_mac()
        self.sent_from_to()
        self.event_special()
        Meter698_core.event_blacklist = self.ui.lineEdit_22.text().split(';')

    def event_special(self):
        Meter698_core.apdu_3320 = self.ui.lineEdit_3.text().replace(" ", '')
        if self.ui.radioButton_4.isChecked():
            Meter698_core.event_stat = 0
        elif self.ui.radioButton_5.isChecked():
            Meter698_core.event_stat = 1
        else:
            Meter698_core.event_stat = 2

    def Curve_leak(self):
        if self.ui.checkBox_6.isChecked():
            self.ui.label_4.setDisabled(0)
            self.ui.label_5.setDisabled(0)
            self.ui.timeEdit.setDisabled(0)
            self.ui.timeEdit_2.setDisabled(0)
            Meter698_core.set_from_to_sign(1)
        else:
            self.ui.label_4.setDisabled(1)
            self.ui.label_5.setDisabled(1)
            self.ui.timeEdit.setDisabled(1)
            self.ui.timeEdit_2.setDisabled(1)
            self.from_to = []
            Meter698_core.set_from_to_sign(0)

    def sent_from_to(self):
        if self.ui.checkBox_6.isChecked():
            from_ = self.ui.timeEdit_2.text().split(':')
            from_ = int(from_[0]) * 60 + int(from_[1])
            to_ = self.ui.timeEdit.text().split(':')
            to_ = int(to_[0]) * 60 + int(to_[1])
            self.from_to = [from_, to_]
            print('self.from_to', self.from_to)
            Meter698_core.set_from_to(self.from_to)
        else:
            self.from_to = []
            Meter698_core.set_from_to(self.from_to)

    def get_max(self):
        self.ui.lineEdit.setText(str(Meter698_core.re_max()))

    def set_max(self):
        text = self.ui.lineEdit.displayText()
        print('通配地址数量:', text)
        Meter698_core.change_max(text)

    def bw(self):
        re_ = self.black_and_white()
        Meter698_core.B_W_add(re_[0], re_[1])

    def black_and_white(self):
        if self.ui.radioButton_3.isChecked():  # 未启用
            return 0, 0

        elif self.ui.radioButton.isChecked():  # 黑名单
            return 1, self.ui.textEdit.toPlainText()

        elif self.ui.radioButton_2.isChecked():  # 白名单
            return 2, self.ui.textEdit_2.toPlainText()

    def output_log(self):
        txt = QFileDialog.getSaveFileName(self, '文件保存', 'C:/', 'Text Files (*.txt)')
        try:
            with open(txt[0], 'w') as f:
                text = MainWindow.ui.textEdit.toPlainText()
                f.write(text)
        except:
            QMessageBox.about(self, 'ERROR', '文件保存失败')

    def clear(self):
        x = self.ui.tableWidget.rowCount() - 1
        while x:
            self.ui.tableWidget.removeRow(x)
            x -= 1
        self.deal_list()

    def get_auto_day_frozon(self):
        print('self.ui.checkBox.isChecked()', self.ui.checkBox.isChecked())
        if self.ui.checkBox.isChecked() is True:
            print('get_auto_day_frozon TURE')
            Meter698_core.set_auto_day_frozon(1)
        else:
            print('get_auto_day_frozon FLASE')
            Meter698_core.set_auto_day_frozon(0)

        return self.ui.checkBox.isChecked()

    def get_auto_curve_frozon(self):
        print('curve', self.ui.checkBox_2.isChecked())
        if self.ui.checkBox_2.isChecked() is True:
            print('get_auto_curve_frozon TURE')
            Meter698_core.curve_frozon(1)
        else:
            print('get_auto_curve_frozon FLASE')
            Meter698_core.curve_frozon(0)
        return self.ui.checkBox_2.isChecked()

    def get_auto_increase(self):
        print('increase', self.ui.checkBox_3.isChecked())
        if self.ui.checkBox_3.isChecked() is True:
            print('get_auto_increase TURE')
            Meter698_core.auto_00100200(1)
        else:
            print('get_auto_increase FLASE')
            Meter698_core.auto_00100200(0)
        return self.ui.checkBox_3.isChecked()

    def get_auto_increase_5004020000100200(self):
        print('increase', self.ui.checkBox_4.isChecked())
        if self.ui.checkBox_4.isChecked() is True:
            print('get_auto_increase TURE')
            Meter698_core.auto_500400100200(1)
        else:
            print('get_auto_increase FLASE')
            Meter698_core.auto_500400100200(0)
        return self.ui.checkBox_4.isChecked()

    def set_mac(self):
        print('set', self.ui.checkBox_5.isChecked())
        if self.ui.checkBox_5.isChecked() is True:
            print('set_mac TURE')
            Meter698_core.add_mac(1)
        else:
            print('set_mac FLASE')
            Meter698_core.add_mac(0)
        return self.ui.checkBox_5.isChecked()

    def list_increas(self):
        num = self.ui.tableWidget.currentRow()
        self.ui.tableWidget.insertRow(num)

    def list_decreas(self):
        num = self.ui.tableWidget.currentRow()
        self.ui.tableWidget.removeRow(num)

    def deal_list(self):
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.conf.read('config.ini', encoding='utf-8')
        x = 0  # 行
        text = self.conf.items('MeterData698')
        for items in text:
            y = 0
            self.ui.tableWidget.setItem(x, y, QTableWidgetItem(items[0]))
            for item in items[1].split(' '):
                y += 1
                self.ui.tableWidget.setItem(x, y, QTableWidgetItem(item))
            x += 1
            self.ui.tableWidget.insertRow(x)
        self.ui.tableWidget.removeRow(x)

    def list_save(self):
        try:
            x = self.ui.tableWidget.rowCount() - 1
            while x:
                y = 0
                text_0 = self.ui.tableWidget.item(x, y).text()
                text_1 = ''
                while y < 2:
                    y += 1
                    text_1 = text_1 + ' ' + self.ui.tableWidget.item(x, y).text()
                text_1 = text_1
                self.conf.set('MeterData698', text_0, text_1)
                x -= 1
            self.conf.write(open('config.ini', 'w', encoding='utf-8'))
        except:
            print_exc(file=open('bug.txt', 'a+'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())

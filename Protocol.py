from socket import *
import select, threading, Comm, binascii
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject


class Pro376(QObject):
    _signal_advance_text = pyqtSignal(str)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.x = threading.Thread(target=self.start_to_connect, daemon=True)
        self.x.start()
        self.flag = 0

    def start_to_connect(self):
        host = '0.0.0.0'
        ADDR = (host, int(self.port))
        self.tctime = socket(AF_INET, SOCK_STREAM)
        self.tctime.bind(ADDR)
        self.tctime.listen(5)
        print('Waiting for connection ...')
        self._signal_advance_text.emit('Waiting for connection ...')
        while 1:
            def loop():
                buffsize = 2048
                try:
                    print("Connection from :", self.add)
                    self._signal_advance_text.emit("Connection from :" + self.add[0])
                    while True:
                        try:
                            if self.flag == 1:
                                print("29")
                                return 1
                            readable, [], exceptional = select.select([self.tctimeClient], [], [self.tctimeClient], 0)
                            if self.tctimeClient in readable:
                                data = self.tctimeClient.recv(buffsize)
                                data = Comm.makestr(str(binascii.b2a_hex(data))[2:-1])
                                if data is not None and data != '':
                                    print('Received message:', data)
                                    self._signal_advance_text.emit('Received message:' + data)
                                    message = self.analysis376(data.replace(' ', ''))
                                    print('adssss', message)
                                    if message is None:
                                        continue
                                    if message[0] == 0:
                                        print('Send message:', Comm.makestr(message[1]))
                                        self._signal_advance_text.emit(
                                            'Send message:' + Comm.makestr(message[1]) + ' 登录/心跳')
                                        self.tctimeClient.send(binascii.a2b_hex(message[1]))
                            if self.tctimeClient in exceptional:
                                break
                        except:
                            break
                except:
                    # self._signal_warm.emit((0, '端口被占用'))
                    pass

            try:
                readable, [], exception = select.select([self.tctime], [], [self.tctime])
                if self.tctime in readable:
                    connection, self.add = self.tctime.accept()
                    self.tctimeClient = connection
                    if loop() == 1:
                        print("66")
                        break
                if self.tctime in exception:
                    break
            except:
                break
        self.tctime.close()
        print("进程结束")

    def analysis376(self, code):
        code = Comm.makelist(code)
        while 1:
            if code[0] == '68':
                break
            else:
                code = code[1:]
        L1 = code[1:3]
        APDU_len = self.lenth(L1)
        APDU = code[6:6 + APDU_len]
        global A1, A2
        A1 = Comm.list2str(APDU[1:3])
        A2 = Comm.list2str(APDU[3:5])
        return self.AFN(A1, A2, APDU[6:])

    def lenth(self, code):
        L1 = bin(int(code[0], 16))[2:-2].zfill(6)
        L2 = bin(int(code[1], 16))[2:].zfill(8)
        len_ = int(L2 + L1, 2)
        print('len', len_)
        return len_

    def SEQ(self, num):
        bin_ = bin(int(num, 16))[2:].zfill(8)
        PSEQ = bin_[-4:]
        return PSEQ

    def AFN(self, A1, A2, data):
        if data[0] == '00':
            print('确认/否认')
            if Comm.list2str(data[2:6]) == '00000100':
                print('终端确认所发请求')
                return 1, '终端确认所发请求'
            else:
                print('Others')

        if data[0] == '02':
            print('链路接口检测')
            if Comm.list2str(data[2:6]) == '00000100' or Comm.list2str(data[2:6]) == '00000400':
                seq = hex(int('0110' + self.SEQ(data[1]), 2))[2:].zfill(2)
                print('seq', seq)
                re_data = '00' + seq + '00000100'
                L_ = '68 32 00 32 00 68'
                A3 = '66'
                C = '40'
                re_message = C + A1 + A2 + A3 + re_data.replace(' ', '')
                cs = self.CS(Comm.strto0x(Comm.makelist(re_message)))
                re_message = (L_ + re_message + cs + '16').replace(' ', '')
                return 0, re_message
        if data[0] == '0a':
            print('读取参数')
            if Comm.list2str(data[2:6]) == '00008018':
                x = 'F200\n' + '冻结时间间隔 ' + data[6] + '分钟'
                print(x)
                return 1, x

        if data[0] == '0c':
            print('请求一类数据')
            if Comm.list2str(data[2:6]) == '000080fe':
                x = 'F2040 \n' + '信号强度:' + data[6] + '\n电话号码:' + Comm.list2str(data[7:13]) + '\nICCID:' + Comm.list2str(
                    data[13:])
                print(x)
                return 1, x
            if Comm.list2str(data[2:6]) == '01010103':
                list_ = [Comm.list2str(data[13:10:-1]), Comm.list2str(data[16:13:-1]), Comm.list2str(data[19:16:-1]),
                         Comm.list2str(data[22:19:-1]), Comm.list2str(data[25:22:-1]), Comm.list2str(data[28:25:-1]),
                         Comm.list2str(data[31:28:-1]), Comm.list2str(data[34:31:-1]), Comm.list2str(data[36:34:-1]),
                         Comm.list2str(data[38:36:-1]), Comm.list2str(data[40:38:-1]), Comm.list2str(data[42:40:-1]),
                         Comm.list2str(data[44:42:-1]), Comm.list2str(data[46:44:-1]), Comm.list2str(data[48:46:-1]),
                         Comm.list2str(data[51:48:-1]), Comm.list2str(data[54:51:-1]), Comm.list2str(data[57:54:-1]),
                         Comm.list2str(data[60:57:-1]), Comm.list2str(data[63:60:-1]), Comm.list2str(data[66:63:-1]),
                         Comm.list2str(data[69:66:-1]), Comm.list2str(data[72:69:-1])
                         ]

                x = ['一类数据F25:',
                     '抄表日期:' + data[10] + '年' + data[9] + '月' + data[8] + '日' + data[7] + '时' + data[6] + '分',
                     '当前总有功功率:' + self.add_point(list_[0], 0.0001), '当前A相有功功率:' + self.add_point(list_[1], 0.0001),
                     '当前B相有功功率:' + self.add_point(list_[2], 0.0001), '当前C相有功功率:' + self.add_point(list_[3], 0.0001),
                     '当前总无功功率:' + self.add_point(list_[4], 0.0001), '当前A相无功功率:' + self.add_point(list_[5], 0.0001),
                     '当前B相无功功率:' + self.add_point(list_[6], 0.0001), '当前C相无功功率:' + self.add_point(list_[7], 0.0001),
                     '当前总功率因数:' + self.add_point(list_[8], 0.1), '当前A相功率因数:' + self.add_point(list_[9], 0.1),
                     '当前B相功率因数:' + self.add_point(list_[10], 0.1), '当前C相功率因数:' + self.add_point(list_[11], 0.1),
                     '当前A相电压:' + self.add_point(list_[12], 0.1), '当前B相电压:' + self.add_point(list_[13], 0.1),
                     '当前C相电压:' + self.add_point(list_[14], 0.1),
                     '当前A相电流:' + self.add_point(list_[15], 0.001), '当前B相电流:' + self.add_point(list_[16], 0.001),
                     '当前C相电流:' + self.add_point(list_[17], 0.001), '当前零序电流:' + self.add_point(list_[18], 0.001),
                     '当前总视在功率:' + self.add_point(list_[19], 0.0001), '当前A相视在功率:' + self.add_point(list_[20], 0.0001),
                     '当前B相视在功率:' + self.add_point(list_[21], 0.0001), '当前C相视在功率:' + self.add_point(list_[22], 0.0001)
                     ]
                data_ = ['333333', '222222', '111111', '666666', '033333', '022222', '011111', '066666', '0321', '0654',
                         '0987',
                         '0789', '2233', '2212', '2211', '005300', '005200', '005100', '444444', '055005', '055050',
                         '055500', '055555']
                print('list', list_, 'data_', data_, 'x', x)
                q = 0
                error_list = []
                for a in list_:
                    if data_[q] == a:
                        pass
                    else:
                        error_list.append(x[q])
                    q += 1
                print('error_list', error_list)
                if not error_list:
                    x.append('数据正确,与模拟表数值一致')
                else:
                    x.append('数据错误!')
                    x.append(error_list)
                return 3, x
        else:
            print('data[0]', data[0])

    def add_point(self, num, bit):
        if bit == 0.1:
            return '{:.1f}'.format(int(num) * bit)
        elif bit == 0.01:
            return '{:.2f}'.format(int(num) * bit)
        elif bit == 0.001:
            return '{:.3f}'.format(int(num) * bit)
        elif bit == 0.0001:
            return '{:.4f}'.format(int(num) * bit)
        return str(int(num) * bit)

    def CS(self, list):
        sum = 0
        while list:
            sum = sum + ord(list.pop())
        sum = hex(sum & 0xff)[2:]
        if len(sum) == 1:
            sum = "0" + sum
        return sum

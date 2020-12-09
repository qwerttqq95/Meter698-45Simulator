import re, time

def ShowTime(text):
    year = text[0:4]
    mouth = text[4:6]
    day = text[6:8]
    hour = text[8:10]
    mi=text[10:12]
    sec = text[12:14]
    return str(int(mouth,16))+"月"+str(int(day,16))+"日"+str(int(hour,16))+"时"+str(int(mi,16))+"分"+str(int(sec,16))+"秒"


def time_add(ori, add):
    if add == 0:
        return ori
    hex_text_list1 = makestr(ori).split(" ")
    save1 = hex_text_list1[0:5]
    times = (int(hex_text_list1[5], 16) * 3600) + (int(hex_text_list1[6], 16) * 60) + int(hex_text_list1[7], 16) + add
    hour = times // 3600
    min = times // 60 - hour * 60
    sec = times - hour * 3600 - min * 60
    print("aaaaaaaa",hour,min,sec)
    print("aaaaaaaaa",hex(hour)[2:].zfill(2),hex(min)[2:].zfill(2),hex(sec)[2:].zfill(2))
    return list2str(save1) + hex(hour)[2:].zfill(2) + hex(min)[2:].zfill(2) + hex(sec)[2:].zfill(2)


def time_cacl(hex_text1, hex_text2, gaps):
    hex_text_list1 = makestr(hex_text1).split(" ")
    save1 = hex_text_list1[0:5]
    times1 = int(hex_text_list1[5], 16) * 3600 + int(hex_text_list1[6], 16) * 60 + int(hex_text_list1[7], 16)

    hex_text_list2 = makestr(hex_text2).split(" ")
    save2 = hex_text_list2[0:5]
    times2 = int(hex_text_list2[5], 16) * 3600 + int(hex_text_list2[6], 16) * 60 + int(hex_text_list2[7], 16)

    count = (times1 - times2) // gaps + 1
    return count


def list_append(list_):
    text = ''
    for i in list_:
        text = text + i
    return text


def get_list_sum(list_):
    text = ''
    for i in list_:
        text = text + ' ' + i
    return text


def Inverse_code(codes):
    recode = ''
    for code in codes[2:]:
        if code == '1':
            code_ = '0'

        else:
            code_ = '1'
        recode = recode + code_
    return recode


def makestr(message):
    str_ = ''
    x = 0
    lenth = len(message)
    while lenth > 0:
        str_ = str_ + message[x:x + 2] + ' '
        x += 2
        lenth -= 2
    return str_


def makelist(message):
    list = []
    x = 0
    lenth = len(message)
    while lenth > 0:
        list.append(message[x:x + 2])
        x += 2
        lenth -= 2
    return list


def strto0x(context):
    # print('context:', context)
    context = [int(x, 16) for x in context]
    new_context = []
    while context:
        current_context = chr(context.pop())
        new_context.append(current_context)
    new_context.reverse()
    return new_context


def pppfcs16(fcs, p, length):
    fcstab = (
        0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
        0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
        0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
        0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
        0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
        0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
        0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
        0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
        0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
        0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
        0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
        0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
        0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
        0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
        0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
        0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
        0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
        0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
        0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
        0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
        0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
        0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
        0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
        0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
        0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
        0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
        0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
        0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
        0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
        0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
        0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
        0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78)
    i = 0
    while length:
        length -= 1
        fcs = (fcs >> 8) ^ fcstab[(fcs ^ ord(p[i])) & 0xff]
        i += 1
    return fcs ^ 0xffff


def list2str(message):
    text = ''
    i = 0
    lenth = len(message)
    while lenth > 0:
        text = text + message[i]
        i += 1
        lenth -= 1
    return text


def dec2bin(num):
    l = []
    if num < 0:
        return '-' + dec2bin(abs(num))
    while True:
        num, remainder = divmod(num, 2)
        l.append(str(remainder))
        if num == 0:
            return ''.join(l[::-1])


def BuildMessage(APDU, SA_address, stat):
    if SA_address == '':
        message_full = '0'
    else:
        C = '43'
        if stat == 'zu':
            SA_sign = '8'
        else:
            SA_sign = '0'
        CA = '00'
        APDUlist = makelist(APDU)
        SA_address_nospace = list2str(SA_address)
        lenth = int(dec2bin(len(SA_address)), 2)
        SA_sign = SA_sign + str(lenth - 1)
        Total_length = hex(5 + lenth + 3 + len(APDUlist) + 3 - 2)[2:].zfill(4)
        lenth1 = Total_length[2:]
        lenth2 = Total_length[0:2]
        print('Comm line:126', lenth1, lenth2, C, SA_sign, SA_address_nospace, CA)
        Head = strto0x(makelist(lenth1 + lenth2 + C + SA_sign + SA_address_nospace + CA))
        HCS = str(hex(pppfcs16(0xffff, Head, len(Head)))).zfill(4)[2:]
        if len(HCS) == 3:
            HCS = '0' + HCS
        HCS = HCS[2:] + HCS[0:2]
        message = strto0x(makelist(lenth1 + lenth2 + C + SA_sign + SA_address_nospace + CA + HCS + APDU))
        FCS = hex(pppfcs16(0xffff, message, len(message))).zfill(4)[2:]
        if len(FCS) == 3:
            FCS = '0' + FCS
        FCS = FCS[2:] + FCS[0:2]
        message_full = '68' + lenth1 + lenth2 + C + SA_sign + SA_address_nospace + CA + HCS + APDU + FCS + '16'
        print('组成报文:', message_full)
    return message_full


class Analysis:
    def IsRight(self, num, code):
        code = makelist(code)
        while 1:
            if code[0] == '68':
                break
            else:
                del code[0]

    def start698(self, code):
        self.code = self.clear(makelist(code))
        if self.code == 'ERROR':
            print('star698,ERROR')
        else:
            lenth = int(self.code[2] + self.code[1], 16)  # exception 68 16
            ctrlcode = self.ctrlc_1(dec2bin(int(self.code[3], 16)).zfill(2))
            code_remain = self.code[4:]
            # if ctrlcode == 3:
            SA_len_num = self.SASign(dec2bin(int(code_remain[0], 16)).zfill(8))
            self.SA_len = code_remain[1:1 + SA_len_num]
            global SA_add
            SA_add = self.SA_len
            CA = code_remain[1 + SA_len_num:][0]
            HCS = code_remain[1 + SA_len_num:][1] + code_remain[1 + SA_len_num:][2]
            APDU = code_remain[1 + SA_len_num:][3:-3]
            print(APDU)

    def clear(self, code):
        while 1:
            if not code:
                code = 'ERROR'
                break
            if code[0] == '68':
                break
            else:
                del code[0]

        return code

    def ctrlc_1(self, num):
        if num[0] == '0' and num[1] == '0':
            # print(num, 'DIR=0 PRM=0 客户机对服务器上报的响应')
            return 0
        elif num[0] == '0' and num[1] == '1':
            # print(num, 'DIR=0 PRM=1 客户机发起请求')
            return 1
        elif num[0] == '1' and num[1] == '0':
            # print(num, 'DIR=1 PRM=0 服务器发起上报')
            return 2
        else:
            # print(num, 'DIR=1 PRM=1 服务器对客户机请求的响应')
            return 3

    def SASign(self, num):
        numadd = int(str(num[0] + num[1]), 2)
        if numadd == 0:
            # print('0 单地址')
            pass
        elif numadd == 1:
            # print('1 通配地址')
            pass
        elif numadd == 2:
            print('2 组地址')
        else:
            print('3 广播地址')
        # print(' 逻辑地址: ', num[2], num[3])
        numadd1 = int(num[4:], base=2)
        # print('地址长度 N: ', numadd1+1)
        return numadd1 + 1


def SetSA(SA):
    global SA_add
    SA_add = SA


SA_add = ''

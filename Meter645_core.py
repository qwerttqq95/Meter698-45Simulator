'''
    645模拟表程序
'''
import Comm, binascii, re, serial, time, datetime, configparser, traceback

black_white_SA_address = ''
black = []
white = []
address = []
stat = 0


def Electricity_meter_date_and_week_and_time(data):
    if data == '@GetDateWeek@':
        time1_str = datetime.datetime.now().strftime('%y%m%d%w')
        if len(time1_str) == 7:
            time1_str = time1_str[0:6] + '0' + time1_str[-1]
        return time1_str
    elif data == '@GetTime@':
        time2_str = datetime.datetime.now().strftime('%T').replace(':', '')
        return time2_str
    elif data == '@FreezeTime@':
        # time3_str = datetime.datetime.now().strftime('%M%H%d%m%y').replace(':', '')
        time3_str = datetime.datetime.now().strftime('%y%m%d0000')
        return time3_str
    else:
        print('Electricity_meter_date_and_week_and_time not found!')


def conctrlcode(code):
    if code == '11':
        recode = int(code, 16) + 128
        recode = hex(recode)[2:]
        return recode
    if code == "14":
        return "94"


def data_len(code):
    m = hex(int(code, 16) - 4)[2]
    if m == '0':
        return m
    if m == '1':
        pass
    if m == '6':
        return m


def strto0x(context):  # list
    context = [int(x, 16) for x in context]
    new_context = []
    while context:
        current_context = chr(context.pop())
        new_context.append(current_context)
    new_context.reverse()
    return new_context


def CS(list, b):
    sum = 0
    while list:
        sum = sum + ord(list.pop())
    sum = hex(sum & 0xff)[2:]
    if len(sum) == 1:
        sum = "0" + sum
    try:
        if sum == b.lower():
            pass
    except:
        if b is None:
            pass
        else:
            print('校验错误')
    return sum


def readdata(OI):
    conf_new = configparser.ConfigParser()
    conf_new.read('config.ini', encoding='utf-8')
    try:
        get = conf_new.get('MeterData645', OI)
        get = get.split(' ')
        text = [OI, get[0], get[1]]
        print("事件", text)
        # data = (text[-1]).replace(',', '')
        data = text[-1]
        name = text[-2]
        if data[0] == '@':
            data_time = Electricity_meter_date_and_week_and_time(data)
            print('数据标识及时间', name, datetime.datetime.now().strftime('%T'))
            return data_time, name
        print('数据标识及时间:', name, datetime.datetime.now().strftime('%T'))
        print('readdata ', data, name)
        return data, name

    except:
        print('未知数据标识: ', OI)
        if OI[0].upper() == 'X' or OI.__len__() != 8:
            return None
        # else:
        #     traceback.print_exc(file=open('bug.txt', 'a+'))
    return None


def plus33(message):
    newstr = ''
    if message is None:
        print('plus33 is none')
    else:
        if re.findall(',', message):
            # line
            message = message.split(',')
            lenth = len(message)
            i = 0
            while lenth:
                new_list = []
                lenth -= 1
                returnvalue = Comm.makelist(message[i])
                i += 1
                while returnvalue:
                    new_list.append(hex(int(returnvalue.pop(), 16) + 51)[2:])
                value_str = Comm.list2str(new_list)
                newstr = newstr + value_str
        else:
            message = Comm.makelist(message)
            lenth = len(message)
            new_list = []
            while lenth:
                lenth -= 1
                new_list.append(hex(int(message.pop(), 16) + 51)[2:])
            newstr = Comm.list2str(new_list)
        return newstr


def minus33(list):
    new_list = []
    while list:
        middle = hex(int(list.pop(), 16) - 51)[2:]
        if len(middle) == 1:
            middle = '0' + middle
        if middle == 'x1':
            middle = 'FF'
        new_list.append(middle)
    return new_list


def returnframe(add, reconctrlcode, L, D, N):
    text = '68' + add + '68' + reconctrlcode + L + D + N
    cs = CS(strto0x(Comm.makelist(text)), None)
    text = text + cs + '16'
    return text


def B_W_add(stat_, add):
    global black_white_SA_address, black, white, stat
    stat = stat_
    print('changed stat',stat)
    if stat == 0:
        black = []
        white = []
    elif stat == 1:
        black_white_SA_address = add.replace(' ', '')
        black_white_SA_address = black_white_SA_address.split('/')
        black = black_white_SA_address
    elif stat == 2:
        black_white_SA_address = add.replace(' ', '')
        black_white_SA_address = black_white_SA_address.split('/')
        white = black_white_SA_address


def deal_receive(message):
    # if message[8] == "13":
    #     text = "68 01 00 00 00 00 00 68 93 06 34 33 33 33 33 33 9D 16".replace(' ', '')
    #     return (text, '0', '0')
    while 1:
        if message[0] == '68':
            global address,white,stat
            address = message[1:7]
            if address == ['aa', 'aa', 'aa', 'aa', 'aa', 'aa'] or address == ['99', '99', '99', '99', '99', '99']:
                if stat != 2:
                    return '2'
                reconctrlcode = '93'
                L = '06'
                D = '343333333333'
                add = Comm.makelist(white[0])[::-1]
                text = '68' + Comm.list2str(add) + '68' + reconctrlcode + L + D
                cs = CS(strto0x(Comm.makelist(text)), None)
                text = text + cs + '16'
                print("返回发送",text)
                return (text,"645广播")
            for x in address:
                if x.find('a') > -1:
                    print('find a re None')
                    return None
            # insert
            print("stat ",stat)
            if stat == 1:
                for add in black:
                    print('add: ', add)
                    if add.find('-') > 0:
                        add_range = add.split('-')
                        start = int(add_range[0])
                        end = int(add_range[1])
                        print("start: ", start, "end: ", end)
                        if start <= int(Comm.list2str(address[::-1])) <= end:
                            print('检测到黑名单地址范围')
                            return None
            elif stat == 2:
                num = 0
                for add in white:
                    print('add: ', add)
                    if add.find('-') > 0:
                        add_range = add.split('-')
                        start = int(add_range[0])
                        end = int(add_range[1])
                        print("start: ", start, "end: ", end)
                        if start <= int(Comm.list2str(address[::-1])) <= end:
                            print('检测到白名单地址范围')
                            num = -1
                            break
                        else:
                            num = 1
                    elif add == Comm.list2str(address[::-1]):
                        print('发现白名单')
                        break
                    else:
                        num = 1
                print("白名单判断 ", Comm.list2str(address[::-1]))
                if num != 1:
                    print('通过')
                else:
                    print('不通过')
                    return None
            break
        else:
            del message[0]

    reconctrlcode = conctrlcode(message[8])
    if reconctrlcode == "94":
        returnstr = ''
        L = ''
        reconctrlcode = '9400'
        D = ''
        text = returnframe(Comm.list2str(address), reconctrlcode, L, D, returnstr)
        print('Sending:', text)
        return (text,'SET', 'TRUE')
    datasign = message[10:14]
    D = Comm.list2str(datasign)
    cs = CS(strto0x(message[0:-2]), message[-2])
    OI = Comm.list2str(minus33(datasign)).upper()
    a = readdata(OI)
    if not a:
        print('OI 无法解析: ', OI)
        returnstr = ''
        reconctrlcode = 'D100'
        L = ''
        D = ''
        text = returnframe(Comm.list2str(address), reconctrlcode, L, D, returnstr)
        if OI[0].upper() == 'X':
            return (text, '无法解析')
        else:
            return (text, '无法解析:', OI)
    else:
        # if re.match("0201FF00", OI):
        #     returnstr = "3232" + "3232" * 2;

        if re.match("0610", OI):
            TIME = Comm.list2str(message[15:20])
            print("time:", TIME, message[14])
            times = int(hex(int(message[14], 16) - 51)[2:].zfill(2))
            print("times:", times)
            returnstr = TIME + plus33(a[0]) * times
        else:
            returnstr = plus33(a[0])  # Date!!!!
        L = hex(4 + len(Comm.makelist(returnstr)))[2:].zfill(2)
        print("长度:",hex(4 + len(Comm.makelist(returnstr)))[2:])
        text = returnframe(Comm.list2str(address), reconctrlcode, L, D, returnstr)
        print('Sending:', text)
    return (text, OI + " " + a[1], a[0])

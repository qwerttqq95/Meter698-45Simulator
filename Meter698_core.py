import Comm, time, traceback, configparser, random, Meter645_core, re


def Re_priority(data, fulltext_list):
    """

    :type fulltext_list: list
    """
    list_ = fulltext_list.copy()
    code = Comm.makelist(data)
    re_ = check(code)
    if re_ == 0:
        print("re=0")
        SA_add = code[5:11]
        print("SA_add ", SA_add)
        print("fulltext_list ", list_)
        print("code", code)
        i = 5
        for x in range(6):  # 换地址
            list_[i] = code[i]
            i += 1
        while 1:
            if list_[-1] != "16":
                if list_.__len__() == 1:
                    return "EE"
                list_.pop()

            else:
                break
        if list_.__len__() < 15:
            return "FF"
        list_.pop()  # 去掉检验
        list_.pop()
        list_.pop()

        head_message = Comm.strto0x(list_[1:12])
        HCS = str(hex(Comm.pppfcs16(0xffff, head_message, len(head_message)))).zfill(4)[2:]
        HCS.replace("x", "")
        if len(HCS) == 3:
            HCS = '0' + HCS
        HCS = HCS[2:] + HCS[0:2]
        if len(HCS) == 2:
            HCS = HCS + '00'
        print("HCS: ", HCS)
        HCS_list = Comm.makestr(HCS).split(" ")
        list_[12] = HCS_list[0]
        list_[13] = HCS_list[1]

        full_message = Comm.strto0x(list_[1:])
        FCS = str(hex(Comm.pppfcs16(0xffff, full_message, len(full_message)))).zfill(4)[2:]
        if len(FCS) == 3:
            FCS = '0' + FCS
        FCS = FCS[2:] + FCS[0:2]
        if len(FCS) == 2:
            FCS = FCS + '00'
        if FCS[0] == "x":
            FCS = '0' + FCS[1:]
        print("FCS: ", FCS)
        x = Comm.list2str(list_).replace("\n", "") + FCS + "16"
        return x

    print("645 pri")
    return "FFEE"


def check(code):
    if len(code) < 20:
        print('不符合698长度', code)
        return 1
    lenth = int(code[2] + code[1], 16)  # 长度
    if len(code) >= lenth + 2:
        if code[lenth + 1] == '16':
            full_message = Comm.strto0x(code[1:lenth - 1])
            FCS_calc = str(hex(Comm.pppfcs16(0xffff, full_message, len(full_message)))).zfill(4)[2:]
            if len(FCS_calc) == 3:
                FCS_calc = '0' + FCS_calc
            FCS_calc = FCS_calc[2:] + FCS_calc[0:2]
            if len(FCS_calc) == 2:
                FCS_calc = FCS_calc + '00'
            if FCS_calc[0] == "x":
                FCS_calc = '0' + FCS_calc[1:]
            print("FCS_calc: ", FCS_calc)
            FCS_rec = code[lenth - 1] + code[lenth]
            print("FCS_rec: ", FCS_rec)
            if FCS_calc == FCS_rec:
                print('check granted')
                return 0
            else:
                print("校验错误")
                return 1
        else:
            print('lenth check denied')
            return 1
    else:
        print('698 check denied')
        return 1


def B_W_add(stat, add):
    global black_white_SA_address, black, white, b_w_stat
    if stat == 0:
        b_w_stat = 0
        black = []
        white = []
    elif stat == 1:
        b_w_stat = 1
        black_white_SA_address = add.replace(' ', '')
        black_white_SA_address = black_white_SA_address.split('/')
        black = black_white_SA_address
    elif stat == 2:
        b_w_stat = 2
        black_white_SA_address = add.replace(' ', '')
        black_white_SA_address_list = black_white_SA_address.split('/')
        white = black_white_SA_address_list
    print('B_W_add:', black_white_SA_address)
    Meter645_core.B_W_add(stat, add)


def Wild_match_Analysis(code):
    code = Comm.makelist(code)
    re_ = check(code)
    print('Wild_match_Analysis: ', re_)
    if re_ == 0:
        lenth = SASign(Comm.dec2bin(int(code[4], 16)).zfill(8))
        wild_a_full = 'aa' * lenth
        add_wild = Comm.list2str(code[5:5 + lenth])
        global SA_num
        if SA_num == 1 and wild_a_full == add_wild:
            return 0
        else:
            return 1
    else:
        return 1


def Analysis(code):
    if code.find("21300202") != -1 or code.find("21300200") != -1 or code.find("21300201") != -1:
        print("111111111111")
        return 2
    code = Comm.makelist(code)
    re_ = check(code)
    if re_ == 0:
        try:
            ctrlc_1(Comm.dec2bin(int(code[3], 16)))  # 控制码
        except:
            print("控制码错误")

        code_remain = code[4:]
        SA_len_num = SASign(Comm.dec2bin(int(code_remain[0], 16)).zfill(8))
        if SA_len_num == 0:
            return 1
        global SA_num_len, LargeOAD, relen, data, data_list, frozenSign, b_w_stat, black, white, curve_list, Curve_gaps_times_multi, OI_list_re, count_re, Recive_add
        Curve_gaps_times_multi = 0
        OI_list_re = [" "]
        relen = 0
        LargeOAD = ''
        data = ''
        data_list = []
        curve_list = []
        frozenSign = 0
        count_re = 1
        SA_num_len = code_remain[0:1 + SA_len_num]
        print('SA_num_len:', SA_num_len)

        Recive_add = Comm.list2str(SA_num_len[::-1][0:SA_len_num])  # 收到报文的地址
        print('Recive_add', Recive_add)

        if b_w_stat == 0 and Recive_add.find('a') > -1:
            print("blocked")
            return 3
        if Recive_add.find('a') == -1:
            if b_w_stat == 1:
                for add in black:
                    print('add: ', add)
                    if add.find('-') > 0:
                        add_range = add.split('-')
                        start = int(add_range[0])
                        end = int(add_range[1])
                        print("start: ", start, "end: ", end)
                        if start <= int(Recive_add) <= end:
                            print('检测到黑名单地址范围')
                            return 1
                        else:
                            continue
                    elif add == Recive_add:
                        return 1
            elif b_w_stat == 2:
                num = 0
                for add in white:
                    print('add: ', add)
                    if add.find('-') > 0:
                        add_range = add.split('-')
                        start = int(add_range[0])
                        end = int(add_range[1])
                        print("start: ", start, "end: ", end)
                        if start <= int(Recive_add) <= end:
                            print('检测到白名单地址范围')
                            num = -1
                            break
                        else:
                            num = 1
                    elif add == Recive_add:
                        print('发现白名单')
                        num = -1
                        break
                    else:
                        num = 1
                print("白名单判断 ", Recive_add, num)
                if num != 1:
                    print('通过')
                else:
                    print('不通过')
                    return 1
        else:
            print("find a")
            global match_add
            if Recive_add != 'aaaaaaaaaaaa':
                if b_w_stat == 2:
                    whitelist = []
                    find_aa = 0
                    match = 0
                    black_white_SA_address_makelist = Comm.makelist(Recive_add)
                    for x in range(6):
                        if black_white_SA_address_makelist[x] == 'aa':
                            find_aa += 1
                    black_white_SA_address_makelist_int = int(Comm.list2str(black_white_SA_address_makelist[find_aa:]))
                    for add in white:
                        print('add: ', add)
                        if add.find('-') > 0:
                            add_range = add.split('-')
                            start = int(add_range[0])
                            end = int(add_range[1])
                            print("start: ", start, "end: ", end)
                            while start <= end:
                                whitelist.append(start)
                                start += 1
                            print("whitelist: ", whitelist)
                            for x in whitelist:
                                x_makelist = int(Comm.list2str(Comm.makelist(str(x).zfill(12))[find_aa:]))
                                print('matching', black_white_SA_address_makelist_int, x_makelist)
                                if black_white_SA_address_makelist_int == x_makelist:
                                    match = 1
                                    match_add = x
                                    print('match', x)
                                    break
                            if match == 0:
                                return 1
                        else:
                            for x in white:
                                x_makelist = int(Comm.list2str(Comm.makelist(str(x))[find_aa:]))
                                print('matching', black_white_SA_address_makelist_int, x_makelist)
                                if black_white_SA_address_makelist_int == x_makelist:
                                    print('match')
                                    match = 1
                                    match_add = x
                                    break
                            if match == 0:
                                return 1

                else:
                    print("blocked")
                    return 1
            else:
                global trans
                if white[0].find('-') > 0:
                    add_1 = white[0].split('-')
                    trans = add_1[0]
                    match_add = trans
                else:
                    trans = white[0]
                    match_add = trans
        CA = code_remain[1 + SA_len_num:][0]
        HCS = code_remain[1 + SA_len_num:][1] + code_remain[1 + SA_len_num:][2]
        APDU = code_remain[1 + SA_len_num:][3:-3]
        if Information(APDU[0], APDU[1], APDU[2:]) is None:
            print("198")
            return 1
        s = LargeOAD
        LargeOAD = ''
        data_list = []
        data = ''
        relen = 0
        frozenSign = 0
        return s
    else:
        print('非698,尝试645')
        Meter645_core.plus_one = plus_645
        text = Meter645_core.deal_receive(code)
        if text is None:
            print('645解析失败')
            return 1
        if text[0] == '2':
            return 3
        global OI
        OI = text[1:]
        Recive_add = Comm.list2str(Meter645_core.address[::-1])
        return text[0]


def Information(num, detail, APDU):
    global service_code, LargeOAD, GetRequestNormal_0501, relen
    service_code = APDU[0]
    if num == '01':
        print(num, '预链接请求')
    elif num == '81':
        print(num, '预链接响应')
    elif num == '02':
        print(num, '应用链接请求')
    elif num == '82':
        print(num, '应用链接响应')
    elif num == '03':
        print(num, '断开链接响应')
    elif num == '83':
        print(num, '断开链接请求')
    elif num == '05':
        print(num, '读取请求', end=' ')
        if detail == '01':
            print(detail, '读取一个对象属性请求(GetRequestNormal) ')
            GetRequestNormal_0501 = 1
            returnvalue = A_ResultRecord_SEQUENCE(APDU[1:5])
            if returnvalue == 0:
                print('0501抄事件')  # 3320
                # LargeOAD = '850100' + Comm.list2str(
                #     APDU[1:5]) + '01 01 04 51 30 1b 02 00 51 30 2a 02 00 51 30 13 02 00 51 30 11 02 00 00 00'.replace(
                #     ' ', '')
                if APDU[1:5] == ["33", "20", "02", "00"]:
                    global apdu_3320
                    LargeOAD = apdu_3320
                    print('0501抄事件', LargeOAD)
                    st = [Comm.list2str(APDU[1:5]), '事件特殊处理', '']
                    global OI  # 屏幕显示
                    OI = OI + st[0:2]
            else:
                LargeOAD = LargeOAD + '0000'
                ReturnMessage().reAPDUtype(num + detail + service_code)
            ReturnMessage().head()
            GetRequestNormal_0501 = 0

        elif detail == '02':
            print(detail, '读取若干个对象属性请求 (GetRequestNormalList) ')
            if SequenceOfLen(APDU[1:]) is None:
                print("读取若干个对象属性请求 None")
                return None
            LargeOAD = LargeOAD + '0000'
            ReturnMessage().reAPDUtype(num + detail + service_code)
            ReturnMessage().head()
            print('返回项数量', relen)

        elif detail == '03':
            print(detail, '读取一个记录型对象属性请求 (GetRequestRecord) ')
            returnvalue = A_ResultRecord_SEQUENCE(APDU[1:5])
            if returnvalue is None:
                print("读取一个记录型对象属性请求 None")
                return None
            global frozenSign, data_list
            if returnvalue == 0:
                print('抄事件')
                if Event(APDU[1:]) is None:
                    print("抄事件 None")
                    return None
                return 0
            if returnvalue == '5002':
                frozenSign = 1
            if returnvalue == '5004':
                frozenSign = 2
            if returnvalue == '5006':
                frozenSign = 3
            if returnvalue == '5032':
                frozenSign = 4
            if returnvalue == '5005':
                frozenSign = 5
            reCSD = RSD(APDU[5:])
            if reCSD is None:
                return 0
            if RCSD(reCSD[0], reCSD[1:]) is None:
                print("RCSD is None")
                return None
            # print('LargeOAD-1', LargeOAD)
            # print('返回项数量', relen)
            datatype = num + detail + service_code
            datatype = '8' + datatype[1:]
            datatype = datatype.replace(' ', '')
            global from_to_sign, from_to, hour_, minute_
            print('from_to_sign', from_to_sign)
            if from_to_sign == 1:
                print('from_to', from_to)
                no_timme = int(hour_) * 60 + int(minute_)
                print('no_timme', no_timme)
                if from_to[0] < no_timme < from_to[1]:
                    print('pass the times')
                    LargeOAD = datatype + str(returnvalue) + '0200' + hex(relen)[2:].zfill(2) + LargeOAD + '01000000'
                else:
                    LargeOAD = str(returnvalue) + '0200' + hex(relen)[2:].zfill(2) + LargeOAD + '0101'
                    LargeOAD = datatype + LargeOAD + Comm.list_append(data_list) + '0000'

            else:
                global Curve_gaps_times, count_re, OI_list_re
                relen = OI_list_re.__len__() - 1
                print("ReturnIsNULL ",ReturnIsNULL)
                if ReturnIsNULL:
                    LargeOAD = datatype+str(returnvalue) + '0200' + hex(relen)[2:].zfill(2) + LargeOAD + "01000000"
                else:
                    LargeOAD = str(returnvalue) + '0200' + hex(relen)[2:].zfill(2) + LargeOAD + '01' + str(count_re).zfill(
                        2)
                    # print('data_list', data_list)

                    LargeOAD = datatype + LargeOAD + Comm.list_append(data_list) + '0000'

            ReturnMessage().head()
            # print('data_list', Comm.list_append(data_list))
            # print('组成', LargeOAD)

        elif detail == '04':
            print(detail, '读取若干个记录型对象属性请求 (GetRequestRecordList) ')
        elif detail == '05':
            print(detail, '读取分帧响应的下一个数据块请求 (GetRequestNext) ')
        elif detail == '06':
            print(detail, '读取一个对象属性的 MD5 值 (GetRequestMD5) ')
        else:
            print('ERROR:05??')
    elif num == '85':
        if detail == '01':
            print(detail, '读取一个对象属性的响应(GetResponseNormal) ')
        elif detail == '02':
            print(detail, '读取若干个对象属性的响应 (GetResponseNormalList) ')
        elif detail == '03':
            print(detail, '读取一个记录型对象属性的响应 (GetResponseRecord) ')
        elif detail == '04':
            print(detail, '读取若干个记录型对象属性的响应 (GetResponseRecordList) ')
        elif detail == '05':
            print(detail, '分帧响应一个数据块 (GetResponseNext) ')
        elif detail == '06':
            print(detail, '读取一个对象属性的 MD5 值的响应 (GetResponseMD5) ')
        else:
            print('ERROR:85??')
    elif num == '06':
        print(num, '设置请求')
        return None
    elif num == '86':
        print(num, '设置响应')
    elif num == '07':
        print(num, '操作请求')
        return None
    elif num == '87':
        print(num, '操作响应')
    elif num == '08':
        print(num, '上报回应')
    elif num == '88':
        print(num, '上报请求')
    elif num == '10':
        print(num, '安全请求', end=' ')
        if detail == '00':
            print('解析明文')
            seclen = int(APDU[0], 16)
            realAPDU = APDU[1:seclen + 1]
            left = APDU[seclen + 1:]
            global SecType
            SecType = left[0]
            if SecType == '01':
                global mac
                if mac == 1:
                    pass
                else:
                    SecType = '00'

                if Information(realAPDU[0], realAPDU[1], realAPDU[2:]) is None:
                    print("Information None")
                    return None

            else:
                print('非随机数无法读取')
        if detail == '01':
            print('密文无法读取!!')
    return 0


def SequenceOfLen(remain):
    global LargeOAD, relen
    lenth = int(remain[0], 16)
    remain = remain[1:]
    while lenth > 0:
        returnvalue = A_ResultRecord_SEQUENCE(remain[0:4])
        if returnvalue is None:
            print('returnvalue is None2')
            return None
        if returnvalue == 0:
            print('0502抄事件临时处理')
            ReturnMessage().save(['事件响应', Comm.list2str(remain[0:4]), ''])
            LargeOAD = Comm.list2str(remain[0:4]) + '0100'
            relen += 1

        remain = remain[4:]
        lenth -= 1
    return 1


def A_ResultRecord_SEQUENCE(remain):
    OAD = str(remain[0] + remain[1])
    print("oad: " + OAD)
    if OAD == '5004' or OAD == '5002' or OAD == '5006' or OAD == '5005':
        print('冻结')
        return OAD
    if OAD == '5032':
        print('直流冻结')
        return OAD
    if OAD[0] == '3':
        return 0
    else:
        if OAD_SEQUENCE(OAD, remain[2], remain[3]) is None:
            print("OAD_SEQUENCE is None")
            return None
        else:
            return 1


def Event(APDU):
    global LargeOAD
    '''Selector'''
    message = '850300' + Comm.list2str(APDU[0:4])
    if APDU[4] == '09':
        print('事件响应', Comm.list2str(APDU[0:4]))
        ReturnMessage().save(['事件响应', Comm.list2str(APDU[0:4]), ''])
        last_n = APDU[5]
        RCSD_len = int(APDU[6], 16)
        message = message + APDU[6]
        remain = APDU[7:]
        while RCSD_len:
            RCSD_len -= 1
            message = message + Comm.list2str(remain[0:5])
            value = Comm.list2str(remain[1:5]).zfill(4)
            if event_compose_data(value) is None:
                print("event_compose_data None")
                return None
            remain = remain[5:]
        global event_stat
        print("event_stat:", event_stat)
        if event_stat == 0:
            LargeOAD = message + '0101' + LargeOAD + '0000'
        elif event_stat == 2:
            LargeOAD = message + '01000000'
        else:
            stat = 0
            global event_blacklist
            print("event_blacklist:", event_blacklist)
            print("Comm.list2str(APDU[0:4]):", Comm.list2str(APDU[0:4]))
            for x in event_blacklist:
                if x == Comm.list2str(APDU[0:4]):
                    print("x:", x)
                    print("Comm.list2str(APDU[0:4]):", Comm.list2str(APDU[0:4]))
                    LargeOAD = message + '01000000'
                    stat = 1
                    break
            if stat == 0:
                LargeOAD = message + '0101' + LargeOAD + '0000'

        ReturnMessage().head()
        # print('组成', LargeOAD)
        return 1
    else:
        print('其他')
        return 0


def event_compose_data(OI):
    conf_new = configparser.ConfigParser()
    conf_new.read('config.ini', encoding='utf-8')
    try:
        get = conf_new.get('MeterData698', OI)
        get = get.split(' ')
        text = [OI, get[0], get[1]]
        print("事件", text)
        global LargeOAD
        LargeOAD = LargeOAD + text[2]
        return 0
    except:
        print('未知数据标识: ', OI)
        traceback.print_exc(file=open('bug.txt', 'a+'))
        return None


def A_ResultRecord_SEQUENCE_RSD(remain):
    try:
        OI = remain[0] + remain[1]
        unsigned11 = Comm.dec2bin(int(remain[2])).zfill(8)  # 特征值
        unsigned11 = int(unsigned11[0:4], 10)
        print(OI + remain[2] + remain[3], end='\n')
    except:
        traceback.print_exc(file=open('bug.txt', 'a+'))


def RSD(remain):
    global relen, sele, count_re, curve_list,Curve_gaps_times
    if remain[0] == '01':
        sele = 1
        print('Selector 01')
        A_ResultRecord_SEQUENCE_RSD(remain[1:5])
        reMessage = Data(remain[5], remain[6:])  # 收到的冻结时间
        relen = 0
        return reMessage
    if remain[0] == '02':
        sele = 2
        print('Selector 02')
        A_ResultRecord_SEQUENCE_RSD(remain[1:5])
        reMessage1 = Data(remain[5], remain[6:])
        Data(reMessage1[0], reMessage1[1:])
        reMessage2 = Data(reMessage1[8], reMessage1[9:])  # 收到的冻结时间
        try:
            count_re = Comm.time_cacl(curve_list[1], curve_list[0], Curve_gaps_times)
        except:
            print("Curve_gaps_times is None")
            return None
        print("count_re:", count_re)
        relen = 0
        return reMessage2
    if remain[0] == '09':
        sele = 9
        print('Selector 09')
        return remain[2:]
    else:
        print('Selector ERROR: ', remain[0])


def RCSD(remain_len, args):
    lens = int(remain_len, 16)
    print('lens', lens)
    backup_args = args
    backup_len = lens
    global count_re
    print("count_re rcsd:", count_re)
    for x in range(count_re):
        args = backup_args
        lens = backup_len
        while lens > 0:
            args = CSD_CHOICE(args)
            if args is None:
                print("arg is None")
                return None
            lens -= 1
    return args


def CSD_CHOICE(args):
    type = args[0]
    if type == '00':
        OAD = str(args[1] + args[2])
        if OAD_SEQUENCE(OAD, args[3], args[4]) is None:
            print("OAD_SEQUENCE(OAD, args[3], args[4]) is None")
            return None
        if args == []:
            print('CSD_CHOICE is NULL')
        return args[5:]
    elif type == '01':
        value = ROAD(args[1:])
        if value == []:
            print('CSD_CHOICE is NULL')
        return value
    else:
        print('ERRORS:CSD_CHOICE')


def ROAD(args):
    pass


def OAD_SEQUENCE(OI, unsigned1, unsigned2):
    try:
        # unsigned11 = Comm.dec2bin(int(unsigned1)).zfill(8)  # 特征值
        # unsigned11 = int(unsigned11[0:4], 10)
        # unsigned1 = '属性 ' + unsigned1[1]
        # print('OI, unsigned1', OI, unsigned1)
        value = str(OI).zfill(4) + unsigned1[-1].zfill(2) + str(unsigned2).zfill(2)
        ReturnMessage().sequence_of_len()
        global frozenSign
        if frozenSign != 0:
            ReturnMessage().composefrozen(value.lower())
            return 1
        else:
            if ReturnMessage().compose_data(value.lower()) is None:
                traceback.print_exc(file=open('bug.txt', 'a+'))
                print("ReturnMessage().compose_data(value.lower()) is None")
                return None

            else:
                return 1
    except:
        traceback.print_exc(file=open('bug.txt', 'a+'))
        print("???")
        return None


def Data(DataDescribe, args):
    try:
        DataDescribe = str(int(DataDescribe, 16)).zfill(2)
        if DataDescribe == '00':
            print('NULL', DataDescribe)
            return args

        elif DataDescribe == '01':
            print('array:', DataDescribe, end=' ')
            len1 = int(args[0], 16)
            lenori = len1
            args = args[1:]
            while len1 > 0:
                args = Data(args[0], args[1:])
                len1 -= 1
                print('Data', args)
            return args
        elif DataDescribe == '02':
            print('structure: ', DataDescribe)
            len2 = int(args[0], 16)
            lenori = len2
            args = args[1:]
            print('len:', len2)
            while len2 > 0:
                args = Data(args[0], args[1:])
                len2 -= 1
                print('Data', args)

            return args
        elif DataDescribe == '03':
            print('bool:', DataDescribe)
        elif DataDescribe == '04':
            print('bit-string:', DataDescribe)
            value = Comm.list2str(args[1:3])
            print('value', Comm.list2str(value))
            return args[3:]
        elif DataDescribe == '05':
            print('double-long: ', DataDescribe)
            value = int(args[0] + args[1] + args[2] + args[3], 16)
            if value > 2147483647:
                value = Comm.Inverse_code(bin(value))
                value = int(value, 2) + 1
                value = -value
            print('value', value)
            return args[4:]
        elif DataDescribe == '06':  # 4byte
            print('double-long-unsigned: ', DataDescribe)
            value = int(args[0] + args[1] + args[2] + args[3], 16)
            if value > 2147483647:
                value = Comm.Inverse_code(bin(value))
                value = int(value, 2) + 1
                value = -value
            print('value', value)
            return args[4:]
        elif DataDescribe == '09':
            print('octet-string: ', DataDescribe)
        elif DataDescribe == '10':
            print('visible-string: ', DataDescribe)
        elif DataDescribe == '12':
            print('UTF8-string:', DataDescribe)
        elif DataDescribe == '15':
            print('integer:', DataDescribe)
        elif DataDescribe == '16':
            print('long: ', DataDescribe)
            value = int(args[0] + args[1], 16)
            if value > 32767:
                value = Comm.Inverse_code(bin(value))
                value = int(value, 2) + 1
                value = -value
            print('value', value)
            return args[2:]
        elif DataDescribe == '17':
            print('unsigned:', DataDescribe)
        elif DataDescribe == '18':
            print('long-unsigned:', DataDescribe)
            value = int(args[0] + args[1], 16)
            if value > 32767:
                value = Comm.Inverse_code(bin(value))
                value = int(value, 2) + 1
                value = -value
            print('value', value)
            return args[2:]
        elif DataDescribe == '20':
            print('long64: ', DataDescribe)
        elif DataDescribe == '21':
            print('long64-unsigned', DataDescribe)
        elif DataDescribe == '22':
            print('enum', DataDescribe)
        elif DataDescribe == '23':
            print('float32', DataDescribe)
        elif DataDescribe == '24':
            print('float64', DataDescribe)
        elif DataDescribe == '25':
            print('date_time', DataDescribe)
        elif DataDescribe == '26':
            print('date', DataDescribe)
        elif DataDescribe == '27':
            print('time', DataDescribe)
        elif DataDescribe == '28':
            print('DataDescribe:', DataDescribe, 'date_time_s', end=' ')
            year = int(args[0] + args[1], 16)
            mouth = int(args[2], 16)
            day = int(args[3], 16)
            global hour, hour_, minute, minute_
            hour = int(args[4], 16)
            hour_ = hour
            minute = int(args[5], 16)
            minute_ = minute
            second = int(args[6], 16)
            datatime = str(year) + '年' + str(mouth) + '月' + str(day) + '日' + '   ' + str(hour).zfill(2) + ':' + str(
                minute).zfill(2) + ':' + str(
                second).zfill(2)
            print(datatime)
            global Daily_freeze, curve_list
            Daily_freeze = '1c' + Comm.list2str(args[0:7])  # 冻结返回时间
            curve_list.append(Daily_freeze)
            print('Daily_freeze', Daily_freeze, curve_list)
            global Difference
            Difference = abs(int(time.strftime('%m%d'), 10) - (mouth * 100 + day))

            return args[7:]
        elif DataDescribe == '80':
            print('OAD ', DataDescribe)
        elif DataDescribe == '82':
            print('ROAD ', DataDescribe)
        elif DataDescribe == '83':
            print('OMD ', DataDescribe)
        elif DataDescribe == '84':
            print('TI', DataDescribe)
            timeUnit = int(args[0], 16)
            times = int(args[1] + args[2], 16)
            if timeUnit == 1:
                global Curve_gaps_times
                Curve_gaps_times = 60 * times
                print(times, '分钟')
            return args[3:]
        elif DataDescribe == '85':
            print('TSA', DataDescribe)
            value = args[0:8]
            print('TSA', value)
            return args[8:]
        elif DataDescribe == '86':
            print('MAC', DataDescribe)
        elif DataDescribe == '87':
            print('RN', DataDescribe)
        elif DataDescribe == '88':
            print('Region', DataDescribe)
        elif DataDescribe == '89':
            print('Scaler_Unit ', DataDescribe)
        elif DataDescribe == '90':
            print('RSD', DataDescribe)
        elif DataDescribe == '91':
            print('CSD', DataDescribe)
        elif DataDescribe == '92':
            print('MS', DataDescribe)
        elif DataDescribe == '93':
            print('SID', DataDescribe)
        elif DataDescribe == '94':
            print('SID_MAC', DataDescribe)
        elif DataDescribe == '95':
            print('COMDCB', DataDescribe)
        elif DataDescribe == '96':
            print('RCSD', DataDescribe)
        else:
            print('ERROR on Data')
    except:
        traceback.print_exc(file=open('bug.txt', 'a+'))


def SASign(num):
    global SA_num
    numadd = int(str(num[0] + num[1]), 2)
    if numadd == 0:
        # print('0 单地址')
        SA_num = 0

    elif numadd == 1:
        print('1 通配地址')
        SA_num = 1

    elif numadd == 2:
        print('2 组地址')

    else:
        print('3 广播地址')
        return 0
    # print(' 逻辑地址: ', num[2], num[3])
    numadd1 = int(num[4:], base=2)
    print('地址长度 N: ', numadd1 + 1)
    return numadd1 + 1


def ctrlc_1(num):
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


def SequenceOf_ARecordRow(data):
    global data_list
    data_list.append(data)


class ReturnMessage():
    def __init__(self):
        self.conf_new = configparser.ConfigParser()
        self.conf_new.read('config.ini', encoding='utf-8')

    def head(self):
        global SA_num, match_add
        self.ctrlzone = 'c3'
        self.add = Comm.list2str(SA_num_len)
        if SA_num == 0:
            if self.add.find('a') > -1:
                self.add = '05' + Comm.list2str(Comm.makelist(str(match_add))[::-1])
                print('add1', self.add)
        elif SA_num == 1:
            if self.add.find('a') == -1:
                pass
            else:
                self.add = '05' + Comm.list2str(Comm.makelist(str(match_add))[::-1])
            print('add2', self.add)
        self.CA = '00'
        self.totallenth()

    def totallenth(self):
        print("self.ctrlzone , self.add , self.CA:", self.ctrlzone, self.add, self.CA)
        self.total = self.ctrlzone + self.add + self.CA
        global LargeOAD, SecType
        print('完整的APDU ', LargeOAD)
        print('SecType', SecType)
        if SecType == '01':
            sec_len = len(LargeOAD) // 2
            print('sec_len1:', sec_len)
            if sec_len > 127:
                if sec_len < 255:
                    sec_len = '81' + hex(len(LargeOAD) // 2)[2:]
                elif sec_len > 255 and sec_len < 65535:
                    sec_len = '82' + hex(len(LargeOAD) // 2)[2:].zfill(4)
            else:
                sec_len = hex(len(LargeOAD) // 2)[2:].zfill(2)
            print('sec_len2:', sec_len)
            LargeOAD = '9000' + sec_len + LargeOAD + '0100040a0b0c0d'
            SecType == '00'
            print('完整的APDU加MAC ', LargeOAD)
        APDU_len = hex(len(Comm.makelist(LargeOAD)) + 6 + len(Comm.makelist(self.total)))[2:].zfill(4)
        print('总长（不包括头和尾）', APDU_len)

        self.head_message = Comm.strto0x(Comm.makelist(APDU_len[2:] + APDU_len[0:2] + self.total))
        self.HCS = str(hex(Comm.pppfcs16(0xffff, self.head_message, len(self.head_message)))).zfill(4)[2:]
        self.HCS = self.HCS.replace("x", "")
        if len(self.HCS) == 3:
            self.HCS = '0' + self.HCS
        if len(self.HCS) == 2:
            self.HCS = '00' + self.HCS
        if len(self.HCS) == 1:
            self.HCS = '000' + self.HCS

        self.HCS = self.HCS[2:] + self.HCS[0:2]
        if len(self.HCS) == 2:
            self.HCS = self.HCS + '00'
        print("HCS: ", self.HCS)
        LargeOAD = APDU_len[2:] + APDU_len[0:2] + self.total + self.HCS + LargeOAD
        self.full_message = Comm.strto0x(Comm.makelist(LargeOAD))
        self.FCS = str(hex(Comm.pppfcs16(0xffff, self.full_message, len(self.full_message)))).zfill(4)[2:]
        self.FCS = self.FCS.replace("x", "")
        if len(self.FCS) == 3:
            self.FCS = '0' + self.FCS
        if len(self.FCS) == 2:
            self.FCS = '00' + self.FCS
        if len(self.FCS) == 1:
            self.FCS = '000' + self.FCS
        self.FCS = self.FCS[2:] + self.FCS[0:2]
        if len(self.FCS) == 2:
            self.FCS = self.FCS + '00'
        if self.FCS[0] == "x":
            self.FCS = '0' + self.FCS[1:]
        print("FCS: ", self.FCS)
        LargeOAD = '68' + LargeOAD + self.FCS + '16'
        if LargeOAD.__len__() % 2 != 0:
            print("发送报文: ERROR")
        print('发送报文:', LargeOAD, '\n')

    def Full_LargeOAD(self):
        global LargeOAD
        return LargeOAD

    def reAPDUtype(self, datatype):
        datatype = '8' + datatype[1:]
        self.datatype = datatype.replace(' ', '')
        global LargeOAD, GetRequestNormal_0501
        if GetRequestNormal_0501 == 1:
            LargeOAD = self.datatype + LargeOAD
        else:
            LargeOAD = self.datatype + hex(relen)[2:].zfill(2) + LargeOAD
        print('reapdu', self.datatype)

    def sequence_of_len(self):
        global relen
        relen += 1

    def compose_data(self, OI):
        global LargeOAD, auto_increase, trans, SA_num_len, match_add
        try:
            self.get = self.conf_new.get('MeterData698', OI)
            self.get = self.get.split(' ')
            text = [OI, self.get[0], self.get[1]]
        except:
            print('未知数据标识: ', OI)
            traceback.print_exc(file=open('bug.txt', 'a+'))
            return None

        if OI == '40010200' or OI == '40020200' or OI == '202a0200':
            st = ['202a0200/40010200/40020200', '目标服务器地址/通信地址/表号', '']
            self.save(st)
            print('b_w_stat: ', b_w_stat, 'black_white_SA_address', black_white_SA_address, 'white', white)
            if b_w_stat == 2 and black_white_SA_address.find('a') != -1 and black_white_SA_address != 'aaaaaaaaaaaa':
                # add_aa_2 = int(black_white_SA_address[-2:])
                # for add in white:
                #     if add.find('-') > 0:
                #         add_range = add.split('-')
                #         start = int(add_range[0])
                #         end = int(add_range[1])
                #         add_list = []
                #         while start <= end:
                #             add_list.append(start)
                #             start += 1
                #         for y in add_list:
                #             if y % 100 == add_aa_2:
                #                 trans = str(int(y / 100) * 100 + add_aa_2).zfill(12)

                #                 print('compose_data_trans', trans)

                self.message = OI + '01' + '0906' + match_add
                SA_num_len = '05' + Comm.list2str(Comm.makelist(match_add)[::-1])
                print('message', self.message)
                LargeOAD = LargeOAD + self.message
                return 0
            if Comm.list2str(SA_num_len).find('a') == -1:
                trans = Comm.list2str(SA_num_len[1:][::-1])
            else:
                trans = Comm.list2str(Comm.makelist(str(match_add))[::-1])
            print('compose_data_trans', trans)
            self.message = OI + '01' + '0906' + trans
            print('message', self.message)
            LargeOAD = LargeOAD + self.message
            return 0

        if OI == '40000200':
            text = time.strftime('%Y%m%d%H%M%S')
            year = hex(int(text[0:4], 10))[2:].zfill(4)
            mouth = hex(int(text[4:6], 10))[2:].zfill(2)
            day = hex(int(text[6:8], 10))[2:].zfill(2)
            hour = hex(int(text[8:10], 10))[2:].zfill(2)
            min = hex(int(text[10:12], 10))[2:].zfill(2)
            sec = hex(int(text[12:], 10))[2:].zfill(2)
            times = '1c' + year + mouth + day + hour + min + sec
            st = ['40000200', '(当前)日期时间', '']
            self.save(st)
            self.message = '40000200' + '01' + times
            print('message', self.message)
            LargeOAD = LargeOAD + self.message
            return 1
        elif text[0] == OI:
            print('text', text)
            self.save(text)
            if text[0] == '00100200' and auto_increase == 1:
                global start_time
                stop_time = int(time.time() - start_time)
                OI_B = str(int(text[2][16:24], 16) + stop_time + 4).zfill(8)
                OI_C = str(int(text[2][26:34], 16) + stop_time + 3).zfill(8)
                OI_D = str(int(text[2][36:44], 16) + stop_time + 2).zfill(8)
                OI_E = str(int(text[2][46:54], 16) + stop_time + 1).zfill(8)
                OI_A = str(int(text[2][6:14], 16) + stop_time * 2 + 10).zfill(8)
                print('start time:', start_time, 'stop time:', stop_time)
                print('正向有功递增数值', OI_A)
                text[2] = '010506' + OI_A + '06' + OI_B + '06' + OI_C + '06' + OI_D + '06' + OI_E
            self.message = text[0] + '01' + text[2]
            print('message', self.message, 'text[2]', text[2])
            LargeOAD = LargeOAD + self.message
            return 1
        else:
            print('compose_data ERROR')
            return 0

    def save(self, text):
        global OI
        OI = OI + text[0:2]

    def transport(self):
        global OI
        return OI

    def clear_OI(self):
        global OI
        OI = []

    def composefrozen(self, OI):
        global frozenSign, auto_day_frozon_sign, auto_curve_sign, sele, SA_num_len
        print("composefrozen OI", OI, "frozenSign", frozenSign)
        if frozenSign == 1 and OI[0] != '5':
            newOI = '50020200_' + OI
        if frozenSign == 2 and OI[0] != '5':
            newOI = '50040200_' + OI
        if frozenSign == 3 and OI[0] != '5':
            newOI = '50060200_' + OI
        if frozenSign == 4 and OI[0] != '5':
            newOI = '50320200_' + OI
        if frozenSign == 5 and OI[0] != '5':
            newOI = '50050200_' + OI
        # print('new OI',newOI)
        if auto_day_frozon_sign == 1 and newOI == '50040200_20210200' and sele != 9:
            print('自动日冻结时标')
            global Daily_freeze  # 冻结时间
            print('newOI', newOI)
            self.save(['50040200_20210200', '自动日冻结({})'.format(Comm.ShowTime(Daily_freeze[2:])), ''])
            SequenceOf_ARecordRow(Daily_freeze)

        if auto_day_frozon_sign == 1 and newOI == '50050200_20210200' and sele != 9:
            print('5005自动结算日冻结时标')
            print('newOI', newOI)
            self.save(['50050200_20210200', '自动结算日冻结', ''])
            SequenceOf_ARecordRow(Daily_freeze)

        if auto_day_frozon_sign == 1 and newOI == '50060200_20210200' and sele != 9:
            print('自动月冻结时标')
            print('newOI', newOI)
            self.save(['50060200_20210200', '自动月冻结({})'.format(Comm.ShowTime(Daily_freeze[2:])), ''])
            SequenceOf_ARecordRow(Daily_freeze)

        if auto_curve_sign == 1 and newOI == '50020200_20210200' and sele != 9:
            global curve_list, Curve_gaps_times, Curve_gaps_times_multi
            print('自动曲线时标')
            print('curve_newOI', newOI)
            self.save(['50020200_20210200', '自动曲线冻结({})'.format(Comm.ShowTime(curve_list[0][2:])), ''])
            print("curve_list", curve_list)
            x = Comm.time_add(curve_list[0], Curve_gaps_times_multi * Curve_gaps_times)
            print("x: ", x)
            SequenceOf_ARecordRow(x)
            Curve_gaps_times_multi += 1

        if auto_day_frozon_sign == 1 and newOI == '50320200_20210200' and sele != 9:
            print('自动直流日冻结时标')
            # global Daily_freeze  # 冻结时间
            print('newOI', newOI)
            self.save(['50320200_20210200', '自动直流日冻结', ''])
            SequenceOf_ARecordRow(Daily_freeze)


        else:
            try:
                self.get = self.conf_new.get('MeterData698', newOI)
                self.get = self.get.split(' ')
                text = [newOI, self.get[0], self.get[1]]
            except:
                traceback.print_exc(file=open('bug.txt', 'a+'))
                if OI == '202a0200':
                    pass
                else:
                    print('未知数据标识 composefrozen  {}'.format(newOI))
            if newOI == '50020200_202a0200' or newOI == '50040200_202a0200' or newOI == '50050200_202a0200':
                text = [newOI, '目标服务器地址', '5507' + Comm.list2str(SA_num_len)]
            self.save(text)

            if auto_increase_500400100200 == 1 and newOI == '50320200_00100200':  # new  直流
                SequenceOf_ARecordRow(analysis_increase(text[2]))

            if auto_increase_500400100200 == 1 and (newOI == '50040200_00100200' or newOI == '50050200_00100200'):
                SequenceOf_ARecordRow(analysis_increase(text[2]))
            elif auto_curve_sign == 1 and newOI == '50020200_20210200':
                if sele == 9:
                    SequenceOf_ARecordRow(text[2])
            elif (auto_day_frozon_sign == 1 and newOI == '50040200_20210200') or (
                    auto_day_frozon_sign == 1 and newOI == '50060200_20210200') or (
                    auto_day_frozon_sign == 1 and newOI == '50320200_20210200') or (
                    auto_day_frozon_sign == 1 and newOI == '50050200_20210200'):
                if sele == 9:
                    text__ = time.strftime('%Y%m%d%H%M%S')
                    year = hex(int(text__[0:4], 10))[2:].zfill(4)
                    mouth = hex(int(text__[4:6], 10))[2:].zfill(2)
                    day = hex(int(text__[6:8], 10))[2:].zfill(2)
                    times = '1c' + year + mouth + day + '00' + '00' + '00'
                    SequenceOf_ARecordRow(times)
            else:
                SequenceOf_ARecordRow(text[2])
        global LargeOAD, OI_list_re
        OI_list_re_flag = 0
        print(OI_list_re)
        for x in OI_list_re:
            if OI == x:
                OI_list_re_flag = 1
                break

        if OI_list_re_flag == 0:
            OI_list_re.append(OI)
            LargeOAD = LargeOAD + '00' + OI
        sele = 0


def analysis_increase(data):
    global Difference
    print('Difference:', Difference)
    data = Comm.makelist(data)
    value = data[2:]
    count = len(value) // 5
    value_after = '0105'
    while count:
        value_1 = value[1:5]
        value_after = value_after + '06' + str(int(Comm.list2str(value_1)) + Difference).zfill(8)
        count -= 1
        print('value_after1', value_after)
    print('value_after2', value_after)
    return value_after


def set_auto_day_frozon(stat):
    global auto_day_frozon_sign
    auto_day_frozon_sign = stat


def curve_frozon(stat):
    global auto_curve_sign
    auto_curve_sign = stat


def auto_00100200(stat):
    global auto_increase
    auto_increase = stat


def auto_500400100200(stat):
    global auto_increase_500400100200
    auto_increase_500400100200 = stat


def add_mac(stat):
    global mac
    mac = stat


def change_max(mun):
    global _max
    _max = int(mun)


def re_max():
    global _max
    return _max


def set_from_to(x):
    global from_to
    from_to = x


def set_from_to_sign(x):
    global from_to_sign, from_to
    from_to_sign = x
    from_to = []


OI = []
start_time = time.time()
auto_day_frozon_sign = 1
auto_curve_sign = 1
auto_increase_500400100200 = 0
auto_increase = 0
mac = 1
GetRequestNormal_0501 = 0
service_code = ''
SA_num = 0
black_white_SA_address = ''
black = []
white = []
b_w_stat = 0
sele = 0
_max = 3
trans = ''
SecType = '00'
Difference = 0
from_to = []
from_to_sign = 0
hour_ = 0
minute_ = 0
apdu_3320 = ''
event_stat = 0
event_blacklist = []
plus_645 = 0
curve_list = []
OI_list_re = [" "]
Curve_gaps_times_multi = 0
count_re = 1
Recive_add = ""
match_add = 0
ReturnIsNULL = False

# coding=utf-8
# work on 2017.8.7

from send_cmd import *
from to_log import *
from ssh_connect import ssh_conn

Pass = "'result': 'p'"
Fail = "'result': 'f'"

def findBgaSId(c):
    bgaSInfo = SendCmd(c, 'bgasched')
    bgaSId = []

    if 'Type' and 'ID' in bgaSInfo:
        row = bgaSInfo.split('\r\n')
        for i in range(4, len(row)-2):
            if len(row[i].split()) >= 6:
                bgaSId.append(row[i].split()[1] + ':' + row[i].split()[0])
    else:
        tolog('There is no bgasched')

    return bgaSId

def findPlId(c):
    plInfo = SendCmd(c, 'pool')
    pdId = []
    row = plInfo.split('\r\n')

    for i in range(4, len(row) - 2):
        if len(row[i].split()) >= 9:
            pdId.append(row[i].split()[0])

    return pdId

def bvt_verifyBgaschedAdd(c):
    FailFlag = False

    # precondition
    def delOldBgasched(c):
        bgaSId = findBgaSId(c)
        if len(bgaSId) != 0:
            for typeId in bgaSId:
                if 'BatteryRecondition' in typeId:
                    SendCmd(c, 'bgasched -a del -t br -i ' + typeId[0])
                elif 'SpareCheck' in typeId:
                    SendCmd(c, 'bgasched -a del -t sc -i ' + typeId[0])
                elif 'RedundancyCheck' in typeId:
                    SendCmd(c, 'bgasched -a del -t rc -i ' + typeId[0])

    # delete old bgasched
    delOldBgasched(c)

    # create pool
    plId = findPlId(c)
    if len(plId) !=0:
        for i in plId:
            SendCmdconfirm(c, 'pool -a del -f -i ' + i)

        pdInfo = SendCmd(c, 'phydrv')
        pdId = []
        pdRow = pdInfo.split('\r\n')
        for i in range(4, (len(pdRow) - 2)):
            if "Unconfigured" in pdRow[i] and 'HDD' in pdRow[i]:
                pdId.append(pdRow[i].split()[0])
        if len(pdId) >= 5:
            SendCmd(c, 'pool -a add -s "name=testBgasched1, raid=1" -p ' + pdId[0] + ',' + pdId[1])
            SendCmd(c, 'pool -a add -s "name=testBgasched2, raid=1" -p ' + pdId[2] + ',' + pdId[3])
            SendCmd(c, 'pool -a add -s "name=testBgasched3, raid=0" -p ' + pdId[4])
        else:
            tolog('\n\n The lack of pd')
            exit()
    else:
        pdInfo = SendCmd(c, 'phydrv')
        pdId = []
        pdRow = pdInfo.split('\r\n')
        for i in range(4, (len(pdRow) - 2)):
            if "Unconfigured" in pdRow[i]:
                pdId.append(pdRow[i].split()[0])
        if len(pdId) >= 5:
            SendCmd(c, 'pool -a add -s "name=testBgasched1, raid=1" -p ' + pdId[0] + ',' + pdId[1])
            SendCmd(c, 'pool -a add -s "name=testBgasched2, raid=1" -p ' + pdId[2] + ',' + pdId[3])
            SendCmd(c, 'pool -a add -s "name=testBgasched3, raid=0" -p ' + pdId[4])
        else:
            tolog('\n\n The lack of pd')
            exit()

    poolId = findPlId(c)
    type = ['rc', 'br', 'sc']
    # confirm information
    listType = ['Type: RedundancyCheck', 'Type: BatteryRecondition', 'Type: SpareCheck']
    defaultStatus = ['OperationalStatus: Disabled']
    defaultStartTime = ['StartTime: 22:00', 'StartTime: 02:00', 'StartTime: 22:00']
    startDay = SendCmd(c, 'date').split('\r\n')[-3].split()[-2]
    # recurtype = ['daily', 'weekly', 'monthly']

    # add bgasched of daily type
    tolog('add bgasched of daily type')
    for i in range(0, 3):
        if type[i] == 'rc':
            result = SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "recurtype=daily,poolid=' + poolId[0] + '"'),\
                     SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "recurtype=daily,poolid=' + poolId[1] + '"')
        else:
            result = SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "recurtype=daily"')

        checkResult = SendCmd(c, 'bgasched -v -t ' + type[i])
        if 'Error (' in result or listType[i] not in checkResult or defaultStatus[0] not in checkResult or \
                        defaultStartTime[i] not in checkResult or 'Daily' not in checkResult or startDay not in checkResult:
            tolog('Fail: ' + 'bgasched -a add -t ' + type[i] + ' -s "recurtype=daily')
            FailFlag = True

    delOldBgasched(c)
    # pool of raid0 can not create rc bgasched
    result = SendCmd(c, 'bgasched -a add -t rc -s "recurtype=daily,poolid=2"')
    if 'Error (' not in result:
        FailFlag = True
        tolog('Fail: bgasched -a add -t rc -s "recurtype=daily,poolid=2"')

    delOldBgasched(c)

    # add bgasched of weekly type
    tolog('add bgasched of weekly type')
    for i in range(0, 3):
        if type[i] == 'rc':
            result = SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "poolid=' + poolId[0] + '"'),\
                     SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "poolid=' + poolId[1] + '"')
        else:
            result = SendCmd(c, 'bgasched -a add -t ' + type[i])

        checkResult = SendCmd(c, 'bgasched -v -t ' + type[i])
        if type[i] == 'br':
            if 'Error (' in result or listType[i] not in checkResult or defaultStatus[0] not in checkResult or \
                            defaultStartTime[i] not in checkResult or 'Monthly' not in checkResult or startDay not in checkResult:
                tolog('Fail: ' + 'bgasched -a add -t ' + type[i])
                FailFlag = True
        else:
            if 'Error (' in result or listType[i] not in checkResult or defaultStatus[0] not in checkResult or \
                            defaultStartTime[i] not in checkResult or 'Weekly' not in checkResult or startDay not in checkResult:
                tolog('Fail: ' + 'bgasched -a add -t ' + type[i])
                FailFlag = True

    delOldBgasched(c)

    # add bgasched of monthly type
    tolog('add bgasched of monthly type')
    for i in range(0, 3):
        if type[i] == 'rc':
            result = SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "recurtype=monthly,poolid=' + poolId[0] + '"'), \
                     SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "recurtype=monthly,poolid=' + poolId[1] + '"')
        else:
            result = SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "recurtype=monthly"')

        checkResult = SendCmd(c, 'bgasched -v -t ' + type[i])
        if 'Error (' in result or listType[i] not in checkResult or defaultStatus[0] not in checkResult or \
                        defaultStartTime[i] not in checkResult or 'Monthly' not in checkResult or startDay not in checkResult:
            tolog('Fail: ' + 'bgasched -a add -t ' + type[i] + ' -s "recurtype=monthly')
            FailFlag = True

    delOldBgasched(c)

    if FailFlag:
        tolog('\n<font color="red">Fail: To verify add bgasched </font>')
        tolog(Fail)
    else:
        tolog('\n<font color="green">Pass</font>')
        tolog(Pass)

    return FailFlag

def bvt_verifyBgaschedMod(c):
    FailFlag = False
    type = ['rc', 'br', 'sc']
    recurtype = ['daily', 'weekly', 'monthly']
    # precondition
    for i in range(0, 3):
        if 'Error (' in SendCmd(c, 'bgasched -a add -t ' + type[i] + ' -s "recurtype=' + recurtype[i] + '"'):
            tolog('to create precondition is failed')
            exit()

    # setting by type of type
    globalSettings = [
        # status
        ['Disable', 'Disable', 'Enable', 'Enable'],
        # startTime
        ['00:00', '06:10', '12:20', '23:59'],
        # startFrom : year value range 1970~2037
        ['1970-01-01', '2037-12-31', '2000-01-01', '2000-01-01'],
        # endOn
        ['1', '255', '1970-01-01', '2037-12-31'],
        # autoFix
        ['Enable', 'Enable', 'Disable', 'Disable'],
        # pause
        ['Enable', 'Enable', 'Disable', 'Disable']
    ]
    for t in type:
        tolog('verify: bgasched -a mod -t ' + t)

        for i in range(0, 4):
            # setting autoFix and pause for rc
            result = SendCmd(c, 'bgasched -a mod -t rc -s "autofix='
                             + globalSettings[4][i] + ',pause='
                             + globalSettings[5][i] + '"')
            checkResult = SendCmd(c, 'bgasched -v -t rc')
            if 'Error (' in result or ('AutoFix: '
                             + globalSettings[4][i]) not in checkResult or ('PauseOnError: '
                             + globalSettings[5][i]) not in checkResult:
                FailFlag = True
                tolog('Fail: ' + 'bgasched -a mod -t rc -s "autofix='
                             + globalSettings[4][i] + ',pause='
                             + globalSettings[5][i] + '"')

            # setting status/startTime/startDay/endOn for all type
            result = SendCmd(c, 'bgasched -a mod -t ' + t + ' -s "status='
                             + globalSettings[0][i] + ',starttime='
                             + globalSettings[1][i] + ',startfrom='
                             + globalSettings[2][i] + ',endon='
                             + globalSettings[3][i] + '"')
            checkResult = SendCmd(c, 'bgasched -v -t ' + t)
            if 'Error (' in result or ('OperationalStatus: '
                        + globalSettings[0][i]) not in checkResult or ('StartTime: '
                        + globalSettings[1][i]) not in checkResult or ('StartDay: '
                        + globalSettings[2][i]) not in checkResult or (''
                        + globalSettings[3][i][:4]) not in checkResult:
                FailFlag = True
                tolog('Fail: ' + 'bgasched -a mod -t ' + t + ' -s "status='
                             + globalSettings[0][i] + ',starttime='
                             + globalSettings[1][i] + ',startfrom='
                             + globalSettings[2][i] + ',endon='
                             + globalSettings[3][i] + '"')

    # Setting the parameters associated with recurType of daily
    tolog('Setting the parameters associated with recurType of daily')
    dailySettings = ['1', '2', '254', '255']

    for ds in dailySettings:
        result = SendCmd(c, 'bgasched -a mod -t rc -s "recurInterval=' + ds + '"')
        checkResult = SendCmd(c, 'bgasched -v -t rc')
        if "Error (" in result or ('RecurrenceInterval: ' + ds) not in checkResult:
            FailFlag = True
            tolog('Fail: ' + 'bgasched -a mod -t rc -s "recurInterval=' + ds + '"')

    # Setting the parameters associated with recurType of weekly
    tolog('Setting the parameters associated with recurType of weekly')
    weeklySettings = [
        # recurInterval
        ['1', '2', '51', '52', '52', '52', '52'],
        # dow
        ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat']
    ]

    for i in range(0, 7):
        result = SendCmd(c, 'bgasched -a mod -t br -s "recurInterval='
                         + weeklySettings[0][i] + ',dow='
                         + weeklySettings[1][i] + '"')
        checkResult = SendCmd(c, 'bgasched -v -t br')
        if 'Error (' in result or ('RecurrenceInterval: '
                         + weeklySettings[0][i]) not in checkResult or ('DayOfWeek: '
                         + weeklySettings[1][i]) not in checkResult:
            FailFlag = True
            tolog('Fail: '
                         + 'bgasched -a mod -t br -s "recurInterval='
                         + weeklySettings[0][i] + ',dow='
                         + weeklySettings[1][i] + '"')

    # Setting the parameters associated with recurType of monthly
    tolog('Setting the parameters associated with recurType of monthly')
    monthlySettings = [
        # dom
        ['1', '2', '30', '31'],
        # dow
        ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat'],
        # wom
        ['1st', '2nd', '3rd', '4th', 'Last', 'Last', 'Last']
    ]

    for i in range(0, len(monthlySettings[0])):
        result = SendCmd(c, 'bgasched -a mod -t sc -s "daypattern=dom,dom=' + monthlySettings[0][i] + '"')
        checkResult = SendCmd(c, 'bgasched -v -t sc')
        if "Error (" in result or ('DayOfMonth: ' + monthlySettings[0][i]) not in checkResult:
            FailFlag = True
            tolog('Fail: ' + 'bgasched -a mod -t sc -s "daypattern=dom,dom=' + monthlySettings[0][i] + '"')

    for i in range(0, len(monthlySettings[1])):
        result = SendCmd(c, 'bgasched -a mod -t sc -s "daypattern=dow,dow='
                         + monthlySettings[1][i] + ',wom='
                         + monthlySettings[2][i] + '"')
        checkResult = SendCmd(c, 'bgasched -v -t sc')
        if 'Error (' in result or ('DayOfMonth: ' + monthlySettings[2][i] + ' ' + monthlySettings[1][i]) not in checkResult:
            FailFlag = True
            tolog('Fail: ' + 'bgasched -a mod -t sc -s "daypattern=dow,dow='
                         + monthlySettings[1][i] + ',wom='
                         + monthlySettings[2][i] + '"')

    if FailFlag:
        tolog('\n<font color="red">Fail: To verify modify bgasched </font>')
        tolog(Fail)
    else:
        tolog('\n<font color="green">Pass</font>')
        tolog(Pass)

    return FailFlag

def bvt_verifyBgaschedList(c):
    FailFlag = False
    command = ['bgasched',
               'bgasched -v',
               'bgasched -v -t br',
               'bgasched -v -t rc',
               'bgasched -v -t sc'
               ]

    for com in command:
        tolog('verify: ' + com)
        result = SendCmd(c, com)
        if 'Error (' in result:
            FailFlag = True
            tolog("Fail: " + com)

    if FailFlag:
        tolog('\n<font color="red">Fail: To verify list bgasched </font>')
        tolog(Fail)
    else:
        tolog('\n<font color="green">Pass</font>')
        tolog(Pass)

    return FailFlag

def bvt_verifyBgaschedDel(c):
    FailFlag = False
    bgaSId = findBgaSId(c)
    if len(bgaSId) != 0:
        for typeId in bgaSId:
            if 'BatteryRecondition' in typeId:
                result = SendCmd(c, 'bgasched -a del -t br -i ' + typeId[0])
                if 'Error (' in result:
                    FailFlag = True
                    tolog('Fail: ' + 'bgasched -a del -t br -i ' + typeId[0])
            elif 'SpareCheck' in typeId:
                result = SendCmd(c, 'bgasched -a del -t sc -i ' + typeId[0])
                if 'Error (' in result:
                    FailFlag = True
                    tolog('Fail: ' + 'bgasched -a del -t sc -i ' + typeId[0])
            elif 'RedundancyCheck' in typeId:
                result = SendCmd(c, 'bgasched -a del -t rc -i ' + typeId[0])
                if 'Error (' in result:
                    FailFlag = True
                    tolog('Fail: ' + 'bgasched -a del -t rc -i ' + typeId[0])

    if FailFlag:
        tolog('\n<font color="red">Fail: To verify delete bgasched </font>')
        tolog(Fail)
    else:
        tolog('\n<font color="green">Pass</font>')
        tolog(Pass)

    return FailFlag

def bvt_verifyBgaschedHelp(c):
    FailFlag = False
    result = SendCmd(c, 'bgasched -h')
    if 'Error (' in result or '<action>' not in result:
        FailFlag = True
        tolog('Fail: bgasched -h')

    if FailFlag:
        tolog('\n<font color="red">Fail: Verify Bgasched help </font>')
        tolog(Fail)
    else:
        tolog('\n<font color="green">Pass</font>')
        tolog(Pass)

    return FailFlag

def bvt_verifyBgaschedInvalidOption(c):
    FailFlag = False
    command = ['bgasched -x',
               'bgasched -a list -x',
               'bgasched -a mod -x',
               'bgasched -a del -x'
               ]
    for com in command:
        result = SendCmd(c, com)
        if 'Error (' not in result or 'Invalid option' not in result:
            FailFlag = True
            tolog('Fail: ' + com)

    if FailFlag:
        tolog('\n<font color="red">Fail: Verify Bgasched invalid option </font>')
        tolog(Fail)
    else:
        tolog('\n<font color="green">Pass</font>')
        tolog(Pass)

    return FailFlag

def bvt_verifyBgaschedInvalidParameters(c):
    FailFlag = False
    command = ['bgasched -t x',
               'bgasched -a mod -t x',
               'bgasched -a add -t sc -s "status=x"',
               'bgasched -a add -t sc -s "recurtype=x"',
               # startTime range is 0-23
               'bgasched -a add -t sc -s "starttime=-1"',
               'bgasched -a add -t sc -s "starttime=24"',
               # recurInterval For Daily type, the range is 1-255
               'bgasched -a add -t sc -s "recurtype=daily,recurInterval=0"',
               'bgasched -a add -t sc -s "recurtype=daily,recurInterval=256"',
               # recurInterval For weekly type, the range is 1-52
               'bgasched -a add -t sc -s "recurtype=weekly,recurInterval=0"',
               'bgasched -a add -t sc -s "recurtype=weekly,recurInterval=53"',
               # dom The range is 1~31
               'bgasched -a add -t sc -s "daypattern=dom,dom=0"',
               'bgasched -a add -t sc -s "daypattern=dom,dom=32"',
               'bgasched -a add -t sc -s "daypattern=dow,wom=x"',
               # mm/dd/yyyy where month's range is 1-12, day's range is 1-31, year value range 1970~2037
               'bgasched -a add -t sc -s "startfrom=2017-0-1"',
               'bgasched -a add -t sc -s "startfrom=2017-13-1"',
               'bgasched -a add -t sc -s "startfrom=2017-1-0"',
               'bgasched -a add -t sc -s "startfrom=2017-1-32"',
               'bgasched -a add -t sc -s "startfrom=3038-1-1"',
               # endOn range is 0-255,month's range is 1-12 and day's range is 1-31
               'bgasched -a add -t sc -s "endon=-1"',
               'bgasched -a add -t sc -s "endon=256"',
               'bgasched -a add -t sc -s "endon=2017-0-1"',
               'bgasched -a add -t sc -s "endon=2017-13-1"',
               'bgasched -a add -t sc -s "endon=2017-1-0"',
               'bgasched -a add -t sc -s "endon=2017-32-1"',
               'bgasched -a add -t rc -s "autofix=x"',
               'bgasched -a add -t rc -s "pause=x"',
               'bgasched -a del -t x'
               ]
    for com in command:
        result = SendCmd(c,com)
        if "Error (" not in result or 'Invalid setting parameters' not in result:
            FailFlag = True
            tolog('Fail: ' + com)

    if FailFlag:
        tolog('\n<font color="red">Fail: Verify Bgasched invalid parameters </font>')
        tolog(Fail)
    else:
        tolog('\n<font color="green">Pass</font>')
        tolog(Pass)

    return FailFlag

def bvt_verifyBgaschedMissingParameters(c):
    FailFlag = False
    command = ['bgasched -t ',
               'bgasched -a mod -t rc -s',
               'bgasched -a del -t'
               ]
    for com in command:
        result = SendCmd(c, com)
        if 'Error (' not in result or 'Missing parameter' not in result:
            FailFlag = True
            tolog("Fail: " + com)

    if FailFlag:
        tolog('\n<font color="red">Fail: Verify Bgasched missing parameters </font>')
        tolog(Fail)
    else:
        tolog('\n<font color="green">Pass</font>')
        tolog(Pass)

    return FailFlag

def bvt_clearUp(c):
    plInfo = SendCmd(c, 'pool')
    row = plInfo.split('\r\n')
    plId = []
    for i in range(4, len(row) - 2):
        if len(row[i].split()) >= 9 and 'testBgasched' in row[i]:
            plId.append(row[i].split()[0])

    for i in plId:
        SendCmdconfirm(c, 'pool -a del -f -i ' + i)



if __name__ == "__main__":
    start = time.clock()
    c, ssh = ssh_conn()
    bvt_verifyBgaschedAdd(c)
    bvt_verifyBgaschedMod(c)
    bvt_verifyBgaschedList(c)
    bvt_verifyBgaschedDel(c)
    bvt_verifyBgaschedHelp(c)
    bvt_verifyBgaschedInvalidOption(c)
    bvt_verifyBgaschedInvalidParameters(c)
    bvt_verifyBgaschedMissingParameters(c)
    bvt_clearUp(c)
    ssh.close()
    elasped = time.clock() - start
    print "Elasped %s" % elasped
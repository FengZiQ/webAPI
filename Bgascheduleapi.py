# -*- coding: utf-8 -*-

from remote import server
import json
from to_log import tolog

Pass = "'result': 'p'"
Fail = "'result': 'f'"

def findPlId():
    pdResponseInfo = server.webapi('get', 'phydrv')
    pdInfo = json.loads(pdResponseInfo['text'])

    for pd in pdInfo[1:]:
        if 'Pool' in pd['cfg_status']:
            plResponseInfo = server.webapi('get', 'pool')
            plInfo = json.loads(plResponseInfo['text'])
            for pl in plInfo:
                server.webapiurl('delete', 'pool', str(pl['id']) + '?force=1')

    pdResponseInfo = server.webapi('get', 'phydrv')
    pdInfo = json.loads(pdResponseInfo['text'])
    pdId = []
    for pd in pdInfo:
        if pd['op_status'] == 'OK' and pd['cfg_status'] == 'Unconfigured' and pd['type'] == 'SAS HDD':
            pdId.append(pd['id'])

    return pdId

def BgascheduleApiPost():
    Failflag = False
    FailFlagList = []
    tolog("To add bgaschedule by api\r\n")

    # precondition
    def deleteBgaschedule():
        ResponseInfo = server.webapi('get', 'bgaschedule')
        bgaInfo = json.loads(ResponseInfo['text'])
        if len(bgaInfo) > 1:
            for bga in bgaInfo:
                if bga['id'] == 'brc':
                    server.webapiurl('delete', 'bgaschedule', 'brc')
                elif bga['id'] == 'rc_1':
                    server.webapiurl('delete', 'bgaschedule', 'rc_1')
                elif bga['id'] == 'rc_2':
                    server.webapiurl('delete', 'bgaschedule', 'rc_2')
                elif bga['id'] == 'sc':
                    server.webapiurl('delete', 'bgaschedule', 'sc')

    deleteBgaschedule()
    pdId = findPlId()

    if len(pdId) >= 5:
        server.webapi('post', 'pool', {'name': 'testBgaschedApi1',
                                          'sector': '512B', 'raid_level': 'RAID1',
                                          'ctrl_id': 1, 'force_sync': 0,
                                          'pds': [pdId[0], pdId[1]]
                                          })
        server.webapi('post', 'pool', {'name': 'testBgaschedApi2',
                                          'sector': '512B', 'raid_level': 'RAID1',
                                          'ctrl_id': 1, 'force_sync': 0,
                                          'pds': [pdId[2], pdId[3]]
                                          })
        server.webapi('post', 'pool', {'name': 'testBgaschedApi3',
                                          'sector': '512B', 'raid_level': 'RAID0',
                                          'ctrl_id': 1, 'force_sync': 0,
                                          'pds': [pdId[4]]
                                          })

    bga_type = ['rc', 'brc', 'sc']

    # add bgasched of daily type
    tolog('add bgasched of daily type\r\n')
    def addDailyBgasched():
        Failflag = False
        dayTypeParameters = {
            "status": 1,
            "start_time": 1439,
            "interval": 255,
            "day_start": 30,
            "month_start": 12,
            "year_start": 2037,
            "range_end": 2,
            "recurrence_count": 255
        }

        for i in range(3):
            if bga_type[i] == 'rc':
                parameters = dict(dayTypeParameters.items() + {
                    'bga_type': bga_type[i],
                    'recurrence_type': 1,
                    'rc_pools': [0],
                    "rc_fix": 0,
                    "rc_pause": 0
                }.items())
                server.webapi('post', 'bgaschedule', parameters)

                tolog('Expect:' + json.dumps(parameters) + '\r\n')
                expectResult = dict(dayTypeParameters.items() +{
                    'bga_type': bga_type[i],
                    "recurrence_type": "Daily",
                    'rc_pools': [0],
                    "rc_fix": 0,
                    "rc_pause": 0
                }.items())

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                for r in result:
                    if r["bga_type"] == 'rc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult.keys():
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))

                deleteBgaschedule()

            else:
                parameters = dict(dayTypeParameters.items() + {
                    'bga_type': bga_type[i],
                    'recurrence_type': 1
                }.items())
                server.webapi('post', 'bgaschedule', parameters)

                tolog('Expect:' + json.dumps(parameters) + '\r\n')
                expectResult = dict(dayTypeParameters.items() + {
                    'bga_type': bga_type[i],
                    'recurrence_type': "Daily"
                }.items())

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                for r in result:
                    if r["bga_type"] == 'sc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult.keys():
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))
                    elif r["bga_type"] == 'brc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))

                deleteBgaschedule()

        return Failflag

    FailFlagList.append(addDailyBgasched())

    # add bgasched of weekly type
    tolog('add bgasched of weekly type \r\n')
    def addWeeklyBgasched():
        Failflag = False
        weeklyTypeParameters = {
            "status": 0,
            "start_time": 0,
            "interval": 1,
            "day_mask": 127,
            "day_start": 1,
            "month_start": 1,
            "year_start": 1971,
            "range_end": 3,
            "day_end": 1,
            "month_end": 1,
            "year_end": 2018
        }

        for i in range(3):
            if bga_type[i] == 'rc':
                parameters = dict(weeklyTypeParameters.items() + {
                    'bga_type': bga_type[i],
                    'recurrence_type': 2,
                    'rc_pools': [0],
                    "rc_fix": 1,
                    "rc_pause": 1
                }.items())

                server.webapi('post', 'bgaschedule', parameters)

                tolog('Expect:' + json.dumps(parameters) + '\r\n')
                expectResult = dict(weeklyTypeParameters.items() +{
                    'bga_type': bga_type[i],
                    "recurrence_type": "Weekly",
                    'rc_pools': [0],
                    "rc_fix": 1,
                    "rc_pause": 1
                }.items())

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                for r in result:
                    if r["bga_type"] == 'rc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult.keys():
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))

                deleteBgaschedule()

            else:
                parameters = dict(weeklyTypeParameters.items() + {
                    'bga_type': bga_type[i],
                    'recurrence_type': 2
                }.items())

                server.webapi('post', 'bgaschedule', parameters)

                tolog('Expect:' + json.dumps(parameters) + '\r\n')
                expectResult = dict( weeklyTypeParameters.items() +{
                    'bga_type': bga_type[i],
                    "recurrence_type": "Weekly"
                }.items())

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                for r in result:
                    if r["bga_type"] == 'sc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult.keys():
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))
                    elif r["bga_type"] == 'brc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))

                deleteBgaschedule()

        return Failflag

    FailFlagList.append(addWeeklyBgasched())

    # add bgasched of monthly type
    tolog('add bgasched of monthly type\r\n')
    def addmonthlyBgasched():
        Failflag = False
        monthlyTypeParameters = {
            "status": 1,
            "start_time": 0,
            "day_pattern": 0,
            "day_of_month": 5,
            "month_mask": 4095,
            "day_start": 28,
            "month_start": 9,
            "year_start": 2018,
            "range_end": 3,
            "day_end": 1,
            "month_end": 1,
            "year_end": 2019
        }

        for i in range(3):
            if bga_type[i] == 'rc':
                parameters = dict(monthlyTypeParameters.items() + {
                    'bga_type': bga_type[i],
                    'recurrence_type': 3,
                    'rc_pools': [0],
                    "rc_fix": 1,
                    "rc_pause": 1
                }.items())

                server.webapi('post', 'bgaschedule', parameters)

                tolog('Expect:' + json.dumps(parameters) + '\r\n')
                expectResult = dict(monthlyTypeParameters.items() + {
                    'bga_type': bga_type[i],
                    "recurrence_type": "Monthly",
                    'rc_pools': [0],
                    "rc_fix": 1,
                    "rc_pause": 1
                }.items())

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                for r in result:
                    if r["bga_type"] == 'rc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult.keys():
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))

                deleteBgaschedule()

            else:
                parameters = dict(monthlyTypeParameters.items() + {
                    'bga_type': bga_type[i],
                    'recurrence_type': 3
                }.items())
                server.webapi('post', 'bgaschedule', parameters)

                tolog('Expect:' + json.dumps(parameters) + '\r\n')
                expectResult = dict(monthlyTypeParameters.items() +{
                    'bga_type': bga_type[i],
                    "recurrence_type": "Monthly"
                }.items())

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                for r in result:
                    if r["bga_type"] == 'sc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult.keys():
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))
                    elif r["bga_type"] == 'brc':
                        actualResult = r
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))

                deleteBgaschedule()

        return Failflag

    FailFlagList.append(addmonthlyBgasched())

    for Flag in FailFlagList:
        if Flag == True:
            Failflag = True

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def BgascheduleApiPut():
    Failflag = False
    tolog("To modify bgaschedule by api")
    # precondition: create different types of bgaschedule
    for bga_type in ['rc', 'brc', 'sc']:
        if bga_type == 'rc':
            server.webapi('post', 'bgaschedule', parameters={
                'bga_type': bga_type,
                'status': 0,
                'start_time': 0,
                'recurrence_type': 1,
                "day_start": 1,
                "month_start": 1,
                "year_start": 1970,
                "range_end": 1,
                'rc_fix': 0,
                'rc_pause': 0,
                'rc_pools': [0]
            })
        else:
            server.webapi('post', 'bgaschedule', parameters={
                'bga_type': bga_type,
                'status': 0,
                'start_time': 0,
                'recurrence_type': 1,
                "day_start": 1,
                "month_start": 1,
                "year_start": 1970,
                "range_end": 1
            })

    # testing data

    bga_id = ['rc_1', 'brc', 'sc']
    dailySettingList = {
        "status": [0, 1, 1],
        "start_time": [0, 512, 1439],
        "recurrence_type": [1, 1, 1],
        "interval": [1, 125, 255],
        "day_start": [1, 16, 31],
        "month_start": [1, 6, 12],
        "year_start": [1970, 2017, 2037],
        "range_end": [1, 1, 1]
    }

    weeklySettingList = {
        "status": [0, 0, 1, 1, 0, 1, 1],
        "start_time": [0, 0, 512, 512, 1439, 1439, 513],
        "recurrence_type": [2, 2, 2, 2, 2, 2, 2],
        "interval": [1, 1, 25, 25, 52, 52, 2],
        "day_mask": [32, 68, 41, 85, 91, 111, 127],
        "day_start": [1, 1, 16, 16, 31, 31, 15],
        "month_start": [1, 1, 6, 6, 12, 12, 7],
        "year_start": [1970, 1970, 2017, 2017, 2037, 2037, 2020],
        "range_end": [1, 1, 1, 1, 1, 1, 1]
    }

    monthlySettingListPart = {
        "status": [0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
        "start_time": [0, 0, 512, 512, 1439, 1439, 513, 512, 1439, 1439, 513, 513],
        "month_mask": [4095, 4079, 3567, 3517, 3435, 2922, 2730, 2356, 2338, 2314, 2112, 32],
        "day_start": [1, 1, 16, 16, 25, 25, 15, 16, 31, 31, 15, 15],
        "month_start": [1, 1, 6, 6, 12, 12, 7, 6, 12, 12, 7, 8],
        "year_start": [1970, 1970, 2017, 2017, 2037, 2037, 2020, 2017, 2037, 2037, 2020, 2019],
        "range_end": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "recurrence_type": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    }

    # To modify monthly bgaschedule
    tolog('To modify monthly bgaschedule \r\n')
    for id in bga_id:
        if id == 'rc_1':
            monthlySettingList = dict(monthlySettingListPart.items() + {
                "day_pattern": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "day_of_month": [1, 1, 16, 16, 31, 31, 15, 16, 28, 28, 15, 15],
                "rc_fix": [0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
                "rc_pause": [1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1],
                "rc_pools": [[1], [1], [0], [0], [1], [1], [0], [0], [1], [1], [0], [0]]
            }.items())

            expectResult = {}
            for i in range(12):
                for k in monthlySettingList:
                    expectResult[k] = monthlySettingList[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                for r in result:
                    if r["bga_type"] == 'rc':
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        actualResult = r
                        for key in expectResult:
                            if expectResult[key] != 3:
                                if expectResult[key] != actualResult[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))

        elif id == 'brc':
            monthlySettingList = dict(monthlySettingListPart.items() + {
                "day_pattern": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                "day_of_week": [0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6, 6]
            }.items())

            expectResult = {}
            for i in range(12):
                for k in monthlySettingList:
                    expectResult[k] = monthlySettingList[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])
                for r in result:
                    if r["bga_type"] == 'brc':
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        actualResult = r
                        for key in expectResult:
                            if expectResult[key] != 3:
                                if expectResult[key] != actualResult[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))
        elif id == 'sc':
            monthlySettingList = dict(monthlySettingListPart.items() + {
                "day_pattern": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                "day_of_week": [0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6, 6]
            }.items())

            expectResult = {}
            for i in range(12):
                for k in monthlySettingList:
                    expectResult[k] = monthlySettingList[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])
                for r in result:
                    if r["bga_type"] == 'sc':
                        tolog('Actual:' + json.dumps(r) + '\r\n')
                        actualResult = r
                        for key in expectResult:
                            if expectResult[key] != 3:
                                if expectResult[key] != actualResult[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(actualResult[key]))

    range_endList = [2, 3]
    for id in bga_id:
        for range_end in range_endList:
            if id == 'rc_1' and range_end == 2:
                for recurrence_count in [0, 255]:
                    tolog('Expect: ' + json.dumps({"range_end": 2, "recurrence_count": recurrence_count}) + '\r\n')

                    server.webapi('put', 'bgaschedule/' + id, {
                        "range_end": 2,
                        "recurrence_count": recurrence_count
                    })

                    check = server.webapi('get', 'bgaschedule')
                    result = json.loads(check['text'])

                    for r in result:
                        if r["id"] == "rc_1":
                            actualResult = r
                            tolog("Actual: " + json.dumps(actualResult) + '\r\n')
                            if r["range_end"] != 2 and r["recurrence_count"] != 0:
                                Failflag = True
                                tolog('Fail: parameters "range_end" !=2 and "recurrence_count" != 0')
            elif id == 'brc' and range_end == 3:
                untilSetting = [[1, 31], [1, 12], [1970, 2037]]
                for i in range(2):
                    tolog('Expect: ' + json.dumps({
                        "range_end": 3,
                        "day_end": untilSetting[0][i],
                        "month_end": untilSetting[1][i],
                        "year_end": untilSetting[2][i]
                    }) + '\r\n')

                    server.webapi('put', 'bgaschedule/' + id, {
                        "range_end": 3,
                        "day_end": untilSetting[0][i],
                        "month_end": untilSetting[1][i],
                        "year_end": untilSetting[2][i]
                    })

                    check = server.webapi('get', 'bgaschedule')
                    result = json.loads(check['text'])

                    for r in result:
                        if r["id"] == "brc":
                            actualResult = r
                            tolog("Actual: " + json.dumps(actualResult) + '\r\n')
                            if r["range_end"] != 3 and r["year_end"] != untilSetting[2][i]:
                                Failflag = True
                                tolog('Fail: parameters "range_end" !=3 and "year_end" != ' + str(untilSetting[2][i]))
            elif id == 'sc' and range_end == 3:
                untilSetting = [[1, 31], [1, 12], [1970, 2037]]
                for i in range(2):
                    tolog('Expect: ' + json.dumps({
                        "range_end": 3,
                        "day_end": untilSetting[0][i],
                        "month_end": untilSetting[1][i],
                        "year_end": untilSetting[2][i]
                    }) + '\r\n')

                    server.webapi('put', 'bgaschedule/' + id, {
                        "range_end": 3,
                        "day_end": untilSetting[0][i],
                        "month_end": untilSetting[1][i],
                        "year_end": untilSetting[2][i]
                    })

                    check = server.webapi('get', 'bgaschedule')
                    result = json.loads(check['text'])

                    for r in result:
                        if r["id"] == "sc":
                            actualResult = r
                            tolog("Actual: " + json.dumps(actualResult) + '\r\n')
                            if r["range_end"] != 3 and r["month_end"] != untilSetting[1][i]:
                                Failflag = True
                                tolog('Fail: parameters "range_end" !=3 and "month_end" != ' + str(untilSetting[1][i]))

    # To modify weekly bgaschedule
    tolog('To modify weekly bgaschedule \r\n')
    for id in bga_id:
        if id == 'rc_1':
            weeklySetting = dict(weeklySettingList.items() + {
                "rc_fix": [0, 0, 1, 1, 0, 1, 1],
                "rc_pause": [1, 1, 0, 0, 0, 1, 1]
            }.items())
            for i in range(7):
                expectResult = {}
                for k in weeklySetting:
                    expectResult[k] = weeklySetting[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if r["id"] == 'rc_1':
                        actualResult = r
                        tolog('Actual: ' + json.dumps(actualResult) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != 2:
                                if expectResult[key] != r[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(r[key]))
        elif id == 'brc':
            for i in range(7):
                expectResult = {}
                for k in weeklySettingList:
                    expectResult[k] = weeklySettingList[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if r["id"] == 'brc':
                        actualResult = r
                        tolog('Actual: ' + json.dumps(actualResult) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != 2:
                                if expectResult[key] != r[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(r[key]))
        elif id == 'sc':
            for i in range(7):
                expectResult = {}
                for k in weeklySettingList:
                    expectResult[k] = weeklySettingList[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if r["id"] == 'sc':
                        actualResult = r
                        tolog('Actual: ' + json.dumps(actualResult) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != 2:
                                if expectResult[key] != r[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(r[key]))

    # To modify daily bgaschedule
    tolog('To modify daily bgaschedule \r\n')
    for id in bga_id:
        if id == 'rc_1':
            dailySetting = dict(dailySettingList.items() + {
                "rc_fix": [0, 0, 1],
                "rc_pause": [1, 0, 1]
            }.items())
            for i in range(3):
                expectResult = {}
                for k in dailySetting:
                    expectResult[k] = dailySetting[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if r["id"] == 'rc_1':
                        actualResult = r
                        tolog('Actual: ' + json.dumps(actualResult) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != 1:
                                if expectResult[key] != r[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(r[key]))
        elif id == 'brc':
            for i in range(3):
                expectResult = {}
                for k in dailySettingList:
                    expectResult[k] = dailySettingList[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if r["id"] == 'brc':
                        actualResult = r
                        tolog('Actual: ' + json.dumps(actualResult) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != 1:
                                if expectResult[key] != r[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(r[key]))
        elif id == 'sc':
            for i in range(3):
                expectResult = {}
                for k in dailySettingList:
                    expectResult[k] = dailySettingList[k][i]

                tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
                server.webapi('put', 'bgaschedule/' + id, expectResult)

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if r["id"] == 'sc':
                        actualResult = r
                        tolog('Actual: ' + json.dumps(actualResult) + '\r\n')
                        for key in expectResult:
                            if expectResult[key] != 1:
                                if expectResult[key] != r[key]:
                                    Failflag = True
                                    tolog('Fail: parameters ' + str(expectResult[key]) + '!=' + str(r[key]))


    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def BgascheduleApiDelete():
    Failflag = False
    ResponseInfo = server.webapi('get', 'bgaschedule')
    bgaInfo = json.loads(ResponseInfo['text'])
    tolog('To delete bgaschedule by api \r\n')
    if len(bgaInfo) > 1:
        for bga in bgaInfo:
            if bga['id'] == 'brc':
                # delete brc type
                tolog('Expect: delete brc type \r\n')
                server.webapiurl('delete', 'bgaschedule', 'brc')

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if 'brc' in r.values():
                        Failflag = True
                        tolog('Fail: Did not delete brc type')
                    else:
                        tolog('Actual: brc type deletes successfully \r\n')
                        break

            elif bga['id'] == 'rc_1':
                # delete rc type
                tolog('Expect: delete rc type\r\n')
                server.webapiurl('delete', 'bgaschedule', 'rc_1')

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if 'rc' in r.values():
                        Failflag = True
                        tolog('Fail: Did not delete rc type')
                    else:
                        tolog('Actual: rc type deletes successfully\r\n')
                        break

            elif bga['id'] == 'rc_2':
                # delete rc type
                tolog('Expect: delete rc type\r\n')
                server.webapiurl('delete', 'bgaschedule', 'rc_2')

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if 'rc' in r.values():
                        Failflag = True
                        tolog('Fail: Did not delete rc type')
                    else:
                        tolog('Actual: rc type deletes successfully\r\n')
                        break

            elif bga['id'] == 'sc':
                # delete sc type
                tolog('Expect: delete sc type\r\n')
                server.webapiurl('delete', 'bgaschedule', 'sc')

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check["text"])

                for r in result:
                    if 'sc' in r.values():
                        Failflag = True
                        tolog('Fail: Did not delete sc type')
                    else:
                        tolog('Actual: sc type deletes successfully\r\n')
                        break

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)


if __name__ == "__main__":
    BgascheduleApiPost()
    BgascheduleApiPut()
    BgascheduleApiDelete()
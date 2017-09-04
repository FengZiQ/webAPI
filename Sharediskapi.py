# -*- coding: utf-8 -*-

from remote import server
import json
from to_log import tolog

Pass = "'result': 'p'"
Fail = "'result': 'f'"

def findPlId():
    # get physical drive id
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

    # to create pool
    if len(pdId) >= 5:
        server.webapi('post', 'pool', {
            'name': 'testSharediskApi2',
            'sector': '512B',
            'raid_level': 'RAID5',
            'ctrl_id': 1,
            'force_sync': 0,
            'pds': [pdId[0], pdId[1], pdId[2], pdId[3], pdId[4]]
        })
    else:
        tolog('lack of physical drive')
        exit()

    # get pool id
    plResponseInfo = server.webapi('get', 'pool')
    plInfo = json.loads(plResponseInfo['text'])
    plId = []
    for pl in plInfo:
        plId.append(pl['id'])

    return plId

def sharediskApiPost():
    Failflag = False
    plId = findPlId()

    # test date
    settingsList = {
        "pool_id": [plId[0], plId[0], plId[0]],
        "capacity": ['1GB', '2GB', '1TB'],
        "recsize": ['128KB', '512B', '1MB'],
        "sync": ['always', 'standard', 'disabled'],
        "logbias": ['latency', 'throughput', 'throughput']
    }
    compress = ['off', 'on', 'lzjb', 'gzip', 'gzip-1', 'gzip-9', 'zle', 'lz4']

    recsizeResult = ['128 KB', '512 Bytes', '1 MB']
    capacityResult = [1000000000, 2000000000, 1000000000000]

    # To add sharedisk by api
    tolog('To add sharedisk by api \r\n')
    for i in range(3):
        settings = {}
        for k in settingsList:
            settings[k] = settingsList[k][i]

        for comp in compress:
            expectResult = dict(settings.items() + {
                "name": 'testSharedisk_' + str(i) + comp[-1],
                "compress": comp
            }.items())

            tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
            server.webapi('post', 'sharedisk', expectResult)

            check = server.webapi('get', 'sharedisk')
            result = json.loads(check["text"])

            for r in result:
                if r["name"] == 'testSharedisk_' + str(i) + comp[-1]:
                    actualResult = r
                    tolog('Actual: ' + json.dumps(actualResult) + '\r\n')
                    for key in expectResult:
                        if key != "recsize" and key != "capacity":
                            if expectResult[key] != actualResult[key]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(expectResult[key]) + ' != ' + str(actualResult[key]))
                        elif key == "recsize":
                            if actualResult["recsize"] != recsizeResult[i]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(actualResult["recsize"]) + ' != ' + str(recsizeResult[i]))
                        elif key == "capacity":
                            if actualResult["total_capacity"] != capacityResult[i]:
                                Failflag = True
                                tolog('Fail: parameters ' + str(actualResult["total_capacity"]) + ' != ' + str(capacityResult[i]))

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def sharediskApiMountAndUnmount():
    Failflag = False
    tolog('Mount/Un-mount sharedisk by api \r\n')
    sdResponseInfo = server.webapi('get', 'sharedisk')
    sdInfo = json.loads(sdResponseInfo["text"])
    sdId = []
    for sd in sdInfo:
        sdId.append(sd['id'])

    # test data
    mount = ['mount', 'mount', 'unmount', 'mount']
    unmount = ['unmount', 'unmount', 'mount', 'unmount']

    mountResult = ['Mounted', 'Mounted', 'Un-Mounted', 'Mounted']
    unmountResult = ['Un-Mounted', 'Un-Mounted', 'Mounted', 'Un-Mounted']

    # To mount
    for i in range(4):
        tolog('Expect: ' + mount[i] + '\r\n')
        server.webapi('post', 'sharedisk/' + str(sdId[0]) + '/' + mount[i])

        check = server.webapi('get', 'sharedisk/' + str(sdId[0]))
        actualResult = json.loads(check["text"])[0]

        tolog('Actual: ' + str(actualResult["status"]) + '\r\n')

        if actualResult["status"] != mountResult[i]:
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["status"]) + '!=' + mountResult[i])

    # To un-mount
    for i in range(4):
        tolog('Expect: ' + unmount[i] + '\r\n')
        server.webapi('post', 'sharedisk/' + str(sdId[8]) + '/' + unmount[i])

        check = server.webapi('get', 'sharedisk/' + str(sdId[8]))
        actualResult = json.loads(check["text"])[0]

        tolog('Actual: ' + str(actualResult["status"]) + '\r\n')

        if actualResult["status"] != unmountResult[i]:
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["status"]) + '!=' + unmountResult[i])

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def sharediskApiModify():
    Failflag = False
    tolog('To modify sharedisk by api\r\n')

    # test data
    capacitySettings = ['1GB', '2GB', '2GB', '2TB']
    nameSettings = ['n', 'name_2', '123455', 'TestName']
    capacityResult = [1000000000, 2000000000, 2000000000, 2000000000000]

    for i in range(4):
        expectResult = {
            "name": nameSettings[i],
            "capacity": capacitySettings[i]
        }
        tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
        server.webapi('put', 'sharedisk/0', expectResult)

        check = server.webapi('get', 'sharedisk/0')
        actualResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps({
            "name": actualResult["name"],
            "total_capacity": actualResult["total_capacity"]
        })+ '\r\n')

        if str(actualResult["name"]) != nameSettings[i]:
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["name"]) + '!=' + nameSettings[i])

        if actualResult["total_capacity"] != capacityResult[i]:
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["total_capacity"]) + '!=' + str(capacityResult[i]))

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def sharediskApiList():
    Failflag = False

    # To verify search function
    tolog('To verify parameters: search/page/page_size \r\n')
    for i in [1, 10, 23]:
        tolog('Expect: To list sharedisk that id is ' + str(i) + '\r\n')

        searchResponse = server.webapi('get', 'sharedisk?page=1&page_size=' + str(i) + '&search=id+in+(' + str(i) + ')')
        actualResult = json.loads(searchResponse["text"])[0]

        tolog('Actual: The sharedisk id is ' + str(actualResult["id"]) + '\r\n')

        if actualResult['id'] != i:
            Failflag = True
            tolog('Fail: Did not find sharedisk of id ' + str(i))

    # server.webapi('get', 'sharedisk?sort="name,pool_name"&direct="asc"')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def sharediskApiDelete():
    Failflag = False
    # get sharedisk id
    sharediskId = []
    ResponseInfo = server.webapi('get', 'sharedisk?page_size=100')
    sharediskInfo = json.loads(ResponseInfo['text'])
    for info in sharediskInfo:
        sharediskId.append(info["id"])

    # To delete sharedisk by api
    tolog('To delete sharedisk by aip')
    for i in sharediskId:
        tolog('Expect: Delete sharedisk id is ' + str(i) + '\r\n')
        server.webapiurl('delete', 'sharedisk', str(i) + '?force=1')

        check = server.webapi('get', 'sharedisk')
        result = json.loads(check["text"])

        for r in result:
            if r["id"] == i:
                Failflag = True
                tolog('Fail: sharedisk ' + str(i) + ' is not deleted')
        if not Failflag:
            tolog('Actual: sharedisk ' + str(i) + ' is deleted \r\n')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def sharediskApiFailedTest():
    Failflag = False
    # test data
    settings = [
        [5, '1GB', '128KB', 'always', 'latency', 'gzip', 'FailedTest'],
        [0, '1KB', '128KB', 'always', 'latency', 'gzip', 'FailedTest'],
        [0, '1GB', '1GB', 'always', 'latency', 'gzip', 'FailedTest'],
        [0, '1GB', '128KB', 'test', 'latency', 'gzip', 'FailedTest'],
        [0, '1GB', '128KB', 'always', 'test', 'gzip', 'FailedTest'],
        [0, '1GB', '128KB', 'always', 'latency', 'test', 'FailedTest'],
        [0, '1GB', '128KB', 'always', 'latency', 'gzip', '#$@*']
    ]
    expectResult = [
        'Empty query result, please check input parameters. Pool id=[5] is not existed',
        '[capacity] must between 1GB to 1PB',
        'invalid recsize',
        'invalid sync',
        'invalid logbias',
        'invalid compress',
        'name contain only alphanumeric characters and underscores'
    ]

    for i in range(7):
        tolog('Expect: ' + expectResult[i] + '\r\n')

        parameters = {
            "pool_id": settings[i][0],
            "capacity": settings[i][1],
            "recsize": settings[i][2],
            "sync": settings[i][3],
            "logbias":settings[i][4],
            "compress": settings[i][5],
            "name": settings[i][6]
        }

        result = server.webapi('post', 'sharedisk', parameters)

        if expectResult[i] not in result:
            Failflag = True
            tolog('Fail: ' + expectResult[i])
        else:
            tolog('Actual: ' + result + '\r\n')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)


if __name__ == '__main__':
    sharediskApiPost()
    sharediskApiMountAndUnmount()
    sharediskApiModify()
    sharediskApiDelete()
    sharediskApiList()
    sharediskApiFailedTest()
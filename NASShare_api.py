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
            'name': 'testNASShareApi2',
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


def NASShareApiPost():
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

    # To add NASShare by api
    tolog('To add NASShare by api \r\n')
    for i in range(3):
        settings = {}
        for k in settingsList:
            settings[k] = settingsList[k][i]

        for comp in compress:
            expectResult = dict(settings.items() + {
                "name": 'testNASShare_' + str(i) + comp[-1],
                "compress": comp
            }.items())

            tolog('Expect: ' + json.dumps(expectResult) + '\r\n')
            server.webapi('post', 'nasshare', expectResult)

            check = server.webapi('get', 'nasshare?page=1&page_size=50')
            result = json.loads(check["text"])

            for r in result:
                if r["name"] == 'testNASShare_' + str(i) + comp[-1]:
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


def NASShareApiMountAndUnmount():
    Failflag = False
    tolog('Mount/Un-mount NASShare by api \r\n')
    sdResponseInfo = server.webapi('get', 'nasshare')
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
        server.webapi('post', 'nasshare/' + str(sdId[0]) + '/' + mount[i])

        check = server.webapi('get', 'nasshare/' + str(sdId[0]))
        actualResult = json.loads(check["text"])[0]

        tolog('Actual: ' + str(actualResult["status"]) + '\r\n')

        if actualResult["status"] != mountResult[i]:
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["status"]) + '!=' + mountResult[i])

    # To un-mount
    for i in range(4):
        tolog('Expect: ' + unmount[i] + '\r\n')
        server.webapi('post', 'nasshare/' + str(sdId[8]) + '/' + unmount[i])

        check = server.webapi('get', 'nasshare/' + str(sdId[8]))
        actualResult = json.loads(check["text"])[0]

        tolog('Actual: ' + str(actualResult["status"]) + '\r\n')

        if actualResult["status"] != unmountResult[i]:
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["status"]) + '!=' + unmountResult[i])

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)


def NASShareApiModify():
    Failflag = False
    tolog('To modify NASShare by api\r\n')

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
        server.webapi('put', 'nasshare/0', expectResult)

        check = server.webapi('get', 'nasshare/0')
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


def NASShareApiList():
    Failflag = False

    # To verify search function
    tolog('To verify parameters: search/page/page_size \r\n')
    for i in [1, 10, 23]:
        tolog('Expect: To list NASShare that id is ' + str(i) + '\r\n')

        searchResponse = server.webapi('get', 'nasshare?page=1&page_size=' + str(i) + '&search=id+in+(' + str(i) + ')')
        actualResult = json.loads(searchResponse["text"])[0]

        tolog('Actual: The NASShare id is ' + str(actualResult["id"]) + '\r\n')

        if actualResult['id'] != i:
            Failflag = True
            tolog('Fail: Did not find NASShare of id ' + str(i))

    # server.webapi('get', 'nasshare?sort="name,pool_name"&direct="asc"')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)


def NASShareApiDelete():
    Failflag = False
    # get NASShare id
    NASShareId = []
    ResponseInfo = server.webapi('get', 'nasshare?page_size=100')
    NASShareInfo = json.loads(ResponseInfo['text'])
    for info in NASShareInfo:
        NASShareId.append(info["id"])

    # To delete NASShare by api
    tolog('To delete NASShare by aip')
    for i in NASShareId:
        tolog('Expect: Delete NASShare id is ' + str(i) + '\r\n')
        server.webapiurl('delete', 'nasshare', str(i) + '?force=1')

        check = server.webapi('get', 'nasshare')
        result = json.loads(check["text"])

        for r in result:
            if r["id"] == i:
                Failflag = True
                tolog('Fail: NASShare ' + str(i) + ' is not deleted')

    if Failflag:
        tolog(Fail)
    else:
        tolog('Actual: NASShare ' + str(i) + ' is deleted \r\n')
        tolog(Pass)


def NASShareApiFailedTest():
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

        result = server.webapi('post', 'nasshare', parameters)

        if expectResult[i] not in result:
            Failflag = True
            tolog('Fail: ' + expectResult[i])
        else:
            tolog('Actual: ' + result + '\r\n')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

    # clean up environment
    server.webapiurl('delete', 'pool', '0?force=1')


def add_NASShare_missing_body():
    Failflag = False

    tolog('Expect: To add NASShare missing body will hint error\r\n')
    result1 = server.webapi('post', 'nasshare')

    if isinstance(result1, dict):

        Failflag = True
        tolog('Fail: add NASShare missing body\r\n')

    else:
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: To add NASShare by empty body will hint error\r\n')
    result2 = server.webapi('post', 'nasshare', {})

    if isinstance(result2, dict):

        Failflag = True
        tolog('Fail: add NASShare by empty body\r\n')

    else:
        tolog('Actual: ' + result2 + '\r\n')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)


def modify_NASShare_missing_body():
    Failflag = False

    tolog('Expect: To modify NASShare missing body will hint error\r\n')
    result1 = server.webapi('put', 'nasshare/0')

    if isinstance(result1, dict):

        Failflag = True
        tolog('Fail: modify NASShare missing body\r\n')

    else:
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: To modify NASShare by empty body will hint error\r\n')
    result2 = server.webapi('put', 'nasshare/0', {})

    if isinstance(result2, dict):

        Failflag = True
        tolog('Fail: modify NASShare by empty body\r\n')

    else:
        tolog('Actual: ' + result2 + '\r\n')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)


if __name__ == '__main__':
    NASShareApiPost()
    NASShareApiMountAndUnmount()
    NASShareApiModify()
    NASShareApiList()
    NASShareApiDelete()
    NASShareApiFailedTest()
    add_NASShare_missing_body()
    modify_NASShare_missing_body()
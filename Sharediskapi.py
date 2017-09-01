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
    mount = ['/mount', '/mount', '/unmount', '/mount']
    unmount = ['/unmount', '/unmount', '/mount', '/unmount']

    mountResult = ['Mounted', 'Mounted', 'Un-Mounted', 'Mounted']
    unmountResult = ['Un-Mounted', 'Un-Mounted', 'Mounted', 'Un-Mounted']

    # To mount
    for i in range(4):
        tolog('Expect: ' + mount[i] + '\r\n')
        server.webapi('post', 'sharedisk/' + str(sdId[0]) + mount[i])

        check = server.webapi('get', 'sharedisk/' + str(sdId[0]))
        actualResult = json.loads(check["text"])[0]

        tolog('Actual: ' + str(actualResult["status"]) + '\r\n')

        if actualResult["status"] != mountResult[i]:
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["status"]) + '!=' + mountResult[i])

    # To un-mount
    for i in range(4):
        tolog('Expect: ' + unmount[i] + '\r\n')
        server.webapi('post', 'sharedisk/' + str(sdId[8]) + unmount[i])

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
        server.webapi('put', 'sharedisk/2', expectResult)

        check = server.webapi('get', 'sharedisk/2')
        actualResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(actualResult))

        if str(actualResult["name"]) != str(nameSettings[i]):
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["name"]) + '!=' + nameSettings[i])

        if str(actualResult["total_capacity"]) != capacityResult[i]:
            Failflag = True
            tolog('Fail: parameters ' + str(actualResult["total_capacity"]) + '!=' + str(capacityResult[i]))

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)


def sharediskApiDelete():
    ResponseInfo = server.webapi('get', 'sharedisk')
    sharediskInfo = json.loads(ResponseInfo['text'])
    sharediskId = []
    for info in sharediskInfo:
        sharediskId.append(info["id"])
    for i in sharediskId:
        server.webapiurl('delete', 'sharedisk', str(i) + '?force=1')




if __name__ == '__main__':
    # sharediskApiPost()
    # sharediskApiDelete()
    # sharediskApiMountAndUnmount()
    sharediskApiModify()
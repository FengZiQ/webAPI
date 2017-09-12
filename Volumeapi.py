# coding = utf-8
# 2017.9.11

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
    plId = None
    createPool = server.webapi('post', 'pool', {
            'name': 'testVolumeApi',
            'sector': '512B',
            'raid_level': 'RAID5',
            'force_sync': 0,
            'pds': [pdId[3], pdId[5], pdId[6]]
        })

    if isinstance(createPool, str):
        tolog(createPool)
        tolog('Fail: To create pool is failed')
    else:
        plId = 0

    return plId

def addVolume():
    FailFlag = False
    tolog('add volume by api \r\n')

    # test data
    plId = findPlId()

    settingsList = [
        ['n', '12', 'Name_11', '1_name', '1'*31, '2'*32, 'a', '1', 'b'*31, 'T'*32],
        [plId for i in range(10)],
        ['1GB', '2GB', '3GB', '4GB', '5GB', '6GB', '9GB', '10GB', '1TB', '2TB'],
        ['512b', '1kb', '2kb', '4kb', '8kb', '16kb', '32kb', '64kb', '128kb', '512b'],
        ['512b', '1kb', '2kb', '4kb', '512b', '1kb', '2kb', '4kb', '512b', '1kb'],
        ['on', 'off', 'lzjb', 'gzip', 'gzip-1', 'gzip-2', 'gzip-8', 'gzip-9', 'zle', 'lz4'],
        ['standard', 'always', 'disabled', 'standard', 'always', 'disabled', 'standard', 'always', 'disabled', 'always'],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    ]

    checkpoint = [
        ['512 Bytes', '1 KB', '2 KB', '4 KB', '512 Bytes', '1 KB', '2 KB', '4 KB', '512 Bytes', '1 KB'],
        ['Disabled', 'Enabled', 'Disabled', 'Enabled', 'Disabled', 'Enabled', 'Disabled', 'Enabled', 'Disabled', 'Enabled'],
        ['512 Bytes', '1 KB', '2 KB', '4 KB', '8 KB', '16 KB', '32 KB', '64 KB', '128 KB', '512 Bytes']
    ]

    for i in range(len(settingsList[5])):
        settings = {
            "name": settingsList[0][i],
            "pool_id": settingsList[1][i],
            "capacity": settingsList[2][i],
            "block": settingsList[3][i],
            "sector": settingsList[4][i],
            "compress": settingsList[5][i],
            "sync": settingsList[6][i],
            "thin_prov": settingsList[7][i],
            "quantity": settingsList[8][i]
        }

        tolog('Expect: ' + json.dumps(settings) + '\r\n')

        result = server.webapi('post', 'volume', settings)

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        check = server.webapi('get', 'volume')
        checkResult = json.loads(check["text"])
        for cr in checkResult:
            if cr["id"] == i:
                tolog('Actual: ' + json.dumps(cr) + '\r\n')
                if settings["name"] != cr["name"]:
                    FailFlag = True
                    tolog('Fail: please check out parameter: name')

                if settings["pool_id"] != cr["pool_id"]:
                    FailFlag = True
                    tolog('Fail: please check out parameter: pool_id')

                if settings["sync"] != cr["sync"]:
                    FailFlag = True
                    tolog('Fail: please check out parameter: sync')

                if cr["sector"] != checkpoint[0][i]:
                    FailFlag = True
                    tolog('Fail: please check out parameter: sector ')

                if cr["thin_prov"] != checkpoint[1][i]:
                    FailFlag = True
                    tolog('Fail: please check out parameter: thin_prov')

                if cr["block"] != checkpoint[2][i]:
                    FailFlag = True
                    tolog('Fail: please check out parameter: block')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)

def listVolume():
    FailFlag = False
    tolog('Expect: List all of the volume \r\n')

    allResult = server.webapi('get', "volume")

    if isinstance(allResult, str):
        FailFlag = True
        tolog('Fail: ' + allResult)
    else:
        tolog('Actual: All of volume are listed \r\n')

        tolog('To list specify the volume \r\n')
        volumeId = []

        result = json.loads(allResult["text"])

        for r in result:
            volumeId.append(r["id"])

        if len(volumeId) > 0:
            for i in volumeId:
                tolog('Expect: list volume ' + str(i) + '\r\n')

                oneResult = server.webapiurl('get', 'volume', str(i))
                check = json.loads(oneResult["text"])[0]

                if isinstance(oneResult, str) or check["id"] != i:
                    FailFlag = True
                    tolog('Fail: To list volume ' + str(i) + ' is failed \r\n')
                else:
                    tolog('Actual: volume ' + str(i) + ' is listed \r\n')

    tolog('Expect: Search volume by volume name and pool_name \r\n')

    searchResult = server.webapi('get', "volume?page=1&page_size=25&search=name+like+'%n%' and pool_name+like+'%t%'")

    if isinstance(searchResult, str):
        FailFlag = True
        tolog('Fail: ' + searchResult + '\r\n')
    else:
        tolog('Actual: The qualified volume is listed \r\n')


    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)

def modifyVolume():
    FailFlag = False

    # test data
    settingsList = [['5'*31, '6'*32, 'x', '00']]

    for i in range(len(settingsList[0])):
        settings = {"name": settingsList[0][i]}

        tolog('Expect: To modify name ' + settings["name"] + '\r\n')

        result = server.webapi('put', 'volume/0', settings)

        check = server.webapi('get', 'volume/0')
        checkResult = json.loads(check["text"])[0]

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        if settings["name"] != checkResult["name"]:
            FailFlag = True
            tolog('Fail: name ' + settings["name"] + ' != ' + checkResult["name"] + '\r\n')
        else:
            tolog('Actual: after modification name is ' + checkResult["name"] + '\r\n')


    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)

def exportVolume():
    FailFlag = False
    tolog('Export volume \r\n')



def deleteVolume():
    FailFlag = False
    tolog('delete volume by api \r\n')

    volumeId = []

    volumeResponse = server.webapi('get', 'volume?page=1&page_size=100')
    volumeInfo = json.loads(volumeResponse["text"])

    for info in volumeInfo:
        volumeId.append(info["id"])

    for i in volumeId:
        tolog('Expect: To delete volume ' + str(i) + '\r\n')

        result = server.webapiurl('delete', 'volume', str(i) + '?force=1')

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        checkResponse = server.webapi('get', 'volume?page=1&page_size=100')
        checkResult = json.loads(checkResponse["text"])

        for cR in checkResult:
            if cR['id'] != i:
                FailFlag = True
                tolog('Fail: The volume ' + str(i) + ' is not deleted \r\n')
            else:
                tolog('Actual: the volume ' + str(i) + ' is deleted \r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


if __name__ == "__main__":
    # addVolume()
    # listVolume()
    modifyVolume()
    # deleteVolume()


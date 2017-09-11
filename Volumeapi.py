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


def addVolume():
    FailFlag = False
    tolog('add volume by api \r\n')

    # test data
    # findPlId()

    settingsList = [
        ['n', '12', 'Name_11', '1_name', '1'*31, '2'*32, 'N', '1', 'T'*31, 'T'*32],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ['1GB', '2GB', '3GB', '4GB', '5GB', '6GB', '9GB', '10GB', '1TB', '2TB'],
        ['512b', '1kb', '2kb', '4kb', '8kb', '16kb', '32kb', '64kb', '128kb', '512b'],
        ['512b', '1kb', '2kb', '4kb', '512b', '1kb', '2kb', '4kb', '512b', '1kb'],
        ['on', 'off', 'lzjb', 'gzip', 'gzip-1', 'gzip-2', 'gzip-8', 'gzip-9', 'zle', 'lz4'],
        ['standard', 'always', 'disabled', 'standard', 'always', 'disabled', 'standard', 'always', 'disabled', 'always'],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
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
                for key in settings:
                    if settings[key] != 'capacity':
                        if settings[key] != cr[key]:
                            FailFlag = True
                            tolog('Fail: please check out ' + str(settings[key]) + ' != ' + str(cr[key]))

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)



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
            if cR['id'] == i:
                FailFlag = True
                tolog('Fail: The volume ' + str(i) + ' is not deleted \r\n')
            else:
                tolog('Actual: the volume ' + str(i) + ' is deleted \r\n')
        else:
            tolog('Actual: the volume ' + str(i) + ' is deleted \r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


if __name__ == "__main__":
    addVolume()
    # deleteVolume()
# coding = utf-8
# 2017.9.11

from remote import server
import json
from to_log import tolog
import time

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
    plId = []
    createPool1 = server.webapi('post', 'pool', {
            'name': 'testVolumeApi1',
            'sector': '512B',
            'raid_level': 'RAID5',
            'force_sync': 0,
            'pds': [pdId[3], pdId[7], pdId[8]]
        })

    if isinstance(createPool1, str):
        tolog(createPool1)
        tolog('Fail: To create pool is failed')
    else:
        plId.append(0)

    createPool2 = server.webapi('post', 'pool', {
        'name': 'testVolumeApi2',
        'sector': '512B',
        'raid_level': 'RAID0',
        'force_sync': 0,
        'pds': [pdId[1]]
    })

    if isinstance(createPool2, str):
        tolog(createPool2)
        tolog('Fail: To create pool is failed')
    else:
        plId.append(1)

    return plId


def addVolume():
    FailFlag = False
    tolog('add volume by api use all of settings \r\n')

    # test data
    plId = findPlId()

    settingsList = [
        ['n', '12', 'Name_11', '1_name', '1'*31, '2'*32, 'a', '1', 'b'*31, 'T'*32],
        [plId[0] for i in range(10)],
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
                    tolog('Fail: please check out parameter name')

                if settings["pool_id"] != cr["pool_id"]:
                    FailFlag = True
                    tolog('Fail: please check out parameter pool_id')

                if settings["sync"] != cr["sync"]:
                    FailFlag = True
                    tolog('Fail: please check out parameter sync')

                if cr["sector"] != checkpoint[0][i]:
                    FailFlag = True
                    tolog('Fail: please check out parameter sector ')

                if cr["thin_prov"] != checkpoint[1][i]:
                    FailFlag = True
                    tolog('Fail: please check out parameter thin_prov')

                if cr["block"] != checkpoint[2][i]:
                    FailFlag = True
                    tolog('Fail: please check out parameter block')

    tolog('add volume by api use must settings \r\n')

    # test data
    mustParameters = {
        "name": 'Must_parameters',
        "capacity": '1GB',
        "pool_id": 0
    }

    defaultValues = {
        "block": '8 KB',
        "sector": '512 Bytes',
        "compress": 'off',
        "sync": 'always'
    }

    tolog('Expect: ' + json.dumps(dict(mustParameters.items() + defaultValues.items())) + '\r\n')

    mustsettings = server.webapi('post', 'volume', mustParameters)

    if isinstance(mustsettings, str):
        FailFlag = True
        tolog('Fail: ' + mustsettings + '\r\n')

    check2 = server.webapi('get', "volume?page=1&page_size=50&search=name+like+'%Must_parameters%'")
    checkResult2 = json.loads(check2["text"])[0]

    tolog('Actual: ' + json.dumps(checkResult2) + '\r\n')

    if isinstance(check2, dict):
        if checkResult2["name"] != mustParameters["name"]:
            FailFlag = True
            tolog('Fail: please check out parameter name \r\n')

        if checkResult2["pool_id"] != mustParameters["pool_id"]:
            FailFlag = True
            tolog('Fail: please check out parameter pool_id \r\n')

        for key in defaultValues:
            if key != 'compress':
                if defaultValues[key] != checkResult2[key]:
                    FailFlag = True
                    tolog('Fail: please check out parameter ' + key + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def listVolume():
    FailFlag = False
    tolog('Expect: List all of the volume \r\n')

    allResult = server.webapi('get', "volume")
    result = json.loads(allResult["text"])

    if isinstance(allResult, str):
        FailFlag = True
        tolog('Fail: ' + allResult)
    else:
        allVolumeInfo = str(result).replace('{', '').replace('u', '').replace('}', '\r\n')

        tolog('Actual: All of volumes \r\n' + allVolumeInfo + '\r\n')

        tolog('To list specify the volume \r\n')
        volumeId = []

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
                    specifyResult = str(check).replace('u', '')
                    tolog('Actual: \r\n' + specifyResult + '\r\n')

    tolog('Expect: Searching volume by volume name contains "n" and pool_name contains "t" \r\n')

    searchResult = server.webapi('get', "volume?page=1&page_size=25&search=name+like+'%n%' and pool_name+like+'%t%'")

    if isinstance(searchResult, str):
        FailFlag = True
        tolog('Fail: ' + searchResult + '\r\n')
    else:
        search = str(json.loads(searchResult["text"]))
        tolog('Actual:\r\n' + search.replace('u', ''))

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

    volumeResponse = server.webapi('get', 'volume/1')
    volumeInfo = json.loads(volumeResponse["text"])[0]

    if volumeInfo["status"] == "Exported":

        # precondition
        server.webapiurl('post', 'volume/1', 'unexport')
        time.sleep(1)

        tolog('Expect: export volume \r\n')
        result = server.webapiurl('post', 'volume/1', 'export')

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        check = server.webapi('get', 'volume/1')
        checkResult = json.loads(check["text"])[0]

        if checkResult["status"] != 'Exported':
            FailFlag = True
            tolog('Fail: To export volume is failed\r\n')
        else:
            tolog('Actual: volume export successfully \r\n')

    else:
        tolog('Expect: export volume \r\n')
        result = server.webapiurl('post', 'volume/1', 'export')

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        check = server.webapi('get', 'volume/1')
        checkResult = json.loads(check["text"])[0]

        if checkResult["status"] != 'Exported':
            FailFlag = True
            tolog('Fail: To export volume is failed\r\n')
        else:
            tolog('Actual: volume export successfully \r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def unexportVolume():
    FailFlag = False
    tolog('Un-Export volume \r\n')

    volumeResponse = server.webapi('get', 'volume/1')
    volumeInfo = json.loads(volumeResponse["text"])[0]

    if volumeInfo["status"] == "Un-Exported":

        # precondition
        server.webapiurl('post', 'volume/1', 'export')
        time.sleep(1)

        tolog('Expect: un-export volume \r\n')
        result = server.webapiurl('post', 'volume/1', 'unexport')

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        check = server.webapi('get', 'volume/1')
        checkResult = json.loads(check["text"])[0]

        if checkResult["status"] != 'Un-Exported':
            FailFlag = True
            tolog('Fail: To un-export volume is failed\r\n')
        else:
            tolog('Actual: volume un-export successfully \r\n')

    else:
        tolog('Expect: un-export volume \r\n')
        result = server.webapiurl('post', 'volume/1', 'unexport')

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        check = server.webapi('get', 'volume/1')
        checkResult = json.loads(check["text"])[0]

        if checkResult["status"] != 'Un-Exported':
            FailFlag = True
            tolog('Fail: To un-export volume is failed\r\n')
        else:
            tolog('Actual: un-volume export successfully \r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def invalidSettingNameVolume():
    FailFlag = False
    tolog('Verify invalid setting name \r\n')

    # test data
    settingsNameList = [
        ['a#', 0, '1GB', '512b', '512b', 'zip', 'always', 0, 1],
        ['a'*33, 0, '1GB', '512b', '512b', 'zip', 'always', 0, 1],
        ['', 0, '1GB', '512b', '512b', 'zip', 'always', 0, 1]
    ]

    for i in range(3):
        settings = {
            "name": settingsNameList[i][0],
            "pool_id": settingsNameList[i][1],
            "capacity": settingsNameList[i][2],
            "block": settingsNameList[i][3],
            "sector": settingsNameList[i][4],
            "compress": settingsNameList[i][5],
            "sync": settingsNameList[i][6],
            "thin_prov": settingsNameList[i][7],
            "quantity": settingsNameList[i][8]
        }

        tolog('Expect: hint naming rules \r\n')

        result = server.webapi('post', 'volume', settings)

        if isinstance(result, dict):
            FailFlag = True
            tolog("Fail: " + json.dumps(settings) + '\r\n')
        else:
            tolog('Actual: ' + result + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def invalidSettingVolume():
    FailFlag = False
    tolog('Verify invalid setting \r\n')

    # test data
    settingsList = [
        # invalid setting pool_id
        ['legal_name1', 100, '1GB', '512b', '512b', 'off', 'always', 0, 1],
        ['legal_name2', 'test', '1GB', '512b', '512b', 'off', 'always', 0, 1],

        # invalid setting capacity
        ['legal_name3', 0, '1B', '512b', '512b', 'off', 'always', 0, 1],
        ['legal_name4', 0, 0, '512b', '512b', 'off', 'always', 0, 1],

        # invalid setting block
        ['legal_name5', 0, '1GB', '512GB', '512b', 'off', 'always', 0, 1],
        ['legal_name6', 0, '1GB', 0, '512b', 'off', 'always', 0, 1],

        # invalid setting sector
        ['legal_name7', 0, '1GB', '512b', '512GB', 'off', 'always', 0, 1],
        ['legal_name8', 0, '1GB', '512b', 0, 'off', 'always', 0, 1],

        # invalid setting compress
        ['legal_name9', 0, '1GB', '512b', '512b', 'test', 'always', 0, 1],
        ['legal_name10', 0, '1GB', '512b', '512b', 0, 'always', 0, 1],

        # invalid setting sync
        ['legal_name11', 0, '1GB', '512b', '512b', 'off', 'test', 0, 1],
        ['legal_name12', 0, '1GB', '512b', '512b', 'off', 0, 0, 1],

        # invalid setting thin_prov
        ['legal_name13', 0, '1GB', '512b', '512b', 'off', 'always', 2, 1],
        ['legal_name14', 0, '1GB', '512b', '512b', 'off', 'always', 'test', 1],

        # invalid setting quantity
        ['legal_name15', 0, '1GB', '512b', '512b', 'off', 'always', 0, 0],
        ['legal_name16', 0, '1GB', '512b', '512b', 'off', 'always', 0, -1],
        ['legal_name17', 0, '1GB', '512b', '512b', 'off', 'always', 0, 'test']
    ]

    expectResult = [
        'invalid setting pool_id',
        'invalid setting pool_id',
        'invalid setting capacity',
        'invalid setting capacity',
        'invalid setting block',
        'invalid setting block',
        'invalid setting sector',
        'invalid setting sector',
        'invalid setting compress',
        'invalid setting compress',
        'invalid setting sync',
        'invalid setting sync',
        'invalid setting thin_prov',
        'invalid setting thin_prov',
        'invalid setting quantity',
        'invalid setting quantity',
        'invalid setting quantity'
    ]

    for i in range(len(settingsList)):
        settings = {
            "name": settingsList[i][0],
            "pool_id": settingsList[i][1],
            "capacity": settingsList[i][2],
            "block": settingsList[i][3],
            "sector": settingsList[i][4],
            "compress": settingsList[i][5],
            "sync": settingsList[i][6],
            "thin_prov": settingsList[i][7],
            "quantity": settingsList[i][8]
        }

        tolog('Expect: ' + expectResult[i] + '\r\n')

        result = server.webapi('post', 'volume', settings)

        if isinstance(result, dict):
            FailFlag = True
            tolog("Fail: " + json.dumps(settings) + '\r\n')
        else:
            tolog('Actual: ' + result + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_volume_miss_body():
    FailFlag = False

    tolog('Expect: To add volume missing body will hint error\r\n')
    result1 = server.webapi('post', 'volume')

    if isinstance(result1, dict):

        FailFlag = True
        tolog('Fail: add volume missing body\r\n')

    else:
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: To add volume by empty body will hint error\r\n')
    result2 = server.webapi('post', 'volume', {})

    if isinstance(result2, dict):
        FailFlag = True
        tolog('Fail: add volume missing body\r\n')

    else:
        tolog('Actual: ' + result2 + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def modify_volume_miss_body():
    FailFlag = False

    tolog('Expect: To modify volume missing body will hint error\r\n')
    result1 = server.webapi('put', 'volume/0')

    if isinstance(result1, dict):

        FailFlag = True
        tolog('Fail: modify volume missing body\r\n')

    else:
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: To modify volume by empty body will hint error\r\n')
    result2 = server.webapi('put', 'volume/0', {})

    if isinstance(result2, dict):

        FailFlag = True
        tolog('Fail: modify volume by empty body\r\n')

    else:
        tolog('Actual: ' + result2 + '\r\n')

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

        if not FailFlag:
            tolog('volume ' + str(i) + ' is deleted \r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)

    # clean up environment
    server.webapiurl('delete', 'pool', '0?force=1')
    server.webapiurl('delete', 'pool', '1?force=1')


if __name__ == "__main__":
    addVolume()
    # listVolume()
    # modifyVolume()
    # exportVolume()
    # unexportVolume()
    # invalidSettingNameVolume()
    # invalidSettingVolume()
    # add_volume_miss_body()
    # modify_volume_miss_body()
    # deleteVolume()
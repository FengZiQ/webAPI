# coding = utf-8
# 2017.9.26

from remote import server
import json
from to_log import tolog

Pass = "'result': 'p'"
Fail = "'result': 'f'"


def find_pdId():

    pdId = []

    # delete pool
    poolResponse = server.webapi('get', 'pool')

    if isinstance(poolResponse, dict):
        poolInfo = json.loads(poolResponse["text"])

        for pool in poolInfo:
            server.webapiurl('delete', 'pool', str(pool['id']) + '?force=1')

    # find pd id
    pdResponse = server.webapi('get', 'phydrv')
    pdInfo = json.loads(pdResponse["text"])

    for pd in pdInfo:
        if pd["cfg_status"] == 'Unconfigured' and pd["media_type"] == 'HDD':
            pdId.append(pd["id"])

    if len(pdId) < 10:
        tolog('\r\nLack of the physical drive\r\n')

    return pdId


def add_pool_raid0():
    FailFlag = False

    # test data
    pdId = find_pdId()

    setting = {
        "sector": "512B",
        "ctrl_id": 2,
        "name": "t",
        "pds": pdId,
        "raid_level": "raid0",
        "stripe": "64KB",
        "force_sync": 0
    }

    checkpoint = {
        "sector": "512 Bytes",
        "prefer_ctrl_id": 2,
        "name": "t",
        "pds": str(pdId).replace('[', '').replace(']', '').replace(', ', ','),
        "raid_level": 0,
        "stripe": "64 KB",
        "force_sync": 'Disabled'
    }

    tolog('Expect: ' + json.dumps(setting) + '\r\n')
    result = server.webapi('post', 'pool', setting)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        check = server.webapi('get', 'pool')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for key in checkpoint:

            if checkResult[key] != checkpoint[key]:

                FailFlag = True
                tolog('Fail: please check out parameter ' + key + '\r\n')
                tolog(str(checkResult[key]) + '!=' + str(checkpoint[key]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_pool_raid1():
    FailFlag = False

    # test data
    pdId = find_pdId()

    setting = {
        "sector": "1KB",
        "ctrl_id": 2,
        "name": "TN",
        "pds": [pdId[0], pdId[1]],
        "raid_level": "raid1",
        "stripe": "128KB",
        "force_sync": 1
    }

    checkpoint = {
        "sector": "1 KB",
        "prefer_ctrl_id": 2,
        "name": "TN",
        "pds": str(pdId[0]) + ',' + str(pdId[1]),
        "raid_level": 1,
        "stripe": "128 KB",
        "force_sync": 'Enabled'
    }

    tolog('Expect: ' + json.dumps(setting) + '\r\n')
    result = server.webapi('post', 'pool', setting)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        check = server.webapi('get', 'pool')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for key in checkpoint:

            if checkResult[key] != checkpoint[key]:

                FailFlag = True
                tolog('Fail: please check out parameter ' + key + '\r\n')
                tolog(str(checkResult[key]) + '!=' + str(checkpoint[key]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_pool_raid5():
    FailFlag = False

    # test data
    pdId = find_pdId()

    setting = {
        "sector": "2KB",
        "ctrl_id": 2,
        "name": '1'*31,
        "pds": pdId,
        "raid_level": "raid5",
        "stripe": "256KB",
        "force_sync": 1
    }

    checkpoint = {
        "sector": "2 KB",
        "prefer_ctrl_id": 2,
        "name": '1'*31,
        "pds": str(pdId).replace('[', '').replace(']', '').replace(', ', ','),
        "raid_level": 5,
        "stripe": "256 KB",
        "force_sync": 'Enabled'
    }

    tolog('Expect: ' + json.dumps(setting) + '\r\n')
    result = server.webapi('post', 'pool', setting)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        check = server.webapi('get', 'pool')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for key in checkpoint:

            if checkResult[key] != checkpoint[key]:

                FailFlag = True
                tolog('Fail: please check out parameter ' + key + '\r\n')
                tolog(str(checkResult[key]) + '!=' + str(checkpoint[key]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_pool_raid6():
    FailFlag = False

    # test data
    pdId = find_pdId()

    setting = {
        "sector": "4KB",
        "ctrl_id": 2,
        "name": '2'*31,
        "pds": pdId,
        "raid_level": "raid6",
        "stripe": "512KB",
        "force_sync": 0
    }

    checkpoint = {
        "sector": "4 KB",
        "prefer_ctrl_id": 2,
        "name": '2'*31,
        "pds": str(pdId).replace('[', '').replace(']', '').replace(', ', ','),
        "raid_level": 6,
        "stripe": "512 KB",
        "force_sync": 'Disabled'
    }

    tolog('Expect: ' + json.dumps(setting) + '\r\n')
    result = server.webapi('post', 'pool', setting)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        check = server.webapi('get', 'pool')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for key in checkpoint:

            if checkResult[key] != checkpoint[key]:

                FailFlag = True
                tolog('Fail: please check out parameter ' + key + '\r\n')
                tolog(str(checkResult[key]) + '!=' + str(checkpoint[key]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_pool_raid10():
    FailFlag = False

    # test data
    pdId = find_pdId()

    setting = {
        "sector": "2KB",
        "ctrl_id": 2,
        "name": "Test_",
        "pds": pdId[1:],
        "raid_level": "raid10",
        "stripe": "64KB",
        "force_sync": 0
    }

    checkpoint = {
        "sector": "2 KB",
        "prefer_ctrl_id": 2,
        "name": "Test_",
        "pds": str(pdId[1:]).replace('[', '').replace(']', '').replace(', ', ','),
        "raid_level": 10,
        "stripe": "64 KB",
        "force_sync": 'Disabled'
    }

    tolog('Expect: ' + json.dumps(setting) + '\r\n')
    result = server.webapi('post', 'pool', setting)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        check = server.webapi('get', 'pool')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for key in checkpoint:

            if checkResult[key] != checkpoint[key]:

                FailFlag = True
                tolog('Fail: please check out parameter ' + key + '\r\n')
                tolog(str(checkResult[key]) + '!=' + str(checkpoint[key]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_pool_raid50():
    FailFlag = False

    # test data
    pdId = find_pdId()

    setting = {
        "sector": "4KB",
        "ctrl_id": 2,
        "name": "_1",
        "pds": pdId,
        "raid_level": "raid50",
        "stripe": "512KB",
        "axle": 3,
        "force_sync": 0
    }

    checkpoint = {
        "sector": "4 KB",
        "prefer_ctrl_id": 2,
        "name": "_1",
        "pds": str(pdId).replace('[', '').replace(']', '').replace(', ', ','),
        "raid_level": 50,
        "stripe": "512 KB",
        "axle": 3,
        "force_sync": 'Disabled'
    }

    tolog('Expect: ' + json.dumps(setting) + '\r\n')
    result = server.webapi('post', 'pool', setting)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        check = server.webapi('get', 'pool')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for key in checkpoint:

            if checkResult[key] != checkpoint[key]:

                FailFlag = True
                tolog('Fail: please check out parameter ' + key + '\r\n')
                tolog(str(checkResult[key]) + '!=' + str(checkpoint[key]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_pool_raid60():
    FailFlag = False

    # test data
    pdId = find_pdId()

    setting = {
        "sector": "512B",
        "ctrl_id": 2,
        "name": "1_T",
        "pds": pdId,
        "raid_level": "raid60",
        "stripe": "1MB",
        "axle": 2,
        "force_sync": 0
    }

    checkpoint = {
        "sector": "512 Bytes",
        "prefer_ctrl_id": 2,
        "name": "1_T",
        "pds": str(pdId).replace('[', '').replace(']', '').replace(', ', ','),
        "raid_level": 60,
        "stripe": "1 MB",
        "axle": 2,
        "force_sync": 'Disabled'
    }

    tolog('Expect: ' + json.dumps(setting) + '\r\n')
    result = server.webapi('post', 'pool', setting)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        check = server.webapi('get', 'pool')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for key in checkpoint:

            if checkResult[key] != checkpoint[key]:

                FailFlag = True
                tolog('Fail: please check out parameter ' + key + '\r\n')
                tolog(str(checkResult[key]) + '!=' + str(checkpoint[key]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_pool_default():
    FailFlag = False

    # test data
    pdId = find_pdId()

    setting = {
        "name": "test_default",
        "pds": [pdId[0], pdId[1], pdId[2]],
        "raid_level": "raid5"
    }

    checkpoint = {
        "sector": "512 Bytes",
        "prefer_ctrl_id": 1,
        "name": "test_default",
        "pds": str(pdId[0]) + ',' + str(pdId[1]) + ',' + str(pdId[2]),
        "raid_level": 5,
        "stripe": "64 KB",
        "axle": 1,
        "force_sync": 'Disabled'
    }

    tolog('Expect: ' + json.dumps(setting) + '\r\n')
    result = server.webapi('post', 'pool', setting)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        check = server.webapi('get', 'pool')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for key in checkpoint:

            if checkResult[key] != checkpoint[key]:
                FailFlag = True
                tolog('Fail: please check out parameter ' + key + '\r\n')
                tolog(str(checkResult[key]) + '!=' + str(checkpoint[key]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def list_all_of_pool():
    FailFlag = False

    # test data
    pdId = find_pdId()

    # precondition
    server.webapi('post', 'pool', {
        "name": "test_list_1",
        "pds": [pdId[0]],
        "raid_level": "raid0"
    })

    server.webapi('post', 'pool', {
        "name": "test_list_2",
        "pds": [pdId[1], pdId[2]],
        "raid_level": "raid1"
    })

    server.webapi('post', 'pool', {
        "name": "test_list_3",
        "pds": [pdId[3], pdId[4], pdId[5]],
        "raid_level": "raid5"
    })

    server.webapi('post', 'pool', {
        "name": "test_list_4",
        "pds": [pdId[6], pdId[7], pdId[8], pdId[9]],
        "raid_level": "raid6"
    })

    # list all of pool
    tolog('Expect: list all of pool \r\n')

    result = server.webapi('get', 'pool')

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        checkResult = json.loads(result["text"])

        poolInfo = ''

        for pool in checkResult:
            poolInfo = poolInfo + json.dumps(pool) + '\r\n'

        tolog('Actual: \r\n' + poolInfo)

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def search_pool():
    FailFlag = False

    # search of pool
    tolog('Expect: search of pool by name "test_list_2" \r\n')

    result = server.webapi('get', "pool?page=1&page_size=25&search=name+like+'%test_list_2%'")

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        checkResult = json.loads(result["text"])[0]

        tolog('Actual: \r\n' + json.dumps(checkResult) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def rename_pool():
    FailFlag = False

    # rename pool
    tolog('rename pool\r\n')

    # test data
    name = ['a', 'a_', '1'*31, '2'*32, '1_g']

    for i in range(len(name)):

        tolog('Expect: To modify name is ' + name[i] + '\r\n')
        result = server.webapi('put', 'pool/0/rename', {"name": name[i]})

        if isinstance(result, str):

            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = server.webapi('get', 'pool/0')
            checkResult = json.loads(check["text"])[0]

            tolog('Actual ' + json.dumps(checkResult) + '\r\n')

            if checkResult["name"] != name[i]:
                FailFlag = True
                tolog('Fail: please check out name after modified\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def view_pool():
    FailFlag = False

    # test data
    checkpoint = [
        'name', 'raid_level', 'pref_ctrl', 'stripe', 'sector', 'force_sync',
        'total_capacity', 'used_capacity', 'usage', 'pool_avail', 'pd_info',
        'free_capacity', 'status', 'ctrl_id', 'pds', 'pd_group', 'pool_reserved'
    ]

    # view pool
    tolog('Expect: returned values contain ' + str(checkpoint).replace('[', '').replace(']', '') + '\r\n')
    result = server.webapiurl('get', 'pool', '3')

    if isinstance(result, str):

        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = json.loads(result["text"])[0]

        checkResult = [key for key in check]

        for key in checkpoint:

            if key not in str(checkResult):

                FailFlag = True
                tolog('Fail: please check out ' + key + ' in returned result\r\n')

        else:

            tolog('Actual: ' + str(checkResult).replace('[', '').replace(']', '').replace('u', '') + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def get_pool_global_setting():
    FailFlag = False

    # test data
    upper_limit = 95
    lower_limit = 75

    tolog('Expect: The value of capacity_threshold range is ' + str(lower_limit) + '-' + str(upper_limit) + '\r\n')
    result = server.webapi('get', 'poolglobal')

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        checkResult = json.loads(result["text"])[0]

        if checkResult["capacity_threshold"] < lower_limit or checkResult["capacity_threshold"] > upper_limit:

            FailFlag = True
            tolog('Fail: The capacity_threshold value is ' + str(checkResult["capacity_threshold"]) + "\r\n")

        else:
            tolog('Actual: capacity_threshold is ' + str(checkResult["capacity_threshold"]) + "\r\n")

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def set_pool_global_setting():
    FailFlag = False

    # test data
    capacity_threshold = [75, 76, 94, 95]

    for i in range(len(capacity_threshold)):

        tolog('Expect: modify pool global setting is ' + str(capacity_threshold[i]) + '\r\n')
        result = server.webapi('post', 'poolglobal', {"capacity_threshold": capacity_threshold[i]})

        if isinstance(result, str):

            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = server.webapi('get', 'poolglobal')
            checkResult = json.loads(check["text"])[0]

            if checkResult["capacity_threshold"] != capacity_threshold[i]:

                FailFlag = True
                tolog('Fail: please check out result after modified')

            else:
                tolog('Actual: modified result is ' + str(checkResult["capacity_threshold"]) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def transfer_pool():
    FailFlag = False

    # test data
    ctrl_id = [1, 2]

    # precondition
    poolResponse = server.webapiurl('get', 'pool', '3')
    poolInfo = json.loads(poolResponse["text"])[0]

    for i in range(len(ctrl_id)):

        if poolInfo["prefer_ctrl_id"] == 1:

            tolog('Expect: transfer pool ctrl ' + str(ctrl_id[1]) + ' from ctrl 1\r\n')
            result = server.webapi('put', 'pool/3/transfer', {"prefer_ctrl_id": ctrl_id[1]})

            if isinstance(result, str):

                FailFlag = True
                tolog('Fail: ' + result + '\r\n')

            else:
                tolog('Actual: pool transfer ctrl 1 to ctrl ' + str(ctrl_id[1]) + '\r\n')

        elif poolInfo["prefer_ctrl_id"] == 2:

            tolog('Expect: transfer pool ctrl ' + str(ctrl_id[0]) + ' from ctrl 2\r\n')
            result = server.webapi('put', 'pool/3/transfer', {"prefer_ctrl_id": ctrl_id[0]})

            if isinstance(result, str):

                FailFlag = True
                tolog('Fail: ' + result + '\r\n')

            else:
                tolog('Actual: pool transfer ctrl 2 to ctrl ' + str(ctrl_id[0]) + '\r\n')


    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def extend_pool_raid0():
    FailFlag = False

    # test data
    pdId = find_pdId()

    # precondition
    server.webapi('post', 'pool', {
        "name": "test_list_1",
        "pds": [pdId[0]],
        "raid_level": "raid0"
    })

    tolog('Expend pd list ' + str([i for i in pdId[1:]]) + '\r\n')
    result = server.webapi('put', 'pool/0/extend', {"pds": [i for i in pdId[1:]]})

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = server.webapi('get', 'pool/0')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual ' + checkResult["pds"] + '\r\n')

        if checkResult["pds"] != str(pdId).replace('[', '').replace(']', '').replace(', ', ','):
            FailFlag = True
            tolog('Fail: please check out pds after extend\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def extend_pool_raid1():
    FailFlag = False

    # test data
    pdId = find_pdId()

    # precondition
    server.webapi('post', 'pool', {
        "name": "test_list_1",
        "pds": [pdId[0], pdId[1]],
        "raid_level": "raid1"
    })

    tolog('Expend pd list ' + str([i for i in pdId[-3: -1]]) + '\r\n')
    result = server.webapi('put', 'pool/0/extend', {"pds": [i for i in pdId[-3: -1]]})

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = server.webapi('get', 'pool/0')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual ' + checkResult["pds"] + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def extend_pool_raid5():
    FailFlag = False

    # test data
    pdId = find_pdId()

    # precondition
    server.webapi('post', 'pool', {
        "name": "test_list_1",
        "pds": [pdId[0], pdId[2], pdId[1]],
        "raid_level": "raid5"
    })

    tolog('Expend pd list ' + str([i for i in pdId[3:]]) + '\r\n')
    result = server.webapi('put', 'pool/0/extend', {"pds": [i for i in pdId[3:]]})

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = server.webapi('get', 'pool/0')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual ' + checkResult["pds"] + '\r\n')

        if checkResult["pds"] != str(pdId).replace('[', '').replace(']', '').replace(', ', ','):
            FailFlag = True
            tolog('Fail: please check out pds after extend\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def extend_pool_raid6():
    FailFlag = False

    # test data
    pdId = find_pdId()

    # precondition
    server.webapi('post', 'pool', {
        "name": "test_list_1",
        "pds": [pdId[0], pdId[2], pdId[1], pdId[3]],
        "raid_level": "raid6"
    })

    tolog('Expend pd list ' + str([i for i in pdId[4:]]) + '\r\n')
    result = server.webapi('put', 'pool/0/extend', {"pds": [i for i in pdId[4:]]})

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = server.webapi('get', 'pool/0')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual ' + checkResult["pds"] + '\r\n')

        if checkResult["pds"] != str(pdId).replace('[', '').replace(']', '').replace(', ', ','):
            FailFlag = True
            tolog('Fail: please check out pds after extend\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def extend_pool_raid10():
    FailFlag = False

    # test data
    pdId = find_pdId()

    # precondition
    server.webapi('post', 'pool', {
        "name": "test_list_1",
        "pds": [pdId[2], pdId[1], pdId[3], pdId[4]],
        "raid_level": "raid10"
    })

    tolog('Expend pd list ' + str([i for i in pdId[5:]]) + '\r\n')
    result = server.webapi('put', 'pool/0/extend', {"pds": [i for i in pdId[5:]]})

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = server.webapi('get', 'pool/0')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual ' + checkResult["pds"] + '\r\n')

        if checkResult["pds"] != str(pdId[1:]).replace('[', '').replace(']', '').replace(', ', ','):
            FailFlag = True
            tolog('Fail: please check out pds after extend\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def extend_pool_raid50():
    FailFlag = False

    # test data
    pdId = find_pdId()

    if len(pdId) >= 12:
        # precondition
        server.webapi('post', 'pool', {
            "name": "test_list_1",
            "pds": pdId[:6],
            "raid_level": "raid50"
        })

        tolog('Expend pd list ' + str([i for i in pdId[6:]]) + '\r\n')
        result = server.webapi('put', 'pool/0/extend', {"pds": [i for i in pdId[6:]]})

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = server.webapi('get', 'pool/0')
            checkResult = json.loads(check["text"])[0]

            tolog('Actual ' + checkResult["pds"] + '\r\n')

            if checkResult["pds"] != str(pdId).replace('[', '').replace(']', '').replace(', ', ','):
                FailFlag = True
                tolog('Fail: please check out pds after extend\r\n')

    else:
        tolog('\r\nLack of physical drive\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def extend_pool_raid60():
    FailFlag = False

    # test data
    pdId = find_pdId()

    if len(pdId) >= 16:
        # precondition
        server.webapi('post', 'pool', {
            "name": "test_list_1",
            "pds": pdId[:8],
            "raid_level": "raid60"
        })

        tolog('Expend pd list ' + str([i for i in pdId[8:]]) + '\r\n')
        result = server.webapi('put', 'pool/0/extend', {"pds": [i for i in pdId[8:]]})

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = server.webapi('get', 'pool/0')
            checkResult = json.loads(check["text"])[0]

            tolog('Actual ' + checkResult["pds"] + '\r\n')

            if checkResult["pds"] != str(pdId).replace('[', '').replace(']', '').replace(', ', ','):
                FailFlag = True
                tolog('Fail: please check out pds after extend\r\n')

    else:
        tolog('\r\nLack of physical drive\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def delete_pool():
    FailFlag = False

    # test data
    poolId = []

    # precondition
    pdId = find_pdId()

    server.webapi('post', 'pool', {
        "name": "test_list_1",
        "pds": [pdId[0]],
        "raid_level": "raid0"
    })

    server.webapi('post', 'pool', {
        "name": "test_list_2",
        "pds": [pdId[1], pdId[2]],
        "raid_level": "raid1"
    })

    server.webapi('post', 'pool', {
        "name": "test_list_3",
        "pds": [pdId[3], pdId[4], pdId[5]],
        "raid_level": "raid5"
    })

    server.webapi('post', 'pool', {
        "name": "test_list_4",
        "pds": [pdId[6], pdId[7], pdId[8], pdId[9]],
        "raid_level": "raid6"
    })

    poolResponse = server.webapi('get', 'pool')
    poolInfo = json.loads(poolResponse["text"])

    for pool in poolInfo:

        poolId.append(pool["id"])

    for i in poolId:

        tolog('Expect: delete pool ' + str(i) + '\r\n')

        result = server.webapiurl('delete', 'pool', str(i) + '?force=1')

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            tolog('Actual: pool ' + str(i) + ' is deleted\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def invalid_pool_name():
    FailFlag = False

    # test data
    pdId = find_pdId()
    name = ['', '3'*33, 'a#']

    for i in range(len(name)):

        tolog('Expect: hint error when pool name sets ' + name[i] + '\r\n')

        result = server.webapi('post', 'pool', {
            "name": name[i],
            "pds": [pdId[0]],
            "raid_level": "raid0"
        })

        if isinstance(result, dict):
            FailFlag = True
            tolog('Fail: pool name can set ' + name[i] + '\r\n')

        else:
            tolog('Actual: ' + result + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def invalid_pool_parameters():
    FailFlag = False

    # test data
    pdId = find_pdId()

    key = ['name', 'pds', 'raid_level', 'axle', 'ctrl_id', 'stripe', 'sector', 'force_sync']

    values = [
        # invalid pds
        ['1', [], 'raid0', 2, 1, '64KB', '512B', 0],
        ['2', [100], 'raid0', 2, 1, '64KB', '512B', 0],
        # invalid raid_level
        ['3', [pdId[0]], 'test', 2, 1, '64KB', '512B', 0],
        # invalid axle
        ['4', pdId, 'raid50', 4, 1, '64KB', '512B', 0],
        # invalid ctrl_id
        ['5', [pdId[0]], 'raid0', 2, 3, '64KB', '512B', 0],
        # invalid strip
        ['6', [], 'raid', 2, 1, '2MB', '512B', 0],
        # invalid sector
        ['7', [], 'raid', 2, 1, '64KB', '512KB', 0],
        # invalid force_sync
        ['7', [], 'raid', 2, 1, '64KB', '512KB', -1]
    ]

    for i in range(len(values)):

        settings = dict(zip(key, values[i]))

        tolog('Expect: ' + json.dumps(settings) + '\r\n')
        result = server.webapi('post', 'pool', settings)

        if isinstance(result, dict):

            FailFlag = True
            tolog('Fail parameters ' + json.dumps(settings) + ' can be set\r\n')

        else:
            tolog('Actual: ' + result + '\r\n')


    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def add_pool_missing_body():
    FailFlag = False

    tolog('Expect: To add pool missing body will hint error\r\n')
    result1 = server.webapi('post', 'pool')

    if isinstance(result1, dict):

        FailFlag = True
        tolog('Fail: add pool missing body\r\n')

    else:
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: To add pool by empty body will hint error\r\n')
    result2 = server.webapi('post', 'pool', {})

    if isinstance(result2, dict):
        FailFlag = True
        tolog('Fail: add pool missing body\r\n')

    else:
        tolog('Actual: ' + result2 + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def transfer_pool_missing_body():
    FailFlag = False

    # test data
    pdId = find_pdId()

    # precondition
    server.webapi('post', 'pool', {
        "name": "test_",
        "pds": pdId[:3],
        "raid_level": "raid5"
    })

    tolog('Expect: To transfer pool missing body will come true\r\n')
    result1 = server.webapi('put', 'pool/0/transfer')

    if isinstance(result1, str):

        FailFlag = True
        tolog('Fail: ' + result1 + '\r\n')

    else:
        tolog('Actual: pool successfully transfer\r\n')

    tolog('Expect: To transfer pool by empty body will come true\r\n')
    result2 = server.webapi('put', 'pool/0/transfer', {})

    if isinstance(result2, str):

        FailFlag = True
        tolog('Fail: ' + result2 + '\r\n')

    else:
        tolog('Actual: pool successfully transfer\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def extend_pool_missing_body():
    FailFlag = False

    tolog('Expect: To extend pool missing body will hint error\r\n')
    result1 = server.webapi('post', 'pool/0/extend')

    if isinstance(result1, dict):

        FailFlag = True
        tolog('Fail: extend pool missing body\r\n')

    else:
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: To extend pool by empty body will hint error\r\n')
    result2 = server.webapi('post', 'pool/0/extend', {})

    if isinstance(result2, dict):
        FailFlag = True
        tolog('Fail: extend pool missing body\r\n')

    else:
        tolog('Actual: ' + result2 + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def list_pool_missing_body():
    FailFlag = False

    tolog('Expect: To list pool missing body will come true\r\n')
    result1 = server.webapi('get', 'pool')

    if isinstance(result1, str):

        FailFlag = True
        tolog('Fail: ' + result1 + '\r\n')

    else:
        tolog('Actual: successfully get pool list\r\n')

    tolog('Expect: To list pool by empty body will come true\r\n')
    result2 = server.webapi('get', 'pool', {})

    if isinstance(result2, str):

        FailFlag = True
        tolog('Fail: ' + result2 + '\r\n')

    else:
        tolog('Actual: successfully get pool list\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def rename_pool_missing_body():
    FailFlag = False

    tolog('Expect: To rename pool missing body will hint error\r\n')
    result1 = server.webapi('put', 'pool/0/rename')

    if isinstance(result1, dict):

        FailFlag = True
        tolog('Fail: rename pool missing body\r\n')

    else:
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: To rename pool by empty body will hint error\r\n')
    result2 = server.webapi('put', 'pool/0/rename', {})

    if isinstance(result2, dict):
        FailFlag = True
        tolog('Fail: rename pool missing body\r\n')

    else:
        tolog('Actual: ' + result2 + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def set_pool_global_missing_body():
    FailFlag = False

    tolog('Expect: To set pool global missing body will hint error\r\n')
    result1 = server.webapi('post', 'poolglobal')

    if isinstance(result1, dict):

        FailFlag = True
        tolog('Fail: set pool global missing body\r\n')

    else:
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: To set pool global by empty body will hint error\r\n')
    result2 = server.webapi('post', 'poolglobal', {})

    if isinstance(result2, dict):
        FailFlag = True
        tolog('Fail: set pool global missing body\r\n')

    else:
        tolog('Actual: ' + result2 + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


if __name__ == "__main__":
    add_pool_raid0()
    add_pool_raid1()
    add_pool_raid5()
    add_pool_raid6()
    add_pool_raid10()
    add_pool_raid50()
    add_pool_raid60()
    add_pool_default()
    list_all_of_pool()
    search_pool()
    rename_pool()
    view_pool()
    get_pool_global_setting()
    set_pool_global_setting()
    transfer_pool()
    extend_pool_raid0()
    extend_pool_raid1()
    extend_pool_raid5()
    extend_pool_raid6()
    extend_pool_raid10()
    extend_pool_raid50()
    extend_pool_raid60()
    delete_pool()
    invalid_pool_name()
    invalid_pool_parameters()
    add_pool_missing_body()
    transfer_pool_missing_body()
    extend_pool_missing_body()
    list_pool_missing_body()
    rename_pool_missing_body()
    set_pool_global_missing_body()
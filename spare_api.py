# coding = utf-8
# 2017.9.25

from remote import server
import json
from to_log import tolog

Pass = "'result': 'p'"
Fail = "'result': 'f'"


def find_pd_id():

    pd_id2 = []
    pd_id4 = []

    # delete pool
    poolResponse = server.webapi('get', 'pool')

    if isinstance(poolResponse, dict):
        poolInfo = json.loads(poolResponse["text"])

        for pool in poolInfo:
            server.webapiurl('delete', 'pool', str(pool['id']) + '?force=1')

    # delete spare
    spareResponse = server.webapi('get', 'spare')

    if isinstance(spareResponse, dict):
        spareInfo = json.loads(spareResponse["text"])

        for spare in spareInfo:
            server.webapiurl('delete', 'spare', str(spare["id"]))

    # find pd id
    pdResponse = server.webapi('get', 'phydrv')
    pdInfo = json.loads(pdResponse["text"])

    for pd in pdInfo:
        if pd["cfg_status"] == 'Unconfigured' and pd["physical_capacity"] == '2 TB' and pd["media_type"] == 'HDD':
            pd_id2.append(pd["id"])

        if pd["cfg_status"] == 'Unconfigured' and pd["physical_capacity"] == '4 TB' and pd["media_type"] == 'HDD':
            pd_id4.append(pd["id"])

    return pd_id2, pd_id4


def post_global_spare_revertible_0():
    FailFlag = False
    tolog('add global spare drive that is not revertible by api\r\n')

    # test data
    pdId2, pdId4 = find_pd_id()

    settings = {
        "dedicated": 'Global',
        "revertible": 0,
        "pd_id": pdId4[-1],
        "pool_list": []
    }

    # precondition
    server.webapi('post', 'pool', {
        'name': 'test_spare1',
        'raid_level': 'RAID5',
        'pds': [pdId2[0], pdId2[1], pdId2[2]]
    })

    tolog('Expect: ' + json.dumps(settings) + '\r\n')

    result = server.webapi('post', 'spare', settings)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        spareResponse = server.webapi('get', 'spare')

        if isinstance(spareResponse, dict):
            spareInfo = json.loads(spareResponse["text"])
            tolog('Actual: ' + json.dumps(spareInfo[0]) + '\r\n')

            for value in settings.values():

                if str(value) not in json.dumps(spareInfo[0]):
                    FailFlag = True
                    tolog("Fail: please check out parameter " + str(value) + '\r\n')

        # server.webapiurl('post', 'phydrv', str(pdId2[0]) + '/offline')
        #
        # time.sleep(3)
        #
        # rbResponse = server.webapi('get', 'rebuild')
        #
        # if isinstance(rbResponse, str):
        #     FailFlag = True
        #     tolog('Fail: ' + rbResponse + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def post_global_spare_revertible_1():
    FailFlag = False
    tolog('add global spare drive that is revertible by api\r\n')

    # test data
    pdId2, pdId4 = find_pd_id()

    settings = {
        "dedicated": 'Global',
        "revertible": 1,
        "pd_id": pdId4[-1],
        "pool_list": []
    }

    # precondition
    server.webapi('post', 'pool', {
        'name': 'test_spare1',
        'raid_level': 'RAID5',
        'pds': [pdId2[0], pdId2[1], pdId2[2]]
    })

    tolog('Expect: ' + json.dumps(settings) + '\r\n')

    result = server.webapi('post', 'spare', settings)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        spareResponse = server.webapi('get', 'spare')

        if isinstance(spareResponse, dict):
            spareInfo = json.loads(spareResponse["text"])
            tolog('Actual: ' + json.dumps(spareInfo[0]) + '\r\n')

            for value in settings.values():

                if str(value) not in json.dumps(spareInfo[0]):
                    FailFlag = True
                    tolog("Fail: please check out parameter " + str(value) + '\r\n')

        # server.webapiurl('post', 'phydrv', str(pdId2[0]) + '/offline')
        #
        # time.sleep(3)
        #
        # rbResponse = server.webapi('get', 'rebuild')
        #
        # if isinstance(rbResponse, str):
        #     FailFlag = True
        #     tolog('Fail: ' + rbResponse + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def post_dedicated_spare_revertible_0():
    FailFlag = False
    tolog('add dedicated spare drive that is not revertible by api\r\n')

    # test data
    pdId2, pdId4 = find_pd_id()

    settings = {
        "dedicated": 'Dedicated',
        "revertible": 0,
        "pd_id": pdId4[-1],
        "pool_list": [0, 1]
    }

    # precondition
    server.webapi('post', 'pool', {
        'name': 'test_spare1',
        'raid_level': 'RAID5',
        'pds': [pdId2[0], pdId2[1], pdId2[2]]
    })

    server.webapi('post', 'pool', {
        'name': 'test_spare2',
        'raid_level': 'RAID5',
        'pds': [pdId4[0], pdId4[1], pdId4[2]]
    })

    tolog('Expect: ' + json.dumps(settings) + '\r\n')

    result = server.webapi('post', 'spare', settings)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        spareResponse = server.webapi('get', 'spare')

        if isinstance(spareResponse, dict):
            spareInfo = json.loads(spareResponse["text"])
            tolog('Actual: ' + json.dumps(spareInfo[0]) + '\r\n')

            for value in settings.values():

                if str(value) not in json.dumps(spareInfo[0]):
                    FailFlag = True
                    tolog("Fail: please check out parameter " + str(value) + '\r\n')

        # server.webapiurl('post', 'phydrv', str(pdId2[0]) + '/offline')
        #
        # time.sleep(3)
        #
        # rbResponse = server.webapi('get', 'rebuild')
        #
        # if isinstance(rbResponse, str):
        #     FailFlag = True
        #     tolog('Fail: ' + rbResponse + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def post_dedicated_spare_revertible_1():
    FailFlag = False
    tolog('add dedicated spare drive that is revertible by api\r\n')

    # test data
    pdId2, pdId4 = find_pd_id()

    settings = {
        "dedicated": 'Dedicated',
        "revertible": 1,
        "pd_id": pdId4[-1],
        "pool_list": [0]
    }

    # precondition
    server.webapi('post', 'pool', {
        'name': 'test_spare1',
        'raid_level': 'RAID5',
        'pds': [pdId2[0], pdId2[1], pdId2[2]]
    })

    tolog('Expect: ' + json.dumps(settings) + '\r\n')

    result = server.webapi('post', 'spare', settings)

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:
        spareResponse = server.webapi('get', 'spare')

        if isinstance(spareResponse, dict):
            spareInfo = json.loads(spareResponse["text"])
            tolog('Actual: ' + json.dumps(spareInfo[0]) + '\r\n')

            for value in settings.values():

                if str(value) not in json.dumps(spareInfo[0]):
                    FailFlag = True
                    tolog("Fail: please check out parameter " + str(value) + '\r\n')

        # server.webapiurl('post', 'phydrv', str(pdId2[0]) + '/offline')
        #
        # time.sleep(3)
        #
        # rbResponse = server.webapi('get', 'rebuild')
        #
        # if isinstance(rbResponse, str):
        #     FailFlag = True
        #     tolog('Fail: ' + rbResponse + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def get_spare():
    FailFlag = False

    # test data
    pdId2, pdId4 = find_pd_id()

    # precondition
    server.webapi('post', 'pool', {
        'name': 'test_spare1',
        'raid_level': 'RAID5',
        'pds': [pdId2[0], pdId2[1], pdId2[2]]
    })

    key = ["dedicated", "revertible", "pd_id", "pool_list"]

    values = [
        ['Global', 0, pdId2[-1], []],
        ['Global', 1, pdId4[0], []],
        ['Dedicated', 0, pdId4[1], [0]],
        ['Dedicated', 1, pdId4[2], [0]]
    ]

    for i in range(len(values)):
        tolog('Expect: ' + json.dumps(dict(zip(key, values[i]))) + '\r\n')

        pre = server.webapi('post', 'spare', dict(zip(key, values[i])))

        if isinstance(pre, str):
            tolog('please check out precondition: ' + pre + '\r\n')

    # list all of spare
    tolog('list all of spare drive\r\n')

    result = server.webapi('get', 'spare')

    if isinstance(result, str):
        FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        checkResult = json.loads(result["text"])

        if len(checkResult) < 4:
            FailFlag = True
            tolog('Fail: please check out spare drive quantity\r\n')

        tolog('Actual:\r\n' + str(checkResult).replace('{', '').replace('u', '').replace('}', '\r\n') + '\r\n')

    # list specific spare drive
    tolog('list specific spare drive\r\n')
    spareInfo = json.loads(result["text"])

    for spare in spareInfo:
        tolog('Expect: list spare drive ' + str(spare["id"]) + '\r\n')

        one = server.webapiurl('get', 'spare', str(spare["id"]))

        if isinstance(one, str):
            FailFlag = True
            tolog('Fail: ' + one + '\r\n')

        else:
            oneCheck = json.loads(one["text"])[0]

            tolog('Actual: ' + json.dumps(oneCheck) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def delete_spare():
    FailFlag = False
    tolog('delete spare drive by api')

    # precondition
    spareResponse = server.webapi('get', 'spare')
    spareInfo = json.loads(spareResponse["text"])

    for spare in spareInfo:
        tolog('Expect: delete spare drive ' + str(spare["id"]) + '\r\n')

        result = server.webapiurl('delete', 'spare', str(spare["id"]))

        if isinstance(result, str):
            FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:
            tolog('Actual: spare drive ' + str(spare["id"]) + ' is deleted\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def failing_post_spare():
    FailFlag = False

    # test data
    pdId2, pdId4 = find_pd_id()

    # precondition
    server.webapi('post', 'pool', {
        'name': 'test_spare1',
        'raid_level': 'RAID5',
        'pds': [pdId2[0], pdId2[1], pdId2[2]]
    })

    key = ["dedicated", "revertible", "pd_id", "pool_list"]

    values = [
        ['test', 0, pdId2[-1], []],
        [0, 1, pdId4[0], []],
        ['Global', 2, pdId4[1], [0]],
        ['Dedicated', 'test', pdId4[2], [0]],
        ['Global', 0, 100, []],
        ['Dedicated', 1, 'test', []],
        ['Dedicated', 1, pdId4[2], ['10', '12']]
    ]

    for i in range(len(values)):
        tolog('Expect: ' + json.dumps(dict(zip(key, values[i]))) + '\r\n')

        result = server.webapi('post', 'spare', dict(zip(key, values[i])))

        if isinstance(result, str):
            tolog('Actual: ' + result + '\r\n')

        else:
            FailFlag = True
            tolog('Fail: please ' + json.dumps(dict(zip(key, values[i]))) + '\r\n')

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)

    # clean up environment
    server.webapiurl('delete', 'pool', '0?force=1')


def failing_get_spare():
    FailFlag = False

    tolog('Expect: list spare drive that is inexistent\r\n')

    result = server.webapiurl('get', 'spare', '1000')

    if isinstance(result, str):
        tolog('Actual: ' + result + '\r\n')

    else:
        FailFlag = True
        tolog('Fail: ' + str(json.loads(result["text"])))

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)


def failing_delete_spare():
    FailFlag = False

    tolog('Expect: delete spare drive that is inexistent\r\n')

    result = server.webapiurl('delete', 'spare', '1000')

    if isinstance(result, str):
        tolog('Actual: ' + result + '\r\n')

    else:
        FailFlag = True
        tolog('Fail: ' + str(json.loads(result["text"])))

    if FailFlag:
        tolog(Fail)
    else:
        tolog(Pass)

if __name__ == "__main__":
    post_global_spare_revertible_0()
    post_global_spare_revertible_1()
    post_dedicated_spare_revertible_0()
    post_dedicated_spare_revertible_1()
    get_spare()
    delete_spare()
    failing_post_spare()
    failing_get_spare()
    failing_delete_spare()
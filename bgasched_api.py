import time
from remote import server
import json
import unicodedata
from to_log import tolog
import requests

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

def BgascheduleApiAdd():
    Failflag = False
    tolog("Verify BgascheduleAdd info by api")

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
                                          'sector': '512B', 'raid_level': 'RAID5',
                                          'ctrl_id': 1, 'force_sync': 0,
                                          'pds': [pdId[0], pdId[1], pdId[2]]
                                          })
        server.webapi('post', 'pool', {'name': 'testBgaschedApi3',
                                          'sector': '512B', 'raid_level': 'RAID0',
                                          'ctrl_id': 1, 'force_sync': 0,
                                          'pds': [pdId[3]]
                                          })

    bga_type = ['rc', 'brc', 'sc']

    # add bgasched of daily type
    tolog('add bgasched of daily type')
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

                tolog('Expect:' + json.dumps(parameters))
                expectResult = dict(dayTypeParameters.items() +{
                    'bga_type': bga_type[i],
                    "recurrence_type": "Daily",
                    'rc_pools': [0],
                    "rc_fix": 0,
                    "rc_pause": 0
                }.items())

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                tolog('Actual:' + json.dumps(result[1]))
                actualResult = result[1]

                for key in expectResult.keys():
                    if expectResult[key] != actualResult[key]:
                        Failflag = True

                deleteBgaschedule()

            else:
                parameters = dict({'bga_type': bga_type[i], 'recurrence_type': 1}.items() + dayTypeParameters.items())
                server.webapi('post', 'bgaschedule', parameters)

                tolog('Expect:' + json.dumps(parameters))
                expectResult = dict(
                    dayTypeParameters.items() +{'bga_type': bga_type[i], "recurrence_type": "Daily"}.items()
                )

                check = server.webapi('get', 'bgaschedule')
                result = json.loads(check['text'])

                tolog('Actual:' + json.dumps(result[0]))
                actualResult = result[0]

                for key in expectResult.keys():
                    if expectResult[key] != actualResult[key]:
                        Failflag = True

                deleteBgaschedule()

        return Failflag

    # Failflag = addDailyBgasched()

    # add bgasched of weekly type
    tolog('add bgasched of weekly type')
    



    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def Bgascheduleinfo():
    Failflag = False
    tolog("Verify Bgaschedule list info by api")
    expectResponse = {"id": ['rc_1', 'rc_2', 'brc', 'sc'],
                      "bga_type": ['rc', 'brc', 'sc'],
                      "status": [0, 1],
                      "start_time": [x for x in range(0, 1439)],
                      "day_start": [x for x in range(1, 31)],
                      "month_start": [x for x in range(1, 12)],
                      "year_start": [x for x in range(1970, 2037)],
                      "recurrence_type": ['daily', 'weekly', 'monthly'],
                      "interval": [x for x in range(1, 255)],
                      "day_mask": ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat'],
                      "day_pattern": ['day', 'ordinal'],
                      "month_mask": [x for x in range(1, 12)],
                      "day_of_month": [x for x in range(1, 31)],
                      "ordinal": ['1st', '2nd', '3rd', '4th', 'Last'],
                      "day_of_week": ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat'],
                      "range_end": ['none', 'count', 'date'],
                      "recurrence_count": [x for x in range(0, 255)],
                      "day_end": [x for x in range(1, 31)],
                      "month_end": [x for x in range(1, 12)],
                      "year_end": [x for x in range(1970, 2037)],
                      "rc_fix": [0, 1],
                      "rc_pause": [0, 1],
                      "rc_pools": [x for x in range(0, 31)]
                      }

    bgaSchedulerinfo = server.webapi("get", "bgaschedule")
    actualResponse = json.loads(bgaSchedulerinfo["text"])
    for bgaschedule in actualResponse:

        tolog(str(bgaschedule))

    return Failflag

def BgascheduleApiDel():
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



if __name__ == "__main__":
    BgascheduleApiAdd()
    # Bgascheduleinfo()
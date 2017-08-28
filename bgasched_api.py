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
    # add bgasched of daily type



    # bodyParameters = {"bga_type": "brc",
    #                   "status": 1,
    #                   "start_time": 60,
    #                   "recurrence_type": 1,
    #                   "day_pattern": 0,
    #                   "day_of_month": 1,
    #                   "month_mask": 4095,
    #                   "year_start": 2017,
    #                   "month_start": 8,
    #                   "day_start": 17,
    #                   "range_end": 1
    #                   }
    # result = server.webapi('post', 'bgaschedule', bodyParameters)
    # print result['parameters']
    # print result["response"]
    #
    # checkResult = server.webapi('get', 'bgaschedule')
    #
    #
    # a=json.loads(checkResult['text'])
    # print a
    #
    # server.webapiurl('delete', 'bgaschedule','brc')



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
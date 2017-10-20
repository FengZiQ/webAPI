# coding = utf-8
# 2017.10.20

from remote import server
import json
from to_log import tolog
from result_assert import result_assert
from find_unconfigured_pd_id import find_pd_id


def precondition():
    pdId = find_pd_id('4TB')
    # create pool
    server.webapi('post', 'pool', {"name": "test_quota_API", "pds": pdId, "raid_level": "raid5"})

    # create nasShare
    server.webapi('post', 'nasshare', {'pool_id': 0, 'name': 'test_protocol_api', 'capacity': '2GB'})

    # create clone
    server.webapi('post', 'snapshot', {"name": "test_quota_API_s", "type": 'nasshare', "source_id": 0})

    server.webapi('post', 'clone', {"name": "test_quota_API_c", "source_id": 0})


def get_quota_by_default_path_parameter():
    # precondition
    # precondition()

    # test data
    id = ['nasshare_0', 'clone_0']
    response = ['status', 'qt_list']

    for i in range(len(id)):

        tolog('Expect: \r\n' + str(response) + '\r\n')
        result = server.webapi('get', 'quota/' + id[i])

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = json.loads(result["text"])[0]
            tolog('Actual: \r\n' + str(check.keys()).replace('u', '') + '\r\n')

            if len(response) != len(check.keys()):

                result_assert.FailFlag = True
                tolog('Fail: please check out response parameters count\r\n')

            else:

                for key in check:

                    if key not in response:
                        
                        result_assert.FailFlag = True
                        tolog('Fail: ' + key + ' is not in response\r\n')

    result_assert.result_assert()








if __name__ == "__main__":
    get_quota_by_default_path_parameter()
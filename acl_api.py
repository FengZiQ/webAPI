# coding = utf-8
# 2017.10.9

from remote import server
import json
from to_log import tolog
from result_assert import result
from find_unconfigured_pd_id import find_pd_id


def precondition():

    # create pool
    pdId = find_pd_id()

    server.webapi('post', 'pool', {
        "name": "test_ACL",
        "pds": pdId[:3],
        "raid_level": "raid5"
    })

    # create nas share
    server.webapi('post', 'nasshare', {
        "pool_id": 0,
        "name": 'test_ACL_nasShare',
        "capacity": "10GB"
    })

    # create DSUser
    for i in range(20):
        server.webapi('post', 'dsuser', {
                "id": 'test_ACL_' + str(i),
                "password": '123456'
            })

    # create group
    server.webapi('post', 'dsgroup/addgrpcancel')
    step1 = server.webapi('post', 'dsgroup/addgrpbegin', {
        "id": 'test_ACL_group',
        "page": 1,
        "page_size": 20
    })

    token = str(json.loads(step1["text"])[0]["token"])

    step2 = server.webapi('post', 'dsgroup/addgrpnext', {
        "token": token,
        "page_data": [[1, 1001]],
        "page": 1,
        "page_size": 20
    })

    step3 = server.webapi('post', 'dsgroup/addgrpsave', {
        "id": 'test_ACL_group',
        "token": token,
        "page_data": [[1, 1001]]
    })



if __name__ == "__main__":
    precondition()
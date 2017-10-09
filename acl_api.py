# coding = utf-8
# 2017.10.9

from remote import server
import json
from to_log import tolog
from result_assert import result
from find_unconfigured_pd_id import find_pd_id


def precondition():
    pdId = find_pd_id()

    server.webapi('post', 'pool', {
        "name": "test_ACL",
        "pds": pdId[:3],
        "raid_level": "raid5"
    })



if __name__ == "__main__":
    precondition()
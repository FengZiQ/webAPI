# -*- coding: utf-8 -*-
# 2017.10.09

from remote import server
import json

def find_pd_id(physical_capacity = None):

    pd_id = []

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

    if physical_capacity == None:

        for pd in pdInfo:
            if pd["cfg_status"] == 'Unconfigured' and pd["media_type"] == 'HDD':
                pd_id.append(pd["id"])

    elif physical_capacity == '2TB':

        for pd in pdInfo:
            if pd["cfg_status"] == 'Unconfigured' and pd["physical_capacity"] == '2 TB' and pd["media_type"] == 'HDD':
                pd_id.append(pd["id"])

    elif physical_capacity == '4TB':

        for pd in pdInfo:
            if pd["cfg_status"] == 'Unconfigured' and pd["physical_capacity"] == '4 TB' and pd["media_type"] == 'HDD':
                pd_id.append(pd["id"])

    return pd_id
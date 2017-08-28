import time
from remote_imporved import server
from pool import random_key

import json
import random
from to_log import tolog
import requests

Pass = "'result': 'p'"
Fail = "'result': 'f'"

sectormap = {"512b": "512 Bytes", "1kb": "1 KB", "2kb": "2 KB", "4kb": "4 KB"}

def poolcreatewithallsettings():
    Failflag = False
    name = random_key(30)
    stripesettings = ["64kb", "128kb", "256kb", "512kb", "1mb"]
    sectorsettings = ["512b", "1kb", "2kb", "4kb"]
    force_syncsettings = [0, 1]

    stripemap = {"64kb": "64 KB", "128kb": "128 KB", "256kb": "256 KB", "512kb": "512 KB", "1mb": "1 MB"}
    force_syncmap = {0: "Disabled", 1: "Enabled"}
    raidmap = {"RAID0": 0, "RAID1": 1, "RAID5": 5, "RAID6": 6, "RAID10": 10, "RAID50": 50, "RAID60": 60}
    raids = ["RAID0","RAID1","RAID5","RAID6","RAID10","RAID50","RAID60"]
    availpdlist = getavailpd()
    for raidlevel in raids:
        for stripe in stripesettings:
            for sector in sectorsettings:
                for force_sync in force_syncsettings:
                    if raidlevel=="RAID0":
                        availpdlist=random.sample(availpdlist,2)
                    parameters = {
        "name": name, "pds": availpdlist, "raid_level": raidlevel, "ctrl_id": 1, "stripe": stripe, "sector": sector,
        "force_sync": force_sync}
                    #server.webapiurlbody("post","pool",body=parameters)
                    #print parameters
                    createobj("pool",parameters)
                    res=json.loads(viewobj("pool",0))[0]
                    getpdstr=str(res["pds"]).replace("u","")
                    parapdstr=str(parameters["pds"]).replace("[","").replace("]","").replace(" ","")
                    if res["name"]==parameters["name"] and getpdstr==parapdstr and res["stripe"]==stripemap[parameters["stripe"]]\
                            and res["sector"]==sectormap[parameters["sector"]] and res["force_sync"]==force_syncmap[parameters["force_sync"]] and \
                        res["raid_level"]==raidmap[parameters["raid_level"]]:
                        tolog("Succesfully created pool with parameters %s" %(str(parameters)))
                    else:
                        Failflag=True
                        tolog("Failed to create pool  with parameters %s" % (str(parameters)))

                    deleteobj("pool",0)

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)
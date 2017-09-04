# -*- coding: utf-8 -*-

from remote import server
import json
from to_log import tolog

Pass = "'result': 'p'"
Fail = "'result': 'f'"


def addUser():
    Failflag = False
    settingsList = [
        ['a', 'n'*31, 'test_name', '123'],
        [1, 0, 0, 1],
        ['View', 'Maintenance', 'Power', 'Super'],
        ['', 'N'*31, 'display_name', '123_test'],
        ['', '1@11.11', 'a@aa.aac', '1@11.1234'],
        ['', 'pass_word', '1'*8, 'p'*31]
    ]

    for i in range(4):
        settings = {
            "id": settingsList[0][i],
            "status": settingsList[1][i],
            "privilege": settingsList[2][i],
            "display_name": settingsList[3][i],
            "email": settingsList[4][i],
            "passwd": settingsList[5][i]
        }
        tolog('Expect: ' + json.dumps(settings) + '\r\n')

        server.webapi('post', 'user', settings)

        check = server.webapi('get', 'user/' + settingsList[0][i])
        result = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(result) + '\r\n')
        for key in settings:
            if key != 'passwd':
                if result[key] != settings[key]:
                    Failflag = True
                    tolog('Fail: parameters ' + str(result[key]) + '!=' + str(settings[key]))

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def addSnmpUser():
    Failflag = False
    settingsList = [
        ['b', 'B'*31],
        ['md5', 'sha'],
        ['des', 'aes'],
        ['1'*8, '1*31'],
        ['1'*8, '1*31']
    ]

    for i in range(2):
        settings = {
            "id": settingsList[0][i],
            "auth_protocol": settingsList[1][i],
            "priv_protocol": settingsList[2][i],
            "priv_passwd": settingsList[3][i],
            "auth_passwd": settingsList[4][i]
        }

        tolog('Expect: ' + json.dumps(settings) + '\r\n')

        a= server.webapi('post', 'snmpuser', settings)

        print a



def deleteUser():
    userResponse = server.webapi('get', 'user')
    userInfo = json.loads(userResponse["text"])
    id = []
    for uId in userInfo:
        if uId["id"] != "administrator":
            id.append(uId["id"])

    for i in id:
        server.webapiurl('delete', 'user', i)




if __name__ == '__main__':
    # addUser()
    addSnmpUser()
    # deleteUser()
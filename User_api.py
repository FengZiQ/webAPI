# -*- coding: utf-8 -*-

from remote import server
import json
from to_log import tolog

Pass = "'result': 'p'"
Fail = "'result': 'f'"


def addUser():
    Failflag = False
    settingsList = [
        ['a', 'n'*31, 'test_name', '1'*30],
        [1, 0, 0, 1],
        ['View', 'Maintenance', 'Power', 'Super'],
        ['', 'N'*31, '1'*30, '123_test'],
        ['', '1@11.11', 'a@aa.aac', '1@1.' + '1'*43],
        ['', 'pass_word', '1'*30, 'p'*31]
    ]
    tolog('Add user by api \r\n')
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

        result = server.webapi('post', 'user', settings)

        if isinstance(result, str):
            Failflag = True
            tolog('Fail: ' + result)
            continue

        check = server.webapi('get', 'user/' + settingsList[0][i])
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')
        for key in settings:
            if key != 'passwd':
                if checkResult[key] != settings[key]:
                    Failflag = True
                    tolog('Fail: parameters ' + str(checkResult[key]) + '!=' + str(settings[key]))

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def getUser():
    Failflag = False
    # test data
    userId = ['a', 'n'*31, 'test_name', '1'*30]

    listUserResponse = server.webapi('get', 'user')
    userInfo = json.loads(listUserResponse["text"])

    # list all of user
    tolog('Expect: list all of user \r\n')
    actualResutl = ''
    i = 0
    for info in userInfo:
        actualResutl += json.dumps(info) + '\r\n'
        if i < 3:
            i += 1

    tolog('Actual: \r\n' + actualResutl + '\r\n')

    for i in userId:
        if ('"id": "' + i + '"') not in actualResutl:
            Failflag = True
            tolog('Fail: The user ' + i + ' is not listed')

    # To list specify user
    tolog('To list specify user \r\n')
    for i in userId:
        tolog('Expect: To list user ' + i + '\r\n')
        result = server.webapi('get', 'user/' + i)
        if isinstance(result, str):
            Failflag = True
            tolog('Fail: To list user ' + i + ' is failed')
        else:
            tolog('Actual: The user ' + i + ' is listed \r\n')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def setUser():
    Failflag = False
    settingsList = [
        [0, 0, 1, 1],
        ['View', 'Maintenance', 'Power', 'Super'],
        ['', 'a', '1', 't'*31],
        ['', '', '1@1.11', 'a@a.' + 'a'*43]
    ]

    tolog('Modify user by api \r\n')
    for i in range(4):
        settings = {
            "status": settingsList[0][i],
            "privilege": settingsList[1][i],
            "display_name": settingsList[2][i],
            "email": settingsList[3][i]
        }

        tolog('Expect: ' + json.dumps(settings) + '\r\n')
        result = server.webapi('put', 'user/a', settings)

        if isinstance(result, str):
            Failflag = True
            tolog('Fail: ' + result)
            continue

        check = server.webapi('get', 'user/a')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')
        for key in settings:
            if settings[key] != checkResult[key]:
                Failflag = True
                tolog('Fail: parameters ' + str(settings[key]) + ' != ' + str(checkResult[key]))

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def deleteUser():
    Failflag = False
    userId = []

    userResponse = server.webapi('get', 'user')
    userInfo = json.loads(userResponse["text"])

    for uId in userInfo:
        if uId["id"] != "administrator":
            userId.append(uId["id"])

    tolog('Delete user by api \r\n')
    for i in userId:
        tolog('Expect: To delete user ' + i + '\r\n')
        result = server.webapiurl('delete', 'user', i)
        if isinstance(result, dict):
            tolog('Actual: user ' + i + ' is deleted \r\n')
        else:
            Failflag = True
            tolog('Fail: To delete user ' + i + ' is failed')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def addSNMPUser():
    Failflag = False

    # test data
    settingsList = [
        ['b', 'B'*31, '1T', 'test_1'],
        ['MD5', 'MD5', 'SHA', 'SHA'],
        ['DES', 'AES', 'DES', 'AES'],
        ['1'*8, '1'*31, 'a'*9, '*'*30],
        ['1'*8, '1'*31, '@'*9, 'b'*30]
    ]

    tolog('Add SNMPUser by api \r\n')
    for i in range(4):
        settings = {
            "id": settingsList[0][i],
            "auth": settingsList[1][i],
            "priv": settingsList[2][i],
            "priv_passwd": settingsList[3][i],
            "auth_passwd": settingsList[4][i]
        }

        tolog('Expect: ' + json.dumps(settings) + '\r\n')

        snmpUserAdd = server.webapi('post', 'snmpuser', settings)
        if isinstance(snmpUserAdd, str):
            Failflag = True
            tolog('Fail: ' + snmpUserAdd)

        check = server.webapi('get', 'snmpuser/' + settingsList[0][i])
        result = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(result) + '\r\n')

        for key in settings:
            if settings[key] != result[key] or result["permission"] != "READ_ONLY":
                Failflag = True
                tolog('Fail: parameters ' + str(settings[key]) + '!=' + str(result[key]))

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def getSNMPUser():
    Failflag = False
    # test data
    snmpUserId = ['b', 'B'*31, '1T', 'test_1']

    listSNMPUserResponse = server.webapi('get', 'snmpuser')
    snmpUserInfo = json.loads(listSNMPUserResponse["text"])

    # list all of snmpuser
    tolog('Expect: list all of snmpuser \r\n')
    actualResutl = ''
    i = 0
    for info in snmpUserInfo:
        actualResutl += json.dumps(info) + '\r\n'
        if i < 3:
            i += 1

    tolog('Actual: \r\n' + actualResutl + '\r\n')

    for i in snmpUserId:
        if ('"id": "' + i + '"') not in actualResutl:
            Failflag = True
            tolog('Fail: The snmpuser ' + i + ' is not listed')

    # To list specify snmpuser
    tolog('To list specify snmpuser \r\n')
    for i in snmpUserId:
        tolog('Expect: To list snmpuser ' + i + '\r\n')
        result = server.webapi('get', 'snmpuser/' + i)
        if isinstance(result, str):
            Failflag = True
            tolog('Fail: To list snmpuser ' + i + ' is failed')
        else:
            tolog('Actual: The snmpuser ' + i + ' is listed \r\n')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def setSNMPUser():
    Failflag = False
    settingsList = [
        ['b', 'b', 'b', 'b'],
        ['MD5', 'MD5', 'SHA', 'SHA'],
        ['a'*8, 'a'*8, 't'*31, 't'*31],
        ['DES', 'AES', 'DES', 'AES'],
        ['a'*8, 'a'*8, 't'*31, 't'*31]
    ]

    tolog('Modify SNMPUser by api \r\n')
    for i in range(4):
        settings = {
            "id": settingsList[0][i],
            "auth": settingsList[1][i],
            "auth_passwd": settingsList[2][i],
            "priv": settingsList[3][i],
            "priv_passwd": settingsList[4][i]
        }

        tolog('Expect: ' + json.dumps(settings) + '\r\n')
        result = server.webapi('put', 'snmpuser/' + settingsList[0][i], settings)

        if isinstance(result, str):
            Failflag = True
            tolog('Fail: ' + result)
            continue

        check = server.webapi('get', 'snmpuser/' + settingsList[0][i])
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')
        for key in settings:
            if settings[key] != checkResult[key] or checkResult["permission"] != "READ_ONLY":
                Failflag = True
                tolog('Fail: parameters ' + str(settings[key]) + ' != ' + str(checkResult[key]))

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def deleteSNMPUser():
    Failflag = False
    snmpuserId = []

    snmpuserResponse = server.webapi('get', 'snmpuser')
    snmpuserInfo = json.loads(snmpuserResponse["text"])

    for info in snmpuserInfo:
        snmpuserId.append(info["id"])

    tolog('Delete SNMPUser by api \r\n')
    for i in snmpuserId:
        tolog('Expect: To delete snmpuser ' + i + '\r\n')
        result = server.webapiurl('delete', 'snmpuser', i)
        if isinstance(result, dict):
            tolog('Actual: snmpuser ' + i + ' is deleted \r\n')
        else:
            Failflag = True
            tolog('Fail: To delete snmpuser ' + i + ' is failed')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def addDSUser():
    Failflag = False
    settingsList = [
        ['a', 'n' * 30, 'test_name', '123'],
        ['1'*6, '1'*7, 'p' * 15, 'w' * 16],
        ['', 'display_name1', 'n' * 30, 'm' * 31],
        ['', '1@11.11', 'a@aa.aac', '1@1.' + '1'*43],
        ['', '1_d', 'd' * 30, 'p' * 31],
        ['', '1', '1' * 30, '1' * 31]
    ]

    tolog('Add DSUser by api \r\n')
    for i in range(4):
        settings = {
            "id": settingsList[0][i],
            "password": settingsList[1][i],
            "display_name": settingsList[2][i],
            "email": settingsList[3][i],
            "department": settingsList[4][i],
            "phone": settingsList[5][i]
        }

        tolog('Expect: ' + json.dumps(settings) + '\r\n')

        result = server.webapi('post', 'dsuser', settings)

        if isinstance(result, str):
            Failflag = True
            tolog('Fail: ' + result)
            continue

        check = server.webapi('get', 'dsuser/' + settingsList[0][i])
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for value in settings.values():
            if value != settingsList[1][i]:
                if value not in checkResult.values():
                    Failflag = True
                    tolog('Fail: ' + value)

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def getDSUser():
    Failflag = False
    # test data
    DSUserId = ['a', 'n' * 30, 'test_name', '123']

    listDSUserResponse = server.webapi('get', 'dsuser')
    DSUserInfo = json.loads(listDSUserResponse["text"])

    # list all of user
    tolog('Expect: list all of DSUser \r\n')
    actualResutl = ''
    i = 0
    for info in DSUserInfo:
        actualResutl += json.dumps(info) + '\r\n'
        if i < 3:
            i += 1

    tolog('Actual: \r\n' + actualResutl + '\r\n')

    for i in DSUserId:
        if ('"id": "' + i + '"') not in actualResutl:
            Failflag = True
            tolog('Fail: The DSUser ' + i + ' is not listed')

    # To list specify user
    tolog('To list specify DSUser \r\n')
    for i in DSUserId:
        tolog('Expect: To list DSUser ' + i + '\r\n')
        result = server.webapi('get', 'dsuser/' + i)
        if isinstance(result, str):
            Failflag = True
            tolog('Fail: To list DSUser ' + i + ' is failed')
        else:
            tolog('Actual: The DSUser ' + i + ' is listed \r\n')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def setDSUser():
    Failflag = False
    settingsList = [
        ['', '1_d', 'd' * 30, 'p' * 31],
        ['', '1', '1' * 30, '1' * 31],
        ['', 'a', '1', 't' * 31],
        ['', '', '1@1.11', 'a@a.' + 'a' * 43]
    ]

    tolog('Modify DSUser by api \r\n')
    for i in range(4):
        settings = {
            "department": settingsList[0][i],
            "phone": settingsList[1][i],
            "display_name": settingsList[2][i],
            "email": settingsList[3][i]
        }

        tolog('Expect: ' + json.dumps(settings) + '\r\n')
        result = server.webapi('put', 'dsuser/' + 'a', settings)

        if isinstance(result, str):
            Failflag = True
            tolog('Fail: ' + result)
            continue

        check = server.webapi('get', 'dsuser/a')
        checkResult = json.loads(check["text"])[0]

        tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

        for value in settings.values():
            if value not in checkResult.values():
                Failflag = True
                tolog('Fail: ' + value)

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)

def deleteDSUser():
    Failflag = False
    dsUserId = []

    snmpuserResponse = server.webapi('get', 'dsuser')
    snmpuserInfo = json.loads(snmpuserResponse["text"])

    for info in snmpuserInfo:
        dsUserId.append(info["id"])

    tolog('Delete DSUser by api \r\n')
    for i in dsUserId:
        tolog('Expect: To delete DSUser ' + i + '\r\n')
        result = server.webapiurl('delete', 'dsuser', i)
        if isinstance(result, dict):
            tolog('Actual: DSUser ' + i + ' is deleted \r\n')
        else:
            Failflag = True
            tolog('Fail: To delete DSUser ' + i + ' is failed')

    if Failflag:
        tolog(Fail)
    else:
        tolog(Pass)


if __name__ == '__main__':
    addUser()
    getUser()
    setUser()
    deleteUser()
    addSNMPUser()
    getSNMPUser()
    setSNMPUser()
    deleteSNMPUser()
    addDSUser()
    getDSUser()
    setDSUser()
    deleteDSUser()
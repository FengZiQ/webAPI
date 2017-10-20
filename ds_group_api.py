# coding = utf-8
# 2017.10.10

from remote import server
import json
from to_log import tolog
from result_assert import result_assert


def add_group_and_verify_name_rules():
    # precondition: create DSUser

    for i in range(10):
        server.webapi('post', 'dsuser', {
                "id": 'test_group_' + str(i),
                "password": '123456'
            })

    # test data
    name = ['a', '12', 'N'*29, 't'*30]

    for n in name:
        # precondition: cancel edit
        server.webapi('post', 'dsgroup/editcancel')

        tolog('Expect: add group ' + n + '\r\n')

        step1 = server.webapi('post', 'dsgroup/editbegin', {
            "page": 1,
            "page_size": 20
        })

        if isinstance(step1, str):
            result_assert.FailFlag = True
            tolog("Fail: " + step1 + '\r\n')

        else:
            # test data
            token = json.loads(step1["text"])[0]["token"]
            get_page_data = json.loads(step1["text"])[0]["page_data"]
            page_data = [[0, uid["uid"]] for uid in get_page_data]

            step2 = server.webapi('post', 'dsgroup/editnext', {
                "page": 1,
                "page_size": 20,
                "token": token,
                "page_data": page_data
            })

            if isinstance(step2, str):
                result_assert.FailFlag = True
                tolog("Fail: " + step2 + '\r\n')

            else:

                step3 = server.webapi('post', 'dsgroup/editsave', {
                    "id": n,
                    "token": token,
                    "page_data": page_data
                })

                if isinstance(step3, str):
                    result_assert.FailFlag = True
                    tolog("Fail: " + step3 + '\r\n')

                else:

                    check = server.webapi('get', 'dsgroup/' + n)
                    checkResult = json.loads(check["text"])[0]

                    tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

    result_assert.result_assert()


def add_group_and_users_by_must_parameters():

    # precondition
    server.webapi('post', 'dsgroup/editcancel')

    tolog('Expect: add group "by_must_parameters" and add 10 user\r\n')

    step1 = server.webapi('post', 'dsgroup/editbegin', {
        "page": 1,
        "page_size": 20
    })

    if isinstance(step1, str):

        result_assert.FailFlag = True
        tolog("Fail: " + step1 + '\r\n')

    else:
        # test data
        token = json.loads(step1["text"])[0]["token"]
        get_page_data = json.loads(step1["text"])[0]["page_data"]
        page_data = [[1, uid["uid"]] for uid in get_page_data[1:]]

        step2 = server.webapi('post', 'dsgroup/editnext', {
            "token": token,
            "page_data": page_data,
            "page": 1,
            "page_size": 20
        })

        if isinstance(step2, str):
            result_assert.FailFlag = True
            tolog("Fail: " + step2 + '\r\n')

        else:

            step3 = server.webapi('post', 'dsgroup/editsave', {
                "id": 'by_must_parameters',
                "token": token,
                "page_data": page_data
            })

            if isinstance(step3, str):
                result_assert.FailFlag = True
                tolog("Fail: " + step3 + '\r\n')

            else:

                check = server.webapi('get', 'dsgroup/by_must_parameters')
                checkResult = json.loads(check["text"])[0]

                tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

    result_assert.result_assert()


def get_ds_groups():
    # test data
    response = ['id', 'gid', 'description']

    tolog('Expect: list all of groups sort by desc gro_name ')
    result = server.webapi('get', 'dsgroup?page=1&page_size=500&sort=grp_name&direct=desc')

    if isinstance(result, str):

        result_assert.FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = json.loads(result["text"])

        checkResult = ''.join(str(check)).replace('[{', '').replace('}]', '').replace('{', '').replace('},', '\r\n')

        tolog('Actual: \r\n' + checkResult)

        for group in check:

            if len(response) != len(group.keys()):

                result_assert.FailFlag = True
                tolog('Fail: please check out response parameters count\r\n')
                break

            for p in group.keys():

                if p not in response:

                    result_assert.FailFlag = True
                    tolog('Fail: please check out response parameter: ' + p + '\r\n')

    result_assert.result_assert()


def search_ds_group():

    tolog('Expect: get group that name contains t\r\n')
    result = server.webapi('get', "dsgroup?page=1&page_size=10&search=grp_name+like'%t%'")

    if isinstance(result, str):

        result_assert.FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = json.loads(result["text"])

        checkResult = ''.join(str(check)).replace('[{', '').replace('}]', '').replace('{', '').replace('},', '\r\n')

        tolog('Actual: \r\n' + checkResult)

    result_assert.result_assert()


def get_ds_group():
    # test
    id = 'users'
    response = ['id', 'gid', 'description', 'group_member']

    tolog('Expect: \r\n' + str(response) + '\r\n')

    result = server.webapi('get', 'dsgroup/' + id)

    if isinstance(result, str):

        result_assert.FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = json.loads(result["text"])[0]
        tolog('Actual: \r\n' + str(check.keys()).replace('u', '') + '\r\n')

        if len(response) != len(check.keys()):

            result_assert.FailFlag = True
            tolog('Fail: please check out response parameters count\r\n')

        for p in check.keys():

            if p not in response:

                result_assert.FailFlag = True
                tolog('Fail: please check out response parameter: ' + p + '\r\n')

    result_assert.result_assert()


def modify_ds_group():
    # test data
    id = 'a'
    setting = {"desc": 'this is the test for group description'}

    tolog('Expect: ' + json.dumps(setting) + '\r\n')

    result = server.webapi('put', 'dsgroup/' + id, setting)

    if isinstance(result, str):

        result_assert.FailFlag = True
        tolog('Fail: ' + result + '\r\n')

    else:

        check = server.webapi('get', 'dsgroup/' + id)
        checkResult = json.loads(check["text"])[0]

        if setting["desc"] not in checkResult["description"]:

            result_assert.FailFlag = True
            tolog('Fail: please check description of group' + id + '\r\n')

        else:
            tolog('Actual: ' + json.dumps(checkResult) + '\r\n')

    result_assert.result_assert()


def delete_ds_group():
    # precondition: delete ds user
    ds_user_response = server.webapi('get', 'dsuser?page=1&page_size=500')
    ds_user_info = json.loads(ds_user_response["text"])

    for ds_user in ds_user_info:
        if ds_user["id"] != 'admin':
            server.webapi('delete', 'dsuser/' + ds_user["id"])

    # test data
    id = []
    group_info = server.webapi('get', 'dsgroup?page=1&page_size=500')
    group = json.loads(group_info["text"])

    for one in group:
        if one["id"] != 'users':
            id.append(one["id"])

    for i in range(len(id)):

        tolog('Expect: delete group ' + id[i] + '\r\n')
        result = server.webapi('delete', 'dsgroup/' + id[i])

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            tolog('Actual: group ' + id[i] + ' is deleted\r\n')

    result_assert.result_assert()


def invalid_group_name():
    # test data
    name = ['', 't'*31, 1]

    for n in name:
        # precondition: cancel edit
        server.webapi('post', 'dsgroup/editcancel')

        tolog('Expect: that will hint error when group name is ' + str(n) + '\r\n')

        step1 = server.webapi('post', 'dsgroup/editbegin', {
            "page": 1,
            "page_size": 20
        })

        if isinstance(step1, str):
            result_assert.FailFlag = True
            tolog("Fail: " + step1 + '\r\n')

        else:
            # test data
            token = json.loads(step1["text"])[0]["token"]
            get_page_data = json.loads(step1["text"])[0]["page_data"]
            page_data = [[0, uid["uid"]] for uid in get_page_data]

            step2 = server.webapi('post', 'dsgroup/editnext', {
                "page": 1,
                "page_size": 20,
                "token": token,
                "page_data": page_data
            })

            if isinstance(step2, str):
                result_assert.FailFlag = True
                tolog("Fail: " + step2 + '\r\n')

            else:

                step3 = server.webapi('post', 'dsgroup/editsave', {
                    "id": n,
                    "token": token,
                    "page_data": page_data
                })

        if isinstance(step3, dict):

            result_assert.FailFlag = True
            tolog("Fail: group name can be specified " + str(n) + '\r\n')

        else:
            tolog('Actual: ' + step3 + '\r\n')

    result_assert.result_assert()


def problem_body_add_group_step1():

    tolog('Expect: missing body should do not affect to go on step2\r\n')
    result1 = server.webapi('post', 'dsgroup/editbegin')

    if isinstance(result1, str):

        result_assert.FailFlag = True
        tolog('Fail: ' + result1 + '\r\n')

    else:
        server.webapi('post', 'dsgroup/addgrpcancel')
        tolog('Actual: missing body does not affect step2\r\n')

    tolog('Expect: body is empty that should do not affect to go on step2\r\n')
    result2 = server.webapi('post', 'dsgroup/editbegin', {})

    if isinstance(result2, str):

        result_assert.FailFlag = True
        tolog('Fail: ' + result2 + '\r\n')

    else:
        server.webapi('post', 'dsgroup/addgrpcancel')
        tolog('Actual: missing body does not affect step2\r\n')

    result_assert.result_assert()


def problem_body_add_group_step2():
    # precondition: step1
    server.webapi('post', 'dsgroup/editbegin', {"page": 1, "page_size": 500})

    tolog('Expect: missing body should return error\r\n')
    result1 = server.webapi('post', 'dsgroup/editnext')

    if isinstance(result1, dict):

        result_assert.FailFlag = True
        tolog('Fail: that return 200 when body is missing\r\n')

    else:
        server.webapi('post', 'dsgroup/addgrpcancel')
        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: body is empty that should return error\r\n')
    result2 = server.webapi('post', 'dsgroup/editnext', {})

    if isinstance(result2, dict):

        result_assert.FailFlag = True
        tolog('Fail: that return 200 when body is empty\r\n')

    else:
        server.webapi('post', 'dsgroup/addgrpcancel')
        tolog('Actual: ' + result2 + '\r\n')

    result_assert.result_assert()


def problem_body_add_group_step3():
    # precondition: edit cancel
    server.webapi('post', 'dsgroup/editcancel')

    # step1
    step1 = server.webapi('post', 'dsgroup/editbegin', {"page": 1, "page_size": 500})
    token = json.loads(step1["text"])[0]["token"]

    # step2
    step2 = server.webapi('post', 'dsgroup/editbegin', {"token": token, "page_data": [[1, 1001]]})

    tolog('Expect: missing body should return error\r\n')
    result1 = server.webapi('post', 'dsgroup/editsave')

    if isinstance(result1, dict):

        result_assert.FailFlag = True
        tolog('Fail: that return 200 when body is missing\r\n')
        server.webapi('post', 'dsgroup/editcancel')

    else:
        server.webapi('post', 'dsgroup/editcancel')
        tolog('Actual: ' + result1 + '\r\n')

    # step1
    step1 = server.webapi('post', 'dsgroup/editbegin', {"page": 1, "page_size": 500})
    token = json.loads(step1["text"])[0]["token"]

    # step2
    step2 = server.webapi('post', 'dsgroup/editbegin', {"token": token, "page_data": [[1, 1001]]})

    tolog('Expect: body is empty that should return error\r\n')
    result2 = server.webapi('post', 'dsgroup/editsave', {})

    if isinstance(result2, dict):

        result_assert.FailFlag = True
        tolog('Fail: that return 200 when body is empty\r\n')
        server.webapi('post', 'dsgroup/editcancel')

    else:
        server.webapi('post', 'dsgroup/editcancel')
        tolog('Actual: ' + result2 + '\r\n')

    result_assert.result_assert()


if __name__ == "__main__":
    add_group_and_verify_name_rules()
    add_group_and_users_by_must_parameters()
    get_ds_groups()
    search_ds_group()
    get_ds_group()
    modify_ds_group()
    delete_ds_group()
    invalid_group_name()
    problem_body_add_group_step1()
    problem_body_add_group_step2()
    problem_body_add_group_step3()
# coding = utf-8
# 2017.10.19

from remote import server
import json
from to_log import tolog
from result_assert import result_assert
from find_unconfigured_pd_id import find_pd_id


def precondition():
    pdId = find_pd_id()
    server.webapi('post', 'pool', {"name": "test_protocol_API", "pds": pdId[:3], "raid_level": "raid5"})
    server.webapi('post', 'nasshare', {'pool_id': 0, 'name': 'test_protocol_api', 'capacity': '2GB'})


def disable_protocol():
    # test data
    id = ['FTP', 'NFS', 'SMB']

    for i in range(len(id)):
        # precondition: enable protocol
        server.webapi('post', 'protocol/enable/' + id[i])

        tolog('Expect: ' + id[i] + ' protocol should be disabled when it is enabled\r\n')
        result = server.webapi('post', 'protocol/disable/' + id[i])

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            tolog('Actual: ' + id[i] + ' protocol is disabled\r\n')

    for i in range(len(id)):

        tolog('Expect: ' + id[i] + ' protocol should be disabled when it is disabled\r\n')
        result = server.webapi('post', 'protocol/disable/' + id[i])

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            tolog('Actual: ' + id[i] + ' protocol is disabled\r\n')

    result_assert.result_assert()


def enable_protocol():
    # test data
    id = ['FTP', 'NFS', 'SMB']

    for i in range(len(id)):
        # precondition: disable protocol
        server.webapi('post', 'protocol/disable/' + id[i])

        tolog('Expect: ' + id[i] + ' protocol should be enabled when it is disabled\r\n')
        result = server.webapi('post', 'protocol/enable/' + id[i])

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            tolog('Actual: ' + id[i] + ' protocol is enabled\r\n')

    for i in range(len(id)):

        tolog('Expect: ' + id[i] + ' protocol should be enabled when it is enabled\r\n')
        result = server.webapi('post', 'protocol/enable/' + id[i])

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            tolog('Actual: ' + id[i] + ' protocol is enabled\r\n')

    result_assert.result_assert()


def reset_protocol_setting():
    # test data
    id = ['FTP', 'NFS', 'SMB']

    for i in range(len(id)):

        tolog('Expect: ' + id[i] + ' protocol should be reset\r\n')
        result = server.webapi('post', 'protocol/reset/' + id[i])

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            tolog('Actual: ' + id[i] + ' protocol is reset\r\n')

    tolog('Expect: all protocol should be reset\r\n')
    result2 = server.webapi('post', 'protocol/reset')

    if isinstance(result2, str):

        result_assert.FailFlag = True
        tolog('Fail: ' + result2 + '\r\n')

    else:

        tolog('Actual: all protocol is reset\r\n')

    result_assert.result_assert()


def get_ftp():
    # test data
    response = ['enable', 'encrypt_type', 'port', 'passive_start', 'passive_end', 'charset', 'dw_rate', 'up_rate']

    tolog('Expect: \r\n' + str(response) + '\r\n')
    result = server.webapi('get', 'protocol/ftp')

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

            for key in check.keys():

                if key not in response:

                    result_assert.FailFlag = True
                    tolog('Fail: ' + key + ' is not in response\r\n')

    result_assert.result_assert()


def set_ftp():
    # test data
    settings = {
        'enable': [0, 1, 0, 1, 0],
        'encrypt_type': [0, 1, 2, 3, 0],
        'cmd_port': [1, 2, 65534, 65535, 1],
        'passive_start': [1024, 1025, 65533, 65534, 1024],
        'passive_end': [1025, 1026, 65534, 65535, 1025],
        'charset': ['utf8', 'ja_jp', 'ko_kr', 'zh_cn', 'zh_tw'],
        'dw_rate': [0, 512, 2048, 65535, 65536],
        'up_rate': [65536, 65535, 1024, 126, 0]
    }

    for i in range(len(settings['charset'])):
        # test data
        setting = {}

        for key in settings:

            setting[key] = settings[key][i]

        tolog('Expect: that should return 200 when body is \r\n' + json.dumps(setting) + '\r\n')
        result = server.webapi('post', 'protocol/ftp', setting)

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = server.webapi('get', 'protocol/ftp')
            checkResult = json.loads(check['text'])[0]

            tolog('Actual: return 200, and gets ftp protocol info are \r\n' + json.dumps(checkResult) + '\r\n')

            for v in setting.values():

                if v not in checkResult.values():

                    result_assert.FailFlag = True
                    tolog('Fail: please check out the value ' + str(v) + '\r\n')

    result_assert.result_assert()


def get_nfs():
    # test data
    response = ['enable', 'portmapper_port', 'nfsd_port', 'mountd_port', 'statd_port', 'lockd_port']

    tolog('Expect: \r\n' + str(response) + '\r\n')
    result = server.webapi('get', 'protocol/nfs')

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

            for key in check.keys():

                if key not in response:

                    result_assert.FailFlag = True
                    tolog('Fail: ' + key + ' is not in response\r\n')

    result_assert.result_assert()


def set_nfs():
    # test data
    settings = {
        'enable': [0, 1, 0, 1],
        'mountd_port': [1024, 1025, 65532, 65533]
    }

    for i in range(len(settings['mountd_port'])):
        # test data
        setting = {}

        for key in settings:
            setting[key] = settings[key][i]

        tolog('Expect: that should return 200 when body is \r\n' + json.dumps(setting) + '\r\n')
        result = server.webapi('post', 'protocol/nfs', setting)

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = server.webapi('get', 'protocol/nfs')
            checkResult = json.loads(check['text'])[0]

            tolog('Actual: return 200, and gets ftp protocol info are \r\n' + json.dumps(checkResult) + '\r\n')

            for v in setting.values():

                if v not in checkResult.values():
                    result_assert.FailFlag = True
                    tolog('Fail: please check out the value ' + str(v) + '\r\n')

    result_assert.result_assert()


def get_smb():
    # test data
    response = ['enable', 'desc', 'workgroup', 'nt_acl']

    tolog('Expect: \r\n' + str(response) + '\r\n')
    result = server.webapi('get', 'protocol/smb')

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

            for key in check.keys():

                if key not in response:

                    result_assert.FailFlag = True
                    tolog('Fail: ' + key + ' is not in response\r\n')

    result_assert.result_assert()


def set_smb():
    # test data
    settings = {
        'enable': [0, 1],
        'desc': ['', 'this is the test'],
        'workgroup': ['', 'test'],
        'nt_acl': ['yes', 'no']
    }

    for i in range(len(settings['enable'])):
        # test data
        setting = {}

        for key in settings:
            setting[key] = settings[key][i]

        tolog('Expect: that should return 200 when body is \r\n' + json.dumps(setting) + '\r\n')
        result = server.webapi('post', 'protocol/smb', setting)

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = server.webapi('get', 'protocol/smb')
            checkResult = json.loads(check['text'])[0]

            tolog('Actual: return 200, and gets ftp protocol info are \r\n' + json.dumps(checkResult) + '\r\n')

            for v in setting.values():

                if v not in checkResult.values():
                    result_assert.FailFlag = True
                    tolog('Fail: please check out the value ' + str(v) + '\r\n')

    result_assert.result_assert()


def get_protocol_running_status():
    # test data
    response = ['name', 'status']

    tolog('Expect: \r\n' + str(response) + '\r\n')
    result = server.webapi('get', 'protocol/status')

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

            for key in check.keys():

                if key not in response:
                    result_assert.FailFlag = True
                    tolog('Fail: ' + key + ' is not in response\r\n')

    result_assert.result_assert()


def get_protocol_status_on_storage():
    # precondition
    precondition()

    # test data
    response = ['ftp', 'nfs', 'smb', 'tm_enable', 'allow_ip']

    tolog('Expect: \r\n' + str(response) + '\r\n')
    result = server.webapi('get', 'protocol/storage/nasshare_0')

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

            for key in check.keys():

                if key not in response:
                    result_assert.FailFlag = True
                    tolog('Fail: ' + key + ' is not in response\r\n')

    result_assert.result_assert()


def set_protocol_settings_on_storage():
    # test data
    settings = {
        'ftp': [0, 1],
        'nfs': [1, 0],
        'smb': [1, 0],
        'tm_enable': [1, 0],
        'allow_ip': [[], []]
    }

    for i in range(len(settings['ftp'])):
        # test data
        setting = {}

        for key in settings:
            setting[key] = settings[key][i]

        tolog('Expect: that should return 200 when body is \r\n' + json.dumps(setting) + '\r\n')
        result = server.webapi('post', 'protocol/storage/nasshare_0', setting)

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            check = server.webapi('get', 'protocol/ftp')
            checkResult = json.loads(check['text'])[0]

            tolog('Actual: return 200, and gets ftp protocol info are \r\n' + json.dumps(checkResult) + '\r\n')

            for v in setting.values():

                if v not in checkResult.values():
                    result_assert.FailFlag = True
                    tolog('Fail: please check out the value ' + str(v) + '\r\n')

    result_assert.result_assert()


def invalid_path_parameters_for_disable_protocol():
    # test data
    id = ['', 'test', 0]

    for i in range(len(id)):

        tolog('Expect: that should hint error when path parameter is ' + str(id[i]) + '\r\n')
        result = server.webapi('post', 'protocol/disable/' + str(id[i]))

        if isinstance(result, dict):

            result_assert.FailFlag = True
            tolog('Fail: when path parameter is ' + str(id[i]) + '\r\n')

        else:

            tolog('Actual: ' + result + '\r\n')

    result_assert.result_assert()


def invalid_path_parameters_for_enable_protocol():
    # test data
    id = ['', 'test', 0]

    for i in range(len(id)):

        tolog('Expect: that should hint error when path parameter is ' + str(id[i]) + '\r\n')
        result = server.webapi('post', 'protocol/enable/' + str(id[i]))

        if isinstance(result, dict):

            result_assert.FailFlag = True
            tolog('Fail: when path parameter is ' + str(id[i]) + '\r\n')

        else:

            tolog('Actual: ' + result + '\r\n')

    result_assert.result_assert()


def invalid_path_parameters_for_reset_protocol_setting():
    # test data
    id = ['test', 0]

    for i in range(len(id)):

        tolog('Expect: that should hint error when path parameter is ' + str(id[i]) + '\r\n')
        result = server.webapi('post', 'protocol/reset/' + str(id[i]))

        if isinstance(result, dict):

            result_assert.FailFlag = True
            tolog('Fail: when path parameter is ' + str(id[i]) + '\r\n')

        else:

            tolog('Actual: ' + result + '\r\n')

    result_assert.result_assert()


def invalid_parameters_for_set_ftp():
    # test data
    settings = {
        'enable': [2, ''],
        'encrypt_type': [4, ''],
        'cmd_port': [0, 65536, ''],
        'passive_start': [1023, 65535, ''],
        'passive_end': [1024, 65536, ''],
        'charset': ['test', 0],
        'dw_rate': [''],
        'up_rate': ['']
    }

    for key in settings:

        for i in range(len(settings[key])):

            setting = {key: settings[key][i]}

            tolog('Expect: that should hint error when body is ' + json.dumps(setting) + '\r\n')
            result = server.webapi('post', 'protocol/ftp', setting)

            if isinstance(result, dict):

                result_assert.FailFlag = True
                tolog('Fail: when body is ' + json.dumps(setting) + '\r\n')

            else:
                tolog('Actual: ' + result + '\r\n')

    result_assert.result_assert()


def invalid_parameters_for_set_nfs():
    # test data
    settings = {
        'enable': [-1, 2, ''],
        'mountd_port': [-1, 4, '']
    }

    for key in settings:

        for i in range(len(settings[key])):

            setting = {key: settings[key][i]}

            tolog('Expect: that should hint error when body is ' + json.dumps(setting) + '\r\n')
            result = server.webapi('post', 'protocol/nfs', setting)

            if isinstance(result, dict):

                result_assert.FailFlag = True
                tolog('Fail: when body is ' + json.dumps(setting) + '\r\n')

            else:
                tolog('Actual: ' + result + '\r\n')

    result_assert.result_assert()


def invalid_parameters_for_set_smb():
    # test data
    settings = {
        'enable': [-1, 2, ''],
        'nt_acl': [-1, 0, '']
    }

    for key in settings:

        for i in range(len(settings[key])):

            setting = {key: settings[key][i]}

            tolog('Expect: that should hint error when body is ' + json.dumps(setting) + '\r\n')
            result = server.webapi('post', 'protocol/smb', setting)

            if isinstance(result, dict):

                result_assert.FailFlag = True
                tolog('Fail: when body is ' + json.dumps(setting) + '\r\n')

            else:
                tolog('Actual: ' + result + '\r\n')

    result_assert.result_assert()


def invalid_path_parameters_for_get_protocol_status_on_storage():
    # test data
    id = ['nasshare_100', 'snapshot_100', 'clone_100', 'test', 0]

    for i in range(len(id)):

        tolog('Expect: that should hint error when path parameter is ' + str(id[i]) + '\r\n')
        result = server.webapi('post', 'protocol/storage/' + str(id[i]))

        if isinstance(result, dict):

            result_assert.FailFlag = True
            tolog('Fail: when path parameter is ' + str(id[i]) + '\r\n')

        else:

            tolog('Actual: ' + result + '\r\n')

    result_assert.result_assert()


def problem_body_for_set_ftp():

    tolog('Expect: that should hint error when body is missing\r\n')
    result1 = server.webapi('post', 'protocol/ftp')

    if isinstance(result1, dict):

        result_assert.FailFlag = True
        tolog('Fail: when body is missing\r\n')

    else:

        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: that should hint error when body is empty\r\n')
    result2 = server.webapi('post', 'protocol/ftp', {})

    if isinstance(result2, dict):

        result_assert.FailFlag = True
        tolog('Fail: when body is empty\r\n')

    else:

        tolog('Actual: ' + result2 + '\r\n')

    result_assert.result_assert()


def problem_body_for_set_nfs():

    tolog('Expect: that should hint error when body is missing\r\n')
    result1 = server.webapi('post', 'protocol/nfs')

    if isinstance(result1, dict):

        result_assert.FailFlag = True
        tolog('Fail: when body is missing\r\n')

    else:

        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: that should hint error when body is empty\r\n')
    result2 = server.webapi('post', 'protocol/nfs', {})

    if isinstance(result2, dict):

        result_assert.FailFlag = True
        tolog('Fail: when body is empty\r\n')

    else:

        tolog('Actual: ' + result2 + '\r\n')

    result_assert.result_assert()


def problem_body_for_set_smb():

    tolog('Expect: that should hint error when body is missing\r\n')
    result1 = server.webapi('post', 'protocol/smb')

    if isinstance(result1, dict):

        result_assert.FailFlag = True
        tolog('Fail: when body is missing\r\n')

    else:

        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: that should hint error when body is empty\r\n')
    result2 = server.webapi('post', 'protocol/smb', {})

    if isinstance(result2, dict):

        result_assert.FailFlag = True
        tolog('Fail: when body is empty\r\n')

    else:

        tolog('Actual: ' + result2 + '\r\n')

    result_assert.result_assert()


def problem_body_for_set_protocol_status_on_storage():

    tolog('Expect: that should hint error when body is missing\r\n')
    result1 = server.webapi('post', 'protocol/storage/nasshare_0')

    if isinstance(result1, dict):

        result_assert.FailFlag = True
        tolog('Fail: when body is missing\r\n')

    else:

        tolog('Actual: ' + result1 + '\r\n')

    tolog('Expect: that should hint error when body is empty\r\n')
    result2 = server.webapi('post', 'protocol/storage/nasshare_0', {})

    if isinstance(result2, dict):

        result_assert.FailFlag = True
        tolog('Fail: when body is empty\r\n')

    else:

        tolog('Actual: ' + result2 + '\r\n')

    # clean up environment
    server.webapi('delete', 'pool/0?force=1')

    result_assert.result_assert()


if __name__ == "__main__":
    # disable_protocol()
    # enable_protocol()
    # reset_protocol_setting()
    # get_ftp()
    # set_ftp()
    # get_nfs()
    # set_nfs()
    # get_smb()
    # set_smb()
    # get_protocol_running_status()
    # get_protocol_status_on_storage()
    set_protocol_settings_on_storage()
    # invalid_path_parameters_for_disable_protocol()
    # invalid_path_parameters_for_enable_protocol()
    # invalid_path_parameters_for_reset_protocol_setting()
    # invalid_parameters_for_set_ftp()
    # invalid_parameters_for_set_nfs()
    # invalid_parameters_for_set_smb()
    # invalid_path_parameters_for_get_protocol_status_on_storage()
    # problem_body_for_set_ftp()
    # problem_body_for_set_nfs()
    # problem_body_for_set_smb()
    # problem_body_for_set_protocol_status_on_storage()
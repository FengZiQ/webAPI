# coding = utf-8
# 2017.10.19

from remote import server
import json
from to_log import tolog
from result_assert import result_assert


def disable_protocol():
    # test data
    id = ['FTP', 'NFS', 'SMB']

    for i in range(len(id)):
        # precondition: enable protocol
        server.webapi('post', 'protocol/enable/' + id[i])

        tolog(id[i] + ' protocol should be disabled when it is enabled\r\n')
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

        tolog(id[i] + ' protocol should be enabled when it is disabled\r\n')
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

        tolog(id[i] + ' protocol should be reset\r\n')
        result = server.webapi('post', 'protocol/reset/' + id[i])

        if isinstance(result, str):

            result_assert.FailFlag = True
            tolog('Fail: ' + result + '\r\n')

        else:

            tolog('Actual: ' + id[i] + ' protocol is reset\r\n')

    tolog('Expect: reset all protocol\r\n')
    result2 = server.webapi('post', 'protocol/reset')

    if isinstance(result2, str):

        result_assert.FailFlag = True
        tolog('Fail: ' + result2 + '\r\n')

    else:

        tolog('Actual: all protocol is reset\r\n')

    result_assert.result_assert()









if __name__ == "__main__":
    # disable_protocol()
    # enable_protocol()
    reset_protocol_setting()
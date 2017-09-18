from to_log import tolog
import json
from remote import server

request = ''
service = ''
settingsList = []
settings = {}
expectResult = ''
actualResult = ''

def invalidSettings(request, service, settingsList = None, settings = None, expectResult = '', actualResult = ''):
    FailFlag = False
    tolog('Verify invalid setting \r\n')

    # test data

    for i in range(len(settingsList)):
        tolog(expectResult + '\r\n')

        result = server.webapi(request, service, settings)

        if isinstance(result, dict):
            FailFlag = True
            tolog("Fail: " + json.dumps(settings) + '\r\n')
        else:
            tolog(actualResult + result + '\r\n')

    return FailFlag
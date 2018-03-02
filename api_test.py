# -*- coding: utf-8 -*-
# 2018.02.26

from remote import server
from to_log import tolog
import json
import xlrd
import time

Pass = "'result': 'p'\n"
Fail = "'result': 'f'\n"


class APITest(object):

    def __init__(self, flag=False):
        self.flag = flag

    # For test 'post/put/delete' method
    def settings_test(self, method, service, cases_file, sheet_name, hold_time=0):
        # Open cases file
        # data = xlrd.open_workbook('/home/work/zach/clitest/' + data_file_name)
        data = xlrd.open_workbook(cases_file)
        table = data.sheet_by_name(sheet_name)

        for j in range(1, table.nrows):

            # Building body parameters
            settings = dict((table.cell(0, i).value, table.cell(j, i).value) for i in range(table.ncols))

            # Conversion data type
            for key in settings.keys():
                if type(settings[key]) == float:
                    settings[key] = int(settings[key])
                if type(settings[key]) == str and ',' in settings[key]:
                    settings[key] = settings[key].split(',')

            # Expected result
            tolog('Expect: ' + str(settings) + '\n')

            # Sending request
            result = server.webapi(method, service, settings)
            time.sleep(hold_time)

            # Checking status of request
            if str(result['response']) != '<Response [200]>':
                self.flag = True
                tolog('Fail: HTTP status code is ' + str(result['response']))
                tolog('Error Message: ' + str(result['text']) + '\n')
                continue
            else:
                tolog('Actual: HTTP status code is ' + str(result['response']) + ', request is successful!\n')

        if self.flag:
            tolog(Fail)
        else:
            tolog(Pass)

    # For test 'post/put/delete' method
    def settings_test_and_confirm(self, method, service, cases_file, sheet_name, hold_time=0):
        # Open cases file
        # data = xlrd.open_workbook('/home/work/zach/clitest/' + data_file_name)
        data = xlrd.open_workbook(cases_file)
        table = data.sheet_by_name(sheet_name)

        for j in range(1, table.nrows):

            # Building body parameters
            settings = dict((table.cell(0, i).value, table.cell(j, i).value) for i in range(table.ncols))

            # Conversion data type
            for key in settings.keys():
                if type(settings[key]) == float:
                    settings[key] = int(settings[key])
                if type(settings[key]) == str and ',' in settings[key]:
                    settings[key] = settings[key].split(',')

            # Expected result
            tolog('Expect: ' + str(settings) + '\n')

            # Sending request
            result = server.webapi(method, service, settings)
            time.sleep(hold_time)

            # Verify expected results and actual results
            if str(result['response']) == '<Response [200]>':
                check_result = server.webapiurl('get', server + '/' + table.cell(j, 0).value)
                response = json.loads(check_result['text'])[0]
                for key in settings.keys():
                    if settings[key] != response[key]:
                        self.flag = True
                        tolog('Fail: Expected ' + key + ' is ' + str(settings[key]) + '. Actuality is ' + str(response[key]))
            else:
                tolog('Actual: ' + str(result['text']) + '\n')

        if self.flag:
            tolog(Fail)
        else:
            tolog(Pass)

    # Only confirm return parameters
    def response_test(self, url_parameters, cases_file, sheet_name):
        # Open cases file
        # data = xlrd.open_workbook('/home/work/zach/clitest/' + data_file_name)
        data = xlrd.open_workbook(cases_file)
        table = data.sheet_by_name(sheet_name)

        # data for verification
        parameters = [table.cell(0, i).value for i in range(table.ncols)]

        tolog('Expected: ' + str(parameters) + '\n')

        result = server.webapi('get', url_parameters)

        # Verify expected results and actual results
        if str(result['response']) != '<Response [200]>':
            self.flag = True
            tolog('Fail: ' + str(result['text']))
        else:
            response_info = json.loads(result['text'])
            get_r = str(response_info).replace('},', '\n').replace('[', '\n').replace(']', '').replace('{', '').replace('}', '')
            tolog('Actual: ' + get_r + '\n')

        if self.flag:
            tolog(Fail)
        else:
            tolog(Pass)

    # Confirm return value
    def response_test_and_confirm(self, url_parameters, cases_file, sheet_name):
        # Open cases file
        # data = xlrd.open_workbook('/home/work/zach/clitest/' + data_file_name)
        data = xlrd.open_workbook(cases_file)
        table = data.sheet_by_name(sheet_name)

        ed_r = dict((table.cell(0, i).value, table.cell(1, i).value) for i in range(table.ncols))

        tolog('Expected: ' + str(ed_r) + '\n')

        result = server.webapi('get', url_parameters + '/' + str(table.cell(1, 0).value))

        # Verify expected results and actual results
        if str(result['response']) != '<Response [200]>':
            self.flag = True
            tolog('Fail: ' + str(result['text']))
        else:
            check_result = json.loads(result["text"])[0]
            for key in ed_r:
                if key not in check_result.keys():
                    self.flag = True
                    tolog('Fail: expected parameter ' + key + ' is not contained at response')

            for key in ed_r:
                if ed_r[key] != check_result[key]:
                    self.flag = True
                    tolog('Fail: Expected value is ' + str(ed_r[key]) + '. Actuality is ' + str(check_result[key]))

            tolog('\nActual: Messages are ' + str(check_result) + '\n')

        if self.flag:
            tolog(Fail)
        else:
            tolog(Pass)

    # For test 'delete' method
    def delete_test(self, url_parameters, cases_file, sheet_name):
        # Open cases file
        # data = xlrd.open_workbook('/home/work/zach/clitest/' + data_file_name)
        data = xlrd.open_workbook(cases_file)
        table = data.sheet_by_name(sheet_name)

        for i in range(1, table.nrows):

            tolog('Expected: ' + str(table.cell(i, 0).value) + ' should be deleted\n')
            result = server.webapiurl('delete', url_parameters, str(table.cell(i, 0).value))

            # Checking status of request
            if str(result['response']) != '<Response [200]>':
                self.flag = True
                tolog('Fail: HTTP status code is ' + str(result['response']))
                tolog('Error Message: ' + str(result['text']) + '\n')
                continue
            else:
                tolog('Actual: HTTP status code is ' + str(result['response']) + ', request is successful!\n')

        if self.flag:
            tolog(Fail)
        else:
            tolog(Pass)

    # For test 'delete' method and confirm response after deleting
    def delete_test_and_confirm(self, url_parameters, cases_file, sheet_name):
        # Open cases file
        # data = xlrd.open_workbook('/home/work/zach/clitest/' + data_file_name)
        data = xlrd.open_workbook(cases_file)
        table = data.sheet_by_name(sheet_name)

        for i in range(1, table.nrows):

            tolog('Expected: ' + str(table.cell(i, 0).value) + ' should be deleted\n')
            result = server.webapiurl('delete', url_parameters, str(table.cell(i, 0).value))

            # Checking status of request
            if str(result['response']) != '<Response [200]>':
                self.flag = True
                tolog('Fail: HTTP status code is ' + str(result['response']))
                tolog('Error Message: ' + str(result['text']) + '\n')
                continue
            else:
                check_result = server.webapi('get', url_parameters)
                response_info = json.loads(check_result['text'])
                if str({table.cell(0, 0).value: table.cell(i, 0).value}) in str(response_info):
                    self.flag = True
                    tolog('Fail: parameter ' + str(table.cell(i, 0).value) + ' is not deleted\n')
                else:
                    tolog('Actual: parameter ' + str(table.cell(i, 0).value) + ' is deleted')
                    get_r = str(response_info).replace('},', '\n').replace('[', '\n').replace(']', '').replace('{', '').replace('}', '')
                    tolog('And get response: ' + get_r + '\n')

        if self.flag:
            tolog(Fail)
        else:
            tolog(Pass)
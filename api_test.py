# -*- coding: utf-8 -*-
# 2018.02.26

from remote import server
from to_log import tolog
import json
import xlrd
import time


class APITest(object):

    def __init__(self, flag=False):
        self.flag = flag
        self.flag_container = []
        if 'True' in self.flag_container:
            self.flag = True

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
                self.flag_container.append(str(self.flag))
                tolog('Fail: HTTP status code is ' + str(result['response']))
                tolog('Error Message: ' + str(result['text']) + '\n')
                continue
            else:
                tolog('Actual: HTTP status code is ' + str(result['response']) + ', request is successful!\n')

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
                        self.flag_container.append(str(self.flag))
                        tolog('Fail: Expected ' + key + ' is ' + str(settings[key]) + '. Actuality is ' + str(response[key]))
            else:
                tolog('Actual: ' + str(result['text']) + '\n')

    # Only confirm return parameters
    def message_test(self, service, cases_file, sheet_name):
        # Open cases file
        # data = xlrd.open_workbook('/home/work/zach/clitest/' + data_file_name)
        data = xlrd.open_workbook(cases_file)
        table = data.sheet_by_name(sheet_name)

        # data for verification
        parameters = [table.cell(0, i).value for i in range(table.ncols)]

        result = server.webapi('get', service)

        # Verify expected results and actual results
        if str(result['response']) != '<Response [200]>':
            self.flag = True
            tolog('Fail: ' + str(result['text']))
        else:
            check_result = json.loads(result["text"])[0]
            for key in parameters:
                if key not in check_result.vaules():
                    self.flag = True
                    self.flag_container.append(str(self.flag))
                    tolog('Fail: expected parameter ' + key + ' is not contained at response')

    # Confirm return value
    def message_test_confirm_values(self, service, cases_file, sheet_name):
        # data = xlrd.open_workbook('/home/work/zach/clitest/' + data_file_name)
        data = xlrd.open_workbook(cases_file)
        table = data.sheet_by_name(sheet_name)

        for i in range(1, table.nrows):
            check = server.webapi('get', service + '/' + table.cell(i, 0).value)
            check_result = json.loads(check["text"])[0]


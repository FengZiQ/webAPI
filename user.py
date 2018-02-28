from api_test import *

cases_file = 'cases/user.xlsx'


def add_user():

    tool = APITest()

    tool.settings_test('post', 'user', cases_file, 'add_user')


def get_user():

    tool = APITest()

    tool.response_test('user', cases_file, 'get_user')


def get_mgmt_user():

    tool = APITest()

    tool.response_test_and_confirm('user', cases_file, 'get_mgmt_user')


def delete_user():

    tool = APITest()

    tool.delete_test_and_confirm('user', cases_file, 'delete_user')


if __name__ == "__main__":

    # add_user()
    delete_user()
    # get_user()
    # get_mgmt_user()

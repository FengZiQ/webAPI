from api_test import *

cases_file = 'cases/user.xlsx'


def add_user():

    tool = APITest()

    tool.settings_test('post', 'user', cases_file, 'add_user')

    print tool.flag_container


if __name__ == "__main__":

    add_user()
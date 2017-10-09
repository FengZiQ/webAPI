# coding = utf-8
# 2017.10.9

from to_log import tolog

Pass = "'result': 'p'"
Fail = "'result': 'f'"


class Result():

    FailFlag = False

    def result(self):

        if self.FailFlag:
            tolog(Fail)
        else:
            tolog(Pass)


result = Result()
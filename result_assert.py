# coding = utf-8
# 2017.10.9

from to_log import tolog

Pass = "'result': 'p'"
Fail = "'result': 'f'"


class Result_assert():

    FailFlag = False

    def result_assert(self):

        if self.FailFlag:
            tolog(Fail)
            self.FailFlag = False
        else:
            tolog(Pass)


result_assert = Result_assert()
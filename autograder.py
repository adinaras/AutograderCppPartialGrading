import unittest
import ast
import json
import sys

import tap.parser
import tap.line
from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner
from gradescope_utils.autograder_utils.decorators import partial_credit

testLoader = tap.parser.Parser()
tests = testLoader.parse_file("results.tap")
weights = ast.literal_eval(open("weights.txt", "r").read())
numTests = next(tests).expected_tests
testsPassed = 0

testDescriptions = []
curDesc = -1
for test in tests:
    if not isinstance(test, tap.line.Plan):
        if not isinstance(test, tap.line.Diagnostic):
            curDesc += 1
            testDescriptions += [[test.description.replace(" ", "_"), test.ok, weights[test.description.replace(" ", "_")], "", -1.0]]
            if test.ok:
                testsPassed += 1
        if isinstance(test, tap.line.Diagnostic) and curDesc >= 0:
            if str(test.text).startswith("# \x1F"):
                if testDescriptions[curDesc][4] == -1.0:
                    testDescriptions[curDesc][4] = 0.0
                testDescriptions[curDesc][4] += float(str(test.text)[3:])
            else:
                testDescriptions[curDesc][3] += test.text + "\n"


class TAPTests(unittest.TestCase):
    longMessage = False
    pass


def gen_tap_test(ok, w=100/numTests, errmsg="", score=-1.0):
    @partial_credit(w)
    def test_tap(self, set_score=None):
        if not ok and errmsg:
            print(errmsg)
        if score != -1.0:
            set_score(score)
        self.assertTrue(ok, msg="See output above for help with debugging")
    return test_tap


if __name__ == "__main__":
    for td in testDescriptions:
        name = 'test_%s' % td[0]
        test = gen_tap_test(td[1], td[2], td[3], td[4])
        setattr(TAPTests, name, test)
    testSuite = unittest.defaultTestLoader.loadTestsFromTestCase(TAPTests)

    scaleNum = 0
    scaleScore = 0

    if len(sys.argv) == 3:
        scaleNum = int(sys.argv[1])
        scaleScore = int(sys.argv[2])

    with open("results.json", "w+") as f:
        JSONTestRunner(stream=f, buffer=True, visibility="visible", stdout_visibility="visible").run(testSuite)
        f.seek(0)
        if scaleNum and scaleScore:
            results = json.load(f)
            if testsPassed >= scaleNum:
                results['score'] = scaleScore
            if results['score'] > scaleScore:
                maxScore = sum(weights.values())
                results['score'] = (scaleScore * results['score'])/maxScore
            f.seek(0)
            f.truncate()
            json.dump(results, f)


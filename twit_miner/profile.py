import sys
import os
import unittest

sys.path.insert(0, 'crits')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['DJANGO_TESTING'] = 'true'

import crits.tests.test_recommendation as test_mod

def run():
    tl = unittest.TestLoader()
    suite = tl.loadTestsFromModule(test_mod)
    suite.run(unittest.TestResult())

if __name__ == '__main__':
    run()

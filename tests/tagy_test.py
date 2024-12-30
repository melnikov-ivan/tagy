import unittest

class TagyTest(unittest.TestCase):

    def setUp(self):
        print("SETUP!")

    def tearDown(self):
        print("TEAR DOWN!")

    def test_basic(self):
        print("I RAN!")

if __name__ == '__main__':
    unittest.main()

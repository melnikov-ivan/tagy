import unittest
import tagy
import os

class TagyTest(unittest.TestCase):
    def test_load_page(self):
        thumb = tagy.get_thumbnail("/dev-cover.png", (100, 100), "img")
        self.assertEqual(thumb, "/dev-cover-100x100.png")

    def tearDown(self):
        os.remove("img/dev-cover-100x100.png")


if __name__ == '__main__':
    unittest.main()

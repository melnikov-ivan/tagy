import unittest
import tagy
import os

class TagyTest(unittest.TestCase):

    def setUp(self):
        tagy.LAYOUT_DIR = 'layout'

    def tearDown(self):
        os.remove("public/path/index.html")
        os.rmdir("public/path")
        os.rmdir("public")


    def test_generate_page(self):
        page = tagy.Config({'title': 'title', 'content': 'content', 'layout': 'page.html', 'path': 'path'})
        site = tagy.Config({'domain': 'domain'})
        tagy.generate_page(page, site)

if __name__ == '__main__':
    unittest.main()

import unittest
import tagy
import os

class TagyTest(unittest.TestCase):

    def setUp(self):
        tagy.LAYOUT_DIR = 'layout'

    def tearDown(self):
        # os.remove("public/path/index.html")
        # os.rmdir("public/path")
        # os.rmdir("public")
        print("Clear dirs")


    def test_generate_page(self):
        page = tagy.Config({'title': 'title', 'content': 'content', 'layout': 'page.html', 'path': 'path'})
        site = tagy.Config({'domain': 'domain'})
        tagy.generate_page(page, site)

    def test_generate_index(self):
        site = tagy.Config({'domain': 'domain', 'indexes': {'tag': {'url': '/tag', 'layout': 'page.html', 'terms': []}}})
        tagy.generate_index('tag', site)

if __name__ == '__main__':
    unittest.main()

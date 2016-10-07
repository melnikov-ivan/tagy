import unittest
import sys
sys.path.append('../')
import tagy

class TagyTest(unittest.TestCase):

    def setUp(self):
        print "SETUP!"

    def tearDown(self):
        print "TEAR DOWN!"

    def test_pager(self):
        
        page = {tagy.PAGE_LAYOUT:'pager.html', tagy.PAGE_CONTENT:'text', tagy.PAGE_PATH:'pager'}
        page['list'] = ['one', 'two', 'three']
        page = tagy.Config(page)
        site = {}

        # tagy.env = Environment(loader=FileSystemLoader(layout), autoescape=False)
        tagy.generate_page(page, site)

        if not open('public/pager/index.html').read():
            return -1


if __name__ == '__main__':
    unittest.main()

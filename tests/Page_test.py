import unittest
import tagy

class TagyTest(unittest.TestCase):
    def test_load_page(self):
        page = tagy.load_page("page.md")
        self.assertEqual(page.title, "title")
        self.assertEqual(page.content, "<p>content</p>\n")


if __name__ == '__main__':
    unittest.main()

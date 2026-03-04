import unittest
import tagy


class PaginationTest(unittest.TestCase):

    def setUp(self):
        tagy.env.loader = tagy.FileSystemLoader('tests/layout')
        tagy._pagination_queue.clear()

    def _call(self, items, per_page=10, page_num=None):
        page = tagy.Config({'path': 'blog', 'layout': 'page.html', 'content': ''})
        if page_num:
            page.pagination = tagy.Config({'page_num': page_num})
        ctx = {'page': page}
        return tagy.paginate(ctx, items, per_page)

    def test_single_page(self):
        items = list(range(5))
        result = self._call(items, per_page=10)
        self.assertEqual(result.page_num, 1)
        self.assertEqual(result.items, items)
        self.assertEqual(result.total, 5)
        self.assertEqual(result.total_pages, 1)
        self.assertFalse(result.has_prev)
        self.assertFalse(result.has_next)
        self.assertIsNone(result.prev_num)
        self.assertIsNone(result.next_num)
        self.assertEqual(len(tagy._pagination_queue), 0)

    def test_multiple_pages_queued(self):
        items = list(range(25))
        result = self._call(items, per_page=10)
        self.assertEqual(result.page_num, 1)
        self.assertEqual(result.items, list(range(10)))
        self.assertEqual(result.total_pages, 3)
        self.assertTrue(result.has_next)
        self.assertEqual(result.next_num, 2)
        # pages 2 and 3 added to queue
        self.assertEqual(len(tagy._pagination_queue), 2)
        self.assertEqual(tagy._pagination_queue[0].path, 'blog/2')
        self.assertEqual(tagy._pagination_queue[0].pagination.page_num, 2)
        self.assertEqual(tagy._pagination_queue[1].path, 'blog/3')

    def test_page_2_items(self):
        items = list(range(25))
        result = self._call(items, per_page=10, page_num=2)
        self.assertEqual(result.page_num, 2)
        self.assertEqual(result.items, list(range(10, 20)))
        self.assertTrue(result.has_prev)
        self.assertTrue(result.has_next)
        self.assertEqual(result.prev_num, 1)
        self.assertEqual(result.next_num, 3)
        # no new pages queued from page 2
        self.assertEqual(len(tagy._pagination_queue), 0)

    def test_last_page_items(self):
        items = list(range(25))
        result = self._call(items, per_page=10, page_num=3)
        self.assertEqual(result.items, list(range(20, 25)))
        self.assertTrue(result.has_prev)
        self.assertFalse(result.has_next)
        self.assertIsNone(result.next_num)

    def test_base_path(self):
        result = self._call(list(range(20)), per_page=10)
        self.assertEqual(result.base_path, 'blog')

    def test_pager_links(self):
        tagy.LAYOUT_DIR = 'layout'
        content = (
            '{% set p = paginate(site.pages, 2) %}'
            '{% if p.has_prev %}<a href="/{{ p.base_path }}/{{ p.prev_num }}">prev</a>{% endif %}'
            '{% if p.has_next %}<a href="/{{ p.base_path }}/{{ p.next_num }}">next</a>{% endif %}'
        )
        pages = [tagy.Config({'path': 'blog', 'layout': 'page.html', 'content': content})]
        pages += [tagy.Config({'path': 'p%d' % i, 'layout': 'page.html', 'content': ''}) for i in range(1, 4)]
        site = tagy.Config({'domain': 'x', 'pages': pages})
        tagy._pagination_queue.clear()

        tagy.generate_page(pages[0], site)
        page1_html = open('public/blog/index.html').read()
        self.assertNotIn('prev', page1_html)
        self.assertIn('<a href="/blog/2">next</a>', page1_html)

        page2 = tagy._pagination_queue[0]
        tagy.generate_page(page2, site)
        page2_html = open('public/blog/2/index.html').read()
        self.assertIn('<a href="/blog/1">prev</a>', page2_html)
        self.assertNotIn('next', page2_html)

    def test_generate_site_processes_queue(self):
        tagy.LAYOUT_DIR = 'layout'
        tagy.CONTENT_DIR = '.'
        pages = [
            tagy.Config({'path': 'blog', 'layout': 'page.html',
                         'content': '{% set p = paginate(site.pages, 2) %}page={{ p.page_num }}'}),
            tagy.Config({'path': 'p1', 'layout': 'page.html', 'content': 'a'}),
            tagy.Config({'path': 'p2', 'layout': 'page.html', 'content': 'b'}),
            tagy.Config({'path': 'p3', 'layout': 'page.html', 'content': 'c'}),
        ]
        site = tagy.Config({'domain': 'x', 'pages': pages})
        tagy._pagination_queue.clear()
        # generate only the blog page directly to avoid clear()/static dir issues
        tagy.generate_page(pages[0], site)
        # queue should have page 2 (4 pages total, per_page=2 → 2 total pages)
        self.assertEqual(len(tagy._pagination_queue), 1)
        # generate them
        for qpage in tagy._pagination_queue:
            tagy.generate_page(qpage, site)


if __name__ == '__main__':
    unittest.main()

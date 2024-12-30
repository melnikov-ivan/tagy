import unittest
import yaml
from tagy import Config

class TagyTest(unittest.TestCase):

    def setUp(self):
        print("SETUP!")

    def tearDown(self):
        print("TEAR DOWN!")

    def test_load_config(self):
        text = """
            domain: imelnikov.ru
            file: True
            date: 2014-08-28

            indexes:
            tag : {url: /tag, layout: tag/single.html}
        """
        config = Config(yaml.safe_load(text))

        self.assertEqual(config.domain, 'imelnikov.ru')
        self.assertEqual(config.file, True)

        # why do we need this?
        self.assertTrue(isinstance(config.tag, Config))

if __name__ == '__main__':
    unittest.main()

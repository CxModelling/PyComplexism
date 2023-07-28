import unittest
from misc import *
import os


class IOTestCase(unittest.TestCase):
    def tearDown(self):
        if os.path.isfile('/txt.txt'):
            os.remove('/txt.txt')

        if os.path.isfile('/json.json'):
            os.remove('/json.json')

    def test_txt(self):
        txt_s = 'this is a test'
        save_txt(txt_s, '/txt.txt')
        self.assertTrue(os.path.isfile('/txt.txt'))
        txt_l = load_txt('/txt.txt')
        self.assertEqual(txt_s, txt_l)

    def test_json(self):
        json_s = {'A': 1, 'B': 2}
        save_json(json_s, '/json.json')
        self.assertTrue(os.path.isfile('/json.json'))
        json_l = load_json('/json.json')
        self.assertDictEqual(json_s, json_l)


if __name__ == '__main__':
    unittest.main()

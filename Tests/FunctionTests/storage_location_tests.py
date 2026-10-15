import os

from dotenv import load_dotenv
load_dotenv()

import unittest
from Functions.get_file_path import get_linux_path

class MyTestCase(unittest.TestCase):
    def test_get_linux_path(self):
        """A simple hardcoded path selection test"""

        actual = get_linux_path("test")

        expected = os.environ["PATH_SELECTION_TEST"]

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

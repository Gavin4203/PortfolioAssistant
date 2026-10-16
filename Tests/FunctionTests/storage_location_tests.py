import os

from dotenv import load_dotenv
load_dotenv()

import unittest
from Functions.get_file_path import get_linux_path
from Functions.cover_letter import cv

class MyTestCase(unittest.TestCase):
    def test_get_linux_path(self):
        """A simple hardcoded path selection test"""

        actual = get_linux_path("cover_letter")

        expected = os.environ["PATH_SELECTION_TEST"]

        self.assertEqual(expected, actual)

    def test_odt_cover_letter(self):
        """Tests cover letter is saved correctly"""
        cova_letta = cv()
        text = "Conversational Fluff.Exe Dear Hiring Manager\n\n\n\nI am pretty good at things, all the things really. You should hire me\n\n\n\n\n\n\n\n\n\nI am will be very good asset.\nSincerely\nA Cool Guy"
        actual = cv.md_to_odt.invoke({"text": text})

        expected = f"Cover Letter has been created and saved here: {os.environ['PATH_SELECTION_TEST']}.odt"

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

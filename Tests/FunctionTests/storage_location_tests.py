import os

from dotenv import load_dotenv
load_dotenv()

import unittest
from Functions.get_file_path import get_linux_path
from Functions.file_exporting import markdown_to_file as mtf

class MyTestCase(unittest.TestCase):
    def test_get_linux_path(self):
        """A simple hardcoded path selection test"""
        print("test_get_linux_path")

        actual = get_linux_path("cover_letter")

        expected = os.environ["PATH_SELECTION_TEST"]

        self.assertEqual(expected, actual)

    def test_odt_cover_letter(self):
        print("test_odt_cover_letter")
        """Tests cover letter is saved correctly"""
        text = "Conversational Fluff.Exe Dear Hiring Manager\n\n\n\nI am pretty good at things, all the things really. You should hire me\n\n\n\n\n\n\n\n\n\nI am will be very good asset.\nSincerely\nA Cool Guy"
        actual = mtf.export(text, type="cover_letter")

        expected = f"Cover Letter has been created and saved here: {os.environ['PATH_SELECTION_TEST']}"

        self.assertEqual(expected, actual)

    def test_pdf_cover_letter(self):
        """Tests cover letter is saved correctly"""
        print("test_pdf_cover_letter")
        text = "Conversational Fluff.Exe Dear Hiring Manager\n\n\n\nI am pretty good at things, all the things really. You should hire me\n\n\n\n\n\n\n\n\n\nI am will be very good asset.\nSincerely\nA Cool Guy"
        actual = mtf.export(text, type="cover_letter")

        expected = f"Cover Letter has been created and saved here: {os.environ['PDF_TEST']}"

        self.assertEqual(expected, actual)

    def test_docx_cover_letter(self):
        """Tests cover letter is saved correctly"""
        print("test_docx_cover_letter")
        text = "Conversational Fluff.Exe Dear Hiring Manager\n\n\n\nI am pretty good at things, all the things really. You should hire me\n\n\n\n\n\n\n\n\n\nI am will be very good asset.\nSincerely\nA Cool Guy"
        actual = mtf.export(text, type="cover_letter")

        expected = f"Cover Letter has been created and saved here: {os.environ['DOCX_TEST']}"

        self.assertEqual(expected, actual)

    def test_md_cover_letter(self):
        """Tests cover letter is saved correctly"""
        print("test_md_cover_letter")
        text = "Conversational Fluff.Exe Dear Hiring Manager\n\n\n\nI am pretty good at things, all the things really. You should hire me\n\n\n\n\n\n\n\n\n\nI am will be very good asset.\nSincerely\nA Cool Guy"
        actual = mtf.export(text, type="cover_letter")

        expected = f"Cover Letter has been created and saved here: {os.environ['MD_TEST']}"

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

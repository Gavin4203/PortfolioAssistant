import platform
from typing import Optional

from langchain_core.tools import tool

from . import get_file_path

import re
import pypandoc
from pathlib import Path

PANDOC_FORMATS = {
        ".odt": "odt",
        ".docx": "docx",
        ".pdf": "pdf",
        ".md": "md"
    }

class markdown_to_file:
    @staticmethod
    def export(text, type):
        """
        Saves a completed cover letter into a LibreOffice .odt document.
        Call this tool whenever the user asks to make, write, create, draft, or generate a cover letter.

        Args:
            text: The complete multi-paragraph cover letter text ONLY. Separate paragraphs with double newlines.
            type: The type of file we are making. For example, cover_letter means we are making a cover letter.
        """

        try:
            if platform.system() == "Linux":
                path = get_file_path.get_linux_path("default_filename")
            else:
                path = get_file_path.get_windows_mac_path()
        except Exception as e:
            return f"There was a problem getting the file path\n{e}"

        suffix = PANDOC_FORMATS.get(Path(path).suffix)

        if not suffix:
            return f"Unsupported file extension '{suffix}'. Supported: {', '.join(PANDOC_FORMATS.keys())}"

        success, clean_md = markdown_to_file.clean_markdown(text, type)

        if not success:
            return clean_md

        try:
            output = f"{path}"

            pypandoc.convert_text(
                clean_md,
                suffix,
                format='md',
                outputfile=output
            )

        except Exception as e:
            return f"There was a problem saving the file\n{e}"

        return f"Cover Letter has been created and saved here: {output}"

    @staticmethod
    def clean_markdown(text, type):
        """
        Cleans the llm markdown output

        Args:
            text: The complete multi-paragraph cover letter text ONLY. Separate paragraphs with double newlines.
            type: The type of file we are making. For example, cover_letter means we are making a cover letter.
        """
        # 1. Strip any conversational fluff
        clean_md = markdown_to_file.strip_convo_fluff(text, type)

        # 2. Check length AFTER stripping fluff so preamble doesn't spoof the character count
        if len(clean_md) < 100:
            return (
                False,
                f"ERROR: The 'text' argument passed to 'md_to_odt' was too short ({len(clean_md)} chars). "
                "Please try again and pass the ENTIRE object and wrap it in its correct tag."
            )

        if type == "cover_letter":
            # 3-4. Force cover letter formatting
            clean_md = markdown_to_file.cover_letter_formatting(clean_md)
        elif type == "resume":
            clean_md = markdown_to_file.resume_formatting(clean_md)

        # 5. Normalize any single, double, or quadruple newlines into clean double newlines for Pandoc
        clean_md = re.sub(r"\n+", "\n\n", clean_md)

        return (True, clean_md)

    @staticmethod
    def strip_convo_fluff(text, type):
        """
        Strips conversational fluff from cover letters and resumes

        Args:
            text: The complete multi-paragraph cover letter text ONLY. Separate paragraphs with double newlines.
            type: The type of file we are making. For example, cover_letter means we are making a cover letter.
        """
        clean_md = ""

        if type == "cover_letter":
            clean_md = re.sub(r"^.*?(?=Dear\s)", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
        elif type == "resume":
            clean_md = re.sub(r"^.*?(?=Dear\s)", "", text, flags=re.DOTALL | re.IGNORECASE).strip()

        return clean_md

    @staticmethod
    def cover_letter_formatting(clean_md):
        # 3. Force newlines after the greeting if the LLM mashed them together
        clean_md = re.sub(r"(Dear\s+[^,\n]+,)\s*", r"\1\n\n", clean_md)

        # 4. Force newlines before/after "Sincerely," and Title-Case the user's name
        clean_md = re.sub(
            r"\s*(Sincerely,)\s*([a-zA-Z\s]+)$",
            lambda m: f"\n\nSincerely,\n\n{m.group(2).strip().title()}",
            clean_md,
            flags=re.IGNORECASE
        )

        return clean_md

    @staticmethod
    def resume_formatting(clean_md):
        # 1. Remove any stray [Your Contact Info] placeholders if the LLM still output one
        cleaned = re.sub(r"^.*\[Your Contact Info\].*\n?", "", clean_md, flags=re.MULTILINE | re.IGNORECASE)

        # 2. Ensure there is a blank line before every Markdown header (#, ##, ###)
        cleaned = re.sub(r"([^\n])\n(#{1,3}\s+)", r"\1\n\n\2", cleaned)

        # 3. CRITICAL FOR PANDOC: Ensure a blank line between a header/line and the first bullet point (- or *)
        # Without this blank line, Pandoc turns bullet lists into flat paragraphs!
        cleaned = re.sub(r"^(#{1,4}\s+.*)\n(\s*[-*•]\s+)", r"\1\n\n\2", cleaned, flags=re.MULTILINE)

        # 4. Convert any Unicode '•' bullets into standard Markdown '- ' bullets
        cleaned = re.sub(r"^\s*•\s+", "- ", cleaned, flags=re.MULTILINE)

        return cleaned.strip()
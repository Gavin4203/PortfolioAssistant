import platform
from typing import Optional

from langchain_core.tools import tool

from . import get_file_path

import re
import pypandoc
from pathlib import Path

class cv:

    @staticmethod
    def md_to_odt(text):
        """
        Saves a completed cover letter into a LibreOffice .odt document.
        Call this tool whenever the user asks to make, write, create, draft, or generate a cover letter.

        Args:
            text: The complete multi-paragraph cover letter text ONLY. Separate paragraphs with double newlines.
        """

        default_filename = "cover_letter"
        path = "None"

        # 1. Strip any conversational fluff before "Dear..." FIRST
        clean_md = re.sub(r"^.*?(?=Dear\s)", "", text, flags=re.DOTALL | re.IGNORECASE).strip()

        # 2. Check length AFTER stripping fluff so preamble doesn't spoof the character count
        if len(clean_md) < 100:
            return (
                f"ERROR: The 'text' argument passed to 'md_to_odt' was too short ({len(clean_md)} chars). "
                "Please call 'md_to_odt' again and pass the ENTIRE multi-paragraph cover letter inside the 'text' argument."
            )

        # 3. Force newlines after the greeting if the LLM mashed them together
        clean_md = re.sub(r"(Dear\s+[^,\n]+,)\s*", r"\1\n\n", clean_md)

        # 4. Force newlines before/after "Sincerely," and Title-Case the user's name
        clean_md = re.sub(
            r"\s*(Sincerely,)\s*([a-zA-Z\s]+)$",
            lambda m: f"\n\nSincerely,\n\n{m.group(2).strip().title()}",
            clean_md,
            flags=re.IGNORECASE
        )

        # 5. Normalize any single, double, or quadruple newlines into clean double newlines for Pandoc
        clean_md = re.sub(r"\n+", "\n\n", clean_md)

        try:
            if platform.system() == "Linux":
                path = get_file_path.get_linux_path(default_filename)
            else:
                path = get_file_path.get_windows_mac_path()
        except Exception as e:
            return f"There was a problem getting the file path\n{e}"

        try:
            output = f"{path}.odt"

            pypandoc.convert_text(
                clean_md,
                'odt',
                format='md',
                outputfile=output
            )

        except Exception as e:
            return f"There was a problem saving the file\n{e}"

        return f"Cover Letter has been created and saved here: {output}"
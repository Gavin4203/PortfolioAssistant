import platform
from typing import Optional

from langchain_core.tools import tool

from . import get_file_path

import re
import pypandoc
from pathlib import Path

class cv:

    @staticmethod
    @tool
    def md_to_odt(text: str, file_name: str = "cover_letter", storage_location: Optional[str]="None"):
        """
            Saves a completed Markdown cover letter into a LibreOffice .odt file.

            Ground every claim in the user's actual projects from search_query without mixing technologies between projects
            keep a direct natural tone, and sign off with 'Sincerely, User's Name'
            Ensure the User's name is capitalized.

            Args:
                text: The complete multi-paragraph Markdown cover letter text.
                file_name: The name of the file without extension. Defaults to 'cover_letter'.
                storage_location: Optional folder path. Leave as 'None' to open the GUI folder picker.
        """

        clean_md = text.replace("\\n", "\n")

        if len(clean_md) < 100:
            return (
                "ERROR: The text passed to 'llm_md_cv' was too short "
                f"({len(clean_md)} chars). Please call this tool again and pass the "
                "ENTIRE mult-paragraph cover letter text inside 'llm_md_cv'."
            )

        clean_md = re.sub(r"\n+", "\n\n", clean_md).strip()

        if storage_location == "None" or storage_location == "":
            try:
                if platform.system() == "Linux":
                    storage_location = get_file_path.get_linux_path(file_name)
                else:
                    storage_location = get_file_path.get_windows_mac_path()
            except Exception as e:
                return f"There was a problem getting the file path\n{e}"

        try:
            output = Path(storage_location) / f"{file_name}.odt"

            pypandoc.convert_text(
                clean_md,
                'odt',
                format='md',
                outputfile=output
            )

        except Exception as e:
            return f"There was a problem saving the file\n{e}"

        return f"Cover Letter has been created and saved here: {output}"
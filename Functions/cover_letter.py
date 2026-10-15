import platform
import get_file_path
import pypandoc
from pathlib import Path

class cv:
    os_name = platform.system()

    def make_cover_letter(self, llm_md_cv, file_name="cv", storage_location=None):
        """
        This converts markdown to odt file

        :param llm_md_cv: markdown text from llm
        :param file_name: users chosen file name
        :param storage_location: user chosen directory path. Can be written out by them, or if its empty, this function will provide a gui, where the user can select directory.
        """

        if storage_location is None:
            try:
                if self.os_name == "Linux":
                    storage_location = get_file_path.get_linux_path(file_name)
                else:
                    storage_location = get_file_path.get_windows_mac_path()
            except:
                return "There was a problem getting the file path"

        try:
            output = Path(storage_location) / f"{file_name}.odt"

            pypandoc.convert_text(
                llm_md_cv,
                'odt',
                format='md',
                outputfile=output
            )

        except:
            return "There was a problem saving the file"

        return f"Cover Letter has been created and saved here: {output}"
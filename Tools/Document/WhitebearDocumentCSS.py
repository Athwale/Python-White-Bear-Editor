from typing import Dict

import tinycss
import webcolors
from wx import Colour


class WhitebearDocumentCSS:
    """
    This class represents a css file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    def __init__(self, name: str, path: str):
        """
        Create a new WhitebearDocumentCSS object.
        :param name: Name of the file.
        :param path: Full path on disk to the file
        """
        self._filename = name
        self._file_path = path
        self._color_dict = {}
        self._parse_self()

    def _parse_self(self) -> None:
        """
        Parse this css document and get the colors defined in it.
        :return: None
        """
        parser = tinycss.make_parser('page3')
        stylesheet = parser.parse_stylesheet_file(self._file_path)
        print(stylesheet.errors)

        for rule in stylesheet.rules:
            if rule.selector.as_css().startswith('.'):
                if len(rule.declarations) == 2:
                    dec_names = []
                    dec_color = None
                    for declaration in rule.declarations:
                        dec_names.append(declaration.name)
                        if declaration.name == 'color':
                            dec_color = webcolors.hex_to_rgb(declaration.value.as_css())
                    # This means we have a text color declaration
                    if dec_names == ['color', 'display']:
                        color = Colour(dec_color.red, dec_color.green, dec_color.blue)
                        self._color_dict[rule.selector.as_css().lstrip('.')] = color

        print(self._color_dict)

    def get_colors(self) -> Dict[str, Colour]:
        """
        Return a dictionary of color defined in this css document.
        :return: a dictionary of color defined in this css document.
        """
        return self._color_dict

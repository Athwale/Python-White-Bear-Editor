from typing import Dict

import tinycss
import webcolors
from wx import Colour
from wx import NullColour
from wx import BLUE

from Constants.Constants import Strings
from Exceptions.WrongFormatException import WrongFormatException


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
        # Prepare the color dictionary with a black color which is always the default text color.
        self._str_to_color_dict = {Strings.color_black: Colour(0, 0, 0)}
        self._parse_self()

    def _parse_self(self) -> None:
        """
        Parse this css document and get the colors defined in it.
        :return: None
        """
        parser = tinycss.make_parser('page3')
        stylesheet = parser.parse_stylesheet_file(self._file_path)

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
                        self._str_to_color_dict[rule.selector.as_css().lstrip('.')] = color

    def get_colors(self) -> Dict[str, Colour]:
        """
        Return a dictionary of color defined in this css document.
        :return: a dictionary of color defined in this css document.
        """
        return self._str_to_color_dict

    def translate_str_color(self, name: str) -> Colour:
        """
        Translate a CSS color name into a wx.Colour
        :param name: the name of the color.
        :return: an instance of wx.Colour
        """
        try:
            return self._str_to_color_dict[name]
        except KeyError as _:
            raise WrongFormatException(Strings.exception_unrecognized_color + ': ' + str(name))

    def translate_color_str(self, color: Colour) -> str:
        """
        Decode wx.Colour into string of the loaded color from css.
        :param color: the wx.Colour to translate.
        :return: The css name of the color.
        """
        if color == NullColour:
            # Special case of empty paragraph which should by default be black.
            return Strings.color_black
        if color == BLUE:
            # Special case, deleted link color attribute remains blue for some reason.
            return Strings.color_black
        # wx.Colour can not be used as a key, so we have to find it this way.
        for name, rgb in self._str_to_color_dict.items():
            if rgb == color:
                return name
        raise WrongFormatException(Strings.exception_unrecognized_color + ': ' + str(color))
